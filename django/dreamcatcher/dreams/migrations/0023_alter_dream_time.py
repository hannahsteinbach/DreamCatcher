# Generated by Django 4.1 on 2024-07-15 15:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dreams', '0022_alter_dream_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dream',
            name='time',
            field=models.TimeField(default=datetime.datetime(2024, 7, 15, 15, 32, 36, 449709)),
        ),
    ]
