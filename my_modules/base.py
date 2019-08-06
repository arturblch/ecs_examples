from collections import namedtuple
import math

from entitas import Matcher, ReactiveProcessor, ExecuteProcessor, EntityIndex

Position = namedtuple('Position', 'x y')
Speed = namedtuple('Speed', 'x y')
CircularZone = namedtuple('CircularZone', 'radius')
Score = namedtuple('Score', 'cur_score max_score') 
InvadersList = namedtuple('InvadersList', 'inv_ids_list') 
Owner = namedtuple('Owner', 'owner_team_id')
Team = namedtuple('Team', 'team_id')

Invader = namedtuple('Invader', '')
Movable = namedtuple('Movable', '')

def configure_point(entity):
    entity.add(Position, 3, 3)
    entity.add(Speed, -1, -1)
    entity.add(Movable)
    entity.add(Team, 1)

def configure_base(entity): 
    entity.add(Position, 1, 1) 
    entity.add(CircularZone, 2) 
    entity.add(Score, 0, 100) 
    entity.add(InvadersList, []) 
    entity.add(Owner, 0) 


class TrigerZoneProcessor(ExecuteProcessor):

    def __init__(self, context):
        self._zoneGroup = context.get_group(Matcher(CircularZone, Position, InvadersList))
        self._pointsGroup = context.get_group(Matcher(Position, Movable))

    def execute(self):
        for zone in self._zoneGroup.entities:

            zone_pos = zone.get(Position)
            circular_zone = zone.get(CircularZone)
            invIdList = zone.get(InvadersList).inv_ids_list

            for point in self._pointsGroup.entities:
                point_pos = point.get(Position)

                dist = math.sqrt(
                    pow(point_pos.x - zone_pos.x, 2) +
                    pow(point_pos.y - zone_pos.y, 2)
                )

                if dist < circular_zone.radius and point._creation_index  not in invIdList:
                    point.add(Invader)
                    invIdList.append(point._creation_index)
                    zone.replace(InvadersList, invIdList)
                elif dist >= circular_zone.radius and point._creation_index  in invIdList:
                    point.remove(Invader)
                    invIdList.remove(point._creation_index)
                    zone.replace(InvadersList, invIdList)

class ScoreZoneProcessor(ExecuteProcessor):

    def __init__(self, context):
        self._zoneGroup = context.get_group(Matcher(CircularZone, Position, InvadersList))
        self._invaderGroup = context.get_group(Matcher(Invader))

    def execute(self):
        for zone in self._zoneGroup.entities:
            invIdList = zone.get(InvadersList).inv_ids_list
            score = zone.get(Score)
            owner = zone.get(Owner)
            if not invIdList:
                continue

            zoneInvaders = [point for point in self._invaderGroup.entities if point._creation_index in invIdList]
            scoreDiff = 0
            for point in zoneInvaders:
                scoreDiff = 0

                team = point.get(Team)

                if team.team_id == owner.owner_team_id:
                    scoreDiff += 1
                else:
                    scoreDiff -= 1
            newScore = max(min(score.cur_score + scoreDiff, score.max_score), -100)
            zone.replace(Score, newScore, score.max_score)



class MoveProcessor(ExecuteProcessor):

    def __init__(self, context):
        super().__init__(context)
        self._group = context.get_group(Matcher(Movable, Position, Speed))

    def execute(self, entities):
        for entity in self._group.entities:
            entity.get(Position).x += entity.get(Speed).x
            entity.get(Position).y += entity.get(Speed).y
