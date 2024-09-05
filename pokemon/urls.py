from django.urls import path

from . import views


urlpatterns = [
    path("detailed/", views.pokemon, name="pokemon"),
    path("box/", views.box, name="box"),
    path("make/", views.make, name="make")
]