"""Reutilizable functions for views.py in ERP app"""
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponseBadRequest


from company.models import Company
from .models import (Sale_invoice, Sale_invoice_line, Payment_method, Payment_term,
    Point_of_sell, Document_type, Company_client, Sale_receipt)

def update_invoice_collected_status(invoice):
    """Check and update invoice's collected attribute"""
    receipts = Sale_receipt.objects.filter(related_invoice=invoice
    ).aggregate(total=Sum("total_amount")) 

    if invoice.total_lines_sum() - receipts["total"] == 0:
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
    else :
        return pd.read_excel(file)

def list_file_errors(error_type, row_index):
    """Catch and return all validation errors from a file row"""
    errors = []
    for field, messages in error_type.message_dict.items():
        for message in messages:
            errors.append(f"Row {row_index + 2}, {field}: {message}") 
    return f"{"\n".join(errors)}"

def check_column_len(df, length):
    """Control that the file has the expected number of columns"""
    if len(df.columns) != length:
        return HttpResponseBadRequest(f"The number of columns must be {length}")
    
def standarize_dataframe(df): 
    """Standarize columns' name and change NaN cells to blank"""
    df.columns = [column.lower().strip().replace(" ", "_") for column in df.columns]
    return df.where(pd.notnull(df), "")

def check_column_names(df, field_list):
    """Check that the name of each column matches the fields' name of the model"""
    for field in field_list:
        if field not in df.columns:
            return HttpResponseBadRequest(f"Column {field} not found.")
        
def get_model_fields_name(model, *exclude):
    """Get the names of the fields in a model"""
    model_fields_name = [field.name for field in model._meta.get_fields() 
        if not field.auto_created]
    if exclude:
        for value in exclude:
            model_fields_name.remove(value)
    return model_fields_name

def get_sale_invoice_objects(total_fields_row, index):
    """Get all objects from fields that are related with other models"""
    try:
        message_field = "type"
        total_fields_row[2] = Document_type.objects.get(
                code=total_fields_row[2].zfill(3)
            )
        message_field = "point_of_sell"
        total_fields_row[3] = Point_of_sell.objects.get(
                pos_number=total_fields_row[3].zfill(5)
            )  
        message_field = "sender"
        total_fields_row[4] = Company.objects.get(
                tax_number=total_fields_row[4]
            )
        message_field = "recipient"
        total_fields_row[5] = Company_client.objects.get(
                tax_number=total_fields_row[5]
            )
        message_field = "payment_method"
        total_fields_row[6] = Payment_method.objects.get(
                pay_method=total_fields_row[6].capitalize()
            )
        message_field = "payment_term"
        total_fields_row[7] = Payment_term.objects.get(
                pay_term=total_fields_row[7]
            )
        return total_fields_row
    except ObjectDoesNotExist:
        error_message = (
            f"The input in row {index + 2} and column "
            f"{message_field} doesn't exist in the records."
        )
        raise ValueError(error_message)
    