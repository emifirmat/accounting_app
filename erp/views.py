import csv, os
import pandas as pd
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.conf import settings
from django.db import transaction, IntegrityError
from django.db.models import Sum, F
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse



from company.models import FinancialYear, PersonModel
from .forms import (CclientForm, SupplierForm, PaymentMethodForm, PaymentTermForm, 
    PointOfSellForm, SaleInvoiceForm, SaleInvoiceLineFormSet, SearchInvoiceForm,
    AddPersonFileForm, AddSaleInvoicesFileForm, SearchByYearForm, SearchByDateForm,
    SaleReceiptForm, SearchReceiptForm, AddSaleReceiptsFileForm)
from .models import (Company, Company_client, Supplier, Payment_method, 
    Payment_term, Point_of_sell, Document_type, Sale_invoice, Sale_invoice_line,
    Sale_receipt)
from .utils import (read_uploaded_file, check_column_len, standarize_dataframe,
check_column_names, list_file_errors, get_model_fields_name, get_sale_invoice_objects,
update_invoice_collected_status)


# Create your views here.
def current_year():
    """Define current financial year"""
    try:
        financial_year = FinancialYear.objects.get(current=True)
    except ObjectDoesNotExist:
        financial_year = None
    return financial_year

def client_index(request):
    """Client's overview page"""
    financial_year = current_year()
    clients = Company_client.objects.all()
    return render(request, "erp/client_index.html", {
        "financial_year": financial_year,
        "clients": clients,
    })


def person_new(request, person_type):
    """Add a new client/supplier page"""
    # File form post work in a dif view, so it can be always new in this view
    file_form = AddPersonFileForm()
    if request.method == "POST":
        if person_type == "client":
            form = CclientForm(request.POST)
        elif person_type == "supplier":
            form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(f"erp:{person_type}_index"))
    else:
        if person_type == "client":
            form = CclientForm()
        elif person_type == "supplier":
            form = SupplierForm()

    return render(request, "erp/person_new.html", {
        "form": form,
        "file_form": file_form,
        "person_type": person_type,
    })


def person_new_multiple(request, person_type):
    """Add multiple clients/suppliers"""
    if request.method == "POST":
        file_form = AddPersonFileForm(request.POST, request.FILES)
        
        if file_form.is_valid():
            file = request.FILES["file"]
            
            # Read file according to the extension    
            df = read_uploaded_file(file)
            
            # Check all columns exist and Standarize columns names and blanks
            check_column_len(df, 5)
            df = standarize_dataframe(df)
            person_fields = get_model_fields_name(PersonModel)
            check_column_names(df, person_fields)

            # Pass all values in model
            try:
                with transaction.atomic():
                    for index, row in df.iterrows():
                        # Convert number fields into string to allow me using
                        # validators
                        person_fields_row = list(map(str, row[person_fields]))

                        if person_type == "client":
                            person_model = Company_client
                        elif person_type == "supplier":
                            person_model = Supplier
                        new_person = person_model(
                            tax_number = person_fields_row[0],
                            name = person_fields_row[1],
                            address = person_fields_row[2],    
                            email = person_fields_row[3],
                            phone = person_fields_row[4],
                        )
                        
                        # Execute validators before saving, and show error if exists,
                        try:
                            new_person.full_clean()
                            new_person.save()
                        except ValidationError as ve:
                            # Value error is raised for atomic transaction
                            raise ValueError(list_file_errors(ve, index))
            except ValueError as ve:
                return HttpResponseBadRequest(str(ve))

            # If everything is correct
            return HttpResponseRedirect(reverse(f"erp:{person_type}_index"))
        else:
            return HttpResponseBadRequest("Invalid file.")
    else:
        return HttpResponseRedirect(reverse(f"erp:person_new", 
            kwargs={"person_type": person_type}))


def person_edit(request, person_type):
    """Search and edit an existing client or supplier"""
    if request.method == "GET":
        if person_type == "client":
            person_list = Company_client.objects.all()
            form = CclientForm()
        elif person_type == "supplier":
            person_list = Supplier.objects.all()
            form = SupplierForm()
        
        return render(request, "erp/person_edit.html", {
            "person_list": person_list,
            "form": form,
            "person_type": person_type,
        })


def person_delete(request, person_type):
    """Search and delete an existing client or supplier"""
    if person_type == "client":
        person_list = Company_client.objects.all()
        form = CclientForm()
    elif person_type == "supplier":
        person_list = Supplier.objects.all()
        form = SupplierForm()
    
    return render(request, "erp/person_delete.html", {
        "person_list": person_list,
        "form": form,
        "person_type": person_type,
    })


