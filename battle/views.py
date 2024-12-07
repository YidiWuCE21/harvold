import json

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from harvoldsite import consts
from . import models


def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})


@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
def gyms(request):
    # Check user badges
    gym_badges = request.user.profile.badges
    gym_order = ["grass", "electric", "water", "ground", "fighting", "fire", "ghost", "psychic", "steel", "dragon"]
    html_render_variables = {
        "gyms": [(gym, consts.GYM_LEADERS[gym], gym_badges[gym]) for gym in gym_order]
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
            return redirect("pokecenter")
    # Wild battle creation
    elif "wild" in request.POST:
        wild = request.POST.get("wild")
        try:
            models.create_battle(request.user.profile.pk, wild, "wild")
            return redirect("battle")
        except BaseException as e:
            return redirect("pokecenter")
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

    html_render_variables = {
        "battle_state": json.dumps(battle.battle_state),
        "output_log": battle.output_log,
        "move_history": battle.move_history,
        "type": battle.type,
        "self": "player_1" if battle.player_1 == request.user.profile else "player_2",
        "battle_id": battle.pk,
        "current_turn": battle.current_turn,
        "scene": "default",
        "is_p1": request.user.profile == battle.player_1,
        "move_data": json.dumps({move: {k: v for k, v in consts.MOVES[move].items() if k in ["damage_class", "name", "power", "accuracy", "category", "type", "pp"]} for move in battle.get_all_moves()})
    }
    return render(request, "battle/battle.html", html_render_variables)