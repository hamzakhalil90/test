# Generated by Django 3.2.13 on 2023-02-16 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plant',
            old_name='sap_code',
            new_name='additional_information',
        ),
        migrations.AddField(
            model_name='plant',
            name='address',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='code',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='latitude',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='loading_unloading_info',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='longitude',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='manufacturing_capaity',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='operating_hours',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='pic_email',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='pic_name',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='pic_phone_number',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='product',
            field=models.ManyToManyField(related_name='plant_products', to='inventory_management.Product'),
        ),
        migrations.AddField(
            model_name='plant',
            name='sap_id',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='security_control_mechanism',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='storage_capacity',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plant',
            name='storage_types',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]