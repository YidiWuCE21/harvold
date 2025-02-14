import random
from django.test import TestCase
from django.contrib.auth.models import User
from battle import models
from accounts.models import Profile
from harvoldsite import consts
from pokemon.models import create_pokemon, Pokemon
from battle.battle_manager import BattleState


class TestCreateBattle(TestCase):
    def setUp(self):
        self.user1 = User(username="test1", password="test1", email="test1@test.com")
        self.user1.save()
        self.trainer1 = Profile(character="01", user=self.user1)
        self.trainer1.save()
        self.user2 = User(username="test2", password="test2", email="test2@test.com")
        self.user2.save()
        self.trainer2 = Profile(character="01", user=self.user2)
        self.trainer2.save()
        # Construct team 1
        self.t1p1 = create_pokemon("003", 100, "m", ability_override="Chlorophyll", nature_override="modest",
                                          iv_override={stat: 31 for stat in consts.STATS})
        self.t1p1.assign_trainer(self.trainer1)
        self.t1p2 = create_pokemon("006", 100, "m", ability_override="Blaze", nature_override="modest",
                                          iv_override={stat: 31 for stat in consts.STATS})
        self.t1p2.assign_trainer(self.trainer1)
        self.t1p3 = create_pokemon("009", 100, "m", ability_override="Torrent", nature_override="modest",
                                          iv_override={stat: 31 for stat in consts.STATS})
        self.t1p3.assign_trainer(self.trainer1)
        self.trainer1.add_to_party(self.t1p1)
        self.trainer1.add_to_party(self.t1p2)
        self.trainer1.add_to_party(self.t1p3)
        # Construct team 2
        self.t2p1 = create_pokemon("143", 100, "m", ability_override="Thick Fat", nature_override="impish",
                                   iv_override={stat: 31 for stat in consts.STATS})
        self.t2p1.assign_trainer(self.trainer2)
        self.t2p2 = create_pokemon("143", 100, "m", ability_override="Thick Fat", nature_override="impish",
                                   iv_override={stat: 31 for stat in consts.STATS})
        self.t2p2.assign_trainer(self.trainer2)
        self.trainer2.add_to_party(self.t2p1)
        self.trainer2.add_to_party(self.t2p2)
        # Wild opponent
        self.wild = create_pokemon("143", 50, "m", ability_override="Thick Fat", nature_override="impish",
                                   iv_override={stat: 31 for stat in consts.STATS})



    def test_standard_trainer(self):
        ret = models.create_battle(self.trainer1.pk, "erika_gym", "npc")

        # Test battle object
        battle_obj = ret
        self.assertEqual(self.trainer1, battle_obj.player_1)
        self.assertIsNone(battle_obj.player_2)
        self.assertEqual("erika_gym", battle_obj.npc_opponent)
        self.assertIsNone(battle_obj.wild_opponent)

        # Test battle state
        battle_state = battle_obj.get_battle_state()
        self.assertNotIn("escapes", battle_state)
        self.assertEqual("test1", battle_state["player_1"]["name"])
        self.assertEqual("Erika", battle_state["player_2"]["name"])
        p1_party_exp = [pkmn.get_battle_info() for pkmn in self.trainer1.get_party()]
        self.assertEqual(p1_party_exp, battle_state["player_1"]["party"])

    def test_trainer_missing(self):
        with self.assertRaises(KeyError) as e:
            models.create_battle(self.trainer1.pk, "not_an_npc", "npc")
        self.assertEqual("not_an_npc not recognized as a trainer", e.exception.args[0])

    def test_standard_wild(self):
        ret = models.create_battle(self.trainer1.pk, self.wild.pk, "wild")

        # Test battle object
        battle_obj = ret
        self.assertEqual(self.trainer1, battle_obj.player_1)
        self.assertIsNone(battle_obj.player_2)
        self.assertIsNone(battle_obj.npc_opponent)
        self.assertEqual(self.wild, battle_obj.wild_opponent)

        # Test battle state
        battle_state = battle_obj.get_battle_state()
        self.assertIn("escapes", battle_state)
        self.assertEqual("test1", battle_state["player_1"]["name"])
        self.assertEqual("wild Snorlax", battle_state["player_2"]["name"])
        p1_party_exp = [pkmn.get_battle_info() for pkmn in self.trainer1.get_party()]
        self.assertEqual(p1_party_exp, battle_state["player_1"]["party"])
        p2_party_exp = [self.wild.get_battle_info()]
        self.assertEqual(p2_party_exp, battle_state["player_2"]["party"])

    def test_wild_missing(self):
        with self.assertRaises(Pokemon.DoesNotExist) as e:
            models.create_battle(self.trainer1.pk, 999999999999999, "wild")
        self.assertEqual("Pokemon matching query does not exist.", e.exception.args[0])

    def test_wild_owned(self):
        with self.assertRaises(ValueError) as e:
            models.create_battle(self.trainer1.pk, self.t2p1.pk, "wild")
        self.assertEqual("You cannot catch someone else's Pokémon!", e.exception.args[0])

    def test_standard_live(self):
        ret = models.create_battle(self.trainer1.pk, self.trainer2.pk, "live")

        # Test battle object
        battle_obj = ret
        self.assertEqual(self.trainer1, battle_obj.player_1)
        self.assertEqual(self.trainer2, battle_obj.player_2)
        self.assertIsNone(battle_obj.npc_opponent)
        self.assertIsNone(battle_obj.wild_opponent)

        # Test battle state
        battle_state = battle_obj.get_battle_state()
        self.assertNotIn("escapes", battle_state)
        self.assertEqual("test1", battle_state["player_1"]["name"])
        self.assertEqual("test2", battle_state["player_2"]["name"])
        p1_party_exp = [pkmn.get_battle_info() for pkmn in self.trainer1.get_party()]
        self.assertEqual(p1_party_exp, battle_state["player_1"]["party"])
        p2_party_exp = [pkmn.get_battle_info() for pkmn in self.trainer2.get_party()]
        self.assertEqual(p2_party_exp, battle_state["player_2"]["party"])

    def test_live_missing(self):
        with self.assertRaises(Profile.DoesNotExist) as e:
            models.create_battle(self.trainer1.pk, 999999999999999, "live")
        self.assertEqual("Profile matching query does not exist.", e.exception.args[0])


