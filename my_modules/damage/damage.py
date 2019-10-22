
from collections import namedtuple, defaultdict
import itertools
import math

from entitas import Matcher, ReactiveProcessor, ExecuteProcessor, EntityIndex, GroupEvent
from collision import Collision

Damage = namedtuple('Damage', 'value')


class DamageByCollisionProcessor(ReactiveProcessor):
    def get_trigger(self):
        return {Matcher(Collision): GroupEvent.ADDED}

    def filter(self, entity):
        return entity.has(Collision)

    def react(self, entities):
        print('entities are ', entities)
        for entity in entities:
            entity.add(Damage, 1)
