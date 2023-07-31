# Generated by Django 3.2.13 on 2023-03-16 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0020_alter_usergroup_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default=1, max_length=50),
            preserve_default=False,
        ),
    ]
