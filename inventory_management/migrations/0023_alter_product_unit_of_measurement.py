# Generated by Django 3.2.13 on 2023-06-23 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management', '0022_product_unit_of_measurement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='unit_of_measurement',
            field=models.CharField(choices=[('KG', 'KG'), ('MT', 'MT')], max_length=30),
        ),
    ]