def supplier_index(request):
    """Supplier's overview page"""
    financial_year = current_year()
    suppliers = Supplier.objects.all()
    return render(request, "erp/supplier_index.html", {
        "financial_year": financial_year,
        "suppliers": suppliers,
    })


def payment_conditions(request):
    """Payment conditions webpage"""
    payment_methods = Payment_method.objects.all()
    payment_terms = Payment_term.objects.all()
    term_form = PaymentTermForm()
    method_form = PaymentMethodForm()
    return render(request, "company/payment_conditions.html", {
        "payment_methods": payment_methods,
        "payment_terms": payment_terms,
        "term_form": term_form,
        "method_form": method_form,
    })


def point_of_sell(request):
    """POS webpage"""
    form = PointOfSellForm()
    pos_list = Point_of_sell.objects.filter(disabled=False)
    
    return render(request, "company/points_of_sell.html", {
        "form": form,
        "pos_list": pos_list,
    })


def doc_types(request):
    """Customize available doc types webpage"""
    if not Document_type.objects.exists():
        # Add all types
        load_doc_types()
    return render(request, "company/doc_types.html")


def load_doc_types():
    """Import all doc types according to Argentinian regulations"""
    file_path = os.path.join(settings.STATICFILES_DIRS[0], "data", "doc_types.csv")
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            # Load all data or none
            with transaction.atomic():
                # Remove bom
                first_char = file.read(1)
                if first_char != '\ufeff':
                    first_char = file.seek(0)
                
                # Read file
                reader = csv.DictReader(file)
                for row in reader:
                    Document_type.objects.create(
                        code = row['code'],
                        type = row['initials'],
                        type_description = row['description'],
                    )
    except FileNotFoundError:
        print(f"Couldn't load file")


def sales_index(request):
    """Sales overview webpage"""
    financial_year = current_year()
    sale_invoices = Sale_invoice.objects.all()
    return render(request, "erp/sales_index.html", {
        "financial_year": financial_year,
        "sale_invoices": sale_invoices,
    })

def sales_new(request):
    """New sale invoices webpage"""
    if request.method == "POST":
        invoice_form = SaleInvoiceForm(request.POST)
        line_formset = SaleInvoiceLineFormSet(request.POST)
        if invoice_form.is_valid() and line_formset.is_valid():
            with transaction.atomic():
                sale_invoice = invoice_form.save()
                sale_lines = line_formset.save(commit=False)
                for sale_line in sale_lines:
                    sale_line.sale_invoice = sale_invoice
                    sale_line.save() 
                return HttpResponseRedirect(reverse("erp:sales_invoice", 
                    args=[sale_invoice.id]
                ))

    elif request.method == "GET":
        invoice_form = SaleInvoiceForm()
        line_formset = SaleInvoiceLineFormSet()

    return render(request, "erp/sales_new.html", {
        "invoice_form": invoice_form,
        "line_formset": line_formset,
    })

