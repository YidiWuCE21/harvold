from django.test import TestCase
from pokemon import models


class TestGetXpForLevel(TestCase):
    def test_max_level(self):
        ret = models.get_xp_for_level(100, "medium-fast")
        exp = 1000000
        self.assertEqual(exp, ret)


    def test_zero(self):
        with self.assertRaisesRegex(ValueError, 'lower'):
            models.get_xp_for_level(0, "medium-fast")


class TestGetLevelups(TestCase):
    def test_level_once(self):
        ret = models.get_levelups(5, 220, "medium-fast")
        exp = 1
        self.assertEqual(exp, ret)

        ret = models.get_levelups(5, 180, "fast")
        exp = 1
        self.assertEqual(exp, ret)

        ret = models.get_levelups(5, 190, "medium-slow")
        exp = 1
        self.assertEqual(exp, ret)

        ret = models.get_levelups(5, 277, "slow")
        exp = 1
        self.assertEqual(exp, ret)

        ret = models.get_levelups(5, 406, "erratic")
        exp = 1
        self.assertEqual(exp, ret)

        ret = models.get_levelups(5, 112, "fluctuating")
        exp = 1
        self.assertEqual(exp, ret)


    def test_level_exact(self):
        ret = models.get_levelups(5, 216, "medium-fast")
        exp = 1
        self.assertEqual(exp, ret)

        ret = models.get_levelups(5, 172, "fast")
        exp = 1
        self.assertEqual(exp, ret)

        ret = models.get_levelups(5, 179, "medium-slow")
        exp = 1
        self.assertEqual(exp, ret)

        ret = models.get_levelups(5, 270, "slow")
        exp = 1
        self.assertEqual(exp, ret)

        ret = models.get_levelups(5, 406, "erratic")
        exp = 1
        self.assertEqual(exp, ret)

        ret = models.get_levelups(5, 112, "fluctuating")
        exp = 1
        self.assertEqual(exp, ret)

    def test_no_level(self):
        ret = models.get_levelups(5, 215, "medium-fast")
        exp = 0
        self.assertEqual(exp, ret)

    def test_overlevel(self):
        ret = models.get_levelups(5, 2000, "medium-fast")
        exp = 7
        self.assertEqual(exp, ret)


class TestGetProgressToNextLevel(TestCase):
    def test_min_xp(self):
        ret = models.get_progress_to_next_level(1, 1, "medium-fast")
        exp = 12.5
        self.assertAlmostEqual(exp, ret)

    def test_levelup(self):
        ret = models.get_progress_to_next_level(1, 9, "medium-fast")
        exp = 112.5
        self.assertAlmostEqual(exp, ret, places=1)

    def test_max_xp(self):
        ret = models.get_progress_to_next_level(100, 1000000, "medium-fast")
        exp = 0
        self.assertEqual(exp, ret)

    def test_before_max(self):
        ret = models.get_progress_to_next_level(99, 999990, "medium-fast")
        exp = 99.97
        self.assertAlmostEqual(exp, ret, places=1)

    def test_levelup_exact(self):
        ret = models.get_progress_to_next_level(99, 1000000, "medium-fast")
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


class TestGetBaseStats(TestCase):
    def test_int_dex(self):
        ret = models.get_base_stats(1)
        exp = {
            "hp": 45,
            "atk": 49,
            "def": 49,
            "spa": 65,
            "spd": 65,
            "spe": 45
        }
        self.assertDictEqual(exp, ret)


    def test_standard_dex(self):
        ret = models.get_base_stats("001")
        exp = {
            "hp": 45,
            "atk": 49,
            "def": 49,
            "spa": 65,
            "spd": 65,
            "spe": 45
        }
        self.assertDictEqual(exp, ret)


class TestGetNatureMultiplier(TestCase):
    def test_boosted_stat(self):
        ret = models.get_nature_multiplier("adamant", "atk")
        exp = 1.1
        self.assertEqual(exp, ret)


    def test_reduced_stat(self):
        ret = models.get_nature_multiplier("adamant", "spa")
        exp = 0.9
        self.assertEqual(exp, ret)


    def test_neutral_stat(self):
        ret = models.get_nature_multiplier("adamant", "def")
        exp = 1.0
        self.assertEqual(exp, ret)


    def test_neutral_nature(self):
        ret = models.get_nature_multiplier("serious", "def")
        exp = 1.0
        self.assertEqual(exp, ret)


class TestCreatePokemon(TestCase):
    def test_create_starter(self):
        ret = models.create_pokemon("001", 5, "m")
        # Check moves
        self.assertEqual("Tackle", ret.move1)
        self.assertEqual(35, ret.move1_pp)
        self.assertEqual("Growl", ret.move2)
        self.assertEqual(40, ret.move2_pp)

        # Check HP
        self.assertEqual(ret.hp_stat, ret.current_hp)

        # Check stat calculation successful
        self.assertGreater(ret.hp_stat, 0)
        self.assertGreater(ret.atk_stat, 0)
        self.assertGreater(ret.def_stat, 0)
        self.assertGreater(ret.spa_stat, 0)
        self.assertGreater(ret.spd_stat, 0)
        self.assertGreater(ret.spe_stat, 0)
        # Check no trainer yet
        self.assertIsNone(ret.trainer)
        self.assertIsNone(ret.original_trainer)


class TestAssignTrainer(TestCase):
    def test_assign_trainer(self):
        self.assertFalse(True)


class TestRecalculateStats(TestCase):
    def test_recalculate_stats(self):
        self.assertFalse(True)


class TestRestoreHp(TestCase):
    def test_restore_hp(self):
        self.assertFalse(True)


class TestRestorePp(TestCase):
    def test_restore_pp(self):
        self.assertFalse(True)


class TestCureStatus(TestCase):
    def test_no_status(self):
        self.assertFalse(True)