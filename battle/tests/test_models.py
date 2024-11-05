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
        ret = models.create_battle(self.trainer1.pk, "bug_catcher_1", "npc")

        # Test battle object
        battle_obj = ret[1]
        self.assertEqual(self.trainer1, battle_obj.player_1)
        self.assertIsNone(battle_obj.player_2)
        self.assertEqual("bug_catcher_1", battle_obj.npc_opponent)
        self.assertIsNone(battle_obj.wild_opponent)

        # Test battle state
        battle_state = battle_obj.get_battle_state()
        self.assertNotIn("escapes", battle_state)
        self.assertEqual("test1", battle_state["player_1"]["name"])
        self.assertEqual("Bug Catcher Bob", battle_state["player_2"]["name"])
        p1_party_exp = [pkmn.get_battle_info() for pkmn in self.trainer1.get_party()]
        self.assertEqual(p1_party_exp, battle_state["player_1"]["party"])
        p2_party_exp = consts.TRAINERS["bug_catcher_1"]["team"]
        self.assertEqual(p2_party_exp, battle_state["player_2"]["party"])

    def test_trainer_missing(self):
        with self.assertRaises(KeyError) as e:
            models.create_battle(self.trainer1.pk, "not_an_npc", "npc")
        self.assertEqual("not_an_npc not recognized as a trainer", e.exception.args[0])

    def test_standard_wild(self):
        ret = models.create_battle(self.trainer1.pk, self.wild.pk, "wild")

        # Test battle object
        battle_obj = ret[1]
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
        battle_obj = ret[1]
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
        player_state = {
            "current_pokemon": 0,
            "contributors": [],
            "stat_boosts": [],
            "entry_hazards": [],
            "confusion": False,
            "locked_moves": [],
            "defense_active": [],
            "tailwind": None,
            "name": None
        }
        self.std_battle = {
            "player_1": player_state.copy(),
            "player_2": player_state.copy(),
            "weather": None,
            "weather_turns": 0,
            "terrain": None,
            "outcome": None,
            "type": "npc",
            "trick_room": None,
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

    def test_check_surrender(self):
        battle_state = self.std_battle.copy()
        battle_state["player_1"]["party"] = [
            self.snorlax.get_battle_info(),
            self.gengar.get_battle_info()]
        battle_state["player_2"]["party"] = [
            self.electivire.get_battle_info(),
            self.ferrothorn.get_battle_info()]
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
        self.assertEqual(17, escapes)
        self.assertEqual(83, fails)


    def test_switch(self):
        battle_state = self.std_battle.copy()
        battle_state["player_1"]["party"] = [
            self.snorlax.get_battle_info(),
            self.gengar.get_battle_info()]
        battle_state["player_2"]["party"] = [
            self.raticate.get_battle_info(),
            self.electivire.get_battle_info()]
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

    def test_use_potion(self):
        battle_state = self.std_battle.copy()
        battle_state["player_1"]["party"] = [
            self.snorlax.get_battle_info(),
            self.gengar.get_battle_info()]
        battle_state["player_2"]["party"] = [
            self.raticate.get_battle_info(),
            self.electivire.get_battle_info()]
        battle = BattleState(battle_state)

        # Test potions
        battle.player_1.party[0].current_hp = 10
        ret = battle.use_item(battle.player_1, "potion", 0)
        self.assertFalse(ret)
        self.assertEqual(30, battle.player_1.party[0].current_hp)

        # Test overheal
        battle.player_1.party[0].current_hp = 460
        ret = battle.use_item(battle.player_1, "potion", 0)
        self.assertFalse(ret)
        self.assertEqual(461, battle.player_1.party[0].current_hp)

        # Test max potions
        battle.player_1.party[0].current_hp = 10
        ret = battle.use_item(battle.player_1, "max-potion", 0)
        self.assertFalse(ret)
        self.assertEqual(461, battle.player_1.party[0].current_hp)

        # Test fainted
        battle.player_1.party[0].current_hp = 0
        ret = battle.use_item(battle.player_1, "max-potion", 0)
        self.assertFalse(ret)
        self.assertEqual(0, battle.player_1.party[0].current_hp)

    def test_use_cure(self):
        battle_state = self.std_battle.copy()
        battle_state["player_1"]["party"] = [
            self.snorlax.get_battle_info(),
            self.gengar.get_battle_info()]
        battle_state["player_2"]["party"] = [
            self.raticate.get_battle_info(),
            self.electivire.get_battle_info()]
        battle = BattleState(battle_state)

        # Test wrong status
        battle.player_1.party[0].status = "par"
        ret = battle.use_item(battle.player_1, "antidote", 0)
        self.assertFalse(ret)
        self.assertEqual("par", battle.player_1.party[0].status)

        # Test right status
        battle.player_1.party[0].status = "psn"
        ret = battle.use_item(battle.player_1, "antidote", 0)
        self.assertFalse(ret)
        self.assertIsNone(battle.player_1.party[0].status)

        # Test right status
        battle.player_1.party[0].status = "txc"
        ret = battle.use_item(battle.player_1, "antidote", 0)
        self.assertFalse(ret)
        self.assertIsNone(battle.player_1.party[0].status)

        # Test full heal
        battle.player_1.party[0].status = "par"
        ret = battle.use_item(battle.player_1, "full-heal", 0)
        self.assertFalse(ret)
        self.assertIsNone(battle.player_1.party[0].status)

        # Test full heal
        battle.player_1.party[0].status = "slp"
        ret = battle.use_item(battle.player_1, "full-heal", 0)
        self.assertFalse(ret)
        self.assertIsNone(battle.player_1.party[0].status)

        # Test full heal
        battle.player_1.party[0].status = "txc"
        ret = battle.use_item(battle.player_1, "full-heal", 0)
        self.assertFalse(ret)
        self.assertIsNone(battle.player_1.party[0].status)

    def test_use_revive(self):
        battle_state = self.std_battle.copy()
        battle_state["player_1"]["party"] = [
            self.snorlax.get_battle_info(),
            self.gengar.get_battle_info()]
        battle_state["player_2"]["party"] = [
            self.raticate.get_battle_info(),
            self.electivire.get_battle_info()]
        battle = BattleState(battle_state)

        # Test not dead
        battle.player_1.party[0].current_hp = 30
        ret = battle.use_item(battle.player_1, "revive", 0)
        self.assertFalse(ret)
        self.assertEqual(30, battle.player_1.party[0].current_hp)

        # Test revive
        battle.player_1.party[0].current_hp = 0
        ret = battle.use_item(battle.player_1, "revive", 0)
        self.assertFalse(ret)
        self.assertEqual(231, battle.player_1.party[0].current_hp)

        # Test max revive
        battle.player_1.party[0].current_hp = 0
        ret = battle.use_item(battle.player_1, "max-revive", 0)
        self.assertFalse(ret)
        self.assertEqual(461, battle.player_1.party[0].current_hp)

    def test_catch_pokemon(self):
        battle_state = self.std_battle.copy()
        battle_state["player_1"]["party"] = [
            self.snorlax.get_battle_info(),
            self.gengar.get_battle_info()]
        battle_state["player_2"]["party"] = [
            self.raticate.get_battle_info(),
            self.electivire.get_battle_info()]
        battle = BattleState(battle_state)
        battle.type = "npc"

        # Test not wild
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
        battle.use_item(battle.player_1, "pokeball", 0)
        self.assertEqual([{"text": "You cannot catch a fainted Pokémon!"}], battle.output)

