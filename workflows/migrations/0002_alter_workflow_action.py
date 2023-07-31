# Generated by Django 3.2.13 on 2023-06-02 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflow',
            name='action',
            field=models.CharField(blank=True, choices=[('CREATION', 'CREATION'), ('UPDATION', 'UPDATION'), ('DELETION', 'DELETION')], max_length=10, null=True),
        ),
    ]
