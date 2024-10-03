from django.test import TestCase
from django.contrib.auth.models import User
from accounts import models
from pokemon.models import create_pokemon
from harvoldsite import consts


class TestAddToParty(TestCase):
    def setUp(self):
        self.user1 = User(username="test1", password="test1", email="test1@test.com")
        self.user1.save()
        self.trainer1 = models.Profile(character="1", user=self.user1)
        self.trainer1.save()
        self.user2 = User(username="test2", password="test2", email="test2@test.com")
        self.user2.save()
        self.trainer2 = models.Profile(character="1", user=self.user2)
        self.trainer2.save()
        self.pkmn1 = create_pokemon("001", 5, "m")
        self.pkmn1.assign_trainer(self.trainer1, "pokeball")
        self.pkmn2 = create_pokemon("004", 5, "f")
        self.pkmn2.assign_trainer(self.trainer1, "pokeball")
        self.pkmn3 = create_pokemon("007", 5, "m")
        self.pkmn3.assign_trainer(self.trainer2, "pokeball")
        self.pkmn4 = create_pokemon("001", 5, "m")
        self.pkmn4.assign_trainer(self.trainer1, "pokeball")
        self.pkmn5 = create_pokemon("004", 5, "f")
        self.pkmn5.assign_trainer(self.trainer1, "pokeball")
        self.pkmn6 = create_pokemon("001", 5, "m")
        self.pkmn6.assign_trainer(self.trainer1, "pokeball")
        self.pkmn7 = create_pokemon("004", 5, "f")
        self.pkmn7.assign_trainer(self.trainer1, "pokeball")
        self.pkmn8 = create_pokemon("004", 5, "f")
        self.pkmn8.assign_trainer(self.trainer1, "pokeball")


    def test_standard(self):
        self.trainer1.slot_1 = self.pkmn1
        self.trainer1.slot_2 = None
        self.trainer1.slot_3 = None
        self.trainer1.slot_4 = None
        self.trainer1.slot_5 = None
        self.trainer1.slot_6 = None
        self.trainer1.add_to_party(self.pkmn2)
        self.assertEqual(self.pkmn1, self.trainer1.slot_1)
        self.assertEqual(self.pkmn2, self.trainer1.slot_2)
        self.assertIsNone(self.trainer1.slot_3)


    def test_duplicate(self):
        self.trainer1.slot_1 = None
        self.trainer1.slot_2 = None
        self.trainer1.slot_3 = None
        self.trainer1.slot_4 = None
        self.trainer1.slot_5 = None
        self.trainer1.slot_6 = None
        self.trainer1.add_to_party(self.pkmn1)
        ret = self.trainer1.add_to_party(self.pkmn1)
        self.assertEqual("This Pokemon is already in your party!", ret)


    def test_party_full(self):
        self.trainer1.slot_1 = self.pkmn1
        self.trainer1.slot_2 = self.pkmn4
        self.trainer1.slot_3 = self.pkmn5
        self.trainer1.slot_4 = self.pkmn6
        self.trainer1.slot_5 = self.pkmn7
        self.trainer1.slot_6 = self.pkmn8
        ret = self.trainer1.add_to_party(self.pkmn2)
        self.assertEqual("Party is full.", ret)


    def test_not_owned(self):
        self.trainer1.slot_1 = self.pkmn1
        self.trainer1.slot_2 = None
        self.trainer1.slot_3 = None
        self.trainer1.slot_4 = None
        self.trainer1.slot_5 = None
        self.trainer1.slot_6 = None
        ret = self.trainer1.add_to_party(self.pkmn3)
        self.assertEqual("You don't own this pokemon!", ret)
        self.assertIsNone(self.trainer1.slot_2)


    def test_in_combat(self):
        self.trainer1.state = "battle"
        self.trainer1.slot_1 = self.pkmn1
        self.trainer1.slot_2 = None
        self.trainer1.slot_3 = None
        self.trainer1.slot_4 = None
        self.trainer1.slot_5 = None
        self.trainer1.slot_6 = None
        ret = self.trainer1.add_to_party(self.pkmn2)
        self.assertEqual("Party cannot be modified in battle.", ret)
        self.assertIsNone(self.trainer1.slot_2)
        self.trainer1.state = "idle"


    def test_in_trade(self):
        self.pkmn2.location = "trade"
        self.trainer1.slot_1 = self.pkmn1
        self.trainer1.slot_2 = None
        self.trainer1.slot_3 = None
        self.trainer1.slot_4 = None
        self.trainer1.slot_5 = None
        self.trainer1.slot_6 = None
        ret = self.trainer1.add_to_party(self.pkmn2)
        self.assertEqual("This Pokemon is currently in a trade!", ret)
        self.assertIsNone(self.trainer1.slot_2)
        self.pkmn2.location = "box"


