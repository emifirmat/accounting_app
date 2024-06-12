# Generated by Django 5.0.6 on 2024-05-30 11:35

import django.db.models.deletion
import erp.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tax_number', models.CharField(max_length=11, unique=True, validators=[erp.validators.validate_is_digit])),
                ('name', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=80)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=25, validators=[erp.validators.validate_is_digit])),
                ('creation_date', models.DateField()),
                ('closing_date', models.DateField()),
                ('financial_year', models.CharField(max_length=4, unique=True, validators=[erp.validators.validate_is_digit])),
            ],
            options={
                'verbose_name_plural': 'Company',
            },
        ),
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ending_date', models.DateTimeField(auto_now=True)),
                ('starting_date', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
            ],
            options={
                'verbose_name_plural': 'Calendar',
            },
        ),
    ]