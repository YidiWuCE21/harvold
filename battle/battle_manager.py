import random
import copy
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
        self.player_1.player = "p1"
        self.player_2 = PlayerState(battle_state["player_2"])
        self.player_2.player = "p2"
        # Set opponent
        self.player_1.opponent = self.player_2
        self.player_2.opponent = self.player_1
        # Weather
        self.weather = battle_state["weather"]
        self.weather_turns = battle_state["weather_turns"]
        # Terrain
        self.terrain = battle_state["terrain"]
        self.trick_room = battle_state["trick_room"]
        self.gravity = battle_state["gravity"]
        # Escape attempts, only for wild battles
        self.escapes = battle_state.get("escapes", None)
        # Output to show to user
        self.output = []
        # Battle end or pokemon KO, requiring special input to user
        self.outcome = battle_state["outcome"]


    def requires_switch(self):
        return not (self.player_1.get_current_pokemon().is_alive() and self.player_1.get_current_pokemon().is_alive()) and self.outcome is None


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
        if p2_move["action"] != "attack":
            self.attack(self.player_1, p1_move["move"])
        # Case where only P2 moves
        elif p1_move["action"] != "attack":
            self.attack(self.player_2, p2_move["move"])
        # Determine which move goes first
        else:
            if self.check_p1_first(p1_move["move"], p2_move["move"]):
                self.attack(self.player_1, p1_move["move"])
                self.attack(self.player_2, p2_move["move"])
            else:
                self.attack(self.player_2, p2_move["move"])
                self.attack(self.player_1, p1_move["move"])

        # Decrement weather, trick room, etc.
        # Apply item, weather, status
        # Update outcome if one or both teams have no more useable pokemon
        p1_alive = self.player_1.has_pokemon()
        p2_alive = self.player_2.has_pokemon()
        if p1_alive and not p2_alive:
            self.outcome = "p1_victory"
            self.output.append({"text": "{} has won!".format(self.player_1.name)})
        elif p2_alive and not p1_alive:
            self.outcome = "p2_victory"
            self.output.append({"text": "{} has won!".format(self.player_2.name)})
        elif not p2_alive and not p1_alive:
            self.outcome = "draw"
            self.output.append({"text": "The battle was a draw!"})




    def check_p1_first(self, p1_move, p2_move):
        # Check priority
        p1_priority = self.get_priority(self.player_1.get_current_pokemon(), p1_move)
        p2_priority = self.get_priority(self.player_2.get_current_pokemon(), p2_move)
        # Priority modifiers
        if p1_priority != p2_priority:
            return p1_priority > p2_priority
        p1_speed = self.get_speed(self.player_1)
        p2_speed = self.get_speed(self.player_2)
        # Speed tie
        if p1_speed == p2_speed:
            return bool(random.getrandbits(1))
        # Trick room check
        if self.trick_room is not None:
            if self.trick_room > 0:
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
        if current_pokemon.held_item == "lagging-tail":
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
        stat_multiplier = consts.STAT_BOOSTS[player.stat_boosts["speed"]]
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


    def attack(self, player, move):
        user = player.get_current_pokemon()
        target = player.opponent.get_current_pokemon()
        # Check user not fainted
        if user.current_hp == 0:
            return
        # Freeze and sleep
        if user.status == "slp":
            if user.status_turns == 0:
                self.output.append({"text": "{} woke up!".format(user.name)})
                user.status = ""
            else:
                user.status_turns -= 1
                self.output.append({"text": "{} is fast asleep...".format(user.name), "anim": ["{}_sleep".format(player.player)]})
                return
        if user.status == "frz":
            if random.randrange(100) < 20 or consts.MOVES[move]["type"] == "fire":
                self.output.append({"text": "{} thawed out!".format(user.name)})
                user.status = ""
            else:
                self.output.append({"text": "{} is frozen solid!".format(user.name), "anim": ["{}_frz".format(player.player)]})
                return

        # Confusion roll
        if player.confusion > 0:
            player.confusion -= 1
            self.output.append({"text": "{} is confused...".format(user.name)})
            if bool(random.getrandbits(1)):
                self.output.append({"text": "{} hurt itself in confusion!".format(user.name)})
                confusion_damage = self.move_damage(player, user, user, "normal", 40, "physical", 1, ignore_type=True)
                self.apply_damage(confusion_damage, player)
                return

        # Paralysis
        if user.status == "par":
            if user.ability != "Magic Guard" and random.random() < 0.25:
                self.output.append({"text": "{} is paralyzed! It cannot move!".format(user.name), "anim": ["{}_paralyze".format(player.player)]})
        # Locked move check; outrage, choice items, taunt, etc.
        move_data = consts.MOVES[move]
        if player.locked_moves:
            print()
        # Struggle check
        # Roll for accuracy for attacking moves
        if not self.roll_accuracy(player, move):
            self.output.append({"text": "{} used {}!".format(user.name, move_data["name"]), "anim": ["{}_{}_{}_miss".format(player.player, move_data["damage_class"], move_data["type"])]})
            self.output.append({"text": "The attack missed!"})
            return
        # Case where move is targeted attack
        if target not in ["users-field", "user", "opponents-field"]:
            # Protect/detect/endure check
            self.output.append({"text": "{} used {}!".format(user.name, move_data["name"]), "anim": ["{}_{}_{}".format(player.player, move_data["damage_class"], move_data["type"])]})
            if "protect" in player.opponent.defense_active or "detect" in player.opponent.defense_active:
                self.output.append({"text": "{} protected itself!".format(target.name)})
                return
            if move_data["damage_class"] != "status":
                # Roll for crit
                critical = 1.5 if self.roll_crit(player, move) else 1
                # Roll for damage, if move does damage
                damage = self.move_damage(
                    player,
                    user,
                    target,
                    move_data["type"],
                    move_data["power"],
                    move_data["damage_class"],
                    critical
                )
                self.apply_damage(damage, player.opponent, False)
            # Apply effects
            self.apply_boosts(player, move)
            self.apply_status(player.opponent, target, move)
        # TODO - Case where move is self boost, heal, etc.
        else:
            self.apply_boosts(player, move)


    def roll_accuracy(self, player, move):
        """
        Return a boolean for if a move successfully hit
        """
        move_data = consts.MOVES[move]

        user = player.get_current_pokemon()
        target = player.opponent.get_current_pokemon()
        move_accuracy = move_data["accuracy"]
        # If the move is self-targeted or can't miss, ignore the roll
        if move_accuracy is None:
            return True
        # Determine the modifier
        modified_accuracy = (1.67 if self.gravity is not None else 1) * \
                            (0.5 if (target.ability == "Tangled Feet" and player.opponent.confusion > 0) else 1) * \
                            (0.8 if (user.ability == "Hustle" and move_data["damage_class"] == "physical") else 1) * \
                            (0.8 if (target.ability == "Sand Veil" and self.weather == "sand") else 1) * \
                            (0.8 if (target.ability == "Snow Cloak" and self.weather == "hail") else 1) * \
                            (1.1 if (user.ability == "Victory Star") else 1) * \
                            (1.3 if (user.ability == "Compound Eyes") else 1) * \
                            (0.9 if (target.held_item == "bright-powder") else 1) * \
                            (0.9 if (target.held_item == "lax-incense") else 1) * \
                            (1.1 if (user.held_item == "wide-lens") else 1) * \
                            (1.2 if (user.held_item == "zoom-lens") else 1)
        accuracy_bonus = player.stat_boosts["accuracy"]
        evasion_bonus = player.opponent.stat_boosts["evasion"]
        accuracy_modifier = 3 / (3 - accuracy_bonus) if accuracy_bonus < 0 else (3 + accuracy_bonus) / 3
        evasion_modifier = 3 / (3 + evasion_bonus) if evasion_bonus > 0 else (3 + evasion_bonus) / 3
        accuracy = move_accuracy * modified_accuracy * accuracy_modifier * evasion_modifier
        return random.randrange(100) < accuracy


    def roll_crit(self, player, move):
        """
        Roll for critical hit
        """
        user = player.get_current_pokemon()
        crit_stages = consts.MOVES[move]["crit_rate"]
        if user.held_item in ["razor-claw", "scope-lens"]:
            crit_stages += 1
        elif user.held_item == "lucky-punch" and str(user.dex) == "113":
            crit_stages += 2
        if user.ability == "Super Luck":
            crit_stages += 1
        if crit_stages == 0:
            return random.randrange(100) < 100/24
        if crit_stages == 1:
            return random.randrange(100) < 100/8
        if crit_stages == 2:
            return random.randrange(100) < 100/2
        return True


    def move_damage(self, player, user, target, type, base_power, damage_class, critical, ignore_type=False):
        """
        Calculate damage for a move. Crits applied in advance so can be controlled
        """
        if base_power is None:
            base_power = 0
        weather_boost = 1
        randdmg = random.randrange(85, 101) / 100
        stab = 1.5 if type in consts.POKEMON[user.dex]["typing"] else 1
        burn = 0.5 if (user.status == "brn" and user.ability != "Guts" and damage_class == "physical") else 1
        type_effectiveness = effectiveness(type, target.dex) if not ignore_type else 1
        if type_effectiveness > 1:
            self.output.append({"text": "It's super effective!"})
        elif type_effectiveness <= 0:
            self.output.append({"text": "It's completely ineffective!"})
        elif type_effectiveness < 1:
            self.output.append({"text": "It's not very effective!"})
        other = 1
        attack_stat = user.attack * consts.STAT_BOOSTS[player.stat_boosts["attack"]] \
            if damage_class == "physical" else \
            user.sp_attack * consts.STAT_BOOSTS[player.stat_boosts["special_attack"]]
        defense_stat = target.defense  * consts.STAT_BOOSTS[player.opponent.stat_boosts["defense"]] \
            if damage_class == "physical" else \
            target.sp_defense * consts.STAT_BOOSTS[player.opponent.stat_boosts["special_defense"]]
        damage = int(int(int(int(int(int(int(int((2 * user.level / 5 + 2) * base_power * attack_stat / defense_stat / 50 + 2) \
                 * weather_boost) * critical) * randdmg) * stab) * type_effectiveness) * burn) * other)

        return int(damage)


    def apply_damage(self, damage, player, survive=False):
        """
        Damage and faint a Pokemon
        """
        target = player.get_current_pokemon()
        self.output.append({"anim": ["{}_update_hp".format(player.player)]})
        if damage >= target.current_hp:
            if survive:
                target.current_hp = 1
                return
            else:
                target.current_hp = 0
                self.output.append({"text": "{} has fainted!".format(target.name), "anim": ["{}_faint".format(player.player)]})
                return
        target.current_hp -= damage


    def apply_status(self, opponent, target, move):
        # If target was already KO'd do not apply status
        if not target.is_alive():
            return
        generic_status = {
            "brn": "{} was burned!",
            "par": "{} was paralyzed!",
            "frz": "{} was frozen solid!",
            "slp": "{} fell asleep!",
            "psn": "{} was poisoned!",
            "txc": "{} was badly poisoned!"
        }
        move_data = consts.MOVES[move]
        ailment = move_data["ailment"]
        chance = move_data["ailment_chance"]
        # Do not apply if already afflicted by similar status
        if ailment in generic_status:
            if target.status:
                if move_data["damage_class"] == "status":
                    self.output.append({"text": "But it failed!"})
                return
        # Do not confuse if already confused
        if ailment == "confusion":
            if opponent.confusion > 0:
                self.output.append({"text": "{} is already confused!".format(target.name)})
                return
        # TODO - embargo,  heal block, disable, infatuation, leech seed, nightmare, perish song, trap, torment, yawn, unknown
        # Roll for effect application
        if chance == 0 or random.randrange(100) < chance:
            if ailment in generic_status:
                target.status = ailment
                self.output.append({"anim": ["{}_update_hp".format(opponent.player)]})
                if ailment == "slp":
                    target.status_turns = random.randrange(1, 4)
                self.output.append({"text": generic_status[ailment].format(target.name)})
            elif ailment == "confusion":
                opponent.confusion = random.randrange(2, 6)
                self.output.append({"text": "{} became confused!".format(target.name)})



    def apply_boosts(self, player, move):
        """
        Apply stat boosts
        """
        stat_boosts = consts.MOVES[move]["stat_changes"]
        # Roll for stat chance
        stat_chance = consts.MOVES[move]["stat_chance"]
        if stat_chance != 0:
            if random.randrange(100) > stat_chance:
                return
        if stat_boosts:
            if "opponent" in stat_boosts:
                for boost in stat_boosts["opponent"]:
                    current_boost = player.opponent.stat_boosts[boost[1]]
                    prev_boost = current_boost
                    current_boost = max(-6, min(6, current_boost + boost[0]))
                    player.opponent.stat_boosts[boost[1]] = current_boost
                    if prev_boost == current_boost:
                        self.output.append({"text": "{}'s {} {}!".format(
                            player.opponent.get_current_pokemon().name,
                            boost[1].replace("-", " "),
                            "has already reached its limit" if current_boost > 1 else "cannot go any lower" if current_boost < -1 else "",
                        )})
                    else:
                        self.output.append({"text": "{}'s {} {}{}!".format(
                            player.opponent.get_current_pokemon().name,
                            boost[1].replace("-", " "),
                            "sharply " if boost[0] > 1 else "harshly " if boost[0] < -1 else "",
                            "rose" if boost[0] > 0 else "fell"
                        )})
            if "self" in stat_boosts:
                for boost in stat_boosts["self"]:
                    current_boost = player.stat_boosts[boost[1]]
                    current_boost = max(-6, min(6, current_boost + boost[0]))
                    prev_boost = current_boost
                    player.stat_boosts[boost[1]] = current_boost
                    if prev_boost == current_boost:
                        self.output.append({"text": "{}'s {} {}!".format(
                            player.get_current_pokemon().name,
                            boost[1].replace("-", " "),
                            "has already reached its limit" if current_boost > 1 else "cannot go any lower" if current_boost < -1 else "",
                        )})
                    else:
                        self.output.append({"text": "{}'s {} {}{}!".format(
                            player.get_current_pokemon().name,
                            boost[1].replace("-", " "),
                            "sharply " if boost[0] > 1 else "harshly " if boost[0] < -1 else "",
                            "rose" if boost[0] > 0 else "fell"
                        )})
        return



    def use_item(self, user, item, target):
        """
        Use battle items and pokeballs
        """
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
                    target_pokemon.status = ""
                elif item_effects["status"] == target_pokemon.status:
                    target_pokemon.status = ""
                elif item_effects["status"] == "psn" and target_pokemon.status == "txc":
                    target_pokemon.status = ""
            self.output.append({"text": "Used {} on {}!".format(item, target_pokemon.name)})
            self.output.append({"anim": ["{}_update_hp".format(user.player)]})

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
                self.output.append({"text": "You have caught the wild {}!".format(wild_pokemon.name), "anim": ["caught"]})
                self.outcome = "caught"
                return True
            # Check shakes
            for i in range(3):
                if random.randrange(65535) > shake_chance:
                    self.output.append({"text": "The wild {} escaped!".format(wild_pokemon.name), "anim": ["escape_ball"]})
                    return False
                self.output.append({"anim": ["shake"]})
            self.output.append({"text": "You have caught the wild {}!".format(wild_pokemon.name), "anim": ["caught"]})
            self.outcome = "caught"
            return True
        return False


    def switch(self, player, swap_to, other_move):
        """
        Generic switch, used for player switching, switching moves, and switch-in after KO

        Only apply entry hazards
        """
        # Arena trap/shadow tag check
        if player.opponent.get_current_pokemon().ability in ["Arena Trap", "Shadow Tag"] or player.trapped != 0:
            self.output.append({"text": "{} cannot be switched!"})
            return
        # Pursuit check and KO check
        if other_move.get("move", None) == "pursuit":
            self.attack(self.player.opponent.get_current_pokemon(), player.get_current_pokemon())

        # Check switch to target is alive
        if player.party[swap_to].is_alive():
            if player.get_current_pokemon().is_alive():
                self.output.append({"text": "Come back, {}!".format(player.get_current_pokemon().name), "anim": ["{}_retreat".format(player.player)]})
            player.current_pokemon = swap_to
            player.stat_boosts = copy.deepcopy(consts.PLAYER_STATE["stat_boosts"])
            player.confusion = 0
            player.locked_moves = []
            player.choice = None
            self.output.append({"text": "Go, {}!".format(player.get_current_pokemon().name), "anim": ["{}_new_sprite".format(player.player), "{}_appear".format(player.player)]})
        # TODO - Apply entry hazards



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

    def jsonify(self):
        json_obj = {
            "type": self.type,
            "player_1": self.player_1.jsonify(),
            "player_2": self.player_2.jsonify(),
            "weather": self.weather,
            "weather_turns": self.weather_turns,
            "terrain": self.terrain,
            "trick_room": self.trick_room,
            "gravity": self.gravity,
            "outcome": self.outcome
        }
        if self.escapes is not None:
            json_obj["escapes"] = self.escapes
        return json_obj



