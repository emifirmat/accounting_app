# Generated by Django 5.0.6 on 2024-07-14 11:11

import django.core.validators
import django.db.models.deletion
import erp.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0007_point_of_sell_disabled'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document_type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=1, unique=True, validators=[django.core.validators.RegexValidator(code='Invalid type', message='Enter only a letter', regex='[a-zA-Z]')])),
                ('code', models.CharField(max_length=2, unique=True, validators=[erp.validators.validate_is_digit])),
                ('hide', models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterField(
            model_name='purchase_invoice',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='erp.document_type'),
        ),
        migrations.AlterField(
            model_name='purchase_receipt',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='erp.document_type'),
        ),
        migrations.AlterField(
            model_name='sale_invoice',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='erp.document_type'),
        ),
        migrations.AlterField(
            model_name='sale_receipt',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='erp.document_type'),
        ),
    ]