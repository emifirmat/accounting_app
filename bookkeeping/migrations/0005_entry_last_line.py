# Generated by Django 5.0.6 on 2024-05-26 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookkeeping', '0004_chart_account_unique_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='last_line',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
