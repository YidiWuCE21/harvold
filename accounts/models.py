from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import IntegrityError, transaction
from pokemon.models import Pokemon

# Create your models here.
class Profile(models.Model):
    # Administrative fields
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    banned = models.BooleanField(default=False)

    # Trainer data
    description = models.CharField(max_length=500, null=True)
    title = models.CharField(max_length=50, null=True)
    faction = models.IntegerField(null=True)
    state = models.CharField(default="idle", max_length=10) # Used to control in-battle status
    # TODO - Clan system

    # Trainer values
    money = models.IntegerField(default=10000)
    character = models.IntegerField()

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


    def remove_from_party(self, slot):
        """
        Remove a Pokemon from any slot in the party and bubble upwards.
        """
        # Check if player in battle
        if self.state == "battle":
            return "Party cannot be modified in battle."
        pokemon = self.__getattribute__(slot)

        # Check if it's the last pokemon
        if slot == "slot_1" and self.slot_2 is None:
            return "This is your last Pokemon!"

        # Check if slot has pokemon
        if pokemon is None:
            return "Nothing to remove."

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
