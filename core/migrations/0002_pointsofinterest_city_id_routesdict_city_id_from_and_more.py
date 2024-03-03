# Generated by Django 5.0.1 on 2024-03-03 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pointsofinterest',
            name='city_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='routesdict',
            name='city_id_from',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='routesdict',
            name='city_id_to',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='traintrips',
            name='city_id_from',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='traintrips',
            name='city_id_to',
            field=models.IntegerField(default=0),
        ),
    ]