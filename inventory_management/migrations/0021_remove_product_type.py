# Generated by Django 3.2.13 on 2023-06-13 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management', '0020_product_product_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='type',
        ),
    ]