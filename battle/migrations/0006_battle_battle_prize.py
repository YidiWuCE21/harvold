# Generated by Django 5.0.7 on 2024-12-12 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0005_alter_battle_battle_end'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='battle_prize',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]