class TestRemoveFromParty(TestCase):
    def setUp(self):
        self.user = User(username="test1", password="test1", email="test1@test.com")
        self.user.save()
        self.trainer = models.Profile(character="1", user=self.user)
        self.trainer.save()
        self.pkmn1 = create_pokemon("001", 5, "m")
        self.pkmn1.assign_trainer(self.trainer, "pokeball")
        self.pkmn2 = create_pokemon("004", 5, "f")
        self.pkmn2.assign_trainer(self.trainer, "pokeball")


    def test_standard(self):
        self.trainer.slot_1 = self.pkmn1
        self.trainer.slot_2 = self.pkmn2
        self.trainer.slot_3 = None
        self.trainer.slot_4 = None
        self.trainer.slot_5 = None
        self.trainer.slot_6 = None
        self.trainer.remove_from_party("slot_2")
        self.assertEqual(self.pkmn1, self.trainer.slot_1)
        self.assertIsNone(self.trainer.slot_2)


    def test_remove_first(self):
        self.trainer.slot_1 = self.pkmn1
        self.trainer.slot_2 = self.pkmn2
        self.trainer.slot_3 = None
        self.trainer.slot_4 = None
        self.trainer.slot_5 = None
        self.trainer.slot_6 = None
        self.trainer.remove_from_party("slot_1")
        self.assertEqual(self.pkmn2, self.trainer.slot_1)
        self.assertIsNone(self.trainer.slot_2)


    def test_no_pokemon(self):
        self.trainer.slot_1 = self.pkmn1
        self.trainer.slot_2 = None
        self.trainer.slot_3 = None
        self.trainer.slot_4 = None
        self.trainer.slot_5 = None
        self.trainer.slot_6 = None
        ret = self.trainer.remove_from_party("slot_1")
        self.assertEqual("This is your last Pokemon!", ret)
        self.assertEqual(self.pkmn1, self.trainer.slot_1)


    def test_in_combat(self):
        self.trainer.state = "battle"
        self.trainer.slot_1 = self.pkmn1
        self.trainer.slot_2 = self.pkmn2
        self.trainer.slot_3 = None
        self.trainer.slot_4 = None
        self.trainer.slot_5 = None
        self.trainer.slot_6 = None
        self.trainer.remove_from_party("slot_2")
        self.assertEqual(self.pkmn1, self.trainer.slot_1)
        self.assertEqual(self.pkmn2, self.trainer.slot_2)
        self.trainer.state = "idle"


class TestGetBox(TestCase):
    def setUp(self):
        self.user1 = User(username="test1", password="test1", email="test1@test.com")
        self.user1.save()
        self.trainer1 = models.Profile(character="1", user=self.user1)
        self.trainer1.save()
        self.user2 = User(username="test2", password="test2", email="test2@test.com")
        self.user2.save()
        self.trainer2 = models.Profile(character="1", user=self.user2)
        self.trainer2.save()
        self.pkmn1 = create_pokemon("001", 5, "m", iv_override={stat: 31 for stat in consts.STATS})
        self.pkmn1.assign_trainer(self.trainer1, "pokeball")
        self.pkmn2 = create_pokemon("004", 11, "f", iv_override={stat: 22 for stat in consts.STATS})
        self.pkmn2.assign_trainer(self.trainer1, "pokeball")
        self.pkmn3 = create_pokemon("007", 6, "m", iv_override={stat: 7 for stat in consts.STATS})
        self.pkmn3.assign_trainer(self.trainer1, "pokeball")
        self.pkmn4 = create_pokemon("111", 23, "m", iv_override={stat: 21 for stat in consts.STATS})
        self.pkmn4.assign_trainer(self.trainer1, "pokeball")
        self.pkmn5 = create_pokemon("444", 23, "f", iv_override={stat: 11 for stat in consts.STATS})
        self.pkmn5.assign_trainer(self.trainer1, "pokeball")
        self.pkmn6 = create_pokemon("333", 77, "m", iv_override={stat: 2 for stat in consts.STATS})
        self.pkmn6.assign_trainer(self.trainer1, "pokeball")
        self.pkmn7 = create_pokemon("111", 100, "f", iv_override={stat: 11 for stat in consts.STATS})
        self.pkmn7.assign_trainer(self.trainer1, "pokeball")
        self.pkmn8 = create_pokemon("112", 91, "f", iv_override={stat: 27 for stat in consts.STATS})
        self.pkmn8.assign_trainer(self.trainer1, "pokeball")



    def test_get_box_standard(self):
        box = self.trainer1.pokemon()
        self.assertTrue(False)

    def test_get_box_page_size(self):
        box = self.trainer1.get_box()
        self.assertTrue(False)


    def test_get_box_locked(self):
        box = self.trainer1.get_box()
        self.assertTrue(False)


    def test_get_box_tagged(self):
        box = self.trainer1.get_box()
        self.assertTrue(False)


    def test_get_box_dex(self):
        box = self.trainer1.get_box()
        self.assertTrue(False)


    def test_get_box_level(self):
        box = self.trainer1.get_box()
        self.assertTrue(False)


    def test_get_box_bst(self):
        box = self.trainer1.get_box()
        self.assertTrue(False)


    def test_get_box_iv(self):
        box = self.trainer1.get_box()
        self.assertTrue(False)


    def test_get_box_filter_order(self):
        box = self.trainer1.get_box()
        self.assertTrue(False)




