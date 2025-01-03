import json
import os

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseBadRequest

from harvoldsite import consts
from . import models
from pokemon.models import create_pokemon


@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
def gyms(request):
    gym_order = ["grass", "electric", "water", "ground", "fighting", "fire", "ghost", "psychic", "steel", "dragon"]
    gym_badges = request.user.profile.badges
    def gym_unlocked(gym, elite=False):
        if gym not in gym_order:
            return False
        map_visited = True
        prev_gym_done = False
        if gym == "grass":
            prev_gym_done = not elite or gym_badges["dragon"] is not None
        else:
            prev_gym = gym_order[gym_order.index(gym) - 1]
            if elite:
                prev_gym_done = gym_badges[prev_gym] == "gold"
            else:
                prev_gym_done = gym_badges[prev_gym] == "silver"
        return map_visited and prev_gym_done



    # Check user badges
    gyms = [[gym, consts.GYM_LEADERS[gym], gym_badges[gym]] for gym in gym_order]
    # Check if gym should be unlocked
    for i, gym in enumerate(gyms):
        if i == 0:
            gyms[i] += [True, gym_badges["dragon"] is not None]
        else:
            prev_gym = gym_order[i - 1]
            gyms[i] += [gym_unlocked(gym_order[i]), gym_unlocked(gym_order[i], elite=True)]
    html_render_variables = {
        "gyms": gyms
    }
    return render(request, "battle/gym_select.html", html_render_variables)


@login_required
def battle_create(request):
    if request.user.profile.current_battle is not None:
        return redirect("battle")
    if "trainer" in request.POST:
        trainer = request.POST.get("trainer")
        try:
            models.create_battle(request.user.profile.pk, trainer, "npc")
            return redirect("battle")
        except BaseException as e:
            return HttpResponseBadRequest(str(e))
    # Wild battle creation
    elif "wild" in request.POST:
        wild_data = request.user.profile.wild_opponent
        wild = create_pokemon(wild_data["dex"], wild_data["level"], wild_data["sex"], shiny=wild_data["shiny"])
        wild.save()
        try:
            models.create_battle(request.user.profile.pk, wild.pk, "wild")
            return redirect("battle")
        except BaseException as e:
            return HttpResponseBadRequest(str(e))
    # If valid battle cannot be created, return to pokecenter
    else:
        return redirect("pokecenter")


@login_required
def battle(request):
    # First check that user is not already in battle
    if request.user.profile.current_battle is not None:
        battle = request.user.profile.current_battle
    else:
        return redirect("pokecenter")
    is_p1 = request.user.profile == battle.player_1

    # Fetch player/opp sprites
    player_sprite = str(request.user.profile.character).zfill(2)
    opp_sprite = None
    music = "wild"
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

        except:
            pass
    if battle.type == "live":
        music = "trainer"
        opp_sprite = str(battle.get_opp(request.user.profile).character).zfill(2)

    html_render_variables = {
        "battle_state": json.dumps(battle.battle_state),
        "output_log": json.dumps(battle.output_log).replace("'", "\\'"),
        "move_history": battle.move_history,
        "type": battle.type,
        "self": "player_1" if battle.player_1 == request.user.profile else "player_2",
        "battle_id": battle.pk,
        "current_turn": battle.current_turn,
        "scene": "default",
        "is_p1": is_p1,
        "move_data": json.dumps({move: {k: v for k, v in consts.MOVES[move].items() if k in ["damage_class", "effects", "name", "power", "accuracy", "category", "type", "pp"]} for move in battle.get_all_moves()}).replace("'", "\\'"),
        "balls_allowed": battle.type == "wild",
        "medicines_allowed": battle.type != "live",
        "player_sprite": player_sprite,
        "opp_sprite": opp_sprite,
        "music": music
    }
    return render(request, "battle/battle.html", html_render_variables)