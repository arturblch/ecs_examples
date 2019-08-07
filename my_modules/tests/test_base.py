import pytest
from entitas import Context, Matcher
from my_modules import base


class TestBaseSystems(object):
    def setup_method(self, method):
        self.context = Context()
        point = self.context.create_entity()
        base.configure_point(point)
        zone = self.context.create_entity()
        base.configure_base(zone)

    def teardown_method(self, method):
        pass

    def test_triger_zone_processor(self):
        processor = base.TriggerZoneProcessor(self.context)
        point = self.context.get_group(Matcher(base.Movable)).single_entity
        zone = self.context.get_group(Matcher(base.CircularZone)).single_entity

        point.replace(base.Position, 1, 1)
        processor.execute()

        assert point.has(base.Invader)

        point.replace(base.Position, 3, 3)
        processor.execute()

        assert not point.has(base.Invader)

    def test_score_zone_processor(self):
        processor = base.ScoreZoneProcessor(self.context)

        point = self.context.get_group(Matcher(base.Movable)).single_entity
        zone = self.context.get_group(Matcher(base.CircularZone)).single_entity

        point.add(base.Invader,  zone._creation_index)

        assert zone.get(base.Score).cur_score == 0
        assert zone.get(base.Score).score_team_id == 0

        processor.execute()

        assert zone.get(base.Score).cur_score == 1
        assert zone.get(base.Score).score_team_id == 1

        point.replace(base.Team, 2)

        processor.execute()

        assert zone.get(base.Score).cur_score == 0
        assert zone.get(base.Score).score_team_id == 0

        processor.execute()

        assert zone.get(base.Score).cur_score == 1
        assert zone.get(base.Score).score_team_id == 2

    def test_capture_zone_precessor(self):
        processor = base.CaptureZoneProcessor(self.context)
        processor.activate()

        zone = self.context.get_group(Matcher(base.CircularZone)).single_entity
        zone.replace(base.Score, 5, 10, 1)

        processor.execute()
        assert zone.get(base.Owner).owner_team_id == 0

        zone.replace(base.Score, 10, 10, 1)

        processor.execute()
        assert zone.get(base.Owner).owner_team_id == 1
