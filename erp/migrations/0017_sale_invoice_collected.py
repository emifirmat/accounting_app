# Generated by Django 5.0.6 on 2024-09-09 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0016_remove_purchase_receipt_unique_purchase_receipt_per_supplier_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale_invoice',
            name='collected',
            field=models.BooleanField(default=False),
        ),
    ]
