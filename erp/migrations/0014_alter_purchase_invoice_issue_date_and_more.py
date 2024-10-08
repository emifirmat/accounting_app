# Generated by Django 5.0.6 on 2024-08-28 11:33

import erp.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0013_alter_company_client_tax_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase_invoice',
            name='issue_date',
            field=models.DateField(validators=[erp.validators.validate_in_current_year]),
        ),
        migrations.AlterField(
            model_name='purchase_receipt',
            name='issue_date',
            field=models.DateField(validators=[erp.validators.validate_in_current_year]),
        ),
        migrations.AlterField(
            model_name='sale_invoice',
            name='issue_date',
            field=models.DateField(validators=[erp.validators.validate_in_current_year]),
        ),
        migrations.AlterField(
            model_name='sale_receipt',
            name='issue_date',
            field=models.DateField(validators=[erp.validators.validate_in_current_year]),
        ),
    ]
