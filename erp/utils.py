"""Reutilizable functions for views.py in ERP app"""
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponseBadRequest



from company.models import Company
from .models import (SaleInvoice, SaleInvoiceLine, PaymentMethod, PaymentTerm,
    PointOfSell, DocumentType, CompanyClient, SaleReceipt)

def update_invoice_collected_status(invoice):
    """Check and update invoice's collected attribute"""
    receipts = SaleReceipt.objects.filter(related_invoice=invoice
    ).aggregate(total=Sum("total_amount")) 
    
    # If there's no instance
    receipt_total = receipts["total"] or 0

    if invoice.total_lines_sum() - receipt_total == 0:
        return True
    else:
        return False


def read_uploaded_file(file, date_column=None):
    """Read csv, xls or xlsx files"""
    if(file.name.endswith(".csv")):
        if date_column:
            # Pandas truncate cells in csv files and read them as string,
            # therefore I read them as date types.
            return pd.read_csv(file, parse_dates=[date_column], dayfirst=True)
        else:
            return pd.read_csv(file)
    else:
        return pd.read_excel(file)

def list_file_errors(error_type, row_index):
    """Catch and return all validation errors from a file row"""
    errors = []
    for field, messages in error_type.message_dict.items():
        if field == "__all__":
            field = "general"
        for message in messages:
            errors.append(f"Row {row_index + 2}, {field}: {message}") 
    return "\n".join(errors)

def check_column_len(df, length):
    """Control that the file has the expected number of columns"""
    if len(df.columns) != length:
        raise ValueError
    
def standarize_dataframe(df): 
    """Standarize columns' name and change NaN cells to blank"""
    df.columns = [column.lower().strip().replace(" ", "_") for column in df.columns]
    return df.where(pd.notnull(df), "")

def check_column_names(df, field_list):
    """Check that the name of each column matches the fields' name of the model"""
    for field in field_list:
        if field not in df.columns:
            raise ValueError
        
def get_model_fields_name(model, *exclude):
    """Get the names of the fields in a model"""
    model_fields_name = [field.name for field in model._meta.get_fields() 
        if not field.auto_created]
    if exclude:
        for value in exclude:
            model_fields_name.remove(value)
    return model_fields_name

def get_sale_invoice_objects(total_fields, total_fields_row, index,
    commercial_document=""):
    """Get all objects from fields that are related with other models"""
    
    get_object_from_subfield("point_of_sell", PointOfSell, total_fields,
        total_fields_row, index, "pos_number", value_function=lambda x: x.zfill(5))
    get_object_from_subfield("sender", Company, total_fields,
        total_fields_row, index, "tax_number")
    get_object_from_subfield("recipient", CompanyClient, total_fields,
        total_fields_row, index, "tax_number")    
    
    if commercial_document == "invoice":
        get_object_from_subfield("type", DocumentType, total_fields,
        total_fields_row, index, "code", value_function=lambda x: x.zfill(3))
        get_object_from_subfield("payment_method", PaymentMethod, total_fields,
        total_fields_row, index, "pay_method", 
        value_function=lambda x: x.capitalize())
        get_object_from_subfield("payment_term", PaymentTerm, total_fields,
        total_fields_row, index, "pay_term")
      
    elif commercial_document == "receipt":
        get_object_from_subfield("ri_type", DocumentType, total_fields,
        total_fields_row, index, "code", value_function=lambda x: x.zfill(3))
        get_object_from_subfield("ri_pos", PointOfSell, total_fields,
        total_fields_row, index, "pos_number", value_function=lambda x: x.zfill(5))
        
    return total_fields_row
    
    
def get_object_from_subfield(column, model, columns, row, index, subfield,
    value_function=None):
    """Get the object of a model using subfields and raise ValueError with details
    if it doesn't work."""
    try:
        column_index = columns.index(column)
        value = row[column_index]
        
        if value_function:
            value = value_function(value)
        # Create a dict to pass it dinamically as otherwise objects.get doesn't work.
        lookup_field = {f"{subfield}": value}
        row[column_index] = model.objects.get(**lookup_field)
        return row
    except ObjectDoesNotExist:
        error_message = (
            f"The input in row {index + 2} and column "
            f"{column} doesn't exist in the records."
        )
        raise ValueError(error_message)
    
def get_financial_calendar_dates(year_type, current_year):
    """
    Get both financial and calendar dates.
    Input: 
        - year_type: Determine if it is financial or calendar year.
        - current_year: Current financial year determined by the company.
    Returns:
        - Tuple of two dics: current year {start, end} and previous year {start, end}
    """
    closing_date = Company.objects.first().closing_date

    # Set date range
    if year_type == "financial":
        cur_start_date = date(
            current_year, closing_date.month, closing_date.day
        ) - relativedelta(years=1) + relativedelta(days=1)
        cur_end_date = date(
            current_year, closing_date.month, closing_date.day
        )
    else:
        cur_start_date = date(current_year, 1, 1)
        cur_end_date = date(current_year, 12, 31)

    prev_start_date = cur_start_date - relativedelta(years=1)
    prev_end_date = cur_end_date - relativedelta(years=1)

    current_year_dict = {"start": cur_start_date, "end": cur_end_date}
    previous_year_dict = {"start": prev_start_date, "end": prev_end_date}

    return (current_year_dict, previous_year_dict)