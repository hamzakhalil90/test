# Generated by Django 3.2.13 on 2023-04-16 13:17

from django.db import migrations, models
import django_mysql.models
import json
from user_management.models import Features, Permissions


class Migration(migrations.Migration):

    def add_features(apps, schema_editor):
        with open('user_management/migrations/feature_list.json', 'r') as f:
            feature_data = json.load(f)
            for feature in feature_data:
                Features.objects.create(path=feature.get('path'), name=feature.get('name'))

    def add_permissions(apps, schema_editor):
        with open('user_management/migrations/permissions_list.json', 'r') as f:
            permission_data = json.load(f)
            for permission in permission_data:
                Permissions.objects.create(code=permission.get('code'),
                                           name=permission.get('name'))

    dependencies = [
        ('user_management', '0033_alter_usergroup_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='days_of_week',
            field=django_mysql.models.ListCharField(models.CharField(max_length=10), blank=True, default=list, max_length=250, null=True, size=7),
        ),
        migrations.RunPython(add_features),
        migrations.RunPython(add_permissions),
    ]
