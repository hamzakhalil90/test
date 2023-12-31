# Generated by Django 3.2.13 on 2023-03-27 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0024_auto_20230327_0548'),
    ]

    operations = [
        migrations.RenameField(
            model_name='department',
            old_name='status',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='designation',
            old_name='status',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='status',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='features',
            old_name='status',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='grade',
            old_name='status',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='permissions',
            old_name='status',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='role',
            old_name='status',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='rolefeatureassociation',
            old_name='status',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='token',
            old_name='status',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='usergroup',
            old_name='status',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='userpasswordhistory',
            old_name='status',
            new_name='is_active',
        ),
        migrations.RemoveField(
            model_name='user',
            name='status',
        ),
        migrations.AddField(
            model_name='module',
            name='is_active',
            field=models.CharField(choices=[('INACTIVE', 'INACTIVE'), ('ACTIVE', 'ACTIVE')], default='ACTIVE', max_length=8),
        ),
    ]
