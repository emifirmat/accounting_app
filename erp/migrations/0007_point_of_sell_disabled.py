# Generated by Django 5.0.6 on 2024-07-10 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0006_rename_pos_numbe_point_of_sell_pos_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='point_of_sell',
            name='disabled',
            field=models.BooleanField(default=False),
        ),
    ]