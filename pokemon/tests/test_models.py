from django.test import TestCase
from django.contrib.auth.models import User
from pokemon import models
from accounts.models import Profile
from harvoldsite import consts


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
        self.assertEqual("tackle", ret.move1)
        self.assertEqual(35, ret.move1_pp)
        self.assertEqual("growl", ret.move2)
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


class TestGetBattleInfo(TestCase):
    def test_get_battle_info_standard(self):
        self.pkmn = models.create_pokemon("001", 5, "m", ability_override="Chlorophyll", iv_override={stat: 0 for stat in consts.STATS}, nature_override="bashful")
        ret = self.pkmn.get_battle_info()
        exp = {
            "ability": "Chlorophyll",
            "status": "",
            "status_turns": 0,
            "current_hp": 19,
            "happiness": 70,
            "held_item": None,
            "moves": [
                {"move": "tackle", "pp": 35},
                {"move": "growl", "pp": 40},
                {"move": None, "pp": None},
                {"move": None, "pp": None}
            ],
            "stats": {"atk": 9, "def": 9, "hp": 19, "spa": 11, "spd": 11, "spe": 9},
            "dex_number": "001",
            "level": 5,
            "shiny": False,
            "id": self.pkmn.pk,
            "name": "Bulbasaur"
        }
        self.assertDictEqual(exp, ret)


class TestSetBattleInfo(TestCase):
    def test_set_battle_info_standard(self):
        self.pkmn = models.create_pokemon("001", 5, "m")
        battle_info = {
            "current_hp": 0,
            "status": "brn",
            "moves": [
                {"move": "tackle", "pp": 0},
                {"move": "growl", "pp": 2},
                {"move": None, "pp": None},
                {"move": None, "pp": None}
            ]
        }
        self.pkmn.set_battle_info(battle_info)
        self.assertEqual(0, self.pkmn.current_hp)
        self.assertEqual("brn", self.pkmn.status)
        self.assertEqual(0, self.pkmn.move1_pp)
        self.assertEqual(2, self.pkmn.move2_pp)
        self.assertEqual(None, self.pkmn.move3_pp)
        self.assertEqual(None, self.pkmn.move4_pp)


class TestAssignTrainer(TestCase):
    def setUp(self):
        self.pkmn1 = models.create_pokemon("001", 5, "m")
        self.pkmn2 = models.create_pokemon("001", 5, "m")
        self.user1 = User(username="test1", password="test1", email="test1@test.com")
        self.user1.save()
        self.user2 = User(username="test2", password="test2", email="test2@test.com")
        self.user2.save()
        self.trainer1 = Profile(character="01", user=self.user1)
        self.trainer1.save()
        self.trainer2 = Profile(character="02", user=self.user2)
        self.trainer2.save()


    def test_assign_trainer(self):
        self.pkmn1.assign_trainer(self.trainer1, "pokeball")
        self.assertEqual(self.pkmn1.trainer, self.trainer1)


    def test_assign_trainer_ot(self):
        self.pkmn2.assign_trainer(self.trainer1, "pokeball")
        self.pkmn2.assign_trainer(self.trainer2)
        self.assertEqual(self.pkmn2.trainer, self.trainer2)
        self.assertEqual(self.pkmn2.original_trainer, self.trainer1)


