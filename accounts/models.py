from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

# Create your models here.
class Profile(models.Model):
    # Administrative fields
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    banned = models.BooleanField(default=False)

    # Trainer data
    description = models.CharField(max_length=500, null=True)
    title = models.CharField(max_length=50, null=True)
    faction = models.IntegerField(null=True)
    state = models.CharField(default="idle", max_length=10) # Used to control in-battle status
    # TODO - Clan system

    # Trainer values
    money = models.IntegerField(default=10000)
    character = models.IntegerField()

    # Trainer stats
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    pvp_wins = models.IntegerField(default=0)
    pvp_losses = models.IntegerField(default=0)