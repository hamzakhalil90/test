# Generated by Django 3.2.13 on 2023-06-09 10:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management', '0019_auto_20230602_0705'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='product', to='inventory_management.producttype'),
            preserve_default=False,
        ),
    ]
