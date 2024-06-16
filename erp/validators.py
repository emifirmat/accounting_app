"""Validators file for erp app"""
from django.core.exceptions import ValidationError


def validate_is_digit(value):
    """Check that the value is only digits"""
    if value.isdigit() == False:
        raise ValidationError(f"{value} must be only digits.")
    