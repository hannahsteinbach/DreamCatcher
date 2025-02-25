# Generated by Django 5.0.6 on 2024-05-23 09:03

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
            name='Dream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('content', models.TextField()),
                ('shared', models.BooleanField(default=False)),
                ('processed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DreamAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emotional_valence', models.FloatField()),
                ('topics', models.TextField()),
                ('genre', models.CharField(max_length=100)),
                ('level_of_realism', models.FloatField()),
                ('recurring_characters', models.TextField()),
                ('themes', models.TextField()),
                ('dream', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dreams.dream')),
            ],
        ),
    ]
