from datetime import datetime, date
import pandas as pd
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.urls import reverse
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
    last_city = models.TextField(max_length=20, default="oak_village")
    current_pos = models.JSONField(default=None, blank=True, null=True)
    current_battle = models.ForeignKey("battle.Battle", blank=True, null=True, on_delete=models.SET_NULL)
    current_gauntlet = models.ForeignKey("battle.Gauntlet", blank=True, null=True, on_delete=models.SET_NULL)
    wild_opponent = models.JSONField(blank=True, null=True, default=None)

    # Daily tracker
    last_update = models.DateField(blank=True, null=True, auto_now_add=True)
    trainers_beat = models.JSONField(blank=True, null=True, default=None)

    # Messages
    inbox_flag = models.BooleanField(default=False)

    @property
    def char_id(self):
        return str(self.character).zfill(2)

    @property
    def dex_entries(self):
        return sum(self.pokedex_progress.values())

    def tradeable_items(self):
        tradeable = {}
        for category, grouped_items in self.bag.items():
            if category in ["general", "key"]:
                continue
            for item_name, quantity in grouped_items.items():
                if category in ["machines"] and "hm" in item_name:
                    continue
                tradeable[item_name] = quantity
        return tradeable

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
        if slot_1 not in ["slot_1", "slot_2", "slot_3", "slot_4", "slot_5", "slot_6"]:
            return
        if slot_2 not in ["slot_1", "slot_2", "slot_3", "slot_4", "slot_5", "slot_6"]:
            return
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
            if trainer not in self.trainers_beat:
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


    def teach_tm(self, tm, target, move_slot):
        if target not in ["slot_1", "slot_2", "slot_3", "slot_4", "slot_5", "slot_6"]:
            return "Must be a valid slot"
        pokemon = getattr(self, target)
        if pokemon is None:
            return "Select a valid Pokémon."
        if tm not in consts.ITEMS:
            return "Not a valid item!"
        if consts.ITEMS[tm]["category"] != "machines":
            return "Not a valid TM!"
        move = consts.ITEMS[tm]["move"]
        if not tm in self.bag["machines"]:
            return "You do not have this move!"
        if self.bag["machines"][tm] < 1:
            return "You do not have this move!"
        try:
            with transaction.atomic():
                ret = pokemon.learn_move(move, move_slot, tms=True)
                if ret is not None:
                    return "Did not learn move"
                if not "hm" in tm:
                    if not self.consume_item(tm, 1):
                        return "Did not consume item"
        except:
            return "Failed to teach move."


    def take_item(self, pokemon):
        """
        Take held item from Pokemon, accepts pokemon object or slot
        """
        if pokemon in ["slot_1", "slot_2", "slot_3", "slot_4", "slot_5", "slot_6"]:
            pokemon = getattr(self, pokemon)
        if pokemon.held_item is None:
            return "No item to take."
        if pokemon.trainer != self:
            return "Cannot take someone else's item."
        item = pokemon.held_item
        try:
            with transaction.atomic():
                self.add_item(item, 1)
                pokemon.held_item = None
                self.save()
                pokemon.save()
        except IntegrityError:
            return "Failed to take item."


    def give_item(self, item, pokemon, category="held_items"):
        """
        Give held item to target, target can be slot or pokemon
        """
        if pokemon in ["slot_1", "slot_2", "slot_3", "slot_4", "slot_5", "slot_6"]:
            pokemon = getattr(self, pokemon)

        if pokemon is None:
            return "Select a valid Pokémon."
        if item not in consts.ITEMS:
            return "Not a valid item!"
        if consts.ITEMS[item]["category"] != category:
            return "Not a valid held item!"
        if not item in self.bag[category]:
            return "You do not have this move!"
        if self.bag[category][item] < 1:
            return "You do not have this move!"
        if pokemon.trainer != self:
            return "Cannot give someone else's Pokemon an item."

        if pokemon.held_item is not None:
            self.take_item(pokemon)
        try:
            with transaction.atomic():
                self.consume_item(item, 1)
                pokemon.held_item = item
                pokemon.save()
        except IntegrityError:
            return "Failed to add item"


    def has_unread(self):
        received = Messages.objects.filter(recipient=self, read=False)
        return bool(len(received))


    def has_move_in_party(self, move):
        for pkmn in self.get_party():
            moves = pkmn.get_moves(names=True)
            if move in moves:
                return True
        return False


    def can_use_hm(self, move):
        hm_reqs = {
            "surf": "water",
            "cut": "grass",
            "flash": "electric",
            "fly": "dragon",
            "dive": "steel",
            "rocksmash": "ghost"
        }
        if move not in hm_reqs:
            return False
        badge = hm_reqs[move]
        return self.badges[badge] is not None and self.has_move_in_party(move)


    def use_bag_item(self, item, target):
        # Check target valid
        if target not in ["slot_1", "slot_2", "slot_3", "slot_4", "slot_5", "slot_6"]:
            return "Must be a valid slot"
        pokemon = getattr(self, target)
        if pokemon is None:
            return "Select a valid Pokémon."
        if item not in consts.ITEMS:
            return "Not a valid item!"
        category = consts.ITEMS[item]["category"]

        if category in ["medicine", "berries"]:
            # Check if item is combat medicine/berry item
            if item in consts.ITEM_USAGE[category]:
                item_data = consts.ITEM_USAGE[category][item]
                item_effects = item_data["effects"]
                if item_data["valid_targets"] == "alive":
                    if pokemon.current_hp < 1:
                        return "Cannot use that item on a fainted target."
                elif pokemon.current_hp > 0:
                    return "Cannot use that item on that target."
                if "hp" in item_effects:
                    if item_effects["hp"] == "full":
                        pokemon.current_hp = pokemon.hp_stat
                    # Just for revives
                    elif item_effects["hp"] == "half":
                        pokemon.current_hp = int((pokemon.hp_stat + 1) / 2)
                    else:
                        pokemon.current_hp = min(pokemon.current_hp + item_effects["hp"],
                                                        pokemon.hp_stat)
                if "status" in item_effects:
                    if item_effects["status"] == "any":
                        pokemon.status = ""
                    elif item_effects["status"] == pokemon.status:
                        pokemon.status = ""
                    elif item_effects["status"] == "psn" and pokemon.status == "txc":
                        pokemon.status = ""
                try:
                    with transaction.atomic():
                        self.consume_item(item, 1)
                        pokemon.save()
                except IntegrityError:
                    return "Failed to use item."
            # Check if item is EV reducing berry or medicine
            elif item in consts.EV_MODIFIERS:
                item_effect = consts.EV_MODIFIERS[item]
                try:
                    with transaction.atomic():
                        self.consume_item(item, 1)
                        # If happiness increase, process that
                        if len(item_effect) > 2:
                            pokemon.happiness = min(255, pokemon.happiness + item_effect[2])
                        ev_gain = [item_effect[1] if item_effect[0] == stat else 0 for stat in consts.STATS]
                        pokemon.add_evs(ev_gain, recalculate=True)
                        pokemon.save()
                except IntegrityError:
                    return "Failed to use item."


