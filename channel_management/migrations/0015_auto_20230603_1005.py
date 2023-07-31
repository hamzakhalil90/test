# Generated by Django 3.2.13 on 2023-06-03 10:05

from django.conf import settings
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('channel_management', '0014_channel_marker'),
    ]

    operations = [
        migrations.AddField(
            model_name='outlet',
            name='distributor',
            field=models.ManyToManyField(blank=True, null=True, related_name='_channel_management_outlet_distributor_+', to='channel_management.Outlet'),
        ),
        migrations.AddField(
            model_name='outlet',
            name='dsr',
            field=models.ManyToManyField(blank=True, null=True, related_name='outlets_under_dsr', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='outlet',
            name='is_distributor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='outlet',
            name='name_on_board',
            field=models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9 ]+$', message='Name field should not contain special characters')]),
        ),
        migrations.AddField(
            model_name='outlet',
            name='regional_manager',
            field=models.ManyToManyField(blank=True, null=True, related_name='outlets_under_rm', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='outlet',
            name='zonal_manager',
            field=models.ManyToManyField(blank=True, null=True, related_name='outlets_under_zm', to=settings.AUTH_USER_MODEL),
        ),
    ]