def sales_new_massive(request):
    """New massive sale invoices webpage"""
    if request.method == "POST":
        document_file_form = AddSaleInvoicesFileForm(request.POST, request.FILES)
        if document_file_form.is_valid():
            file = request.FILES["file"]
                      
            # Read file according to the extension
            df = read_uploaded_file(file, "issue_date")
           
            # Check all columns exist   
            check_column_len(df, 12)
             # Standarize and check all columns have the right name
            df = standarize_dataframe(df)
            document_fields = get_model_fields_name(Sale_invoice, "collected")
            line_fields = get_model_fields_name(Sale_invoice_line, "total_amount",
                "sale_invoice"
            )
            total_fields = document_fields + line_fields
            check_column_names(df, total_fields)
     
            # Pass all values in model
            try:
                with transaction.atomic():
                    last_invoice = None
                    for index, row in df.iterrows():
                        # Convert all fields into string to allow me using
                        # validators.
                        total_fields_row = list(map(str, row[total_fields]))
                        date_index = total_fields.index("issue_date")
                        type_index = total_fields.index("type")
                        pos_index = total_fields.index("point_of_sell")
                        number_index = total_fields.index("number")
                        sender_index = total_fields.index("sender")
                        recipient_index = total_fields.index("recipient")
                        pay_method_index = total_fields.index("payment_method")
                        pay_term_index = total_fields.index("payment_term")



                        if last_invoice:
                            current_invoice = (
                                f"{total_fields_row[type_index].zfill(3)}"
                                f"{total_fields_row[pos_index].zfill(5)}"
                                f"{total_fields_row[number_index].zfill(8)}"
                            )
                        
                        # Get objects from related fields                
                        total_fields_row = get_sale_invoice_objects(
                            total_fields, total_fields_row, index, "invoice")
                        
                        # Control if it's new invoice or line
                        if index == 0 or last_invoice_id != current_invoice:
                            new_invoice = Sale_invoice(
                                issue_date = total_fields_row[date_index][0:10],
                                type = total_fields_row[type_index],
                                point_of_sell = total_fields_row[pos_index],
                                number = total_fields_row[number_index],
                                sender = total_fields_row[sender_index],
                                recipient = total_fields_row[recipient_index],
                                payment_method = total_fields_row[pay_method_index],
                                payment_term = total_fields_row[pay_term_index]
                            )
                            
                            # Execute validators before saving, and show error if exists,
                            try:
                                new_invoice.full_clean()
                                new_invoice.save()
                                # Save invoice data for next row
                                last_invoice = new_invoice
                                last_invoice_id = (
                                    f"{new_invoice.type.code}"
                                    f"{new_invoice.point_of_sell.pos_number}"
                                    f"{new_invoice.number}"
                                )
                            except ValidationError as ve:
                                raise ValueError(list_file_errors(ve, index))
                            except IntegrityError:
                                raise ValueError(
                                    f"Invoice {new_invoice.type.type} "
                                    f"{new_invoice.point_of_sell.pos_number}-"
                                    f"{new_invoice.number} already exists or "
                                    f"repeated in file."
                                )
                        # Control that invoice's info for new line is consistent
                        else:                        
                            if (
                            str(last_invoice.issue_date) != total_fields_row[date_index][0:10] or    
                            last_invoice.recipient != total_fields_row[recipient_index] or
                            last_invoice.payment_method != total_fields_row[pay_method_index] or
                            last_invoice.payment_term != total_fields_row[pay_term_index]):
                                raise ValueError(
                                    f"Row {index + 2}: Your invoice's information"
                                    f" doesn't match with row {index + 1}."
                                )

                        # Add invoice line form
                        new_line = Sale_invoice_line(
                            sale_invoice = new_invoice,
                            description = total_fields_row[
                                total_fields.index("description")],
                            taxable_amount = total_fields_row[
                                total_fields.index("taxable_amount")],
                            not_taxable_amount = total_fields_row[
                                total_fields.index("not_taxable_amount")],
                            vat_amount = total_fields_row[
                                total_fields.index("vat_amount")],
                            # Total amount is added to don't raise validation error
                            # in full_clean(), then it's updated in saving.
                            total_amount = "0",
                        )
                        try:
                            new_line.full_clean()
                            new_line.save()
                        except ValidationError as ve:
                            raise ValueError(list_file_errors(ve, index))
            except ValueError as e:
                 return HttpResponseBadRequest(str(e))   
                    
            # If everything is correct
            return HttpResponseRedirect(reverse(f"erp:sales_index"))
        else:
            return HttpResponseBadRequest("Invalid file.")
    # Get method
    else:
        document_file_form = AddSaleInvoicesFileForm()
        return render(request, "erp/sales_new_massive.html", {
            "document_file_form": document_file_form,
            "com_document": "invoice",
        })


def sales_invoice(request, inv_pk):
    """Specific invoice webpage"""
    invoice = Sale_invoice.objects.get(pk=inv_pk)

    return render(request, "erp/sales_invoice.html", {
        "invoice": invoice,
    })


def sales_search(request):
    """Search, and edit or delete invoices webpage"""
    form = SearchInvoiceForm()
    return render(request, "erp/document_search.html", {
        "com_document": "invoice",
        "form": form,
    })

def sales_edit(request, inv_pk):
    """Edit Specific invoice webpage"""
    invoice = Sale_invoice.objects.get(id=inv_pk)

    if request.method == "POST":
        invoice_form = SaleInvoiceForm(instance=invoice, data=request.POST)
        line_formset = SaleInvoiceLineFormSet(instance=invoice, data=request.POST)

        if invoice_form.is_valid() and line_formset.is_valid():
            with transaction.atomic():
                invoice_form.save()
                line_formset.save()

            return HttpResponseRedirect(reverse("erp:sales_invoice", 
                args=[invoice.id]
            ))

    else:
        invoice_form = SaleInvoiceForm(instance=invoice)
        line_formset = SaleInvoiceLineFormSet(instance=invoice)

    return render(request, "erp/sales_edit.html", {
        "invoice": invoice,
        "invoice_form": invoice_form,
        "line_formset": line_formset,
    })

