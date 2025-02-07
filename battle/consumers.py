# chat/consumers.py
import json
import os
import datetime
from . import models
from .battle_manager import BattleState
from harvoldsite import consts
from . import battle_ai
from accounts.models import send_message

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import transaction
from django.urls import reverse


def validate_attack(action, player):
    """
    Check that an attack is valid to make
    """
    current_pokemon = player.get_current_pokemon()

    # Struggle check
    if current_pokemon.struggling():
        return True

    # Generic move check
    if action["move"] in [move["move"] for move in current_pokemon.moves]:
        if current_pokemon.has_pp(action["move"]):
            return True

    return False


def validate_switch(action, player):
    """
    Check that switch is valid to make
    """
    # Cannot switch to same Pokemon
    if action["target"] == player.current_pokemon:
        return False
    # Cannot switch to dead Pokemon
    if not player.party[action["target"]].is_alive():
        return False
    # Check for arena trap and other trap effects
    return True


def validate_item(action, player, type):
    """
    Check that item usage is valid
    """
    # Check that player owns item
    item = action["item"]
    category = consts.ITEMS[item]["category"]
    if player.inventory[category].get(item, 0) < 1:
        return False
    # Check that balls are only used in wild battles
    if category == "ball" and type != "wild":
        return False
    # Check that potions and revives are only used in wild and NPC battles
    if category == "medicine" and type == "live":
        return False
    # Check that target for potion is valid
    if action["target"] is not None:
        pokemon_alive = player.party[action["target"]].is_alive()
        if (consts.ITEM_USAGE[category][item]['valid_targets'] == "alive") != pokemon_alive:
            return False
    return True


def validate_surrender():
    return True


def validate_action(action, player, battle_state):
    """
    Choose the correct validator for the action
    """
    if action["action"] == "attack":
        return validate_attack(action, player)
    if action["action"] == "switch":
        return validate_switch(action, player)
    if action["action"] == "item":
        return validate_item(action, player, battle_state.type)
    if action["action"] == "surrender":
        return validate_surrender()
    return False


def need_to_process(battle, action):
    if battle is None:
        return "You are not in a battle!"
    if battle.status != "ongoing":
        return "The battle is finished!"
    # Exit if wrong turn
    if action["current_turn"] != battle.current_turn:
        return "The current turn is {}, you submitted a move for {}.".format(battle.current_turn, action["current_turn"])


def get_battle_state(battle, player):
    p1 = battle.player_1
    is_p1 = p1 == player
    battle_state = BattleState(battle.battle_state)
    player_state = battle_state.player_1 if is_p1 else battle_state.player_2
    return battle_state, player_state, is_p1

def process_first_turn(battle, battle_state):
    battle_state.process_start()
    battle.battle_state = battle_state.jsonify()
    battle.save()
    return {
        "group": {
            "type": "chat.message",
            "state": battle_state.jsonify(),
            "prompt": None,
            "output": None,
            "turn": battle.current_turn,
            "send_update": True
        }
    }


def has_player_already_moved(is_p1, battle):
    return (is_p1 and battle.player_1_choice is not None) or (not is_p1 and battle.player_2_hoice is not None)


def is_valid_action(battle_state, player_state, action):
    if battle_state.requires_switch():
        # Player is fainted, must either switch or surrender
        if not player_state.get_current_pokemon().is_alive() and action["action"] not in ["switch", "surrender"]:
            return False
        # If battle requires switch and user is not fainted, cannot move until opponent switches
        if player_state.get_current_pokemon().is_alive():
            return False
    return validate_action(action, player_state, battle_state)


def store_player_action(is_p1, battle, action):
    if is_p1:
        battle.player_1_choice = action
    else:
        battle.player_2_choice = action


