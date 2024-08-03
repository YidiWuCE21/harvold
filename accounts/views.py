from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserCreateForm, StarterChoiceForm, TrainerSelectForm
from .models import Profile
from pokemon.models import Pokemon
from harvoldsite import consts


# Additional models required for signup


def signup(request):
    if request.method == "POST":
        # Process forms if data was submitted
        signup_form = UserCreateForm(request.POST)
        starter_form = StarterChoiceForm(request.POST)
        trainer_form = TrainerSelectForm(request.POST)
        if signup_form.is_valid() and starter_form.is_valid() and trainer_form.is_valid():
            new_user = signup_form.save()
            new_user = authenticate(
                username=signup_form.cleaned_data["username"],
                password=signup_form.cleaned_data["password"],
            )
            login(request, new_user)
            # Handle profile setup
            chosen_trainer = trainer_form.cleaned_data["trainer"]
            chosen_starter = starter_form.cleaned_data["pokemon"]
            # Handle starter select
            return redirect("home")
    else:
        # Initialize the signup forms for a fresh page
        signup_form = UserCreateForm()
        starter_form = StarterChoiceForm()
        trainer_form = TrainerSelectForm()

    html_render_variables = {
        "signup_form": signup_form,
        "starter_form": starter_form,
        "trainer_form": trainer_form,
        "asset_paths": consts.ASSET_PATHS
    }

    return render(request, "registration/signup.html", html_render_variables)