# Generated by Django 3.2.13 on 2023-02-28 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system_logs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlogs',
            name='object',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='auditlogs',
            name='operation',
            field=models.CharField(blank=True, choices=[('CREATED', 'CREATED'), ('UPDATED', 'UPDATED'), ('DELETED', 'DELETED')], max_length=10, null=True),
        ),
    ]
