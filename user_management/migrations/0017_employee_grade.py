# Generated by Django 3.2.13 on 2023-03-10 09:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0016_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='grade',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='grade', to='user_management.grade'),
        ),
    ]
