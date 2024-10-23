# Generated by Django 5.0.6 on 2024-10-11 21:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0009_alter_financialyear_options'),
        ('erp', '0018_alter_purchase_invoice_options_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Client_current_account',
            new_name='ClientCurrentAccount',
        ),
        migrations.RenameModel(
            old_name='Company_client',
            new_name='CompanyClient',
        ),
        migrations.RenameModel(
            old_name='Document_type',
            new_name='DocumentType',
        ),
        migrations.RenameModel(
            old_name='Payment_method',
            new_name='PaymentMethod',
        ),
        migrations.RenameModel(
            old_name='Payment_term',
            new_name='PaymentTerm',
        ),
        migrations.RenameModel(
            old_name='Point_of_sell',
            new_name='PointOfSell',
        ),
        migrations.RenameModel(
            old_name='Purchase_invoice',
            new_name='PurchaseInvoice',
        ),
        migrations.RenameModel(
            old_name='Purchase_invoice_line',
            new_name='PurchaseInvoiceLine',
        ),
        migrations.RenameModel(
            old_name='Purchase_receipt',
            new_name='PurchaseReceipt',
        ),
        migrations.RenameModel(
            old_name='Sale_invoice',
            new_name='SaleInvoice',
        ),
        migrations.RenameModel(
            old_name='Sale_invoice_line',
            new_name='SaleInvoiceLine',
        ),
        migrations.RenameModel(
            old_name='Sale_receipt',
            new_name='SaleReceipt',
        ),
        migrations.RenameModel(
            old_name='Supplier_current_account',
            new_name='SupplierCurrentAccount',
        ),
    ]