class TestRelease(TestCase):
    def setUp(self):
        self.pkmn1 = models.create_pokemon("001", 5, "m")
        self.pkmn2 = models.create_pokemon("001", 5, "m")
        self.user1 = User(username="test1", password="test1", email="test1@test.com")
        self.user1.save()
        self.trainer1 = Profile(character="01", user=self.user1)
        self.trainer1.save()
        self.pkmn1.assign_trainer(self.trainer1)
        self.pkmn2.assign_trainer(self.trainer1)


    def test_release_standard(self):
        self.assertIsNotNone(self.pkmn1.trainer)
        self.pkmn1.release(self.trainer1)
        self.assertIsNone(self.pkmn1.trainer)
        self.assertEqual("released", self.pkmn1.location)


    def test_release_not_in_box(self):
        self.assertIsNotNone(self.pkmn2.trainer)
        self.trainer1.add_to_party(self.pkmn2)
        ret = self.pkmn2.release(self.trainer1)
        self.assertIsNotNone(self.pkmn2.trainer)
        self.assertEqual("party", self.pkmn2.location)
        self.assertEqual("Only box pokemon can be released.", ret)


    def test_release_not_owned(self):
        self.assertIsNotNone(self.pkmn2.trainer)
        self.trainer1.add_to_party(self.pkmn2)
        ret = self.pkmn2.release("not trainer")
        self.assertIsNotNone(self.pkmn2.trainer)
        self.assertEqual("party", self.pkmn2.location)
        self.assertEqual("Cannot release Pokemon you don't own!", ret)


class TestAddXp(TestCase):
    def test_levelup(self):
        self.pkmn = models.create_pokemon("001", 5, "m")
        self.pkmn.add_xp(110)
        self.assertEqual(7, self.pkmn.level)


    def test_no_level(self):
        self.pkmn = models.create_pokemon("001", 5, "m")
        self.pkmn.add_xp(40)
        self.assertEqual(5, self.pkmn.level)


class TestAddEvs(TestCase):
    def test_add_evs_new(self):
        self.pkmn = models.create_pokemon("001", 5, "m")
        self.pkmn.add_evs([200, 0, 0, 0, 0, 0])
        self.assertEqual(200, self.pkmn.hp_ev)


    def test_add_evs_existing(self):
        self.pkmn = models.create_pokemon("001", 5, "m", ev_override={
            "hp": 200, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0
        })
        self.pkmn.add_evs([10, 0, 0, 0, 0, 0])
        self.assertEqual(210, self.pkmn.hp_ev)


    def test_add_evs_stat_cap(self):
        self.pkmn = models.create_pokemon("001", 5, "m", ev_override={
            "hp": 250, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0
        })
        self.pkmn.add_evs([10, 0, 0, 0, 0, 0])
        self.assertEqual(252, self.pkmn.hp_ev)


    def test_add_evs_total_cap(self):
        self.pkmn = models.create_pokemon("001", 5, "m", ev_override={
            "hp": 0, "atk": 252, "def": 252, "spa": 0, "spd": 0, "spe": 0
        })
        self.pkmn.add_evs([10, 0, 0, 0, 0, 0])
        self.assertEqual(6, self.pkmn.hp_ev)


    def test_add_evs_reduce(self):
        self.pkmn = models.create_pokemon("001", 5, "m", ev_override={
            "hp": 5, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0
        })
        self.pkmn.add_evs([-10, 0, 0, 0, 0, 0])
        self.assertEqual(0, self.pkmn.hp_ev)


    def test_add_evs_overflow(self):
        self.pkmn = models.create_pokemon("001", 5, "m", ev_override={
            "hp": 250, "atk": 250, "def": 0, "spa": 0, "spd": 0, "spe": 0
        })
        self.pkmn.add_evs([10, 2, 10, 10, 10, 10])
        self.assertEqual(252, self.pkmn.hp_ev)
        self.assertEqual(252, self.pkmn.atk_ev)
        self.assertEqual(6, self.pkmn.def_ev)
        self.assertEqual(0, self.pkmn.spa_ev)
        self.assertEqual(0, self.pkmn.spd_ev)
        self.assertEqual(0, self.pkmn.spe_ev)


