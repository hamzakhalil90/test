# Generated by Django 3.2.13 on 2023-06-23 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('area_management', '0008_auto_20230523_0732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='code',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='country',
            name='code',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='region',
            name='code',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='subzone',
            name='code',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='zone',
            name='code',
            field=models.CharField(max_length=20),
        ),
    ]
