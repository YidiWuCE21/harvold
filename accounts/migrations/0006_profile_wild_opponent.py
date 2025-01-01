# Generated by Django 5.0.7 on 2024-10-07 20:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_profile_current_battle'),
        ('pokemon', '0007_pokemon_locked'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='wild_opponent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wild_mon', to='pokemon.pokemon'),
        ),
    ]
