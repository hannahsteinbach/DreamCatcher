# Generated by Django 4.1 on 2024-07-04 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dreams', '0012_alter_dreamshared_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dream',
            name='anon',
            field=models.BooleanField(default=False),
        ),
    ]
