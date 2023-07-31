# Generated by Django 3.2.13 on 2023-02-16 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management', '0005_auto_20230216_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='type',
            field=models.TextField(blank=True, choices=[('IL', 'Internal'), ('EL', 'External')], max_length=1000, null=True),
        ),
    ]