class TestRecalculateStats(TestCase):
    def test_new_pokemon(self):
        ivs = {
            "hp": 24,
            "atk": 12,
            "def": 30,
            "spa": 16,
            "spd": 23,
            "spe": 5
        }
        evs = {
            "hp": 74,
            "atk": 190,
            "def": 91,
            "spa": 48,
            "spd": 84,
            "spe": 23
        }
        nature = "adamant"
        pkmn = models.create_pokemon("445", 78, "m", iv_override=ivs, ev_override=evs, nature_override=nature)

        self.assertEqual(289, pkmn.hp_stat)
        self.assertEqual(278, pkmn.atk_stat)
        self.assertEqual(193, pkmn.def_stat)
        self.assertEqual(135, pkmn.spa_stat)
        self.assertEqual(171, pkmn.spd_stat)
        self.assertEqual(171, pkmn.spe_stat)


    def test_levelup(self):
        ivs = {
            stat: 31 for stat in consts.STATS
        }
        nature = "serious"
        pkmn = models.create_pokemon("001", 5, "m", iv_override=ivs, nature_override=nature)

        self.assertEqual(21, pkmn.hp_stat)
        self.assertEqual(11, pkmn.atk_stat)
        self.assertEqual(11, pkmn.def_stat)
        self.assertEqual(13, pkmn.spa_stat)
        self.assertEqual(13, pkmn.spd_stat)
        self.assertEqual(11, pkmn.spe_stat)

        pkmn.level = 6
        pkmn.recalculate_stats(skip_save=True)

        self.assertEqual(23, pkmn.hp_stat)
        self.assertEqual(12, pkmn.atk_stat)
        self.assertEqual(12, pkmn.def_stat)
        self.assertEqual(14, pkmn.spa_stat)
        self.assertEqual(14, pkmn.spd_stat)
        self.assertEqual(12, pkmn.spe_stat)


    def test_ev_gain(self):
        ivs = {
            stat: 31 for stat in consts.STATS
        }
        nature = "serious"
        pkmn = models.create_pokemon("001", 5, "m", iv_override=ivs, nature_override=nature)

        self.assertEqual(21, pkmn.hp_stat)
        self.assertEqual(11, pkmn.atk_stat)
        self.assertEqual(11, pkmn.def_stat)
        self.assertEqual(13, pkmn.spa_stat)
        self.assertEqual(13, pkmn.spd_stat)
        self.assertEqual(11, pkmn.spe_stat)

        pkmn.hp_ev = 252
        pkmn.recalculate_stats(skip_save=True)

        self.assertEqual(24, pkmn.hp_stat)


    def test_evolve(self):
        ivs = {
            stat: 31 for stat in consts.STATS
        }
        nature = "serious"
        pkmn = models.create_pokemon("001", 16, "m", iv_override=ivs, nature_override=nature)

        self.assertEqual(45, pkmn.hp_stat)
        self.assertEqual(25, pkmn.atk_stat)
        self.assertEqual(25, pkmn.def_stat)
        self.assertEqual(30, pkmn.spa_stat)
        self.assertEqual(30, pkmn.spd_stat)
        self.assertEqual(24, pkmn.spe_stat)

        pkmn.dex_number = "002"
        pkmn.recalculate_stats(skip_save=True)

        self.assertEqual(50, pkmn.hp_stat)
        self.assertEqual(29, pkmn.atk_stat)
        self.assertEqual(30, pkmn.def_stat)
        self.assertEqual(35, pkmn.spa_stat)
        self.assertEqual(35, pkmn.spd_stat)
        self.assertEqual(29, pkmn.spe_stat)


class TestRestoreHp(TestCase):
    def test_restore_hp(self):
        ivs = {
            stat: 31 for stat in consts.STATS
        }
        pkmn = models.create_pokemon("001", 16, "m", iv_override=ivs)
        pkmn.current_hp = 0
        pkmn.restore_hp(skip_save=True)
        self.assertEqual(45, pkmn.current_hp)


    def test_restore_no_hp(self):
        ivs = {
            stat: 31 for stat in consts.STATS
        }
        pkmn = models.create_pokemon("001", 16, "m", iv_override=ivs)
        pkmn.current_hp = 45
        pkmn.restore_hp(skip_save=True)
        self.assertEqual(45, pkmn.current_hp)


