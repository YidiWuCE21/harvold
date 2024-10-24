
from django.shortcuts import render

from harvoldsite import consts


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