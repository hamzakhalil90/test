 # Generated by Django 3.2.13 on 2023-04-06 08:01

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0030_alter_user_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='employee', to='area_management.region'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='number',
            field=models.CharField(max_length=2, validators=[django.core.validators.RegexValidator('^[0-9]+$', message='Grade-Postfix can only contain digits.')]),
        ),
        migrations.AlterField(
            model_name='grade',
            name='prefix',
            field=models.CharField(blank=True, max_length=4, null=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9 ]+$', message='Grade-Prefix field should not contain special characters')]),
        ),
    ]
