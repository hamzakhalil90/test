# Generated by Django 3.2.13 on 2023-02-20 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0008_alter_features_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_locked',
            field=models.BooleanField(default=True),
        ),
    ]
