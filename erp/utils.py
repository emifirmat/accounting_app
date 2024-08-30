"""Reutilizable functions for views.py in ERP app"""
import pandas as pd
from django.http import HttpResponseBadRequest

from .models import Sale_invoice, Sale_invoice_line

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