class TestRestorePp(TestCase):
    def test_restore_pp_one_count(self):
        pkmn = models.create_pokemon("003", 50, "m")
        pkmn.move1_pp = 0
        pkmn.restore_pp(1, 5)
        self.assertEqual(pkmn.move1_pp, 5)


    def test_restore_pp_overflow(self):
        pkmn = models.create_pokemon("003", 50, "m")
        pkmn.move1_pp = 9
        pkmn.restore_pp(1, 5)
        self.assertEqual(pkmn.move1_pp, 10)


    def test_restore_pp_reset(self):
        pkmn = models.create_pokemon("003", 50, "m")
        pkmn.move1_pp = 19
        pkmn.restore_pp(1, 5)
        self.assertEqual(pkmn.move1_pp, 10)


    def test_restore_pp_full(self):
        pkmn = models.create_pokemon("003", 50, "m")
        pkmn.move1_pp = 0
        pkmn.restore_pp(1)
        self.assertEqual(pkmn.move1_pp, 10)


    def test_restore_pp_all(self):
        pkmn = models.create_pokemon("003", 50, "m")
        pkmn.move1_pp = 0
        pkmn.move2_pp = 0
        pkmn.move3_pp = 0
        pkmn.move4_pp = 0
        pkmn.restore_pp()
        self.assertEqual(pkmn.move1_pp, 10)
        self.assertEqual(pkmn.move2_pp, 10)
        self.assertEqual(pkmn.move3_pp, 5)
        self.assertEqual(pkmn.move4_pp, 15)


class TestCureStatus(TestCase):
    def test_no_status(self):
        pkmn = models.create_pokemon("001", 16, "m")
        pkmn.status = "poison"
        pkmn.cure_status(skip_save=True)
        self.assertEqual("", pkmn.status)


class TestLearnMove(TestCase):
    def setUp(self):
        self.pkmn = models.create_pokemon("003", 50, "m")


    def test_learn_move_standard(self):
        self.pkmn.learn_move("vinewhip", "move4")
        self.assertEqual("vinewhip", self.pkmn.move4)
        self.assertEqual(25, self.pkmn.move4_pp)


    def test_learn_move_known(self):
        ret = self.pkmn.learn_move("petaldance", "move4")
        self.assertNotEqual("petaldance", self.pkmn.move4)
        self.assertEqual("Move is already known!", ret)


    def test_learn_move_overlevel(self):
        ret = self.pkmn.learn_move("solarbeam", "move4")
        self.assertNotEqual("solarbeam", self.pkmn.move4)
        self.assertEqual("Cannot learn this move!", ret)


    def test_learn_move_tm_tutor(self):
        ret = self.pkmn.learn_move("earthquake", "move4")
        self.assertNotEqual("earthquake", self.pkmn.move4)
        self.assertEqual("Cannot learn this move!", ret)
        self.pkmn.learn_move("earthquake", "move4", tms=True)
        self.assertEqual("earthquake", self.pkmn.move4)
        self.assertEqual(10, self.pkmn.move4_pp)


    def test_learn_move_invalid_slot(self):
        ret = self.pkmn.learn_move("tackle", "status")
        self.assertEqual("Not a valid slot to save.", ret)


