# Generated by Django 3.2.10 on 2021-12-28 21:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bangumi_ratings_backend', '0005_auto_20211228_1143'),
    ]

    operations = [
        migrations.RenameField(
            model_name='oldanime',
            old_name='anime_id',
            new_name='anime',
        ),
        migrations.RenameField(
            model_name='quote',
            old_name='anime_id',
            new_name='anime',
        ),
        migrations.RenameField(
            model_name='seasonanimes',
            old_name='anime_id',
            new_name='anime',
        ),
        migrations.RenameField(
            model_name='seasonranking',
            old_name='anime_id',
            new_name='anime',
        ),
    ]