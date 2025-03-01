import csv, os
import pandas as pd
from datetime import datetime
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.conf import settings
from django.db import transaction, IntegrityError
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from pathlib import Path



from company.models import FinancialYear, PersonModel
from .forms import (CclientForm, SupplierForm, PaymentMethodForm, PaymentTermForm, 
    PointOfSellForm, SaleInvoiceForm, SaleInvoiceLineFormSet, SearchInvoiceForm,
    AddPersonFileForm, AddSaleInvoicesFileForm, SearchByYearForm, SearchByDateForm,
    SaleReceiptForm, SearchReceiptForm, AddSaleReceiptsFileForm, cutOffDateForm)
from .models import (Company, CompanyClient, Supplier, PaymentMethod, 
    PaymentTerm, PointOfSell, DocumentType, SaleInvoice, SaleInvoiceLine,
    SaleReceipt, PurchaseInvoice, PurchaseReceipt, ClientCurrentAccount)
from .utils import (read_uploaded_file, check_column_len, standarize_dataframe,
check_column_names, list_file_errors, get_model_fields_name, get_sale_invoice_objects,
update_invoice_collected_status)


# Create your views here.

def client_index(request):
    """Client's overview page"""
    financial_year = FinancialYear.objects.filter(current=True).first()
    clients = CompanyClient.objects.all()
    
    return render(request, "erp/client_index.html", {
        "financial_year": financial_year,
        "clients": clients,
    })


