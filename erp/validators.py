"""Validators file for erp app"""
from datetime import datetime
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
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

def validate_receipt_date_number_correlation(model, instance):    
    """Take the instance about to be save, check if there's a previous one and
    compare the correlation of their dates"""
    try:
        doc_number = int(instance.number)
    # If number is wrong, another validator will handle it
    except ValueError:
        return
    # Check that it's not the first invoice
    if doc_number >  1:
        # Pass string dates to datetime date type
        if type(instance.issue_date) == str:
            instance.issue_date = datetime.strptime(instance.issue_date, "%Y-%m-%d")
            instance.issue_date = datetime.date(instance.issue_date)
        try:
            previous_receipt = model.objects.get(
                point_of_sell = instance.point_of_sell,
                number = str(doc_number - 1).zfill(8)
            )
            if instance.issue_date < previous_receipt.issue_date:
                raise ValidationError("Issue date can't be older than previous receipt.") 
        # Case: The company decides to start adding invoices from a higer number
        except ObjectDoesNotExist:
            pass

def validate_receipt_total_amount(model, instance):
    """Check that total amount of receipt is equal o lower than total amount of
    invoice"""
    invoice_total = instance.related_invoice.total_lines_sum() or 0
    if instance.total_amount > invoice_total:
        raise ValidationError(
            f"Receipt total amount cannot be higher than invoice total amount."
        )

    """Check validator"""
    receipts = model.objects.filter(related_invoice=instance.related_invoice
        ).exclude(pk=instance.pk).aggregate(total=Sum("total_amount")
    )
    # Case: First receipt
    receipts_total = receipts["total"] or 0
  
    if (receipts_total + instance.total_amount) > invoice_total:
        raise ValidationError(
            f"The sum of your receipts cannot be higher than invoice total amount."
        )
