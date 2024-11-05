import random
import json
from functools import partial

from harvoldsite import consts
"""
Battle state is outlined in models.py

Moves should be received as a JSON with "action" being the main key

Surrender - {"action": "surrender"}

Attack - {"action": "attack", "move": <move>}
Target automatically determined by which move is used; no support for double battles

Item - {"action": "item", <item>: "pokeball", "target": <1-6>}
Target only for using medicine, pokeballs always thrown at opponent

Switch - {"action": "switch", "target": <integer>}
"""

class BattleState:
    def __init__(self, battle_state):
        self.type = battle_state["type"]
        # Player state managers
        self.player_1 = PlayerState(battle_state["player_1"])
        self.player_2 = PlayerState(battle_state["player_2"])
        # Set opponent
        self.player_1.opponent = self.player_2
        self.player_2.opponent = self.player_1
        # Weather
        self.weather = battle_state["weather"]
        self.weather_turns = battle_state["weather_turns"]
        # Terrain
        self.terrain = battle_state["terrain"]
        self.trick_room = battle_state["trick_room"]
        # Escape attempts, only for wild battles
        self.escapes = battle_state.get("escapes", None)
        # Output to show to user
        self.output = []
        # Battle end or pokemon KO, requiring special input to user
        self.outcome = battle_state["outcome"]


    def process_battle(self, p1_move, p2_move):
        """
        Function that controls the main turn flow.
        """
        # Check for surrender
        p1_surrendered = p1_move["action"] == "surrender"
        p2_surrendered = p2_move["action"] == "surrender"
        if self.check_surrender(p1_surrendered, p2_surrendered):
            return self.output

        # Check for switch with pursuit check
        if p1_move["action"] == "switch":
            self.switch(self.player_1, p1_move["target"], p2_move)
        if p2_move["action"] == "switch":
            self.switch(self.player_2, p2_move["target"], p1_move)

        # Check for item usage
        if p1_move["action"] == "item":
            self.use_item(self.player_1, p1_move["item"], p1_move.get("target", None))
        if p2_move["action"] == "item":
            self.use_item(self.player_2, p2_move["item"], p2_move.get("target", None))

        # Determine move order
        # Case where only P1 moves
        if p2_move["action"] != "move":
            self.attack(self.player_1.get_current_pokemon(), self.player_2.get_current_pokemon())
        # Case where only P2 moves
        elif p1_move["action"] != "move":
            self.attack(self.player_2.get_current_pokemon(), self.player_1.get_current_pokemon())
        # Determine which move goes first
        else:
            if self.check_p1_first(p1_move["move"], p2_move["move"]):
                self.attack(self.player_1.get_current_pokemon(), p1_move["move"], self.player_2.get_current_pokemon())
                self.attack(self.player_2.get_current_pokemon(), p2_move["move"], self.player_1.get_current_pokemon())
            else:
                self.attack(self.player_2.get_current_pokemon(), p2_move["move"], self.player_1.get_current_pokemon())
                self.attack(self.player_1.get_current_pokemon(), p1_move["move"], self.player_2.get_current_pokemon())

        raise NotImplementedError()


    def check_p1_first(self, p1_move, p2_move):
        # Check priority
        p1_priority = self.get_priority(self.player_1.get_current_pokemon(), p1_move["move"])
        p2_priority = self.get_priority(self.player_2.get_current_pokemon(), p2_move["move"])
        # Priority modifiers
        if p1_priority != p2_priority:
            return p1_priority > p2_priority
        p1_speed = self.get_speed(self.player_1)
        p2_speed = self.get_speed(self.player_2)
        # Speed tie
        if p1_speed == p2_speed:
            return bool(random.getrandbits(1))
        # Trick room check
        if self.trick_room:
            return p1_speed < p2_speed
        # Speed compare
        else:
            return p1_speed > p2_speed



    def get_priority(self, current_pokemon, move):
        base_priority = consts.MOVES[move]["priority"]
        # Quick claw proc
        if current_pokemon.held_item == "quick-claw":
            if random.randrange(5) < 1:
                self.output.append({"text": "{}'s Quick Claw activated!".format(current_pokemon.name)})
                base_priority += 10

        # Lagging tail
        if current_pokemon.held_item == "lagging_tail":
            base_priority -= 1
        # Stall
        if current_pokemon.ability == "Stall":
            base_priority -= 1
        # Gale wings
        if current_pokemon.ability == "Gale Wings" and (current_pokemon.current_hp == current_pokemon.hp):
            base_priority += 1
        # Prankster
        if current_pokemon.ability == "Prankster" and consts.MOVES[move]["damage_class"] == "status":
            base_priority += 1

        return base_priority


    def get_speed(self, player):
        current_pokemon = player.get_current_pokemon()
        base_speed = current_pokemon.speed
        stat_multiplier = consts.STAT_BOOSTS[player.stat_boosts[5]]
        speed = base_speed * stat_multiplier
        if current_pokemon.status == "par" and current_pokemon.ability != "Quick Feet":
            speed = speed / 4
        if current_pokemon.held_item == "choice-scarf":
            speed = speed * 1.5
        elif current_pokemon.held_item in ["iron-ball", "macho-brace", "power-bracer", "power-belt", "power-lens", "power-band", "power-anklet", "power-weight"]:
            speed = speed / 2
        if player.tailwind is not None:
            speed = speed * 2
        weather_boosts = {
            "rain": "Swift Swim",
            "sun": "Chlorophyll",
            "sand": "Sand Rush"
        }
        if weather_boosts.get(self.weather, "mismatch") == current_pokemon.ability:
            speed = speed * 2
        elif current_pokemon.ability == "Unburden" and current_pokemon.held_item == "removed":
            speed = speed * 2
        elif current_pokemon.ability == "Quick Feet" and current_pokemon.status is not None:
            speed = speed * 1.5
        elif current_pokemon.ability == "Slow Start":
            speed = speed / 2
        return speed


    def attack(self, user, move, target):
        raise NotImplementedError()

    def use_item(self, user, item, target):
        target_pokemon = user.party[target]
        item_type = consts.ITEMS[item]["category"]
        item_data = consts.ITEM_USAGE[item_type][item]
        # Medicine usage
        if item_type == "medicine":
            # Check target valid
            valid_targets = item_data.get("valid_targets", "any")
            if valid_targets == "alive":
                if not target_pokemon.is_alive():
                    self.output.append({"text": "You cannot use that item on a fainted Pokémon!"})
                    return False
            elif valid_targets == "dead":
                if target_pokemon.is_alive():
                    self.output.append({"text": "You can only use that item on a fainted Pokémon!"})
                    return False
            # Apply item effects
            item_effects = item_data["effects"]
            if "hp" in item_effects:
                if item_effects["hp"] == "full":
                    target_pokemon.current_hp = target_pokemon.hp
                elif item_effects["hp"] == "half":
                    target_pokemon.current_hp = int((target_pokemon.hp + 1) / 2)
                else:
                    target_pokemon.current_hp = min(target_pokemon.current_hp + item_effects["hp"], target_pokemon.hp)
            if "status" in item_effects:
                if item_effects["status"] == "any":
                    target_pokemon.status = None
                elif item_effects["status"] == target_pokemon.status:
                    target_pokemon.status = None
                elif item_effects["status"] == "psn" and target_pokemon.status == "txc":
                    target_pokemon.status = None
            self.output.append({"text": "Used {} on {}!".format(item, target_pokemon.name), "anim": ["update_hp"], "val": target_pokemon.current_hp})

        # Pokeball usage
        if item_type == "ball":
            # Check battle is the proper type
            if self.type != "wild":
                self.output.append({"text": "You cannot catch Pokémon in a trainer battle!"})
                return False
            wild_pokemon = user.opponent.get_current_pokemon()
            if wild_pokemon.current_hp == 0:
                self.output.append({"text": "You cannot catch a fainted Pokémon!"})
                return False
            self.output.append({"text": "You threw a {}".format(item), "anim": ["throw_{}".format(item)]})

            # Check catch
            ball_bonus = item_data["catch_rate"]
            status_bonus = 2.5 if wild_pokemon.status in ["slp", "frz"] else 1.5 if wild_pokemon.status in ["par", "psn", "brn", "txc"] else 1
            catch_chance = (3 * wild_pokemon.hp - 2 * wild_pokemon.current_hp) / (3 * wild_pokemon.hp) * 4096 * \
                           int(consts.POKEMON[wild_pokemon.dex]["capture_rate"]) * ball_bonus * status_bonus
            shake_chance = int(65536) * (catch_chance / 1044480) ** (1/4)
            # Master ball
            if item == "master-ball":
                self.output.append({"text": "You have caught the wild {}!".format(wild_pokemon.name), "anim": "caught"})
                self.outcome = "caught"
                return True
            # Check shakes
            for i in range(3):
                if random.randrange(65535) > shake_chance:
                    self.output.append({"text": "The wild {} escaped!".format(wild_pokemon.name), "anim": "escape_ball"})
                    return False
                self.output.append({"anim": "shake"})
            self.output.append({"text": "You have caught the wild {}!".format(wild_pokemon.name), "anim": "caught"})
            self.outcome = "caught"
            return True
        return False


    def switch(self, player, swap_to, other_move):
        """
        Generic switch, used for player switching, switching moves, and switch-in after KO

        Only apply entry hazards
        """
        # Pursuit check and KO check
        if other_move.get("move", None) == "pursuit":
            self.attack(self.player.opponent.get_current_pokemon(), player.get_current_pokemon())

        # Check switch to target is alive
        if player.party[swap_to].is_alive():
            self.output.append({"text": "Come back, {}!".format(player.get_current_pokemon().name), "anim": ["p1_retreat"]})
            player.current_pokemon = swap_to
            self.output.append({"text": "Go, {}!".format(player.get_current_pokemon().name), "anim": ["p1_new_sprite", "p1_appear"]})
        # TODO - Apply entry hazards
        # TODO Check new Pokemon KO

    def check_surrender(self, p1_surrender, p2_surrender):
        # Draw
        if p1_surrender and p2_surrender:
            self.outcome = "draw"
            self.output.append({"text": "The battle was a draw!", "anim": ["p1_retreat", "p2_retreat"]})
            return True
        # P1 surrenders
        elif p1_surrender and self.escapes is None:
            self.outcome = "p2_victory"
            self.output.append({"text": "{} has surrendered!".format(self.player_1.name), "anim": ["p1_retreat"]})
            return True
        # P2 surrenders
        elif p2_surrender:
            self.outcome = "p1_victory"
            self.output.append({"text": "{} has surrendered!".format(self.player_2.name), "anim": ["p2_retreat"]})
            return True
        # Flee wild battle
        elif p1_surrender and self.escapes is not None:
            self.escapes += 1

            # Calculate escape odds
            player_speed = self.player_1.get_current_pokemon().speed
            opp_speed = self.player_2.get_current_pokemon().speed
            escape_odds = (int(player_speed * 8 / opp_speed) + 30 * self.escapes) / 256
            escaped = random.randrange(100) < escape_odds * 100

            # Escape outcomes
            if escaped:
                self.outcome = "fled_battle"
                self.output.append({"text": "Ran away from the wild Pokémon!", "anim": ["p1_retreat"]})
                return True
            else:
                self.output.append({"text": "Failed to run away!"})
                return False

        # Did not flee
        elif self.escapes is not None:
            self.escape = 0

        return False



