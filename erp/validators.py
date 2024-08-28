"""Validators file for erp app"""
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps


def validate_is_digit(value):
    """Check that the value is only digits"""
    if value.isdigit() == False:
        raise ValidationError(f"{value} must be only digits.")

def validate_file_extension(value):
    """Check file extension is xls or csv"""
    if not str(value).endswith((".xlsx", ".xls", ".csv")):
        raise ValidationError(f"{value} has the wrong extension.")

def validate_in_current_year(value):
    """Check that the inpt year is in the current financial year"""
    financial_year = apps.get_model("company", "FinancialYear")
    try:
        current_year = financial_year.objects.get(current=True)
    except ObjectDoesNotExist:
        raise ValidationError("First you have to set the current financial year.")
    
    if value.year != int(current_year.year):
        raise ValidationError("The selected date is not within the current year.")

