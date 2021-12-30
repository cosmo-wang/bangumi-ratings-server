# Generated by Django 3.2.10 on 2021-12-28 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bangumi_ratings_backend', '0012_auto_20211228_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anime',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='anime',
            name='douban_rating',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='anime',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='anime',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
