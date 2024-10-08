# Generated by Django 5.0.6 on 2024-07-19 12:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0009_document_type_type_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase_invoice',
            name='description',
        ),
        migrations.RemoveField(
            model_name='purchase_receipt',
            name='description',
        ),
        migrations.RemoveField(
            model_name='sale_invoice',
            name='VAT_amount',
        ),
        migrations.RemoveField(
            model_name='sale_invoice',
            name='description',
        ),
        migrations.RemoveField(
            model_name='sale_invoice',
            name='not_taxable_amount',
        ),
        migrations.RemoveField(
            model_name='sale_invoice',
            name='taxable_amount',
        ),
        migrations.RemoveField(
            model_name='sale_receipt',
            name='description',
        ),
        migrations.CreateModel(
            name='Purchase_invoice_line',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=280)),
                ('taxable_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('not_taxable_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('VAT_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('purchase_invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='p_invoice_lines', to='erp.purchase_invoice')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sale_invoice_line',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=280)),
                ('taxable_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('not_taxable_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('VAT_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('sale_invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='s_invoice_lines', to='erp.sale_invoice')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
