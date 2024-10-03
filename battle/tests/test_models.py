from django.test import TestCase
from django.contrib.auth.models import User
from battle import models
from accounts.models import Profile
from harvoldsite import consts
from pokemon.models import create_pokemon


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


    def test_standard_trainer(self):
        models.create_battle(self.trainer1.pk, 2, "npc")
        self.assertTrue(False)

    def test_trainer_missing(self):
        self.assertTrue(False)

    def test_standard_wild(self):
        self.assertTrue(False)

    def test_wild_missing(self):
        self.assertTrue(False)

    def test_wild_owned(self):
        self.assertTrue(False)

    def test_standard_live(self):
        self.assertTrue(False)

    def test_live_missing(self):
        self.assertTrue(False)
