# Generated by Django 5.0.7 on 2025-01-04 20:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_messages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipient', to='accounts.profile'),
        ),
        migrations.AlterField(
            model_name='messages',
            name='sender',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sender', to='accounts.profile'),
        ),
    ]
