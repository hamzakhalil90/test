# Generated by Django 3.2.13 on 2023-07-12 10:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifications_management', '0010_auto_20230712_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplate',
            name='notification_feature',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_feature_name', to='notifications_management.notificationfeatures'),
        ),
    ]
