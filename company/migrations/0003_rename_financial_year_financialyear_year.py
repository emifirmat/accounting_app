# Generated by Django 5.0.6 on 2024-06-02 00:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_financialyear_remove_company_financial_year'),
    ]

    operations = [
        migrations.RenameField(
            model_name='financialyear',
            old_name='financial_year',
            new_name='year',
        ),
    ]