def call_process_battle(battle, battle_state):
    # Switch case
    if battle_state.requires_switch():
        if battle.player_1_choice["action"] != "idle":
            if battle.player_1_choice["action"] == "switch":
                battle_state.switch(battle_state.player_1, battle.player_1_choice["target"], {})
            else:
                battle_state.process_battle(battle.player_1_choice, battle.player_2_choice)
        if battle.player_2_choice["action"] != "idle":
            if battle.player_1_choice["action"] == "switch":
                battle_state.switch(battle_state.player_2, battle.player_2_choice["target"], {})
            else:
                battle_state.process_battle(battle.player_1_choice, battle.player_2_choice)
    # Case for standard turn
    else:
        battle_state.output.append({"turn": "Turn {}".format(battle.current_turn)})
        battle.current_turn += 1
        if battle.move_history is None:
            battle.move_history = []
        battle.move_history.append({"player_1": battle.player_1_choice, "player_2": battle.player_2_choice})
        battle_state.process_battle(battle.player_1_choice, battle.player_2_choice)


def handle_experience_gain(battle_state, battle, output_log):
    """
    Handle all experience gain functionality
    """
    if battle_state.experience_gain != 0 and battle_state.type != "live":
        for i, pkmn in enumerate(battle.player_1.get_party()):
            if i in battle_state.player_1.participants:
                # Lucky egg multiplier
                egg_multiplier = 1.5 if pkmn.held_item == "lucky-egg" else 1
                true_exp = int(battle_state.experience_gain / len(battle_state.player_1.participants) * egg_multiplier)

                if not battle_state.player_1.party[i].is_alive():
                    continue

                output_log.append({"colour": "rgb(0, 51, 153)", "text": "{} gained {} experience!".format(pkmn.name, true_exp)})
                pkmn.happiness = min(255, pkmn.happiness + 1)
                pkmn.add_evs(battle_state.ev_yield)

                if pkmn.add_xp(true_exp, recalculate=True):
                    anim = ["p1_new_sprite", "p1_update_hp_{}".format(battle_state.player_1.party[i].current_hp)] if pkmn == battle_state.player_1.get_current_pokemon() else []
                    output_log.append({"colour": "rgb(0, 51, 153)", "text": "{} has leveled up to {}!".format(pkmn.name, pkmn.level), "anim": anim})
                    # Get the new stats
                    battle_state.player_1.party[i].update_stats(pkmn.get_battle_info()["stats"])
                    battle_state.player_1.party[i].level = pkmn.level

        battle_state.experience_gain = 0
        battle_state.ev_yield = []
        battle_state.player_1.participants = [pkmn for pkmn in range(len(battle_state.player_1.party)) if pkmn == battle_state.player_1.current_pokemon or battle_state.player_1.party[pkmn].held_item == "exp-share"]


def opponent_switch(battle_state, battle, output_log):
    if battle.type == "npc" and battle_state.outcome is None and not battle_state.player_2.get_current_pokemon().is_alive():
        battle_state.switch(battle_state.player_2, battle_state.player_2.current_pokemon + 1, {})
        output_log += battle_state.output
        battle_state.output = []


def handle_outcome(battle_state, battle, output_log, is_p1):
    # Generic info
    prompt = ["pokecenter", "map"]
    battle.status = battle_state.outcome
    battle.battle_end = datetime.datetime.now()
    player_1, player_2 = battle.player_1, None
    player_1.current_battle = None

    if battle.save_inventory:
        player_1.bag = battle_state.player_1.inventory

    if battle.type == "live":
        player_2 = battle.player_2
        player_2.current_battle = None
        if battle.save_inventory:
            player_2.bag = battle_state.player_2.inventory

    # Caught a wild Pokemon
    if battle_state.outcome == "caught" and battle.type == "wild":
        handle_wild_catch(battle_state, battle, prompt, player_1)

    if battle.type == "npc":
        handle_npc_battle(battle_state, battle, output_log, player_1, prompt)
    # KO loss
    if (is_p1 and not battle_state.player_1.has_pokemon()) or (
            not is_p1 and not battle_state.player_2.has_pokemon()):
        ko_loss(battle_state, output_log, player_1, player_2, is_p1)

    player_1.save()
    if player_2 is not None:
        player_2.save()

    # Gauntlet case; return to gauntlet page
    if battle.gauntlet is not None:
        prompt = [battle.gauntlet.gauntlet_type]
        battle.send_state_to_gauntlet()
        battle.gauntlet.current_battle = "victory" if battle_state.outcome == "p1_victory" else "defeat"
        battle.gauntlet.save()
    return prompt


