# Generated by Django 3.2.13 on 2023-07-12 10:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications_management', '0009_auto_20230623_0652'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationFeatures',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.CharField(choices=[('INACTIVE', 'INACTIVE'), ('ACTIVE', 'ACTIVE')], default='ACTIVE', max_length=8)),
                ('name', models.TextField(max_length=50, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9 ]+$', message='Name field should not contain special characters')])),
            ],
        ),
        migrations.RemoveField(
            model_name='emailtemplate',
            name='recipient_group',
        ),
        migrations.RemoveField(
            model_name='emailtemplate',
            name='recipient_list',
        ),
        migrations.RemoveField(
            model_name='emailtemplate',
            name='recipient_roles',
        ),
        migrations.AddConstraint(
            model_name='notificationfeatures',
            constraint=models.UniqueConstraint(condition=models.Q(('is_deleted', 'f')), fields=('name', 'is_deleted'), name='unique_notification_feature'),
        ),
    ]
