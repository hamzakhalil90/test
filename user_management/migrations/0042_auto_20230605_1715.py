# Generated by Django 3.2.13 on 2023-06-05 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0041_auto_20230605_0655'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]