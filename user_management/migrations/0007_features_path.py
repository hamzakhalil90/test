# Generated by Django 3.2.13 on 2023-02-20 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0006_auto_20230217_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='features',
            name='path',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
    ]