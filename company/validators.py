"""Validators file for company app"""
from datetime import datetime
from django.core.exceptions import ValidationError
# Use apps to get models avoiding circular imports
from django.apps import apps


def validate_valid_year(value):
    """Check that the year is not older that creation date"""
    company = apps.get_model("company", "Company")
    creation_date = company.objects.first().creation_date
    creation_year = creation_date.year

    if int(value) < creation_year :
        raise ValidationError(f"""The year {value} is older than {creation_year}. 
            If you need to add the year {value}, please modify the company's creation
            date.""")