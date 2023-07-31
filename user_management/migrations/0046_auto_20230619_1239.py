# Generated by Django 3.2.13 on 2023-06-19 12:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0045_autofill_weekdays'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinancialDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.CharField(choices=[('INACTIVE', 'INACTIVE'), ('ACTIVE', 'ACTIVE')], default='ACTIVE', max_length=8)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('OPEN', 'OPEN'), ('CLOSED', 'CLOSED'), ('PENDING', 'PENDING')], max_length=8)),
                ('is_locked', models.BooleanField(default=False)),
                ('period', models.CharField(choices=[('ANNUAL', 'ANNUAL'), ('BI-ANNUAL', 'BI-ANNUAL'), ('QUARTERLY', 'QUARTERLY'), ('MONTHLY', 'MONTHLY')], max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='company',
            name='address',
        ),
        migrations.RemoveField(
            model_name='company',
            name='financial_period_end_date',
        ),
        migrations.RemoveField(
            model_name='company',
            name='financial_period_start_date',
        ),
        migrations.CreateModel(
            name='FiscalPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.CharField(choices=[('INACTIVE', 'INACTIVE'), ('ACTIVE', 'ACTIVE')], default='ACTIVE', max_length=8)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('order', models.IntegerField()),
                ('is_locked', models.BooleanField(default=False)),
                ('fiscal_year', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='fiscal_period', to='user_management.financialdetails')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='financialdetails',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='financials', to='user_management.company'),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.CharField(choices=[('INACTIVE', 'INACTIVE'), ('ACTIVE', 'ACTIVE')], default='ACTIVE', max_length=8)),
                ('company_address', models.CharField(blank=True, max_length=50, null=True)),
                ('is_default', models.CharField(blank=True, max_length=50, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='addresses', to='user_management.company')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