class TestGetValidEvolutions(TestCase):
    def test_level_evolve(self):
        self.pkmn = models.create_pokemon("001", 10, "m")
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual([], ret)

        self.pkmn = models.create_pokemon("001", 50, "m")
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual(['002'], ret)

    def test_happiness_evolve(self):
        self.pkmn = models.create_pokemon("172", 10, "m")
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual([], ret)

        self.pkmn.happiness = 230
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual(['025'], ret)

    def test_gender_evolve(self):
        self.pkmn = models.create_pokemon("415", 10, "m")
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual([], ret)

        self.pkmn = models.create_pokemon("415", 50, "f")
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual(['416'], ret)

    def test_move_evolve(self):
        self.pkmn = models.create_pokemon("221", 50, "m")
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual([], ret)

        self.pkmn.learn_move("ancientpower", "move1")
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual(['473'], ret)

    def test_trade_evolve(self):
        self.pkmn = models.create_pokemon("093", 50, "m")
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual([], ret)

        self.pkmn.traded = True
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual(['094'], ret)

    def test_trade_item_evolve(self):
        self.pkmn = models.create_pokemon("125", 50, "m")
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual([], ret)

        self.pkmn.traded = True
        self.pkmn.held_item = "electirizer"
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual(['466'], ret)

    def test_item_evolve(self):
        self.user = User(username="test1", password="test1", email="test1@test.com")
        self.user.save()
        self.trainer = Profile(character="01", user=self.user)
        self.trainer.save()
        self.pkmn = models.create_pokemon("090", 50, "m")
        self.pkmn.assign_trainer(self.trainer)
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual([], ret)

        self.trainer.bag["general"] = {
            "water-stone": 1
        }
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual(['091'], ret)


    def test_eevee(self):
        self.user1 = User(username="test1", password="test1", email="test1@test.com")
        self.user1.save()
        self.trainer1 = Profile(character="01", user=self.user1)
        self.trainer1.save()
        self.pkmn = models.create_pokemon("133", 50, "m")
        self.pkmn.happiness = 230
        self.pkmn.assign_trainer(self.trainer1)
        self.trainer1.bag["general"] = {
            "water-stone": 1,
            "fire-stone": 1,
            "ice-stone": 1,
            "leaf-stone": 1,
            "thunder-stone": 1
        }
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual(['134', '136', '135', '470', '196', '197', '471'], ret)


    def test_kirlia(self):
        self.user2 = User(username="test1", password="test1", email="test1@test.com")
        self.user2.save()
        self.trainer2 = Profile(character="01", user=self.user2)
        self.trainer2.save()
        self.pkmn = models.create_pokemon("281", 50, "m")
        self.pkmn.happiness = 230
        self.pkmn.assign_trainer(self.trainer2)
        self.trainer2.bag["general"] = {
            "dawn-stone": 1
        }
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual(["282", "475"], ret)

        self.pkmn = models.create_pokemon("281", 50, "f")
        self.pkmn.happiness = 230
        self.pkmn.assign_trainer(self.trainer2)
        self.trainer2.bag["general"] = {
            "dawn-stone": 1
        }
        ret = self.pkmn.get_valid_evolutions()
        self.assertEqual(["282"], ret)


class TestEvolve(TestCase):
    def test_level_evolve(self):
        self.pkmn = models.create_pokemon("001", 10, "m")
        ret = self.pkmn.evolve("002")
        self.assertFalse(ret[0])

        self.pkmn = models.create_pokemon("001", 50, "m")
        ret = self.pkmn.evolve("002")
        self.assertTrue(ret[0])

    def test_happiness_evolve(self):
        self.pkmn = models.create_pokemon("172", 10, "m")
        ret = self.pkmn.evolve("025")
        self.assertFalse(ret[0])

        self.pkmn.happiness = 230
        ret = self.pkmn.evolve("025")
        self.assertTrue(ret[0])

    def test_gender_evolve(self):
        self.pkmn = models.create_pokemon("415", 10, "m")
        ret = self.pkmn.evolve("416")
        self.assertFalse(ret[0])

        self.pkmn = models.create_pokemon("415", 50, "f")
        ret = self.pkmn.evolve("416")
        self.assertTrue(ret[0])

    def test_move_evolve(self):
        self.pkmn = models.create_pokemon("221", 50, "m")
        ret = self.pkmn.evolve("473")
        self.assertFalse(ret[0])

        self.pkmn.learn_move("ancientpower", "move1")
        ret = self.pkmn.evolve("473")
        self.assertTrue(ret[0])

    def test_trade_evolve(self):
        self.pkmn = models.create_pokemon("093", 50, "m")
        ret = self.pkmn.evolve("094")
        self.assertFalse(ret[0])

        self.pkmn.traded = True
        ret = self.pkmn.evolve("094")
        self.assertTrue(ret[0])

    def test_trade_item_evolve(self):
        self.pkmn = models.create_pokemon("125", 50, "m")
        ret = self.pkmn.evolve("466")
        self.assertFalse(ret[0])

        self.pkmn.traded = True
        self.pkmn.held_item = "electirizer"
        ret = self.pkmn.evolve("466")
        self.assertTrue(ret[0])