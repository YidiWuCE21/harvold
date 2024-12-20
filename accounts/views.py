import random

from django.shortcuts import render, redirect
from django.db import IntegrityError, transaction
from django.contrib.auth.decorators import login_required

from .forms import UserCreateForm, StarterChoiceForm, TrainerSelectForm
from .models import Profile
from pokemon.models import create_pokemon
from harvoldsite import consts


# Additional models required for signup


def signup(request):
    if request.method == "POST":
        # Process forms if data was submitted
        signup_form = UserCreateForm(request.POST)
        starter_form = StarterChoiceForm(request.POST)
        trainer_form = TrainerSelectForm(request.POST)
        if signup_form.is_valid() and starter_form.is_valid() and trainer_form.is_valid():
            try:
                with transaction.atomic():
                    new_user = signup_form.save()

                    # Handle profile setup and starter selection
                    chosen_trainer = trainer_form.cleaned_data["trainer"]
                    chosen_starter = starter_form.cleaned_data["pokemon"]


                    user_profile = Profile(user=new_user, character=chosen_trainer)
                    user_profile.save()

                    user_starter = create_pokemon(dex_number=chosen_starter, level=5, sex=random.choice(["m", "f"]), iv_advantage=2)
                    user_starter.assign_trainer(user_profile)
                    user_starter.save()

                    # Add the starter to the user's party
                    error_msg = user_profile.add_to_party(user_starter)

                    # This situation shouldn't ever happen but if it does, cancel signup
                    if error_msg is not None:
                        raise IntegrityError("ruh roh raggy")

                    return redirect("login")
            except IntegrityError:
                return redirect("signup")
    else:
        # Initialize the signup forms for a fresh page
        signup_form = UserCreateForm()
        starter_form = StarterChoiceForm()
        trainer_form = TrainerSelectForm()

    html_render_variables = {
        "signup_form": signup_form,
        "starter_form": starter_form,
        "trainer_form": trainer_form,
        "pokemon_data": {starter[0]: consts.POKEMON[starter[0]] for starter in consts.STARTER_CHOICES}
    }

    return render(request, "registration/signup.html", html_render_variables)


@login_required
def view_profile(request):
    profile = Profile.objects.get(pk=request.GET.get("id"))
    self_view =  profile == request.user.profile
    party = profile.get_party()
    party = [pkmn.get_party_info() if pkmn is not None else None for pkmn in party]
    html_render_variables = {
        "username": profile.user.username,
        "character": profile.char_id,
        "trainer_points": profile.trainer_points,
        "description": profile.description,
        "title": profile.title,
        "money": profile.money,
        "wins": profile.wins,
        "losses": profile.losses,
        "pvp_wins": profile.pvp_wins,
        "pvp_losses": profile.pvp_losses,
        "profile_party": party,
        "dex_entries": profile.dex_entries,
        "date_joined": profile.user.date_joined.date,
        "self_view": self_view,
        "badges": {"grass": "silver", "electric": "silver", "fire": "silver", "fighting": "silver", "water": "silver", "dragon": "silver", "ghost": "silver", "ground": "silver"}
    }
    return render(request, "registration/profile.html", html_render_variables)


@login_required
def bag(request):
    bag = request.user.profile.bag
    bag_data = {}
    for category in bag:
        bag_data[category] = {}
        for item, qty in bag[category].items():
            bag_data[category][item] = consts.ITEMS[item]
            bag_data[category][item]["quantity"] = qty
            if category == "machines":
                bag_data[category][item]["move_data"] = consts.MOVES[consts.ITEMS[item]["move"]]
    html_render_variables = {
        "bag": bag_data
    }
    return render(request, "pokemon/bag.html", html_render_variables)


@login_required
def pokemart(request):
    mart_data = {}
    message = None
    # Process purchase request
    if request.POST:
        cost = 0
        funds = request.user.profile.money
        order = {}
        for item in request.POST:
            if item in consts.ITEMS:
                quantity = request.POST.get(item)
                if quantity:
                    quantity = int(quantity)
                    cost += consts.MART[consts.ITEMS[item]["category"]][item]
                    order[item] = quantity
        if cost > funds:
            message = "Insufficient funds!"
        else:
            message = "Purchase successful!"
            for item, quantity in order.items():
                success, ret_msg = request.user.profile.purchase_item(item, quantity)
                if not success:
                    message = "Could not buy {}; {}".format(consts.ITEMS[item]["name"], ret_msg)
                    break



    for category, mart_items in consts.MART.items():
        mart_data[category] = {}
        for item, price in mart_items.items():
            cost = price
            mart_data[category][item] = {
                "price": cost,
                "name": consts.ITEMS[item]["name"],
                "description": consts.ITEMS[item]["description"],
            }
            if "type" in consts.ITEMS[item]:
                mart_data[category][item]["type"] = consts.ITEMS[item]["type"]
    html_render_variables = {
        "mart": mart_data,
        "funds": request.user.profile.money,
        "message": message
    }
    return render(request, "pokemon/pokemart.html", html_render_variables)