class TestSortParty(TestCase):
    def setUp(self):
        self.user = User(username="test1", password="test1", email="test1@test.com")
        self.user.save()
        self.trainer = models.Profile(character="1", user=self.user)
        self.trainer.save()
        self.pkmn1 = create_pokemon("001", 5, "m")
        self.pkmn1.assign_trainer(self.trainer, "pokeball")
        self.pkmn2 = create_pokemon("004", 5, "f")
        self.pkmn2.assign_trainer(self.trainer, "pokeball")
        self.pkmn3 = create_pokemon("007", 5, "m")
        self.pkmn3.assign_trainer(self.trainer, "pokeball")

    def test_standard_party_sort(self):
        self.trainer.slot_1 = None
        self.trainer.slot_2 = self.pkmn1
        self.trainer.slot_3 = None
        self.trainer.slot_4 = self.pkmn2
        self.trainer.slot_5 = None
        self.trainer.slot_6 = self.pkmn3
        self.trainer._sort_party()
        self.assertEqual(self.pkmn1, self.trainer.slot_1)
        self.assertEqual(self.pkmn2, self.trainer.slot_2)
        self.assertEqual(self.pkmn3, self.trainer.slot_3)
        self.assertIsNone(self.trainer.slot_4)
        self.assertIsNone(self.trainer.slot_5)
        self.assertIsNone(self.trainer.slot_6)


    def test_removed_pokemon(self):
        self.trainer.slot_1 = self.pkmn1
        self.trainer.slot_2 = None
        self.trainer.slot_3 = self.pkmn3
        self.trainer.slot_4 = None
        self.trainer.slot_5 = None
        self.trainer.slot_6 = None
        self.trainer._sort_party()
        self.assertEqual(self.pkmn1, self.trainer.slot_1)
        self.assertEqual(self.pkmn3, self.trainer.slot_2)
        self.assertIsNone(self.trainer.slot_3)
        self.assertIsNone(self.trainer.slot_4)
        self.assertIsNone(self.trainer.slot_5)
        self.assertIsNone(self.trainer.slot_6)


    def test_added_pokemon(self):
        self.trainer.slot_1 = self.pkmn1
        self.trainer.slot_2 = self.pkmn3
        self.trainer.slot_3 = None
        self.trainer.slot_4 = None
        self.trainer.slot_5 = None
        self.trainer.slot_6 = self.pkmn2
        self.trainer._sort_party()
        self.assertEqual(self.pkmn1, self.trainer.slot_1)
        self.assertEqual(self.pkmn3, self.trainer.slot_2)
        self.assertEqual(self.pkmn2, self.trainer.slot_3)
        self.assertIsNone(self.trainer.slot_4)
        self.assertIsNone(self.trainer.slot_5)
        self.assertIsNone(self.trainer.slot_6)


