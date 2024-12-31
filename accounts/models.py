from datetime import datetime, date
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import IntegrityError, transaction
from pokemon.models import Pokemon
from harvoldsite import consts

# Create your models here.
def default_bag():
    return {
        "ball": {
            "pokeball": 5
        },
        "medicine": {
            "potion": 5
        },
        "general": {},
        "machines": {},
        "held_items": {},
        "berries": {},
        "key": {}
    }


def item_type(item):
    if item not in consts.ITEMS:
        return False
    return consts.ITEMS[item]["category"]


def default_map():
    return ["oak_village"]


def default_pokedex():
    return {str(dex).zfill(3): False for dex in range(1, 650)}

def default_badges():
    return {
        "grass": None,
        "electric": None,
        "water": None,
        "ground": None,
        "fighting": None,
        "fire": None,
        "ghost": None,
        "psychic": None,
        "steel": None,
        "dragon": None
    }


class Profile(models.Model):
    # Administrative fields
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE
    )
    banned = models.BooleanField(default=False)

    # Trainer data
    description = models.CharField(max_length=500, null=True)
    title = models.CharField(max_length=50, default="Novice Trainer")
    faction = models.IntegerField(null=True)
    state = models.CharField(default="idle", max_length=10) # Used to control in-battle status
    pokedex_progress = models.JSONField(default=default_pokedex)
    badges = models.JSONField(default=default_badges)
    trainer_points = models.IntegerField(default=0)

    # Trainer values
    character = models.IntegerField()
    money = models.IntegerField(default=100000)
    bag = models.JSONField(default=default_bag)

    # Trainer stats
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    pvp_wins = models.IntegerField(default=0)
    pvp_losses = models.IntegerField(default=0)

    # Party info
    slot_1 = models.ForeignKey("pokemon.Pokemon", related_name="slot1", null=True, on_delete=models.SET_NULL)
    slot_2 = models.ForeignKey("pokemon.Pokemon", related_name="slot2", null=True, on_delete=models.SET_NULL)
    slot_3 = models.ForeignKey("pokemon.Pokemon", related_name="slot3", null=True, on_delete=models.SET_NULL)
    slot_4 = models.ForeignKey("pokemon.Pokemon", related_name="slot4", null=True, on_delete=models.SET_NULL)
    slot_5 = models.ForeignKey("pokemon.Pokemon", related_name="slot5", null=True, on_delete=models.SET_NULL)
    slot_6 = models.ForeignKey("pokemon.Pokemon", related_name="slot6", null=True, on_delete=models.SET_NULL)

    # Progress info
    map_progress = models.JSONField(default=default_map)
    current_map = models.TextField(max_length=20, default="oak_village")
    current_pos = models.JSONField(default=None, blank=True, null=True)
    current_battle = models.ForeignKey("battle.Battle", blank=True, null=True, on_delete=models.SET_NULL)
    wild_opponent = models.JSONField(blank=True, null=True, default=None)

    # Daily tracker
    last_update = models.DateField(blank=True, null=True, auto_now_add=True)
    trainers_beat = models.JSONField(blank=True, null=True, default=None)

    @property
    def char_id(self):
        return str(self.character).zfill(2)

    @property
    def dex_entries(self):
        return sum(self.pokedex_progress.values())

    def add_to_party(self, pokemon):
        """
        Add a Pokemon to the last position in the party and bubble upwards.
        """
        # Check if player in battle
        if self.state == "battle":
            return "Party cannot be modified in battle."

        # Check if pokemon is owned
        if pokemon.trainer != self:
            return "You don't own this pokemon!"

        # Check if pokemon is in a trade
        if pokemon.location == "trade":
            return "This Pokemon is currently in a trade!"

        if pokemon.location == "party":
            return "This Pokemon is already in your party!"

        # Check if party is full
        if self.slot_6 is None:
            self.slot_6 = pokemon
            self._sort_party()
            ret = self._check_party_valid()

            # Propagate error message
            if not ret[0]:
                raise ValueError(ret[1])
            pokemon.location = "party"
            try:
                with transaction.atomic():
                    self.save()
                    pokemon.save()
            except IntegrityError:
                return "Failed to add Pokemon to party, please try again in a few moments."
        else:
            return "Party is full."


    def remove_from_party(self, pokemon):
        """
        Remove a Pokemon from any slot in the party and bubble upwards.
        """
        if pokemon is None:
            return
        # Check if player in battle
        if self.state == "battle":
            return "Party cannot be modified in battle."

        slot = None
        if pokemon == self.slot_1:
            slot = "slot_1"
        elif pokemon == self.slot_2:
            slot = "slot_2"
        elif pokemon == self.slot_3:
            slot = "slot_3"
        elif pokemon == self.slot_4:
            slot = "slot_4"
        elif pokemon == self.slot_5:
            slot = "slot_5"
        elif pokemon == self.slot_6:
            slot = "slot_6"
        else:
            return "Pokemon not in party!"

        # Check if it's the last pokemon
        if self.slot_2 is None:
            return "This is your last Pokemon!"

        # Place the Pokemon in the box
        pokemon.location = "box"

        # Empty the slot
        self.__setattr__(slot, None)

        # Reorganize party
        self._sort_party()
        ret = self._check_party_valid()

        # Propagate error message
        if not ret[0]:
            raise ValueError(ret[1])
        try:
            with transaction.atomic():
                self.save()
                pokemon.save()
        except IntegrityError:
            return "Failed to remove Pokemon from party, please try again in a few moments."


    def swap_pokemon(self, slot_1, slot_2, skip_save=False):
        if slot_1 == slot_2:
            return
        slot_1_pkmn = getattr(self, slot_1)
        slot_2_pkmn = getattr(self, slot_2)
        if slot_1_pkmn is None or slot_2_pkmn is None:
            return
        setattr(self, slot_1, slot_2_pkmn)
        setattr(self, slot_2, slot_1_pkmn)
        if skip_save:
            return
        self.save()


    def get_pokemon(self, order_by="caught_date", descending=False, filter_by=None):
        """
        Function to get a user's box, splitting Pokemon into pages.
        """
        if isinstance(descending, str):
            descending = descending == "True"
        filters = {
        }
        valid_filters = ["tag", "trainer", "location"]
        if filter_by is not None:
            for field, value in filter_by.items():
                if field in valid_filters:
                    filters[field] = value
        if order_by not in ["caught_date", "dex_number", "level", "iv_total", "bst"]:
            return "Cannot order by field {}!".format(order_by)
        if descending:
            order_by = "-{}".format(order_by)
        box = list(Pokemon.objects.filter(**filters).order_by(order_by))
        # Convert to dict and save names
        names = [pkmn.name for pkmn in box]
        box = [pkmn.__dict__ for pkmn in box]
        for i, pkmn in enumerate(box):
            pkmn["name"] = names[i]
        # Convert datetime
        for pkmn in box:
            pkmn["caught_date"] = pkmn["caught_date"].timestamp()
            pkmn["dex_number"] = str(pkmn["dex_number"]).zfill(3)
            del pkmn["_state"]
        # Convert to JSON if needed
        return box


    def get_party(self, return_none=False):
        """
        Return the party
        """
        party = [self.slot_1, self.slot_2, self.slot_3, self.slot_4, self.slot_5, self.slot_6]
        if return_none:
            return party
        party = [pkmn for pkmn in party if pkmn is not None]
        return party

    def _sort_party(self):
        """
        Sort party to place pokemon in earliest slots available.

        Does not check if player is in battle.
        """
        slots = ["slot_1", "slot_2", "slot_3", "slot_4", "slot_5", "slot_6"]
        party = []
        for slot in slots:
            if getattr(self, slot) is not None:
                party.append(getattr(self, slot))
        party += [None] * (6 - len(party))
        for pkmn, slot in zip(party, slots):
            setattr(self, slot, pkmn)


    def _check_party_valid(self):
        """
        Check that party is valid

        1. No duplicate pokemon
        2. No empty slots before existing pokemon
        3. No pokemon that are not owned by the trainer

        This function should be called before committing any changes to party
        """
        found_pokemon = []
        found_none = False
        slots = ["slot_1", "slot_2", "slot_3", "slot_4", "slot_5", "slot_6"]
        for slot in slots:
            pokemon = getattr(self, slot)
            if pokemon is None:
                found_none = True
                continue
            elif found_none:
                return (False, "Pokemon party is out of order! Please sort!")
            if pokemon in found_pokemon:
                return (False, "Duplicate Pokemon in party at {}!".format(slot))
            if pokemon.trainer != self:
                return (False, "Pokemon in party that is not owned by trainer!")
            found_pokemon.append(pokemon)
        return (True, "")


    def purchase_item(self, item, quantity):
        """
        Purchase an item from the shop
        """
        category = item_type(item)

        if category is False:
            return (False, "No such item!")

        # Check item category exists
        if category not in consts.MART:
            return (False, "No such category!")

        # Check item in shop
        if item not in consts.MART[category]:
            return (False, "No such item in the shop!")

        # Check for money
        item_price = consts.MART[category][item]
        if self.money < item_price * quantity:
            return (False, "Not enough money!")

        # Transaction
        self.money = self.money - item_price * quantity
        if self.add_item(item, quantity):
            self.save()
            return (True, "")
        return (False, "Failed to add item!")


    def add_item(self, item, quantity):
        """
        Give the user an item
        """
        # Get item type
        category = item_type(item)
        if category is None:
            return False
        if item in self.bag[category]:
            self.bag[category][item] += quantity
        else:
            self.bag[category][item] = quantity
        return True



    def has_item(self, item, quantity=1):
        """
        Check that the user has the item
        """
        # Get item type
        category = item_type(item)
        if category is None:
            return False
        # Check if user has item
        if item not in self.bag[category]:
            return False
        return self.bag[category][item] > (quantity - 1)


    def consume_item(self, item, quantity=1):
        """
        Check that the user has the item
        """
        category = item_type(item)
        if category is None:
            return False
        if item not in self.bag[category]:
            return False
        if self.bag[category][item] < quantity:
            return False
        self.bag[category][item] -= quantity
        if self.bag[category][item] < 1:
            self.bag[category].pop(item)
        self.save()
        return True


    def add_pokedex(self, dex):
        if dex in self.pokedex_progress:
            self.pokedex_progress[dex] = True
            self.save()

    def beat_trainer(self, trainer, skip_save=False):
        self.last_update = date.today()
        if self.trainers_beat is None:
            self.trainers_beat = [trainer]
        else:
            self.trainers_beat.append(trainer)
        if skip_save:
            return
        self.save()


    def has_beat_trainer(self, trainer):
        if self.trainers_beat is None:
            return False
        if self.last_update != date.today():
            return False
        return trainer in self.trainers_beat