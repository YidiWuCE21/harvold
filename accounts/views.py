import random
import os
import json
import pandas as pd
from django.shortcuts import render, redirect
from django.db import IntegrityError, transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseNotFound

from .forms import UserCreateForm, StarterChoiceForm, TrainerSelectForm
from .models import Profile, Messages, send_message, process_messages
from pokemon.models import create_pokemon, Pokemon
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
                    send_message(user_profile, "Professor Oak", "Welcome to Project Harvold! Your first goals in the game should be to complete the 10 gyms. Make sure to catch and train your team first. Good luck!", "Welcome to Project Harvold!", None, "professor_oak", gift_items={"pokeball": 10})

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
        "badges": profile.badges
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
    party_moves = [{
        "dex": pkmn.dex,
        "moves": pkmn.get_moves(),
        "held_item": pkmn.held_item,
        "name": pkmn.name,
        "level": pkmn.level}
        for pkmn in request.user.profile.get_party()]
    html_render_variables = {
        "bag": bag_data,
        "bag_data_str": json.dumps(bag_data).replace("'", "\\'"),
        "tm_compatibility": json.dumps({pkmn.dex: consts.LEARNSETS[pkmn.dex]["tm"] for pkmn in request.user.profile.get_party()}).replace("'", "\\'"),
        "party_moves": party_moves,
        "party_moves_str": json.dumps(party_moves).replace("'", "\\'"),
    }
    return render(request, "pokemon/bag.html", html_render_variables)


@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
@user_passes_test(consts.user_not_in_gauntlet, login_url="/gauntlet")
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

@login_required
def inbox(request):
    profile = request.user.profile
    if profile.inbox_flag != profile.has_unread():
        profile.inbox_flag = profile.has_unread()
        profile.save()
    sent = Messages.objects.filter(sender=profile)
    received = Messages.objects.filter(recipient=profile)
    sent = process_messages(sent)
    sent = sent[["To", "Title", "Date"]]
    received = process_messages(received)
    received = received[["From", "Title", "Date"]]


    # Gather tradeable items
    tradeables = profile.tradeable_items()

    html_render_variables = {
        "sent": sent.to_html(escape=False, table_id="sentMsg", classes=["display", "compact"], index=False),
        "received": received.to_html(escape=False, table_id="receivedMsg", classes=["display", "compact"], index=False),
        "tradeables": tradeables
    }
    return render(request, "pokemon/inbox.html", html_render_variables)


@login_required
def remove_party_ajax(request):
    profile = request.user.profile
    msg = ""
    if profile.current_battle is not None:
        msg = "Cannot swap party in battle!"
    else:
        try:
            slot = request.GET.get("payload")
            msg = profile.remove_from_party(getattr(profile, slot))
        except:
            msg = "Failed to remove from party!"
    party = profile.get_party(return_none=True)
    if msg is None:
        msg = ""
    return render(request, "common/party.html", {"party": [pkmn.get_party_info() if pkmn is not None else None for pkmn in party], "msg": msg})


@login_required
def reorder_party_ajax(request):
    profile = request.user.profile
    msg = ""
    if profile.current_battle is not None:
        msg = "Cannot swap party in battle!"
    else:
        try:
            slot_1 = request.GET.get("slot_1")
            slot_2 = request.GET.get("slot_2")
            profile.swap_pokemon(slot_1, slot_2)
        except:
            msg = "Failed to reorder party!"
    party = profile.get_party(return_none=True)
    return render(request, "common/party.html", {"party": [pkmn.get_party_info() if pkmn is not None else None for pkmn in party], "msg": msg})

@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
def teach_tm_ajax(request):
    profile = request.user.profile
    tm = request.GET.get("tm")
    target = request.GET.get("target")
    slot = request.GET.get("slot")
    msg = profile.teach_tm(tm, target, slot)
    return JsonResponse({"msg": msg})

@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
def take_held_item_ajax(request):
    profile = request.user.profile
    pkmn = request.GET.get("slot", None)
    if pkmn is None:
        pkmn = Pokemon.objects.get(pk=request.GET.get("id"))
    msg = profile.take_item(pkmn)
    return JsonResponse({"msg": msg})

@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
def give_held_item_ajax(request):
    profile = request.user.profile
    slot = request.GET.get("slot")
    item = request.GET.get("item")
    msg = profile.give_item(item, slot)
    return JsonResponse({"msg": msg})

@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
@user_passes_test(consts.user_not_in_gauntlet, login_url="/gauntlet")
def read_message_ajax(request):
    message_id = request.GET.get("msg")
    message = Messages.objects.get(pk=message_id)
    if message:
        body = message.body
        title = message.title
        sender = message.sender_name
        recipient = message.recipient.user.username
        is_receiver = message.recipient == request.user.profile

        processed_gifts = None
        if is_receiver:
            message.read_message()
            gifts = message.gift_items
            processed_gifts = {}
            for gift, qty in gifts.items():
                if "tm" in gift or "hm" in gift:
                    move = consts.ITEMS[gift]["move"]
                    type = consts.MOVES[move]["type"]
                    processed_gifts["tm-{}".format(type)] = qty
                else:
                    processed_gifts[gift] = qty
        sender_url = os.path.join(consts.ASSET_PATHS["trainer_sprite"], "{}.png".format(message.sender_spr))
        if message.sender is not None:
            sender_url = os.path.join(consts.ASSET_PATHS["player_sprite"], "{}.png".format(message.sender_spr))
        html_render_variables = {
            "body": body,
            "title": title,
            "sender": sender,
            "recipient": recipient,
            "gifts": processed_gifts,
            "is_receiver": is_receiver,
            "sender_url": sender_url,
            "date": message.time.strftime("%x %X")
        }
        return render(request, "common/inbox_message.html", html_render_variables)
    raise ValueError("Failed to find message")