class TestCheckPartyValid(TestCase):
    def setUp(self):
        self.user1 = User(username="test1", password="test1", email="test1@test.com")
        self.user1.save()
        self.trainer1 = models.Profile(character="1", user=self.user1)
        self.trainer1.save()
        self.user2 = User(username="test2", password="test2", email="test2@test.com")
        self.user2.save()
        self.trainer2 = models.Profile(character="1", user=self.user2)
        self.trainer2.save()
        self.pkmn1 = create_pokemon("001", 5, "m")
        self.pkmn1.assign_trainer(self.trainer1, "pokeball")
        self.pkmn2 = create_pokemon("004", 5, "f")
        self.pkmn2.assign_trainer(self.trainer1, "pokeball")
        self.pkmn3 = create_pokemon("007", 5, "m")
        self.pkmn3.assign_trainer(self.trainer2, "pokeball")


    def test_wrong_order(self):
        self.trainer1.slot_1 = self.pkmn1
        self.trainer1.slot_2 = None
        self.trainer1.slot_3 = self.pkmn2
        self.trainer1.slot_4 = None
        self.trainer1.slot_5 = None
        self.trainer1.slot_6 = None
        ret = self.trainer1._check_party_valid()
        self.assertFalse(ret[0])
        self.assertEqual("Pokemon party is out of order! Please sort!", ret[1])


    def test_duplicate(self):
        self.trainer1.slot_1 = self.pkmn1
        self.trainer1.slot_2 = self.pkmn1
        self.trainer1.slot_3 = None
        self.trainer1.slot_4 = None
        self.trainer1.slot_5 = None
        self.trainer1.slot_6 = None
        ret = self.trainer1._check_party_valid()
        self.assertFalse(ret[0])
        self.assertEqual("Duplicate Pokemon in party at slot_2!", ret[1])


    def test_unowned(self):
        self.trainer1.slot_1 = self.pkmn1
        self.trainer1.slot_2 = self.pkmn3
        self.trainer1.slot_3 = None
        self.trainer1.slot_4 = None
        self.trainer1.slot_5 = None
        self.trainer1.slot_6 = None
        ret = self.trainer1._check_party_valid()
        self.assertFalse(ret[0])
        self.assertEqual("Pokemon in party that is not owned by trainer!", ret[1])


    def test_valid(self):
        self.trainer1.slot_1 = self.pkmn1
        self.trainer1.slot_2 = self.pkmn2
        self.trainer1.slot_3 = None
        self.trainer1.slot_4 = None
        self.trainer1.slot_5 = None
        self.trainer1.slot_6 = None
        ret = self.trainer1._check_party_valid()
        self.assertTrue(ret[0])
        self.assertEqual("", ret[1])


class TestPurchaseItem(TestCase):
    def setUp(self):
        self.user1 = User(username="test1", password="test1", email="test1@test.com")
        self.user1.save()
        self.trainer1 = models.Profile(character="1", user=self.user1)
        self.trainer1.save()


    def test_no_shop(self):
        self.trainer1.money = 10000
        self.trainer1.bag = models.default_bag()
        ret = self.trainer1.purchase_item("pokeball", 1, "mart1")
        exp = "No such shop!"
        self.assertFalse(ret[0])
        self.assertEqual(exp, ret[1])


    def test_no_item(self):
        self.trainer1.money = 10000
        self.trainer1.bag = models.default_bag()
        ret = self.trainer1.purchase_item("pokeball1", 1, "mart")
        exp = "No such item in the shop!"
        self.assertFalse(ret[0])
        self.assertEqual(exp, ret[1])


    def test_no_money(self):
        self.trainer1.money = 10000
        self.trainer1.bag = models.default_bag()
        ret = self.trainer1.purchase_item("pokeball", 9999, "mart")
        exp = "Not enough money!"
        self.assertFalse(ret[0])
        self.assertEqual(exp, ret[1])


    def test_success(self):
        self.trainer1.money = 10000
        self.trainer1.bag = models.default_bag()
        ret = self.trainer1.purchase_item("pokeball", 1, "mart")
        self.assertTrue(ret[0])
        self.assertEqual(self.trainer1.money, 9800)
        self.assertEqual(self.trainer1.bag["ball"]["pokeball"], 6)


    def test_success_new(self):
        self.trainer1.money = 10000
        self.trainer1.bag = models.default_bag()
        ret = self.trainer1.purchase_item("great_ball", 1, "mart")
        self.assertTrue(ret[0])
        self.assertEqual(self.trainer1.money, 9400)
        self.assertEqual(self.trainer1.bag["ball"]["great_ball"], 1)