def sales_list(request):
    """Show a list of invoices in a specific range webpage"""
    # Get list general case, it gets overwritten if it changes
    try:
        financial_year = FinancialYear.objects.get(current=True)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("company:year"))
    
    if request.method == "POST":
        # Search between dates
        if request.POST["form_type"] == "date":
            form_year = SearchByYearForm()
            form_date = SearchByDateForm(request.POST)
            if form_date.is_valid():
                date_from = form_date.cleaned_data["date_from"]
                date_to = form_date.cleaned_data["date_to"]
                # Add input control
                if date_from > date_to:
                    form_date.add_error(
                        "date_from", "'From' should be older than 'To'."
                    )
                invoice_list = Sale_invoice.objects.filter(
                        issue_date__range=(date_from, date_to)
                    )
        # Search by year
        elif request.POST["form_type"] == "year":
            form_year = SearchByYearForm(request.POST)
            form_date = SearchByDateForm()
            if form_year.is_valid():
                try:
                    input_year=form_year.cleaned_data["year"]
                    financial_year = FinancialYear.objects.get(year=input_year)
                except ObjectDoesNotExist:
                    form_year.add_error(
                        "year", f"The year {input_year} doesn't exist in the records."
                    )
                    financial_year = FinancialYear.objects.get(current=True)
                invoice_list = Sale_invoice.objects.filter(issue_date__year=financial_year.year)
    else:
        form_date = SearchByDateForm()
        form_year = SearchByYearForm()
        invoice_list = Sale_invoice.objects.filter(issue_date__year=financial_year.year)

    return render(request, "erp/sales_list.html", {
        "com_document": "invoice",
        "invoice_list": invoice_list,
        "form_date": form_date,
        "form_year": form_year, 
    })

def receivables_index(request):
    """Overview of receivables webpage"""
    financial_year = current_year()
    receipt_list = Sale_receipt.objects.all()
    return render(request, "erp/receivables_index.html", {
        "receipt_list": receipt_list,
        "financial_year": financial_year,
    })

def receivables_new(request):
    """Create new receipt webpage"""
    if request.method == "POST":
        receipt_form = SaleReceiptForm(request.POST)
        if receipt_form.is_valid():
            receipt = receipt_form.save()
            
            # Check and update invoice's collected attribute
            invoice = receipt.related_invoice
            invoice.collected = update_invoice_collected_status(invoice)
            invoice.save()

            return HttpResponseRedirect(reverse("erp:receivables_receipt", 
                args=[receipt.id]))
    else:
        receipt_form = SaleReceiptForm()
    
    return render(request, "erp/receivables_new.html", {
        "receipt_form": receipt_form,
    })

def receivables_new_massive(request):
    """New massive sale receipt webpage"""
    if request.method == "POST":
        document_file_form = AddSaleInvoicesFileForm(request.POST, request.FILES)
        if document_file_form.is_valid():
            file = request.FILES["file"]
                      
            # Read file according to the extension
            df = read_uploaded_file(file, "issue_date")
           
            # Check all columns exist   
            check_column_len(df, 10)
            # Standarize and check all columns have the right name
            df = standarize_dataframe(df)
            document_fields = get_model_fields_name(Sale_receipt, "related_invoice")
            for field in ["ri_type", "ri_pos", "ri_number"]:
                document_fields.append(field)

            check_column_names(df, document_fields)
     
            # Pass all values in model
            try:
                with transaction.atomic():
                    for index, row in df.iterrows():
                        # Convert all fields into string to allow me using
                        # validators.
                        total_fields_row = list(map(str, row[document_fields]))
                        
                        # Get objects from related fields                
                        total_fields_row = get_sale_invoice_objects(
                            document_fields, total_fields_row, index, "receipt")
                        
                        # Get related invoice
                        try:
                            related_invoice_field = Sale_invoice.objects.get(
                                type=total_fields_row[7], 
                                point_of_sell=total_fields_row[8],
                                number=total_fields_row[9].zfill(8)
                            )
                        except ObjectDoesNotExist:
                            error_message = (
                                f"The related invoice in row {index + 2} "
                                f"doesn't exist in the records."
                            )
                            raise ValueError(error_message)

                        # Control if it's new invoice or line
                        try:
                            new_receipt = Sale_receipt(
                                issue_date = total_fields_row[
                                    document_fields.index("issue_date")][0:10],
                                point_of_sell = total_fields_row[
                                    document_fields.index("point_of_sell")],
                                number = total_fields_row[
                                    document_fields.index("number")],
                                sender = total_fields_row[
                                    document_fields.index("sender")],
                                recipient = total_fields_row[
                                    document_fields.index("recipient")],
                                description = total_fields_row[
                                    document_fields.index("description")],
                                total_amount = total_fields_row[
                                    document_fields.index("total_amount")],
                                related_invoice = related_invoice_field
                            )
                            # Execute validators before saving, and show error if exists,
                            new_receipt.full_clean()
                            new_receipt.save()      
                        except ValidationError as ve:
                            raise ValueError(list_file_errors(ve, index))
                        except IntegrityError:
                            raise ValueError(
                                f"Receipt {new_receipt.point_of_sell.pos_number}-"
                                f"{new_receipt.number} already exists or "
                                f"repeated in file."
                            )
                        # Update invoice collected status
                        else:
                            invoice = new_receipt.related_invoice
                            invoice.collected = update_invoice_collected_status(
                                invoice)
                            invoice.save()
                        
            except ValueError as e:
                 return HttpResponseBadRequest(str(e))   
                    
            # If everything is correct
            return HttpResponseRedirect(reverse(f"erp:receivables_index"))
        else:
            return HttpResponseBadRequest("Invalid file.")
    # Get method
    else:
        document_file_form = AddSaleReceiptsFileForm()
        return render(request, "erp/receivables_new_massive.html", {
            "document_file_form": document_file_form,
            "com_document": "receipt",
        })


