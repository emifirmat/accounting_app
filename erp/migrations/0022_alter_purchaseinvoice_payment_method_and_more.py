# Generated by Django 5.1.3 on 2024-12-13 12:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0021_alter_purchaseinvoice_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseinvoice',
            name='payment_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='erp.paymentmethod'),
        ),
        migrations.AlterField(
            model_name='purchaseinvoice',
            name='payment_term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='erp.paymentterm'),
        ),
        migrations.AlterField(
            model_name='saleinvoice',
            name='payment_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='erp.paymentmethod'),
        ),
        migrations.AlterField(
            model_name='saleinvoice',
            name='payment_term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='erp.paymentterm'),
        ),
    ]
