# Generated by Django 3.2.13 on 2023-05-18 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channel_management', '0012_auto_20230327_0647'),
    ]

    operations = [
        migrations.AddField(
            model_name='outlet',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='Images/'),
        ),
    ]
