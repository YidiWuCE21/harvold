import json
import os
import time
import re
import random

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseBadRequest

from harvoldsite import consts
from . import models, battle_mansion
from pokemon.models import create_pokemon


@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
def gauntlet(request):
    gauntlet = request.user.profile.current_gauntlet
    if gauntlet.gauntlet_type == "mansion":
        return redirect("battle_mansion")
    return HttpResponseBadRequest()


@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
@user_passes_test(consts.user_not_in_gauntlet, login_url="/gauntlet")
def gyms(request):
    gym_order = ["grass", "electric", "water", "ground", "fighting", "fire", "ghost", "psychic", "steel", "dragon"]
    gym_badges = request.user.profile.badges
    def gym_unlocked(gym, elite=False):
        if gym not in gym_order:
            return False
        map_visited = True
        if gym == "grass":
            prev_gym_done = not elite or gym_badges["dragon"] is not None
        else:
            prev_gym = gym_order[gym_order.index(gym) - 1]
            if elite:
                prev_gym_done = gym_badges[prev_gym] == "gold"
            else:
                prev_gym_done = gym_badges[prev_gym] is not None
        return map_visited and prev_gym_done



    # Check user badges
    gyms = [[gym, consts.GYM_LEADERS[gym], gym_badges[gym]] for gym in gym_order]
    # Check if gym should be unlocked
    for i, gym in enumerate(gyms):
        if i == 0:
            gyms[i] += [True, gym_badges["dragon"] is not None]
        else:
            gyms[i] += [gym_unlocked(gym_order[i]), gym_unlocked(gym_order[i], elite=True)]
    html_render_variables = {
        "gyms": gyms
    }
    return render(request, "battle/gym_select.html", html_render_variables)


@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
@user_passes_test(consts.user_not_in_gauntlet, login_url="/gauntlet")
def ev_dojo(request):
    coaches = [[stat, consts.EV_COACHES[stat]] for stat in consts.STATS]
    html_render_variables = {
        "coaches": coaches
    }
    return render(request, "battle/ev_dojo.html", html_render_variables)


@login_required
def battle_create(request):
    if request.user.profile.current_battle is not None:
        return redirect("battle")
    if "trainer" in request.POST:
        return create_trainer_battle(request)
    # Wild battle creation
    elif "wild" in request.POST:
        return create_wild_battle(request)
    # If valid battle cannot be created, return to pokecenter
    else:
        return HttpResponseBadRequest("Failed process post request")


def create_trainer_battle(request):
    tries = 0
    retries = 3
    trainer = request.POST.get("trainer")
    while tries < retries:
        try:
            models.create_battle(request.user.profile.pk, trainer, "npc")
            return redirect("battle")
        except BaseException as e:
            tries += 1
            time.sleep(0.2)
    return HttpResponseBadRequest("Failed to make battle.")


def create_wild_battle(request):
    tries = 0
    retries = 3
    while tries < retries:
        try:
            wild_data = request.user.profile.wild_opponent
            # Attempt synchronize
            nature_override = None
            first_pokemon = request.user.profile.slot_1
            if first_pokemon.ability == "Synchronize":
                if random.random() < 0.5:
                    nature_override = first_pokemon.nature
            wild = create_pokemon(wild_data["dex"], wild_data["level"], wild_data["sex"], shiny=wild_data["shiny"], nature_override=nature_override)
            wild.save()
            models.create_battle(request.user.profile.pk, wild.pk, "wild", bg=wild_data["bg"])
            return redirect("battle")
        except BaseException as e:
            tries += 1
            time.sleep(0.2)
    return HttpResponseBadRequest("Failed to make battle.")


