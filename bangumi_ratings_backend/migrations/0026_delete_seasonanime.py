# Generated by Django 3.2.10 on 2022-05-08 03:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bangumi_ratings_backend', '0025_anime_cover_url'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SeasonAnime',
        ),
    ]