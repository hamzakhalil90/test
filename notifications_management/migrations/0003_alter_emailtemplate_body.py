# Generated by Django 3.2.13 on 2023-02-16 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications_management', '0002_auto_20230216_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplate',
            name='body',
            field=models.TextField(),
        ),
    ]
