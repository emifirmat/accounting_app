# Generated by Django 5.0.6 on 2024-07-19 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0011_purchase_receipt_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase_invoice',
            name='VAT_amount',
        ),
        migrations.RemoveField(
            model_name='purchase_invoice',
            name='not_taxable_amount',
        ),
        migrations.RemoveField(
            model_name='purchase_invoice',
            name='taxable_amount',
        ),
    ]