class TestBattleManager(TestCase):
    def setUp(self):
        player_state = consts.PLAYER_STATE
        self.std_battle = {
            "player_1": player_state.copy(),
            "player_2": player_state.copy(),
            "weather": None,
            "weather_turns": 0,
            "terrain": None,
            "outcome": None,
            "type": "npc",
            "trick_room": 0,
            "gravity": None,
        }
        self.std_battle["player_1"]["name"] = "P1"
        self.std_battle["player_2"]["name"] = "P2"

        # Create Pokemon to use for battle
        self.snorlax = create_pokemon("143", 100, "m", iv_override={stat: 31 for stat in consts.STATS},
                                 nature_override="impish")
        self.gengar = create_pokemon("094", 100, "m", iv_override={stat: 31 for stat in consts.STATS},
                                nature_override="timid")
        self.electivire = create_pokemon("466", 100, "m", iv_override={stat: 31 for stat in consts.STATS},
                                    nature_override="jolly")
        self.ferrothorn = create_pokemon("598", 100, "m", iv_override={stat: 31 for stat in consts.STATS},
                                    nature_override="relaxed")
        self.raticate = create_pokemon("020", 100, "m", iv_override={stat: 31 for stat in consts.STATS},
                                  nature_override="relaxed")
        # Populate parties
        self.std_battle["player_1"]["party"] = [
            self.snorlax.get_battle_info(),
            self.gengar.get_battle_info()]
        self.std_battle["player_2"]["party"] = [
            self.raticate.get_battle_info(),
            self.electivire.get_battle_info()]

    def test_jsonify(self):
        battle_state = self.std_battle.copy()
        battle = BattleState(battle_state)
        ret = battle.jsonify()
        self.maxDiff = 10000
        self.assertDictEqual(ret, battle_state)


    def test_check_p1_first(self):
        battle_state = self.std_battle.copy()

        battle = BattleState(battle_state)
        ret = battle.check_p1_first("tackle", "tackle")
        self.assertFalse(ret)

        battle = BattleState(battle_state)
        ret = battle.check_p1_first("quickattack", "tackle")
        self.assertTrue(ret)

        battle = BattleState(battle_state)
        battle.player_1.current_pokemon = 1
        ret = battle.check_p1_first("tackle", "tackle")
        self.assertTrue(ret)

    def test_get_priority(self):
        battle_state = self.std_battle.copy()

        # Standard priority
        battle = BattleState(battle_state)
        ret = battle.get_priority(battle.player_1.get_current_pokemon(), "tackle")
        self.assertEqual(0, ret)

        # Quick attack priority
        battle = BattleState(battle_state)
        ret = battle.get_priority(battle.player_1.get_current_pokemon(), "quickattack")
        self.assertEqual(1, ret)

        # Quick claw activation
        regular = 0
        fast = 0
        random.seed(900)
        for i in range(100):
            battle = BattleState(battle_state)
            battle.player_1.get_current_pokemon().held_item = "quick-claw"
            ret = battle.get_priority(battle.player_1.get_current_pokemon(), "tackle")
            if ret == 10:
                fast += 1
            else:
                regular += 1
        self.assertEqual(25, fast)
        self.assertEqual(75, regular)

        # Lagging tail
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().held_item = "lagging-tail"
        ret = battle.get_priority(battle.player_1.get_current_pokemon(), "tackle")
        self.assertEqual(-1, ret)

        # Stall
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().ability = "Stall"
        ret = battle.get_priority(battle.player_1.get_current_pokemon(), "tackle")
        self.assertEqual(-1, ret)

        # Gale Wings
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().ability = "Gale Wings"
        ret = battle.get_priority(battle.player_1.get_current_pokemon(), "tackle")
        self.assertEqual(1, ret)
        battle.player_1.get_current_pokemon().current_hp = 1
        ret = battle.get_priority(battle.player_1.get_current_pokemon(), "tackle")
        self.assertEqual(0, ret)

        # Prankster
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().ability = "Prankster"
        ret = battle.get_priority(battle.player_1.get_current_pokemon(), "tackle")
        self.assertEqual(0, ret)
        ret = battle.get_priority(battle.player_1.get_current_pokemon(), "flamethrower")
        self.assertEqual(0, ret)
        ret = battle.get_priority(battle.player_1.get_current_pokemon(), "hypnosis")
        self.assertEqual(1, ret)
        ret = battle.get_priority(battle.player_1.get_current_pokemon(), "switcheroo")
        self.assertEqual(1, ret)

    def test_get_speed(self):
        battle_state = self.std_battle.copy()

        # Standard case
        battle = BattleState(battle_state)
        ret = battle.get_speed(battle.player_1)
        self.assertEqual(96, ret)

        # Stat boost
        battle = BattleState(battle_state)
        battle.player_1.stat_boosts["speed"] = 2
        ret = battle.get_speed(battle.player_1)
        self.assertEqual(192, ret)

        # Paralysis
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().status = "par"
        ret = battle.get_speed(battle.player_1)
        self.assertEqual(24, ret)

        # Quick Feet
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().status = "par"
        battle.player_1.get_current_pokemon().ability = "Quick Feet"
        ret = battle.get_speed(battle.player_1)
        self.assertEqual(144, ret)

        # Choice Scarf
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().held_item = "choice-scarf"
        ret = battle.get_speed(battle.player_1)
        self.assertEqual(144, ret)

        # Iron Ball
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().held_item = "macho-brace"
        ret = battle.get_speed(battle.player_1)
        self.assertEqual(48, ret)

        # Tailwind
        battle = BattleState(battle_state)
        battle.player_1.tailwind = 3
        ret = battle.get_speed(battle.player_1)
        self.assertEqual(192, ret)

        # Weather boost
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().ability = "Swift Swim"
        ret = battle.get_speed(battle.player_1)
        self.assertEqual(96, ret)
        battle.weather = "rain"
        ret = battle.get_speed(battle.player_1)
        self.assertEqual(192, ret)

        # Unburden
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().ability = "Unburden"
        ret = battle.get_speed(battle.player_1)
        self.assertEqual(96, ret)
        battle.player_1.get_current_pokemon().held_item = "removed"
        ret = battle.get_speed(battle.player_1)
        self.assertEqual(192, ret)

        # Slow start
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().ability = "Slow Start"
        ret = battle.get_speed(battle.player_1)
        self.assertEqual(48, ret)


    def test_roll_accuracy(self):
        battle_state = self.std_battle.copy()
        random.seed(900)

        # Standard case
        battle = BattleState(battle_state)
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "tackle")
            if ret:
                hits += 1
        self.assertEqual(100, hits)

        # Move inaccurate
        battle = BattleState(battle_state)
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "hydropump")
            if ret:
                hits += 1
        self.assertEqual(83, hits)

        # Gravity
        battle = BattleState(battle_state)
        battle.gravity = 3
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "hydropump")
            if ret:
                hits += 1
        self.assertEqual(100, hits)

        # Tangled Feet
        battle = BattleState(battle_state)
        battle.player_2.get_current_pokemon().ability = "Tangled Feet"
        battle.player_2.confusion = 3
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "tackle")
            if ret:
                hits += 1
        self.assertEqual(47, hits)

        # Hustle
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().ability = "Hustle"
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "tackle")
            if ret:
                hits += 1
        self.assertEqual(76, hits)
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "flamethrower")
            if ret:
                hits += 1
        self.assertEqual(100, hits)

        # Sand Veil
        battle = BattleState(battle_state)
        battle.player_2.get_current_pokemon().ability = "Sand Veil"
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "tackle")
            if ret:
                hits += 1
        self.assertEqual(100, hits)
        battle.weather = "sand"
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "tackle")
            if ret:
                hits += 1
        self.assertEqual(84, hits)

        # Snow Cloak
        battle = BattleState(battle_state)
        battle.player_2.get_current_pokemon().ability = "Snow Cloak"
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "tackle")
            if ret:
                hits += 1
        self.assertEqual(100, hits)
        battle.weather = "hail"
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "tackle")
            if ret:
                hits += 1
        self.assertEqual(83, hits)

        # Compound Eyes
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().ability = "Compound Eyes"
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "hydropump")
            if ret:
                hits += 1
        self.assertEqual(100, hits)

        # Bright powder
        battle = BattleState(battle_state)
        battle.player_2.get_current_pokemon().held_item = "bright-powder"
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "tackle")
            if ret:
                hits += 1
        self.assertEqual(89, hits)

        # Zoom lens
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().held_item = "zoom-lens"
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "rockslide")
            if ret:
                hits += 1
        self.assertEqual(100, hits)

        # Accuracy modifier
        battle = BattleState(battle_state)
        battle.player_1.stat_boosts["accuracy"] = 3
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "rockslide")
            if ret:
                hits += 1
        self.assertEqual(100, hits)

        # Evasion modifier
        battle = BattleState(battle_state)
        battle.player_2.stat_boosts["evasion"] = 3
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "tackle")
            if ret:
                hits += 1
        self.assertEqual(48, hits)

        # Self target
        battle = BattleState(battle_state)
        battle.player_2.stat_boosts["evasion"] = 3
        battle.player_2.get_current_pokemon().held_item = "bright-powder"
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "softboiled")
            if ret:
                hits += 1
        self.assertEqual(100, hits)

        # Never miss
        battle = BattleState(battle_state)
        battle.player_2.stat_boosts["evasion"] = 3
        battle.player_2.get_current_pokemon().held_item = "bright-powder"
        hits = 0
        for i in range(100):
            ret = battle.roll_accuracy(battle.player_1, "vitalthrow")
            if ret:
                hits += 1
        self.assertEqual(100, hits)


    def test_roll_crit(self):
        battle_state = self.std_battle.copy()
        random.seed(900)

        # Standard case
        battle = BattleState(battle_state)
        crits = 0
        for i in range(100):
            ret = battle.roll_crit(
                battle.player_1,
                "tackle"
            )
            if ret:
                crits += 1
        self.assertGreaterEqual(6, crits)

        # Crit 1
        battle = BattleState(battle_state)
        crits = 0
        for i in range(100):
            ret = battle.roll_crit(
                battle.player_1,
                "slash"
            )
            if ret:
                crits += 1
        self.assertGreaterEqual(18, crits)

        # Crit 2
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().ability = "Super Luck"
        crits = 0
        for i in range(100):
            ret = battle.roll_crit(
                battle.player_1,
                "slash"
            )
            if ret:
                crits += 1
        self.assertGreaterEqual(55, crits)

        # Crit 3
        battle = BattleState(battle_state)
        battle.player_1.get_current_pokemon().ability = "Super Luck"
        battle.player_1.held_item = "razor-claw"
        crits = 0
        for i in range(100):
            ret = battle.roll_crit(
                battle.player_1,
                "slash"
            )
            if ret:
                crits += 1
        self.assertGreaterEqual(100, crits)


    def test_move_damage(self):
        battle_state = self.std_battle.copy()
        random.seed(900)

        # Standard case
        battle = BattleState(battle_state)
        min_dmg = 1000
        max_dmg = 0
        for i in range(100):
            ret = battle.move_damage(
                battle.player_1,
                battle.player_1.get_current_pokemon(),
                battle.player_2.get_current_pokemon(),
                "normal",
                85,
                "physical",
                1
            )
            if ret[0] > max_dmg:
                max_dmg = ret[0]
            if ret[0] < min_dmg:
                min_dmg = ret[0]
        self.assertGreaterEqual(min_dmg, 136)
        self.assertLessEqual(max_dmg, 162)

        # Attack boost case
        battle = BattleState(battle_state)
        battle.player_1.stat_boosts["attack"] = 1
        min_dmg = 1000
        max_dmg = 0
        for i in range(100):
            ret = battle.move_damage(
                battle.player_1,
                battle.player_1.get_current_pokemon(),
                battle.player_2.get_current_pokemon(),
                "normal",
                85,
                "physical",
                1
            )
            if ret[0] > max_dmg:
                max_dmg = ret[0]
            if ret[0] < min_dmg:
                min_dmg = ret[0]
        self.assertGreaterEqual(min_dmg, 205)
        self.assertLessEqual(max_dmg, 243)

        # Defense boost case
        battle = BattleState(battle_state)
        battle.player_2.stat_boosts["defense"] = 1
        min_dmg = 1000
        max_dmg = 0
        for i in range(100):
            ret = battle.move_damage(
                battle.player_1,
                battle.player_1.get_current_pokemon(),
                battle.player_2.get_current_pokemon(),
                "normal",
                85,
                "physical",
                1
            )
            if ret[0] > max_dmg:
                max_dmg = ret[0]
            if ret[0] < min_dmg:
                min_dmg = ret[0]
        self.assertGreaterEqual(min_dmg, 93)
        self.assertLessEqual(max_dmg, 109)

        # Defense break case
        battle = BattleState(battle_state)
        battle.player_2.stat_boosts["defense"] = -1
        min_dmg = 1000
        max_dmg = 0
        for i in range(100):
            ret = battle.move_damage(
                battle.player_1,
                battle.player_1.get_current_pokemon(),
                battle.player_2.get_current_pokemon(),
                "normal",
                85,
                "physical",
                1
            )
            if ret[0] > max_dmg:
                max_dmg = ret[0]
            if ret[0] < min_dmg:
                min_dmg = ret[0]
        self.assertGreaterEqual(min_dmg, 205)
        self.assertLessEqual(max_dmg, 243)

        # Special attack case
        battle = BattleState(battle_state)
        min_dmg = 1000
        max_dmg = 0
        for i in range(100):
            ret = battle.move_damage(
                battle.player_1,
                battle.player_1.get_current_pokemon(),
                battle.player_2.get_current_pokemon(),
                "normal",
                85,
                "special",
                1
            )
            if ret[0] > max_dmg:
                max_dmg = ret[0]
            if ret[0] < min_dmg:
                min_dmg = ret[0]
        self.assertGreaterEqual(min_dmg, 78)
        self.assertLessEqual(max_dmg, 93)

        # Super effective
        battle = BattleState(battle_state)
        min_dmg = 1000
        max_dmg = 0
        for i in range(100):
            ret = battle.move_damage(
                battle.player_1,
                battle.player_1.get_current_pokemon(),
                battle.player_2.get_current_pokemon(),
                "fighting",
                75,
                "physical",
                1
            )
            if ret[0] > max_dmg:
                max_dmg = ret[0]
            if ret[0] < min_dmg:
                min_dmg = ret[0]
        self.assertGreaterEqual(min_dmg, 162)
        self.assertLessEqual(max_dmg, 192)

        # Crit case
        battle = BattleState(battle_state)
        min_dmg = 1000
        max_dmg = 0
        for i in range(100):
            ret = battle.move_damage(
                battle.player_1,
                battle.player_1.get_current_pokemon(),
                battle.player_2.get_current_pokemon(),
                "normal",
                85,
                "physical",
                1.5
            )
            if ret[0] > max_dmg:
                max_dmg = ret[0]
            if ret[0] < min_dmg:
                min_dmg = ret[0]
        self.assertGreaterEqual(min_dmg, 205)
        self.assertLessEqual(max_dmg, 243)

        # No effect
        battle = BattleState(battle_state)
        min_dmg = 1000
        max_dmg = 0
        for i in range(100):
            ret = battle.move_damage(
                battle.player_1,
                battle.player_1.get_current_pokemon(),
                battle.player_2.get_current_pokemon(),
                "ghost",
                85,
                "physical",
                1
            )
            if ret[0] > max_dmg:
                max_dmg = ret[0]
            if ret[0] < min_dmg:
                min_dmg = ret[0]
        self.assertGreaterEqual(min_dmg, 0)
        self.assertLessEqual(max_dmg, 0)

        # Burned case
        battle = BattleState(battle_state)
        min_dmg = 1000
        max_dmg = 0
        battle.player_1.get_current_pokemon().status = "brn"
        for i in range(100):
            ret = battle.move_damage(
                battle.player_1,
                battle.player_1.get_current_pokemon(),
                battle.player_2.get_current_pokemon(),
                "normal",
                85,
                "physical",
                1
            )
            if ret[0] > max_dmg:
                max_dmg = ret[0]
            if ret[0] < min_dmg:
                min_dmg = ret[0]
        self.assertGreaterEqual(min_dmg, 68)
        self.assertLessEqual(max_dmg, 81)


    def test_apply_damage(self):
        battle_state = self.std_battle.copy()
        random.seed(900)

        # Standard case
        battle = BattleState(battle_state)
        battle.apply_damage(61, battle.player_1)
        self.assertEqual(400, battle.player_1.get_current_pokemon().current_hp)

        # Standard case
        battle = BattleState(battle_state)
        battle.apply_damage(461, battle.player_1)
        self.assertEqual(0, battle.player_1.get_current_pokemon().current_hp)
        self.assertEqual([
            {"anim": ["p1_update_hp_0"]},
            {"text": "Snorlax has fainted!", "anim": ["p1_faint"]}
        ], battle.output)

        # Standard case
        battle = BattleState(battle_state)
        battle.apply_damage(561, battle.player_1)
        self.assertEqual(0, battle.player_1.get_current_pokemon().current_hp)
        self.assertEqual([
            {"anim": ["p1_update_hp_0"]},
            {"text": "Snorlax has fainted!", "anim": ["p1_faint"]}
        ], battle.output)


    def test_apply_status(self):
        battle_state = self.std_battle.copy()
        random.seed(900)

        # Standard case
        applied = 0
        for i in range(100):
            battle = BattleState(battle_state)
            battle.apply_status(
                battle.player_2,
                battle.player_2.get_current_pokemon(),
                "spore"
            )
            if battle.player_2.get_current_pokemon().status == "slp":
                applied += 1
        self.assertEqual(100, applied)

        # Accuracy; should skip
        applied = 0
        for i in range(100):
            battle = BattleState(battle_state)
            battle.apply_status(
                battle.player_2,
                battle.player_2.get_current_pokemon(),
                "willowisp"
            )
            if battle.player_2.get_current_pokemon().status == "brn":
                applied += 1
        self.assertEqual(100, applied)

        # Chance
        applied = 0
        for i in range(100):
            battle = BattleState(battle_state)
            battle.apply_status(
                battle.player_2,
                battle.player_2.get_current_pokemon(),
                "ember"
            )
            if battle.player_2.get_current_pokemon().status == "brn":
                applied += 1
        self.assertEqual(14, applied)

        # Confusion
        durations = []
        for i in range(100):
            battle = BattleState(battle_state)
            battle.apply_status(
                battle.player_2,
                battle.player_2.get_current_pokemon(),
                "confuseray"
            )
            if battle.player_2.confusion > 0:
                durations.append(battle.player_2.confusion)
        self.assertGreaterEqual(2, min(durations))
        self.assertLessEqual(5, max(durations))

        # Already confused
        battle = BattleState(battle_state)
        battle.player_2.confusion = 31
        battle.apply_status(
            battle.player_2,
            battle.player_2.get_current_pokemon(),
            "confuseray"
        )
        self.assertEqual(31, battle.player_2.confusion)
        self.assertEqual({"text": "Raticate is already confused!"}, battle.output[0])

        # Already statused
        battle = BattleState(battle_state)
        battle.player_2.get_current_pokemon().status = "slp"
        battle.apply_status(
            battle.player_2,
            battle.player_2.get_current_pokemon(),
            "willowisp"
        )
        self.assertEqual("slp", battle.player_2.get_current_pokemon().status)
        self.assertEqual({"text": "But it failed!"}, battle.output[0])


    def test_apply_boosts(self):
        battle_state = self.std_battle.copy()
        random.seed(1)

        # Test boost guarantee
        battle = BattleState(battle_state)
        battle.apply_boosts(battle.player_1, "swordsdance")
        self.assertEqual(2, battle.player_1.stat_boosts["attack"])
        battle.apply_boosts(battle.player_1, "swordsdance")
        self.assertEqual(4, battle.player_1.stat_boosts["attack"])
        battle.apply_boosts(battle.player_1, "swordsdance")
        self.assertEqual(6, battle.player_1.stat_boosts["attack"])
        battle.apply_boosts(battle.player_1, "swordsdance")
        self.assertEqual(6, battle.player_1.stat_boosts["attack"])

        # Test drain guarantee
        battle = BattleState(battle_state)
        battle.apply_boosts(battle.player_1, "metalsound")
        self.assertEqual(-2, battle.player_2.stat_boosts["special_defense"])
        battle.apply_boosts(battle.player_1, "metalsound")
        self.assertEqual(-4, battle.player_2.stat_boosts["special_defense"])
        battle.apply_boosts(battle.player_1, "metalsound")
        self.assertEqual(-6, battle.player_2.stat_boosts["special_defense"])
        battle.apply_boosts(battle.player_1, "metalsound")
        self.assertEqual(-6, battle.player_2.stat_boosts["special_defense"])

        # Test double boost
        battle = BattleState(battle_state)
        battle.apply_boosts(battle.player_1, "dragondance")
        self.assertEqual(1, battle.player_1.stat_boosts["attack"])
        self.assertEqual(1, battle.player_1.stat_boosts["speed"])

        # Test boost chance
        boosts = 0
        for i in range(100):
            battle = BattleState(battle_state)
            battle.apply_boosts(battle.player_1, "ancientpower")
            if battle.player_1.stat_boosts["attack"] > 0:
                boosts += 1
        self.assertEqual(10, boosts)



    def test_use_potion(self):
        battle_state = self.std_battle.copy()
        battle = BattleState(battle_state)

        # Test potions
        battle.player_1.party[0].current_hp = 10
        battle.player_1.inventory = {"medicine": {"potion": 5}}
        ret = battle.use_item(battle.player_1, "potion", 0)
        self.assertFalse(ret)
        self.assertEqual(30, battle.player_1.party[0].current_hp)

        # Test overheal
        battle.player_1.party[0].current_hp = 460
        battle.player_1.inventory = {"medicine": {"potion": 5}}
        ret = battle.use_item(battle.player_1, "potion", 0)
        self.assertFalse(ret)
        self.assertEqual(461, battle.player_1.party[0].current_hp)

        # Test max potions
        battle.player_1.party[0].current_hp = 10
        battle.player_1.inventory = {"medicine": {"max-potion": 5}}
        ret = battle.use_item(battle.player_1, "max-potion", 0)
        self.assertFalse(ret)
        self.assertEqual(461, battle.player_1.party[0].current_hp)

        # Test fainted
        battle.player_1.party[0].current_hp = 0
        battle.player_1.inventory = {"medicine": {"max-potion": 5}}
        ret = battle.use_item(battle.player_1, "max-potion", 0)
        self.assertFalse(ret)
        self.assertEqual(0, battle.player_1.party[0].current_hp)


    def test_use_cure(self):
        battle_state = self.std_battle.copy()
        battle = BattleState(battle_state)

        # Test wrong status
        battle.player_1.party[0].status = "par"
        battle.player_1.inventory = {"medicine": {"antidote": 5}}
        ret = battle.use_item(battle.player_1, "antidote", 0)
        self.assertFalse(ret)
        self.assertEqual("par", battle.player_1.party[0].status)

        # Test right status
        battle.player_1.party[0].status = "psn"
        battle.player_1.inventory = {"medicine": {"antidote": 5}}
        ret = battle.use_item(battle.player_1, "antidote", 0)
        self.assertFalse(ret)
        self.assertEqual("", battle.player_1.party[0].status)

        # Test right status
        battle.player_1.party[0].status = "txc"
        battle.player_1.inventory = {"medicine": {"antidote": 5}}
        ret = battle.use_item(battle.player_1, "antidote", 0)
        self.assertFalse(ret)
        self.assertEqual("", battle.player_1.party[0].status)

        # Test full heal
        battle.player_1.party[0].status = "par"
        battle.player_1.inventory = {"medicine": {"full-heal": 5}}
        ret = battle.use_item(battle.player_1, "full-heal", 0)
        self.assertFalse(ret)
        self.assertEqual("", battle.player_1.party[0].status)

        # Test full heal
        battle.player_1.party[0].status = "slp"
        battle.player_1.inventory = {"medicine": {"full-heal": 5}}
        ret = battle.use_item(battle.player_1, "full-heal", 0)
        self.assertFalse(ret)
        self.assertEqual("", battle.player_1.party[0].status)

        # Test full heal
        battle.player_1.party[0].status = "txc"
        battle.player_1.inventory = {"medicine": {"full-heal": 5}}
        ret = battle.use_item(battle.player_1, "full-heal", 0)
        self.assertFalse(ret)
        self.assertEqual("", battle.player_1.party[0].status)


    def test_use_revive(self):
        battle_state = self.std_battle.copy()
        battle = BattleState(battle_state)

        # Test not dead
        battle.player_1.party[0].current_hp = 30
        battle.player_1.inventory = {"medicine": {"revive": 5}}
        ret = battle.use_item(battle.player_1, "revive", 0)
        self.assertFalse(ret)
        self.assertEqual(30, battle.player_1.party[0].current_hp)

        # Test revive
        battle.player_1.party[0].current_hp = 0
        battle.player_1.inventory = {"medicine": {"revive": 5}}
        ret = battle.use_item(battle.player_1, "revive", 0)
        self.assertFalse(ret)
        self.assertEqual(231, battle.player_1.party[0].current_hp)

        # Test max revive
        battle.player_1.party[0].current_hp = 0
        battle.player_1.inventory = {"medicine": {"max-revive": 5}}
        ret = battle.use_item(battle.player_1, "max-revive", 0)
        self.assertFalse(ret)
        self.assertEqual(461, battle.player_1.party[0].current_hp)


    def test_catch_pokemon(self):
        battle_state = self.std_battle.copy()
        battle = BattleState(battle_state)
        battle.type = "npc"

        # Test not wild
        battle.player_1.inventory = {"ball": {"pokeball": 5}}
        ret = battle.use_item(battle.player_1, "pokeball", 0)
        self.assertFalse(ret)
        self.assertEqual([{"text": "You cannot catch Pokémon in a trainer battle!"}], battle.output)

        # Test standard
        random.seed(900)
        catches = 0
        misses = 0
        for i in range(1000):
            battle = BattleState(battle_state)
            battle.type = "wild"
            battle.player_1.inventory = {"ball": {"pokeball": 5}}
            battle.use_item(battle.player_1, "pokeball", 0)
            if battle.outcome == "caught":
                catches += 1
            else:
                misses += 1
        self.assertEqual(277, catches)
        self.assertEqual(723, misses)

        # Test low hp
        random.seed(900)
        catches = 0
        misses = 0
        outputs = []
        for i in range(1000):
            battle = BattleState(battle_state)
            battle.type = "wild"
            battle.player_2.party[0].current_hp = 1
            battle.player_1.inventory = {"ball": {"pokeball": 5}}
            battle.use_item(battle.player_1, "pokeball", 0)
            outputs.append(battle.output)
            if battle.outcome == "caught":
                catches += 1
            else:
                misses += 1
        self.assertEqual(635, catches)
        self.assertEqual(365, misses)

        # Test status
        random.seed(900)
        catches = 0
        misses = 0
        outputs = []
        for i in range(1000):
            battle = BattleState(battle_state)
            battle.type = "wild"
            battle.player_2.party[0].status = "slp"
            battle.player_1.inventory = {"ball": {"pokeball": 5}}
            battle.use_item(battle.player_1, "pokeball", 0)
            outputs.append(battle.output)
            if battle.outcome == "caught":
                catches += 1
            else:
                misses += 1
        self.assertEqual(558, catches)
        self.assertEqual(442, misses)

        # Test status
        random.seed(900)
        catches = 0
        misses = 0
        outputs = []
        for i in range(1000):
            battle = BattleState(battle_state)
            battle.type = "wild"
            battle.player_2.party[0].status = "psn"
            battle.player_1.inventory = {"ball": {"pokeball": 5}}
            battle.use_item(battle.player_1, "pokeball", 0)
            outputs.append(battle.output)
            if battle.outcome == "caught":
                catches += 1
            else:
                misses += 1
        self.assertEqual(376, catches)
        self.assertEqual(624, misses)

        # Test ultra ball
        random.seed(900)
        catches = 0
        misses = 0
        outputs = []
        for i in range(1000):
            battle = BattleState(battle_state)
            battle.type = "wild"
            battle.player_1.inventory = {"ball": {"ultra-ball": 5}}
            battle.use_item(battle.player_1, "ultra-ball", 0)
            outputs.append(battle.output)
            if battle.outcome == "caught":
                catches += 1
            else:
                misses += 1
        self.assertEqual(464, catches)
        self.assertEqual(536, misses)

        # Test master ball
        random.seed(900)
        catches = 0
        misses = 0
        outputs = []
        for i in range(100):
            battle = BattleState(battle_state)
            battle.type = "wild"
            battle.player_1.inventory = {"ball": {"master-ball": 5}}
            battle.use_item(battle.player_1, "master-ball", 0)
            outputs.append(battle.output)
            if battle.outcome == "caught":
                catches += 1
            else:
                misses += 1
        self.assertEqual(100, catches)
        self.assertEqual(0, misses)

        # Test fainted
        battle = BattleState(battle_state)
        battle.type = "wild"
        battle.player_2.party[0].current_hp = 0
        battle.player_1.inventory = {"ball": {"pokeball": 5}}
        battle.use_item(battle.player_1, "pokeball", 0)
        self.assertEqual([{"text": "You cannot catch a fainted Pokémon!"}], battle.output)


    def test_switch(self):
        battle_state = self.std_battle.copy()
        # Standard switch
        battle = BattleState(battle_state)
        battle.player_2.get_current_pokemon().moves = [
            {"move": "pursuit", "pp": 20},
            {"move": None, "pp": None},
            {"move": None, "pp": None},
            {"move": None, "pp": None}
        ]
        battle.switch(battle.player_1, 1, {"action": "move", "move": "tackle"})
        self.assertEqual(1, battle.player_1.current_pokemon)
        # Pursuit
        # Entry hazard
        # Clear boosts
        battle = BattleState(battle_state)
        battle.player_1.stat_boosts["attack"] = 1
        battle.switch(battle.player_1, 1, {"action": "move", "move": "tackle"})
        self.assertEqual(0, battle.player_1.stat_boosts["attack"])
        self.assertEqual(1, battle.player_1.current_pokemon)

        # Clear choice
        battle = BattleState(battle_state)
        battle.player_1.choice = "tackle"
        battle.switch(battle.player_1, 1, {"action": "move", "move": "tackle"})
        self.assertIsNone(battle.player_1.choice)
        self.assertEqual(1, battle.player_1.current_pokemon)

        # Clear confusion
        battle = BattleState(battle_state)
        battle.player_1.confusion = 3
        battle.switch(battle.player_1, 1, {"action": "move", "move": "tackle"})
        self.assertEqual(0, battle.player_1.confusion)
        self.assertEqual(1, battle.player_1.current_pokemon)


    def test_check_surrender(self):
        battle_state = self.std_battle.copy()
        # P1 surrender case
        battle = BattleState(battle_state)
        ret = battle.check_surrender(True, False)
        self.assertEqual("p2_victory", battle.outcome)
        self.assertEqual([{"text": "P1 has surrendered!", "anim": ["p1_retreat"]}], battle.output)
        self.assertTrue(ret)
        # P2 surrender case
        battle = BattleState(battle_state)
        ret = battle.check_surrender(False, True)
        self.assertEqual("p1_victory", battle.outcome)
        self.assertEqual([{"text": "P2 has surrendered!", "anim": ["p2_retreat"]}], battle.output)
        self.assertTrue(ret)
        # Draw case
        battle = BattleState(battle_state)
        ret = battle.check_surrender(True, True)
        self.assertEqual("draw", battle.outcome)
        self.assertEqual([{"text": "The battle was a draw!", "anim": ["p1_retreat", "p2_retreat"]}], battle.output)
        self.assertTrue(ret)
        # No surrender case
        battle = BattleState(battle_state)
        ret = battle.check_surrender(False, False)
        self.assertIsNone(battle.outcome)
        self.assertEqual([], battle.output)
        self.assertFalse(ret)
        # Flee wild battle
        random.seed(900)
        escapes = 0
        fails = 0
        for i in range(100):
            battle = BattleState(battle_state)
            battle.escapes = 0
            ret = battle.check_surrender(True, False)
            if ret:
                if escapes == 0:
                    self.assertEqual("fled_battle", battle.outcome)
                    self.assertEqual([{"text": "Ran away from the wild Pokémon!", "anim": ["p1_retreat"]}], battle.output)
                escapes += 1
            else:
                if fails == 0:
                    self.assertIsNone(battle.outcome)
                    self.assertEqual([{"text": "Failed to run away!"}], battle.output)
                    self.assertEqual(1, battle.escapes)
                fails += 1
        self.assertEqual(40, escapes)
        self.assertEqual(60, fails)