def handle_wild_catch(battle_state, battle, prompt, player_1):
    prompt.append("caught")
    battle.wild_opponent.status = battle_state.player_2.get_current_pokemon().status
    battle.wild_opponent.current_hp = battle_state.player_2.get_current_pokemon().current_hp
    battle.wild_opponent.assign_trainer(battle.player_1)
    battle.wild_opponent.save()
    player_1.add_to_party(battle.wild_opponent)
    player_1.wild_opponent = None


def save_battle_to_db(battle_state, battle, output_log):
    battle.battle_state = battle_state.jsonify()
    battle.output_log += output_log
    battle.player_1_choice = None
    battle.player_1_choice = None
    if battle_state.requires_switch():
        if battle_state.player_1.get_current_pokemon().is_alive():
            battle.player_1_choice = {"action": "idle"}
        if battle_state.player_2.get_current_pokemon().is_alive():
            battle.player_2_choice = {"action": "idle"}
    battle.save()


def handle_npc_battle(battle_state, battle, output_log, player_1, prompt):
    trainer_json = load_trainer_data(battle.npc_opponent)
    # Not a map trainer

    if "map" not in trainer_json and "map" in prompt:
            prompt.remove("map")
    # Player victory
    if battle_state.outcome == "p1_victory":
        handle_player_victory(battle_state, battle, output_log, player_1, trainer_json)


def load_trainer_data(npc_opponent):
    trainer_data = "{}.json".format(npc_opponent)
    trainer_path = os.path.join(consts.STATIC_PATH, "data", "trainers", trainer_data)
    try:
        with open(trainer_path, encoding="utf-8") as trainer_file:
            return json.load(trainer_file)
    except:
        return {}


def handle_player_victory(battle_state, battle, output_log, player_1, trainer_json):
    if trainer_json:
        output_log.append({"speaker": trainer_json["name"], "text": trainer_json["lines"]["lose"]})
    if battle.battle_prize is not None:
        process_battle_prizes(battle_state, battle, output_log, player_1, trainer_json)


def process_battle_prizes(battle_state, battle, output_log, player_1, trainer_json):
    # Payout
    if "base_payout" in battle.battle_prize:
        max_level = max([pkmn.level for pkmn in battle_state.player_2.party])
        cash_payout = max_level * battle.battle_prize["base_payout"]
        if player_1.has_beat_trainer(battle.npc_opponent):
            cash_payout = int(cash_payout / 10)
        output_log.append(
            {"colour": "rgb(0, 51, 153)", "text": "You received ${} for winning!".format(cash_payout)})
        player_1.money += cash_payout

    if "badges" in battle.battle_prize:
        award_gym_badge(battle.battle_prize["badges"], output_log, player_1, trainer_json)

    player_1.beat_trainer(battle.npc_opponent, skip_save=True)


def award_gym_badge(badges, output_log, player_1, trainer_json):
    for badge, rank in badges.items():
        if player_1.badges.get(badge) is None:
            player_1.badges[badge] = rank
            output_log.append({"colour": "rgb(0, 51, 153)", "text": f"You earned the {badge.capitalize()} Badge!"})
            send_message(player_1, trainer_json["name"], trainer_json["reward"]["message"],
                         f"Congratulations on beating the {badge.capitalize()} gym!", None,
                         trainer_json["sprite"], gift_items={trainer_json["reward"]["first"][0]: 1})
        elif player_1.badges[badge] == "silver" and rank == "gold":
            player_1.badges[badge] = "gold"
            output_log.append({"colour": "rgb(0, 51, 153)", "text": f"You earned the Elite {badge.capitalize()} Badge!"})


