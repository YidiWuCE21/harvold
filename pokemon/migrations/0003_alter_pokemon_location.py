# Generated by Django 5.0.7 on 2024-08-15 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemon', '0002_alter_pokemon_original_trainer_alter_pokemon_trainer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pokemon',
            name='location',
            field=models.CharField(blank=True, default='box', max_length=10, null=True),
        ),
    ]
