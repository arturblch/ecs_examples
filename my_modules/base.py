from collections import namedtuple, defaultdict
import math

from entitas import Matcher, ReactiveProcessor, ExecuteProcessor, EntityIndex, GroupEvent

Position = namedtuple('Position', 'x y')
Speed = namedtuple('Speed', 'x y')
CircularZone = namedtuple('CircularZone', 'radius')
Score = namedtuple('Score', 'cur_score max_score score_team_id') 
ScoreList = namedtuple('ScoreList', 'score_items_list') 
Owner = namedtuple('Owner', 'owner_team_id')
Team = namedtuple('Team', 'team_id')

Invader = namedtuple('Invader', 'zone_id')
Movable = namedtuple('Movable', '')

def configure_point(entity):
    entity.add(Position, 3, 3)
    entity.add(Speed, -1, -1)
    entity.add(Movable)
    entity.add(Team, 1)

def configure_base(entity): 
    entity.add(Position, 1, 1) 
    entity.add(CircularZone, 2) 
    entity.add(Score, 0, 100, 0)
    entity.add(Owner, 0) 


class TriggerZoneProcessor(ExecuteProcessor):

    def __init__(self, context):
        self._zoneGroup = context.get_group(Matcher(CircularZone, Position))
        self._outPointsGroup = context.get_group(
            Matcher(
                all_of=(Position, Movable),
                none_of=(Invader, )
            )
        )
        self._inPointsGroup = context.get_group(Matcher(Position, Movable, Invader))

    def execute(self):
        for zone in self._zoneGroup.entities:
            zone_pos = zone.get(Position)
            circular_zone = zone.get(CircularZone)
            in_list = self._inPointsGroup.entities.copy()
            out_list = self._outPointsGroup.entities.copy()
            for point in in_list:
                point_pos = point.get(Position)

                dist = math.sqrt(
                    pow(point_pos.x - zone_pos.x, 2) +
                    pow(point_pos.y - zone_pos.y, 2)
                )

                if dist >= circular_zone.radius and point.get(Invader).zone_id == zone._creation_index:
                    point.remove(Invader)

            for point in out_list:
                point_pos = point.get(Position)

                dist = math.sqrt(
                    pow(point_pos.x - zone_pos.x, 2) +
                    pow(point_pos.y - zone_pos.y, 2)
                )

                if dist < circular_zone.radius:
                    point.add(Invader, zone._creation_index)

class ScoreZoneProcessor(ExecuteProcessor):

    def __init__(self, context):
        self._zoneGroup = context.get_group(Matcher(CircularZone, Position))
        self._invaderGroup = context.get_group(Matcher(Invader))

    def execute(self):
        for zone in self._zoneGroup.entities:
            score = zone.get(Score)
            zoneInvaders = [point for point in self._invaderGroup.entities if point.get(Invader).zone_id == zone._creation_index]
            if not zoneInvaders:
                continue

            teamScores = defaultdict(int)
            for point in zoneInvaders:
                team = point.get(Team)
                teamScores[team.team_id] += 1


            if score.score_team_id == 0:
                scoreDiff = teamScores[1] - teamScores[2]
                if scoreDiff == 0:
                    continue

                newScore = scoreDiff
                newTeamId = 1 if newScore > 0 else 2
            else:
                invader_team = 1 if score.score_team_id == 2 else 2
                scoreDiff = teamScores[score.score_team_id] - teamScores[invader_team]
                if scoreDiff == 0:
                    continue

                newScore =  score.cur_score + scoreDiff
                if newScore > 0:
                    newTeamId = score.score_team_id
                elif newScore < 0:
                    newTeamId = invader_team
                else:
                    newTeamId = 0

            newScore = abs(newScore)                        
            newScore = max(min(newScore, score.max_score), 0)
            
            if newScore != score.cur_score or newTeamId != score.score_team_id:
                zone.replace(Score, newScore, score.max_score, newTeamId)


class CaptureZoneProcessor(ReactiveProcessor):
    def get_trigger(self):
        return {Matcher(Score): GroupEvent.ADDED}

    def filter(self, entity):
        return entity.has(Score)

    def react(self, entities):
        print('entities are ', entities)
        for entity in entities:
            score = entity.get(Score)
            if score.cur_score == score.max_score:
                entity.replace(Owner, score.score_team_id)


class MoveProcessor(ExecuteProcessor):

    def __init__(self, context):
        super().__init__(context)
        self._group = context.get_group(Matcher(Movable, Position, Speed))

    def execute(self, entities):
        for entity in self._group.entities:
            entity.get(Position).x += entity.get(Speed).x
            entity.get(Position).y += entity.get(Speed).y
