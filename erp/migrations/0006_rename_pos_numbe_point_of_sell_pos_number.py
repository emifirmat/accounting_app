# Generated by Django 5.0.6 on 2024-07-09 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0005_rename_pos_number_point_of_sell_pos_numbe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='point_of_sell',
            old_name='pos_numbe',
            new_name='pos_number',
        ),
    ]
