# Generated by Django 3.2.13 on 2023-03-27 06:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('channel_management', '0011_auto_20230327_0548'),
    ]

    operations = [
        migrations.RenameField(
            model_name='channel',
            old_name='status',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='outlet',
            old_name='status',
            new_name='is_active',
        ),
    ]