class PlayerState:
    def __init__(self, player_state):
        # Stat boosts are in order: attack, defense, sp. attack, sp. defense, speed, accuracy, evasion
        self.party = copy.deepcopy([PokemonState(pkmn) for pkmn in player_state["party"]])
        self.current_pokemon = player_state["current_pokemon"]
        self.contributors = player_state["contributors"]
        self.stat_boosts = copy.deepcopy(player_state["stat_boosts"])
        self.entry_hazards = player_state["entry_hazards"]
        self.confusion = player_state["confusion"]
        self.locked_moves = player_state["locked_moves"]
        self.defense_active = player_state["defense_active"]
        self.tailwind = player_state["tailwind"]
        self.name = player_state["name"]
        self.trapped = player_state["trapped"]
        self.choice = player_state["choice"]
        self.inventory = player_state["inventory"]

        # Not in state
        self.player = None
        self.opponent = None

    def get_current_pokemon(self):
        return self.party[self.current_pokemon]

    def has_pokemon(self):
        return any([pkmn.is_alive() for pkmn in self.party])

    def jsonify(self):
        return {
            "party": [pkmn.jsonify() for pkmn in self.party],
            "current_pokemon": self.current_pokemon,
            "contributors": self.contributors,
            "stat_boosts": self.stat_boosts,
            "entry_hazards": self.entry_hazards,
            "confusion": self.confusion,
            "locked_moves": self.locked_moves,
            "defense_active": self.defense_active,
            "tailwind": self.tailwind,
            "name": self.name,
            "trapped": self.trapped,
            "choice": self.choice,
            "inventory": self.inventory
        }


