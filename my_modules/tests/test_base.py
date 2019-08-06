import pytest
from entitas import Context, Matcher
from my_modules import base


class TestBaseSystems(object):
    def setup_method(self, method):
        print('=== setup_method === ')
        self.context = Context()
        point = self.context.create_entity()
        base.configure_point(point)
        zone = self.context.create_entity()
        base.configure_base(zone)

    def teardown_method(self, method):
        print('=== teardown_method === ')

    def test_triger_zone_processor(self):
        processor = base.TrigerZoneProcessor(self.context)
        point = self.context.get_group(Matcher(base.Movable)).single_entity

        point.replace(base.Position, 1, 1)
        processor.execute()

        assert point.has(base.Invader)

        point.replace(base.Position, 3, 3)
        processor.execute()

        assert not point.has(base.Invader)

    def test_score_zone_processor(self):
        processor = base.ScoreZoneProcessor(self.context)

        point = self.context.get_group(Matcher(base.Movable)).single_entity
        point.add(base.Invader)

        zone = self.context.get_group(Matcher(base.CircularZone)).single_entity
        zone.get(base.InvadersList).inv_ids_list.append(point._creation_index)

        assert zone.get(base.Score).cur_score == 0

        processor.execute()

        assert zone.get(base.Score).cur_score == -1
