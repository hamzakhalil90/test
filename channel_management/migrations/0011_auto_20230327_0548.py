# Generated by Django 3.2.13 on 2023-03-27 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channel_management', '0010_auto_20230321_1011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='outlet',
            name='is_active',
        ),
        migrations.AddField(
            model_name='channel',
            name='status',
            field=models.CharField(choices=[('INACTIVE', 'INACTIVE'), ('ACTIVE', 'ACTIVE')], default='ACTIVE', max_length=8),
        ),
        migrations.AddField(
            model_name='outlet',
            name='status',
            field=models.CharField(choices=[('INACTIVE', 'INACTIVE'), ('ACTIVE', 'ACTIVE')], default='ACTIVE', max_length=8),
        ),
    ]
