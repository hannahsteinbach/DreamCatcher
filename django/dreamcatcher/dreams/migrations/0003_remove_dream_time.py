# Generated by Django 4.1 on 2024-06-14 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dreams', '0002_dream_time_delete_dreamanalysis'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dream',
            name='time',
        ),
    ]
