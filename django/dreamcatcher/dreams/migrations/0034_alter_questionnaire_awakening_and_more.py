# Generated by Django 4.1 on 2024-08-29 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dreams', '0033_alter_profile_avatar_questionnaire'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='awakening',
            field=models.CharField(blank=True, choices=[('0', 'No'), ('1', 'Yes')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='creativity',
            field=models.CharField(blank=True, choices=[('0', 'No'), ('1', 'Yes')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='dream_impact_mood',
            field=models.CharField(blank=True, choices=[('0', 'No'), ('1', 'Yes')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='dream_relation_oneself',
            field=models.CharField(blank=True, choices=[('0', 'No'), ('1', 'Yes')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='morning_mood',
            field=models.CharField(blank=True, choices=[('0', 'No'), ('1', 'Yes')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='sleep_duration',
            field=models.CharField(blank=True, choices=[('0', 'Less than 3 hours'), ('1', '3-5 hours'), ('2', '6-8 hours'), ('3', 'More than 8 hours')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='sleep_quality',
            field=models.CharField(blank=True, choices=[('0', 'Very poor'), ('1', 'Poor'), ('2', 'Neutral'), ('3', 'Good'), ('4', 'Very Good')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='stress',
            field=models.CharField(blank=True, choices=[('0', 'No'), ('1', 'Yes')], max_length=1, null=True),
        ),
    ]