@login_required
def battle(request):
    # First check that user is not already in battle
    if request.user.profile.current_battle is not None:
        battle = request.user.profile.current_battle
    else:
        return redirect("home")
    is_p1 = request.user.profile == battle.player_1

    # Fetch player/opp sprites
    player_sprite = str(request.user.profile.character).zfill(2)
    opp_sprite = None
    music = "wild"
    rebattle = None
    if battle.type == "npc":
        music = "trainer"
        trainer_data = "{}.json".format(battle.npc_opponent)
        try:
            trainer_path = os.path.join(consts.STATIC_PATH, "data", "trainers", trainer_data)
            with open(trainer_path, encoding="utf-8") as trainer_file:
                trainer_json = json.load(trainer_file)
                opp_sprite = trainer_json["sprite"]
                if "music" in trainer_json:
                    music = trainer_json["music"]
                if "gym" in battle.npc_opponent or "ev_dojo" in battle.npc_opponent:
                    rebattle = battle.npc_opponent

        except:
            # Case where trainer is randomly generated
            opp_sprite = battle.npc_opponent
            pass
    if battle.type == "live":
        music = "trainer"
        opp_sprite = str(battle.get_opp(request.user.profile).character).zfill(2)
    wild = None
    if battle.type == "wild":
        wild = battle.wild_opponent.pk

    html_render_variables = {
        "battle_state": json.dumps(battle.battle_state).replace("'", "\\'"),
        "output_log": json.dumps(battle.output_log).replace("'", "\\'"),
        "move_history": battle.move_history,
        "type": battle.type,
        "self": "player_1" if battle.player_1 == request.user.profile else "player_2",
        "battle_id": battle.pk,
        "current_turn": battle.current_turn,
        "scene": battle.background if battle.background is not None else "default",
        "is_p1": is_p1,
        "move_data": json.dumps({move: {k: v for k, v in consts.MOVES[move].items() if k in ["damage_class", "effects", "name", "power", "accuracy", "category", "type", "pp"]} for move in battle.get_all_moves()}).replace("'", "\\'"),
        "balls_allowed": battle.type == "wild",
        "medicines_allowed": battle.type != "live",
        "player_sprite": player_sprite,
        "opp_sprite": opp_sprite,
        "music": music,
        "wild_pk": wild,
        "rebattle": rebattle
    }
    return render(request, "battle/battle.html", html_render_variables)


@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
@user_passes_test(consts.user_not_in_gauntlet, login_url="/gauntlet")
def battle_mansion_start(request):
    if request.user.profile.current_battle is not None:
        return redirect("battle")
    if request.user.profile.current_gauntlet is not None:
        return redirect("battle_mansion")
    html_render_variables = {
        "eligible": not request.user.profile.has_beat_trainer("battle_mansion")
    }
    return render(request, "battle/battle_mansion_start.html", html_render_variables)


@login_required
def battle_mansion_page(request):
    # Redirect if user in battle
    if request.user.profile.current_battle is not None:
        return redirect("battle")
    if request.user.profile.has_beat_trainer("battle_mansion"):
        return redirect("pokecenter")
    gauntlet = request.user.profile.current_gauntlet
    # If the user does not have an active gauntlet, AND has not beat BM, create a BM gauntlet
    if gauntlet is not None and gauntlet.gauntlet_type != "mansion":
        return redirect("pokecenter")
    if gauntlet is None:
        gauntlet, msg = battle_mansion.start_battle_mansion(request.user.profile)
        if not gauntlet:
            messages.success(request, msg)
            return redirect("battle_mansion_start")

    # Get the mansion object
    mansion = battle_mansion.BattleMansion.from_json(gauntlet.gauntlet_state)

    # If we are creating a battle, create it; only accessible if current battle is not there
    if request.POST.get("mansion", None) == "battle":
        mansion_battle = mansion.fight_trainer(gauntlet.team_state, gauntlet)
        return redirect("battle")
    if request.POST.get("mansion", None) == "leave":
        rewards = mansion.cash_out()
        for item, qty in rewards.items():
            request.user.profile.add_item(item, qty)
        request.user.profile.current_gauntlet = None
        request.user.profile.save()
        return redirect("pokecenter")


    # If we have just come back from a battle, we need to update based on victory or defeat
    can_fight = True
    complete = False
    if gauntlet.current_battle == "victory":
        gauntlet.current_battle = "pending"
        progress_update = mansion.beat_trainer()
        if progress_update == "complete":
            mansion.generate_prize(mansion.progress["floor"] - 1)
            can_fight = False
            complete = True
        if progress_update == "new_floor":
            # No logic yet
            gauntlet.heal(0.2, 0.5, status=True)
            mansion.generate_prize(mansion.progress["floor"] - 1)
            pass
    if gauntlet.current_battle == "defeat":
        gauntlet.current_battle = "pending"
        can_fight = False
    gauntlet.save()

    floor_info = mansion.get_floor(mansion.progress["floor"])
    rewards = [
        (item, quantity, consts.ITEMS[item]["name"])
        if consts.ITEMS[item]["category"] != "machines" else (
            "tm-{}".format(consts.ITEMS[item]["type"]),
            quantity,
            "TM {}".format(consts.MOVES[consts.ITEMS[item]["move"]]["name"]))
        for item, quantity in mansion.progress["prizes"].items()]
    # Standard case
    html_render_variables = {
        "current_floor": mansion.progress["floor"],
        "round_progress": mansion.progress["trainer"],
        "rewards": rewards,
        "floor_info": floor_info.jsonify() if floor_info is not None else None,
        "can_fight": can_fight,
        "complete": complete
    }
    return render(request, "battle/battle_mansion.html", html_render_variables)



@login_required
def battle_mansion_next(request):

    # Standard case
    html_render_variables = {
    }
    return render(request, "battle/battle_mansion.html", html_render_variables)
