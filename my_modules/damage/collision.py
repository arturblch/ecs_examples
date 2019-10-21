from collections import namedtuple, defaultdict
import itertools
import math

from entitas import Matcher, ReactiveProcessor, ExecuteProcessor, EntityIndex, GroupEvent


Collider2D = namedtuple('Collider2D', 'maxX maxY minX minY')
Collidable = namedtuple('Collidable', '')
Collision = namedtuple('Collision', '')


def configure_collidable(entity, point):
    entity.add(Collider2D, 1 + point, 1+point, 0+point, 0+point)
    entity.add(Collidable)

class CollisionProcessor(ExecuteProcessor):
    
    def __init__(self, context)
        self._collidableGroup = context.get_group(Matcher(Collider2D, Collidable))

    def execute(self):
        for a, b in itertools.permutations(self._collidableGroup.entities, 2):
            if self.intersect(a.get(Collider2D), b.get(Collider2D)):
                a.add(Collision)

    @staticmethod
    def intersect(a, b):
        return (a.minX <= b.maxX and a.maxX >= b.minX) and
               (a.minY <= b.maxY and a.maxY >= b.minY)

def collider_modifier(entity, next_point):
    entity.replace(Collider2D, 1 + next_point, 1+next_point, 0+next_point, 0+next_point)
