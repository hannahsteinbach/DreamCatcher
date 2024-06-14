# Generated by Django 4.1 on 2024-06-14 08:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dreams', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dream',
            name='time',
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='DreamAnalysis',
        ),
    ]
