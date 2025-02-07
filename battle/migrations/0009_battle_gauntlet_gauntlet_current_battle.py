# Generated by Django 5.0.7 on 2025-02-05 19:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0008_gauntlet'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='gauntlet',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.gauntlet'),
        ),
        migrations.AddField(
            model_name='gauntlet',
            name='current_battle',
            field=models.CharField(default='pending', max_length=10),
        ),
    ]
