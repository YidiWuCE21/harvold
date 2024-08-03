# Generated by Django 5.0.7 on 2024-08-02 13:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('trainer_id', models.IntegerField(primary_key=True, serialize=False)),
                ('banned', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=500, null=True)),
                ('title', models.CharField(max_length=50, null=True)),
                ('faction', models.IntegerField(null=True)),
                ('state', models.CharField(default='idle', max_length=10)),
                ('money', models.IntegerField(default=10000)),
                ('character', models.IntegerField()),
                ('wins', models.IntegerField(default=0)),
                ('losses', models.IntegerField(default=0)),
                ('pvp_wins', models.IntegerField(default=0)),
                ('pvp_losses', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
