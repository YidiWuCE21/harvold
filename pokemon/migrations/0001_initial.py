# Generated by Django 5.0.7 on 2024-08-02 13:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pokemon',
            fields=[
                ('pkmn_id', models.IntegerField(primary_key=True, serialize=False)),
                ('original_trainer', models.IntegerField(null=True)),
                ('dex_number', models.IntegerField()),
                ('level', models.IntegerField()),
                ('experience', models.IntegerField()),
                ('ball', models.CharField(max_length=20, null=True)),
                ('sex', models.CharField(max_length=1)),
                ('nature', models.CharField(max_length=10)),
                ('shiny', models.BooleanField(default=False)),
                ('ability', models.CharField(max_length=20, null=True)),
                ('hp_stat', models.IntegerField(default=1)),
                ('hp_iv', models.IntegerField()),
                ('hp_ev', models.IntegerField(default=0)),
                ('atk_stat', models.IntegerField(default=1)),
                ('atk_iv', models.IntegerField()),
                ('atk_ev', models.IntegerField(default=0)),
                ('def_stat', models.IntegerField(default=1)),
                ('def_iv', models.IntegerField()),
                ('def_ev', models.IntegerField(default=0)),
                ('spa_stat', models.IntegerField(default=1)),
                ('spa_iv', models.IntegerField()),
                ('spa_ev', models.IntegerField(default=0)),
                ('spd_stat', models.IntegerField(default=1)),
                ('spd_iv', models.IntegerField()),
                ('spd_ev', models.IntegerField(default=0)),
                ('spe_stat', models.IntegerField(default=1)),
                ('spe_iv', models.IntegerField()),
                ('spe_ev', models.IntegerField(default=0)),
                ('held_item', models.CharField(max_length=20, null=True)),
                ('current_hp', models.IntegerField()),
                ('status', models.CharField(max_length=20, null=True)),
                ('traded', models.BooleanField(default=False)),
                ('happiness', models.IntegerField(default=200)),
                ('location', models.CharField(max_length=10, null=True)),
                ('move1', models.CharField(max_length=20)),
                ('move1_pp', models.IntegerField()),
                ('move2', models.CharField(max_length=20, null=True)),
                ('move2_pp', models.IntegerField(null=True)),
                ('move3', models.CharField(max_length=20, null=True)),
                ('move3_pp', models.IntegerField(null=True)),
                ('move4', models.CharField(max_length=20, null=True)),
                ('move4_pp', models.IntegerField(null=True)),
                ('trainer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Party',
            fields=[
                ('party_id', models.IntegerField(primary_key=True, serialize=False)),
                ('trainer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accounts.profile')),
                ('slot_1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='slot_1', to='pokemon.pokemon')),
                ('slot_2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='slot_2', to='pokemon.pokemon')),
                ('slot_3', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='slot_3', to='pokemon.pokemon')),
                ('slot_4', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='slot_4', to='pokemon.pokemon')),
                ('slot_5', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='slot_5', to='pokemon.pokemon')),
                ('slot_6', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='slot_6', to='pokemon.pokemon')),
            ],
        ),
    ]