class PokemonState:
    def __init__(self, pokemon_state):
        self.current_hp = pokemon_state["current_hp"]
        self.status = pokemon_state["status"]
        self.status_turns = pokemon_state["status_turns"]
        self.moves = pokemon_state["moves"]
        self.held_item = pokemon_state["held_item"]
        self.happiness = pokemon_state["happiness"]
        self.ability = pokemon_state["ability"]
        self.dex = str(pokemon_state["dex_number"]).zfill(3)
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


    def struggling(self):
        return not any([self.has_pp(move) for move in self.moves])


    def jsonify(self):
        return {
            "current_hp": self.current_hp,
            "status": self.status,
            "status_turns": self.status_turns,
            "moves": self.moves,
            "held_item": self.held_item,
            "happiness": self.happiness,
            "ability": self.ability,
            "dex_number": str(self.dex).zfill(3),
            "level": self.level,
            "shiny": self.shiny,
            "stats": {
                "hp": self.hp,
                "atk": self.attack,
                "def": self.defense,
                "spa": self.sp_attack,
                "spd": self.sp_defense,
                "spe": self.speed,
            },
            "id": self.id,
            "name": self.name
        }


def effectiveness(attacker, defender):
    """
    Calculate the type effectiveness of an attack
    """
    defender_typing = consts.POKEMON[defender]["typing"]
    effectiveness = 1
    for defender_type in defender_typing:
        key = (attacker, defender_type)
        effectiveness *= consts.TYPE_EFFECTIVENESS.get(key, 1)
    return effectiveness