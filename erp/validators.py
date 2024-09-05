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
    if not value.name.endswith((".xlsx", ".xls", ".csv")):
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
    
def validate_invoices_date_number_correlation(model, instance):    
    """Take the instance about to be save, check if there's a previous one and
    compare the correlation of their dates"""
    try:
        doc_number = int(instance.number)
    # If number is wrong, another validator will handle it
    except ValueError:
        return
    # Check that it's not the first invoice
    if doc_number >  1:
        try:
            previous_invoice = model.objects.get(
                type = instance.type,
                point_of_sell = instance.point_of_sell,
                number = str(doc_number - 1).zfill(8)
            )
            if instance.issue_date < previous_invoice.issue_date:
                raise ValidationError("Issue date can't be older than previous invoice.") 
        # Case: The company decides to start adding invoices from a higer number
        except ObjectDoesNotExist:
            pass


