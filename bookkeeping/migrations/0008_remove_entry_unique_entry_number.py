# Generated by Django 5.0.6 on 2024-05-29 20:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookkeeping', '0007_entry_locked_entry_unique_entry_number'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='entry',
            name='unique_entry_number',
        ),
    ]
