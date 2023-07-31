# Generated by Django 3.2.13 on 2023-06-13 11:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('channel_management', '0018_auto_20230612_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outlet',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='corresponding_outlet', to=settings.AUTH_USER_MODEL),
        ),
    ]