def person_new(request, person_type):
    """Add a new client/supplier page"""
    # File form post works in a dif view, so it is not filled in this view
    file_form = AddPersonFileForm()
    if person_type == "client":
        form = CclientForm
    else:
        form = SupplierForm

    if request.method == "POST":
        person_form = form(request.POST)
        if person_form.is_valid():
            person_form.save()
            return HttpResponseRedirect(reverse(f"erp:{person_type}_index"))
    else:
        person_form = form()

    return render(request, "erp/person_new.html", {
        "form": person_form,
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
            try: 
                check_column_len(df, 5)
                df = standarize_dataframe(df)
                person_fields = get_model_fields_name(PersonModel)
                check_column_names(df, person_fields)
            except ValueError:
                return HttpResponseBadRequest(
                    f"The columns in your file don't match the required format."
                )
            

            # Pass all values in model
            try:
                with transaction.atomic():
                    for index, row in df.iterrows():
                        # Convert number fields into string to allow me using
                        # validators
                        person_fields_row = list(map(str, row[person_fields]))

                        if person_type == "client":
                            person_model = CompanyClient
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
            model = CompanyClient
            form = CclientForm
        elif person_type == "supplier":
            model = Supplier
            form = SupplierForm

        person_list = model.objects.all()
        person_form = form()   
        
        return render(request, "erp/person_edit.html", {
            "person_list": person_list,
            "form": person_form,
            "person_type": person_type,
        })


def person_delete(request, person_type):
    """Search and delete an existing client or supplier"""
    if person_type == "client":
        model = CompanyClient
        form = CclientForm
    elif person_type == "supplier":
        model = Supplier
        form = SupplierForm

    person_list = model.objects.all()
    person_form = form()
    
    return render(request, "erp/person_delete.html", {
        "person_list": person_list,
        "form": person_form,
        "person_type": person_type,
    })

def person_related_docs(request, person_type, person_pk):
    """ Show related invoices and receipts of a client or supplier webpage."""
    
    if person_type == "client":
        person_model = CompanyClient
        inv_model = SaleInvoice
        rec_model = SaleReceipt
    else:
        person_model = Supplier
        inv_model = PurchaseInvoice
        rec_model = PurchaseReceipt

    person = person_model.objects.get(pk=person_pk)
    invoice_list = inv_model.objects.filter(recipient=person)
    receipt_list = rec_model.objects.filter(recipient=person)

    return render(request, "erp/person_related_docs.html", {
        "person_type": person_type,
        "person": person,
        "invoice_list": invoice_list,
        "receipt_list": receipt_list,
    })

def person_current_account(request, person_type):
    """Clients/Supplier's current account"""
    financial_year = FinancialYear.objects.filter(current=True).first()
    cur_year = int(financial_year.year)
    prev_year = int(financial_year.year) - 1

    if request.method == "POST":
        form_cutoff = cutOffDateForm(request.POST)
        if form_cutoff.is_valid():
            day = form_cutoff.cleaned_data["day"]
            month = form_cutoff.cleaned_data["month"]
            
            # Check day and month are correct and add default date otherwise
            try:
                datetime(cur_year, month, day)
            except ValueError:
                form_cutoff.add_error(
                    "day", "The date is invalid."
                )
                day = 31
                month = 12

            clients_current_ca = ClientCurrentAccount.objects.filter(
                    date__lte=datetime(cur_year, month, day)
            ).values("client", "client__name", 'client__tax_number').annotate(
                global_balance=Coalesce(Sum("amount"), Decimal(0))
            ).order_by("-date")
        
            clients_prev_ca = ClientCurrentAccount.objects.filter(
                    date__lte=datetime(prev_year, month, day)
            ).values("client", "client__name", 'client__tax_number').annotate(
                global_balance=Coalesce(Sum("amount"), Decimal(0))
            ).order_by("-date")
            
       
    else:
        # current year cca
        day = 31
        month = 12
        clients_current_ca = ClientCurrentAccount.objects.filter(
            date__lte=datetime(cur_year, month, day)
        ).values("client", "client__name", 'client__tax_number').annotate(
            global_balance=Coalesce(Sum("amount"), Decimal(0))
        ).order_by("-global_balance")
        # previous year cca
        clients_prev_ca = ClientCurrentAccount.objects.filter(
            date__lte=datetime(prev_year, month, day)
        ).values("client", "client__name", 'client__tax_number').annotate(
            global_balance=Coalesce(Sum("amount"), Decimal(0))
        ).order_by("-global_balance")
        # new cutoff form
        form_cutoff = cutOffDateForm()

    total_clients_cur = clients_current_ca.aggregate(total_sum=Sum(
        "global_balance"))["total_sum"] or 0
    total_clients_prev = clients_prev_ca.aggregate(total_sum=Sum(
        "global_balance"))["total_sum"] or 0


    return render(request, "erp/person_current_account.html", {
        "person_type": person_type,
        "current_year": financial_year,
        "clients_current_ca": clients_current_ca,
        "clients_prev_ca": clients_prev_ca,
        "total_clients": total_clients_cur,
        "total_clients_prev": total_clients_prev,
        "form_cutoff": form_cutoff,
        "cutoff": f"{day}/{str(month).zfill(2)}"
    })

def person_ca_detail(request, person_type, person_pk):
    """Clients/Supplier's current account"""
    # current year cca
    client = CompanyClient.objects.get(pk=person_pk)
    client_ca = client.current_account.order_by("-date")
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
                client_ca = client.current_account.filter(
                        date__range=(date_from, date_to)
                    ).order_by("-date")
             # Search by year
        elif request.POST["form_type"] == "year":
            form_year = SearchByYearForm(request.POST)
            form_date = SearchByDateForm()
            if form_year.is_valid():
                input_year=form_year.cleaned_data["year"]
            
                client_ca = client.current_account.filter(date__year=input_year).order_by(
                    "-date"
                )       
    # Get method
    else:
        form_date = SearchByDateForm()
        form_year = SearchByYearForm()

    total_client_ca = client_ca.aggregate(total_sum=Sum("amount"))["total_sum"] or 0
    return render(request, "erp/person_ca_detail.html", {
        "person_type": person_type,
        "client": client,
        "client_ca": client_ca,
        "total_client_ca": total_client_ca,
        "form_date": form_date,
        "form_year": form_year
    })

def supplier_index(request):
    """Supplier's overview page"""
    financial_year = FinancialYear.objects.filter(current=True).first()
    suppliers = Supplier.objects.all()

    return render(request, "erp/supplier_index.html", {
        "financial_year": financial_year,
        "suppliers": suppliers,
    })


def payment_conditions(request):
    """Payment conditions webpage"""
    payment_methods = PaymentMethod.objects.first()
    payment_terms = PaymentTerm.objects.first()
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
    pos_list = PointOfSell.objects.filter(disabled=False)
    
    return render(request, "company/points_of_sell.html", {
        "form": form,
        "pos_list": pos_list,
    })


def doc_types(request):
    """Customize available doc types webpage"""
    if not DocumentType.objects.exists():
        # Add all types
        load_doc_types()
    return render(request, "company/doc_types.html")


def load_doc_types():
    """Import all doc types according to Argentinian regulations"""
    file_path = Path.cwd()/"static/data/doc_types.csv"
    
    df = pd.read_csv(file_path)

    # Load all data or none
    with transaction.atomic():     
        # Read file
        for _, row in df.iterrows():
            DocumentType.objects.create(
                code = str(row['code']),
                type = str(row['initials']),
                description = str(row['description']),
            )

def sales_index(request):
    """Sales overview webpage"""
    financial_year = FinancialYear.objects.filter(current=True).first()
    invoice_list = SaleInvoice.objects.all()

    return render(request, "erp/sales_index.html", {
        "financial_year": financial_year,
        "sale_invoices": invoice_list,
    })

def sales_new(request):
    """New sale invoices webpage"""
    if request.method == "POST":
        # Get invoices and invoice's lines forms
        invoice_form = SaleInvoiceForm(request.POST)
        line_formset = SaleInvoiceLineFormSet(request.POST)
        
        if invoice_form.is_valid() and line_formset.is_valid():
            # Process forms and update client's current account
            with transaction.atomic():
                sale_invoice = invoice_form.save()
                sale_lines = line_formset.save(commit=False)
                for sale_line in sale_lines:
                    sale_line.sale_invoice = sale_invoice
                    sale_line.save() 
                
                sale_invoice.update_current_account()
                
                return HttpResponseRedirect(reverse("erp:sales_invoice", 
                    args=[sale_invoice.id]
                ))

    else:
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
           
            try:
                # Check all columns exist   
                check_column_len(df, 12)
                # Standarize and check all columns have the right name
                df = standarize_dataframe(df)
                document_fields = get_model_fields_name(SaleInvoice, "collected")
                line_fields = get_model_fields_name(SaleInvoiceLine, "total_amount",
                    "sale_invoice"
                )
                total_fields = document_fields + line_fields
                check_column_names(df, total_fields)
            except ValueError:   
                return HttpResponseBadRequest(
                    f"The columns in your file don't match the required format."
                )
     
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
                            new_invoice = SaleInvoice(
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
                        new_line = SaleInvoiceLine(
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
                        # Update client's current account
                        new_invoice.update_current_account()
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
    invoice = SaleInvoice.objects.get(pk=inv_pk)

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
    invoice = SaleInvoice.objects.get(id=inv_pk)

    if request.method == "POST":
        invoice_form = SaleInvoiceForm(instance=invoice, data=request.POST)
        line_formset = SaleInvoiceLineFormSet(instance=invoice, data=request.POST)

        if invoice_form.is_valid() and line_formset.is_valid():
            with transaction.atomic():
                invoice_form.save()
                line_formset.save()
                invoice.update_current_account()

            return HttpResponseRedirect(
                reverse("erp:sales_invoice", args=[invoice.id])
            )

    else:
        invoice_form = SaleInvoiceForm(instance=invoice)
        line_formset = SaleInvoiceLineFormSet(instance=invoice)

    return render(request, "erp/sales_edit.html", {
        "invoice": invoice,
        "invoice_form": invoice_form,
        "line_formset": line_formset,
    })

def sales_related_receipts(request, inv_pk):
    """Show a list of specific invoice's related receipts."""
    invoice = SaleInvoice.objects.get(pk=inv_pk)
    receipts = SaleReceipt.objects.filter(related_invoice=invoice)

    return render(request, "erp/sales_related_receipts.html", {
        "invoice": invoice,
        "receipts": receipts,
    })


def sales_list(request):
    """Show a list of invoices in a specific range webpage"""
    # Get list general case, it gets overwritten if it changes
    financial_year = FinancialYear.objects.filter(current=True).first()
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
                invoice_list = SaleInvoice.objects.filter(
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
                invoice_list = SaleInvoice.objects.filter(
                    issue_date__year=financial_year.year
                )
    else:
        form_date = SearchByDateForm()
        form_year = SearchByYearForm()
        invoice_list = SaleInvoice.objects.filter(
            issue_date__year=financial_year.year
        )

    return render(request, "erp/sales_list.html", {
        "com_document": "invoice",
        "invoice_list": invoice_list,
        "form_date": form_date,
        "form_year": form_year, 
    })

def receivables_index(request):
    """Overview of receivables webpage"""
    financial_year = FinancialYear.objects.filter(current=True).first()
    receipt_list = SaleReceipt.objects.all()
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
           
            try:
                # Check all columns exist   
                check_column_len(df, 10)
                # Standarize and check all columns have the right name
                df = standarize_dataframe(df)
                document_fields = get_model_fields_name(SaleReceipt, "related_invoice")
                for field in ["ri_type", "ri_pos", "ri_number"]:
                    document_fields.append(field)
                check_column_names(df, document_fields)
            except ValueError:   
                 return HttpResponseBadRequest(
                        f"The columns in your file don't match the required format."
                    )
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
                            related_invoice_field = SaleInvoice.objects.get(
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
                            new_receipt = SaleReceipt(
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
    receipt = SaleReceipt.objects.get(pk=rec_pk)
    return render(request, "erp/receivables_receipt.html", {
        "receipt": receipt,
    })

def receivables_edit(request, rec_pk):
    """Edit Specific receipt webpage"""
    receipt = SaleReceipt.objects.get(id=rec_pk)

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
    financial_year = FinancialYear.objects.filter(current=True).first()
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
                receipt_list = SaleReceipt.objects.filter(
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
                receipt_list = SaleReceipt.objects.filter(issue_date__year=financial_year.year)
    else:
        form_date = SearchByDateForm()
        form_year = SearchByYearForm()
        receipt_list = SaleReceipt.objects.filter(issue_date__year=financial_year.year)

    return render(request, "erp/receivables_list.html", {
        "com_document": "receipt",
        "receipt_list": receipt_list,
        "form_date": form_date,
        "form_year": form_year, 
    })