@database_sync_to_async
def battle_processor(text_data, sender, first_turn=False):
    action = json.loads(text_data)
    prompt = None
    output_log = []
    player = sender.profile
    battle = player.current_battle

    # Get the player's battle
    ret_message = need_to_process(battle, action)
    if ret_message:
        return {"self": {"nessage": ret_message}}

    # Get a lock on the battle row
    with transaction.atomic():
        battle = models.Battle.objects.select_for_update().get(pk=battle.pk)
        battle_state, player_state, is_p1 = get_battle_state(battle, player)

        # First turn logic
        if first_turn:
            return process_first_turn

        if battle.battle_end is not None:
            return {"self": {"message": "Battle is already over!"}}

        if has_player_already_moved(is_p1, battle):
            return {"self": {"message": "Move has already been made!"}}

        # Initialize battle manager
        if not is_valid_action(battle_state, player_state, action):
            return {"self": {"message": "Invalid action!"}}

        store_player_action(is_p1, battle, action)

        # If non-PVP battle, submit other move as well
        if battle.type != "live" and not battle_state.requires_switch():
            battle.player_2_choice = battle_ai.get_move(battle_state, ai="random_move")

        # Check that moves are complete; if so, start battle processing
        if battle.player_1_choice and battle.player_2_choice:
            # Call function depending on whether switch-in after KO or standard turn
            call_process_battle(battle, battle_state)

            # Remove the output to send to client
            output_log = battle_state.output
            battle_state.output = []

            # Dole out experience for turn if applicable; add prompts for leveling and exp gain
            handle_experience_gain(battle_state, battle, output_log)
            opponent_switch(battle_state, battle, output_log)

            # Check the battle outcome and process if outcome
            if battle_state.outcome is not None:
                prompt = handle_outcome(battle_state, battle, output_log, is_p1)

        # Perform DB updates
        save_battle_to_db(battle_state, battle, output_log)
        save_team(battle, battle_state)

        return {"group": {"type": "chat.message", "state": battle_state.jsonify(), "prompt": prompt, "output": output_log, "turn": battle.current_turn, "send_update": True}}


def save_team(battle, battle_state):
    if battle.save_team:
        for i, pkmn in enumerate(battle.player_1.get_party()):
            # When catching pokemon, break here so we don't try to index into battle with new pokemon in party
            if i == len(battle_state.player_1.party):
                break
            pkmn_state = battle_state.player_1.party[i].jsonify()
            if pkmn_state["id"] == pkmn.pk:
                pkmn.set_battle_info(pkmn_state)
        if battle.type == "live":
            for i, pkmn in enumerate(battle.player_2.get_party()):
                pkmn_state = battle_state.player_2.party[i].jsonify()
                if pkmn_state["id"] == pkmn.pk:
                    pkmn.set_battle_info(pkmn_state)


def ko_loss(battle_state, output_log, player_1, player_2, is_p1):
    output_log.append({"text": "You blacked out!"})
    medical_fees = 10 * max([
        max([pkmn.level for pkmn in battle_state.player_2.party]),
        max([pkmn.level for pkmn in battle_state.player_1.party])
    ])
    output_log.append({"text": "You paid ${} in medical fees!".format(medical_fees)})
    if is_p1:
        player_1.money = max([0, player_1.money - medical_fees])
    else:
        player_2.money = max([0, player_2.money - medical_fees])
    output_log.append({"anim": ["recover"]})



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        payload = await battle_processor(text_data, self.scope["user"])
        if "self" in payload:
            await self.send(text_data=json.dumps(payload["self"]))
        if "group" in payload:
            if "send_update" in payload["group"]:
                await self.channel_layer.group_send(
                    self.room_group_name, payload["group"]
                )

    # Receive message from room group
    async def chat_message(self, event):
        state = event["state"]
        prompt = event["prompt"]
        output = event["output"]
        turn = event["turn"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "state": state,
            "prompt": prompt,
            "output": output,
            "turn": turn}))