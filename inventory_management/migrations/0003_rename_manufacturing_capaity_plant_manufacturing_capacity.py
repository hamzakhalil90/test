# Generated by Django 3.2.13 on 2023-02-16 08:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management', '0002_auto_20230216_1324'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plant',
            old_name='manufacturing_capaity',
            new_name='manufacturing_capacity',
        ),
    ]
