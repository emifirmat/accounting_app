# Generated by Django 5.0.6 on 2024-06-01 23:57

import erp.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinancialYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('financial_year', models.CharField(max_length=4, unique=True, validators=[erp.validators.validate_is_digit])),
            ],
        ),
        migrations.RemoveField(
            model_name='company',
            name='financial_year',
        ),
    ]
