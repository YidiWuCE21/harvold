from django.urls import path

from . import views


urlpatterns = [
    path("detailed", views.pokemon, name="pokemon")
]