class PlayerState:
    def __init__(self, player_state):
        self.party = [PokemonState(pkmn) for pkmn in player_state["party"]]
        self.current_pokemon = player_state["current_pokemon"]
        self.contributors = player_state["contributors"]
        self.stat_boosts = player_state["stat_boosts"]
        self.entry_hazards = player_state["entry_hazards"]
        self.confusion = player_state["confusion"]
        self.locked_moves = player_state["locked_moves"]
        self.defense_active = player_state["defense_active"]
        self.tailwind = player_state["tailwind"]
        self.opponent = None
        self.name = player_state["name"]

    def get_current_pokemon(self):
        return self.party[self.current_pokemon]


class PokemonState:
    def __init__(self, pokemon_state):
        self.current_hp = pokemon_state["current_hp"]
        self.status = pokemon_state["status"]
        self.moves = pokemon_state["moves"]
        self.held_item = pokemon_state["held_item"]
        self.happiness = pokemon_state["happiness"]
        self.ability = pokemon_state["ability"]
        self.dex = pokemon_state["dex_number"]
        self.level = pokemon_state["level"]
        self.shiny = pokemon_state["shiny"]
        self.hp = pokemon_state["stats"]["hp"]
        self.attack = pokemon_state["stats"]["atk"]
        self.defense = pokemon_state["stats"]["def"]
        self.sp_attack = pokemon_state["stats"]["spa"]
        self.sp_defense = pokemon_state["stats"]["spd"]
        self.speed = pokemon_state["stats"]["spe"]
        self.id = pokemon_state["id"]
        self.name = pokemon_state["name"]

    def is_alive(self):
        return self.current_hp > 0


    def has_pp(self, selected_move):
        for move in self.moves:
            if move["move"] == selected_move:
                return move["pp"] > 0
        return False