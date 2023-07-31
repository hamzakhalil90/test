# Generated by Django 3.2.13 on 2023-02-16 11:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channel_management', '0002_auto_20230216_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='name',
            field=models.CharField(max_length=100, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9 ]+$', message='Name field should not contain special characters')]),
        ),
        migrations.AlterField(
            model_name='outlet',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9 ]+$', message='Name field should not contain special characters')]),
        ),
        migrations.AlterField(
            model_name='outlet',
            name='ntn',
            field=models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9 ]+$', message='Name field should not contain special characters')]),
        ),
        migrations.AlterField(
            model_name='outlet',
            name='sap_code',
            field=models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9 ]+$', message='Name field should not contain special characters')]),
        ),
        migrations.AlterField(
            model_name='outlet',
            name='strn',
            field=models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9 ]+$', message='Name field should not contain special characters')]),
        ),
    ]