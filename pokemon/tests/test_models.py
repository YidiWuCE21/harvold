from django.test import TestCase
from pokemon import models


class TestGetXpForLevel(TestCase):
    def test_max_level(self):
        ret = models.get_xp_for_level(1000000, 100)
        exp = 1000000
        self.assertEqual(exp, ret)


    def test_zero(self):
        with self.assertRaisesRegex(ValueError, 'lower'):
            models.get_xp_for_level(1000000, 0)


class TestGetProgressToNextLevel(TestCase):
    def test_min_xp(self):
        ret = models.get_progress_to_next_level(1000000, 1, 1)
        exp = 0
        self.assertAlmostEqual(exp, ret)

    def test_levelup(self):
        ret = models.get_progress_to_next_level(1000000, 1, 9)
        exp = 114.29
        self.assertAlmostEqual(exp, ret, places=1)

    def test_max_xp(self):
        ret = models.get_progress_to_next_level(1000000, 100, 1000000)
        exp = 0
        self.assertEqual(exp, ret)

    def test_before_max(self):
        ret = models.get_progress_to_next_level(1000000, 99, 999990)
        exp = 99.97
        self.assertAlmostEqual(exp, ret, places=1)

    def test_levelup_exact(self):
        ret = models.get_progress_to_next_level(1000000, 99, 1000000)
        exp = 100
        self.assertAlmostEqual(exp, ret, places=1)


class TestPopulateMoveset(TestCase):
    def test_starter_case(self):
        ret = models.populate_moveset("001", 5)
        exp = ["tackle", "growl"]
        self.assertListEqual(exp, ret)

    def test_beldum(self):
        ret = models.populate_moveset("374", 100)
        exp = ["takedown"]
        self.assertListEqual(exp, ret)

    def test_more_moves(self):
        ret = models.populate_moveset("003", 100)
        exp = ["worryseed", "synthesis", "petalblizzard", "solarbeam"]
        self.assertListEqual(exp, ret)