def send_message(recipient, sender_name, body, title, sender, sender_spr, gift_items=None):
    message = Messages(
        recipient=recipient,
        sender_name=sender_name,
        sender=sender,
        body=body,
        title=title,
        gift_items=gift_items,
        sender_spr=sender_spr
    )
    # If the sender is a user, attempt to remove the items from their inventory
    try:
        with transaction.atomic():
            if sender is not None:
                if gift_items is not None:
                    for gift_item, quantity in gift_items.items:
                        if not sender.consume_item(gift_item, quantity=quantity):
                            return "You don't have: {}".format(gift_item)
            message.save()
            recipient.inbox_flag = True
            recipient.save()
    except IntegrityError:
        return "Failed to send message."


class Messages(models.Model):
    # Administrative fields
    recipient = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="recipient"
    )
    sender_name = models.CharField(max_length=20)
    sender = models.ForeignKey(
        Profile,
        blank=True, null=True, default=None,
        related_name="sender",
        on_delete=models.SET_NULL
    )
    time = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    body = models.TextField(blank=True, null=True, default=None)
    title = models.TextField(blank=True, null=True, default=None)
    gift_items = models.JSONField(blank=True, null=True, default=None)
    sender_spr = models.CharField(max_length=20)

    def read_message(self):
        self.read = True
        if self.gift_items is not None:
            if not self.accepted:
                self.accepted = True
                for gift_item, quantity in self.gift_items.items():
                    self.recipient.add_item(gift_item, quantity)
                self.recipient.save()
        self.save()
        if not self.recipient.has_unread():
            self.recipient.inbox_flag = False


def process_messages(messages):
    """
    Processes messages for display in inbox
    """
    if not len(messages):
        return pd.DataFrame(columns=["From", "Title", "Date", "To"])
    messages = [{
        "From": msg.sender_name,
        "sender": msg.sender.pk if msg.sender is not None else "",
        "To": msg.recipient.user.username,
        "recipient": msg.recipient.pk,
        "Title": msg.title,
        "body": msg.body,
        "read": msg.read,
        "accepted": msg.accepted,
        "gift_items": msg.gift_items,
        "time": msg.time,
        "Date": msg.time.strftime("%x %X"),
        "key": msg.pk
    } for msg in messages]
    msg_df = pd.DataFrame(messages)
    # Add link to sender and receiver
    profile_link = reverse("view_profile")
    msg_df["From"] = msg_df.apply(lambda x: "<a href='{}?id={}'>{}</a>".format(profile_link, x["sender"], x["From"]) if x["sender"] != "" else "<span>{}</span>".format(x["From"]), axis=1)
    msg_df["To"] = msg_df.apply(lambda x: "<a href='{}?id={}'>{}</a>".format(profile_link, x["recipient"], x["To"]), axis=1)
    msg_df["Title"] = msg_df.apply(
        lambda x: "<strong onclick='openMessage(\"{}\");'>{}</strong>".format(x["key"], x["Title"]) \
            if not x["read"] else \
            "<p onclick='openMessage(\"{}\");'>{}</p>".format(x["key"], x["Title"]), axis=1)
    return msg_df