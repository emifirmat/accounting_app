"""Validators file for erp app"""
from django.core.exceptions import ValidationError


def validate_is_digit(value):
    """Check that the value is only digits"""
    if value.isdigit() == False:
        raise ValidationError(f"{value} must be only digits.")

def validate_file_extension(value):
    """Check file extension is xls or csv"""
    if not str(value).endswith((".xlsx", ".xls", ".csv")):
        raise ValidationError(f"{value} has the wrong extension.")
    