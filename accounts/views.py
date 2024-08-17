import random

from django.shortcuts import render, redirect
from django.db import IntegrityError, transaction

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
        "asset_paths": consts.ASSET_PATHS,
        "pokemon_data": {starter[0]: consts.POKEMON[starter[0]] for starter in consts.STARTER_CHOICES}
    }

    return render(request, "registration/signup.html", html_render_variables)