# Generated by Django 5.0.7 on 2024-12-07 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemon', '0008_pokemon_status_turns'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pokemon',
            name='status',
            field=models.CharField(default='', max_length=20),
        ),
    ]
