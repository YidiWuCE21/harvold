# Generated by Django 5.0.7 on 2024-10-25 01:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_profile_badges'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='bag',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='money',
        ),
    ]