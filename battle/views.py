
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from harvoldsite import consts
from . import models


def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})


def gyms(request):
    # Check user badges
    gym_badges = request.user.profile.badges
    gym_order = ["grass", "electric", "water", "ground", "fighting", "fire", "ghost", "psychic", "steel", "dragon"]
    html_render_variables = {
        "gyms": [(gym, consts.GYM_LEADERS[gym], gym_badges[gym]) for gym in gym_order]
    }
    return render(request, "battle/gym_select.html", html_render_variables)


@login_required
def battle(request):
    if "trainer" in request.POST:
        trainer = request.POST.get("trainer")
        return redirect("pokemon:pokecenter")
        battle = models.create_battle(request.user.profile.pk, trainer, "npc")
        if battle[0]:
            return redirect("pokemon:pokecenter")
        else:
            return redirect("pokemon:pokecenter")
    else:
        return redirect("pokemon:pokecenter")

    # TODO Check if user in battle, otherwise redirect to pokecenter
    html_render_variables = {}
    return render(request, "battle/battle.html", html_render_variables)