def receivables_receipt(request, rec_pk):
    """Specific receipt webpage"""
    receipt = Sale_receipt.objects.get(pk=rec_pk)
    return render(request, "erp/receivables_receipt.html", {
        "receipt": receipt,
    })

def receivables_edit(request, rec_pk):
    """Edit Specific receipt webpage"""
    receipt = Sale_receipt.objects.get(id=rec_pk)

    if request.method == "POST":
        receipt_form = SaleReceiptForm(instance=receipt, data=request.POST)
        # keep old ri before updating instance
        old_r_invoice = receipt.related_invoice

        if receipt_form.is_valid():
            receipt_edited = receipt_form.save()
            invoice = receipt_edited.related_invoice

            # If related invoice was modified, I have to update old invoice first.
            if old_r_invoice != invoice:
                old_r_invoice.collected = update_invoice_collected_status(
                    old_r_invoice)
                old_r_invoice.save()

            # Check and update invoice's collected attribute
            invoice.collected = update_invoice_collected_status(invoice)
            invoice.save()     

            return HttpResponseRedirect(reverse("erp:receivables_receipt", 
                args=[receipt.pk]
            ))

    else:
        receipt_form = SaleReceiptForm(instance=receipt)
        
    return render(request, "erp/receivables_edit.html", {
        "receipt": receipt,
        "receipt_form": receipt_form,
    })


def receivables_search(request):
    """Search and edit or delete receipt webpage"""
    form = SearchReceiptForm()
    return render(request, "erp/document_search.html", {
        "com_document": "receipt",
        "form": form,
    })


def receivables_list(request):
    """Show a list of receipts in a specific range webpage"""
    # Get list general case, it gets overwritten if it changes
    financial_year = current_year()
    if not financial_year:
        return HttpResponseRedirect(reverse("company:year"))
    
    if request.method == "POST":
        # Search between dates
        if request.POST["form_type"] == "date":
            form_year = SearchByYearForm()
            form_date = SearchByDateForm(request.POST)
            if form_date.is_valid():
                date_from = form_date.cleaned_data["date_from"]
                date_to = form_date.cleaned_data["date_to"]
                # Add input control
                if date_from > date_to:
                    form_date.add_error(
                        "date_from", "'From' should be older than 'To'."
                    )
                receipt_list = Sale_receipt.objects.filter(
                        issue_date__range=(date_from, date_to)
                    )
        # Search by year
        elif request.POST["form_type"] == "year":
            form_year = SearchByYearForm(request.POST)
            form_date = SearchByDateForm()
            if form_year.is_valid():
                try:
                    input_year=form_year.cleaned_data["year"]
                    financial_year = FinancialYear.objects.get(year=input_year)
                except ObjectDoesNotExist:
                    form_year.add_error(
                        "year", f"The year {input_year} doesn't exist in the records."
                    )
                    # Go back to current year in search
                    financial_year = FinancialYear.objects.get(current=True)
                receipt_list = Sale_receipt.objects.filter(issue_date__year=financial_year.year)
    else:
        form_date = SearchByDateForm()
        form_year = SearchByYearForm()
        receipt_list = Sale_receipt.objects.filter(issue_date__year=financial_year.year)

    return render(request, "erp/receivables_list.html", {
        "com_document": "receipt",
        "receipt_list": receipt_list,
        "form_date": form_date,
        "form_year": form_year, 
    })