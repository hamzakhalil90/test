# Generated by Django 3.2.13 on 2023-03-01 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management', '0013_auto_20230224_0604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouse',
            name='items_capacity',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]