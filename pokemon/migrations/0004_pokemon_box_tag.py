# Generated by Django 5.0.7 on 2024-08-21 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemon', '0003_alter_pokemon_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='pokemon',
            name='box_tag',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
