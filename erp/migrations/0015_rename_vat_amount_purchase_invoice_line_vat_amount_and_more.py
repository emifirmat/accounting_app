# Generated by Django 5.0.6 on 2024-08-30 15:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0014_alter_purchase_invoice_issue_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchase_invoice_line',
            old_name='VAT_amount',
            new_name='vat_amount',
        ),
        migrations.RenameField(
            model_name='sale_invoice_line',
            old_name='VAT_amount',
            new_name='vat_amount',
        ),
    ]
