# Generated by Django 3.2.13 on 2023-06-12 09:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('channel_management', '0017_alter_outlet_distributor'),
    ]

    operations = [
        migrations.AddField(
            model_name='outlet',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='corresponding_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='outlet',
            name='distributor',
            field=models.ManyToManyField(blank=True, null=True, related_name='managing_outlets', to='channel_management.Outlet'),
        ),
    ]
