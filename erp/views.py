import csv, os
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from company.models import FinancialYear
from .forms import (CclientForm, SupplierForm, PaymentMethodForm, PaymentTermForm, 
    PointOfSellForm, SaleInvoiceForm, SaleInvoiceLineFormSet)
from .models import (Company, Company_client, Supplier, Payment_method, 
    Payment_term, Point_of_sell, Document_type, Sale_invoice, Sale_invoice_line)


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
    if request.method == "POST":
        if person_type == "client":
            form = CclientForm(request.POST)
        elif person_type == "supplier":
            form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("erp:person_new", kwargs={
                "person_type": person_type,
            }))
    else:
        if person_type == "client":
            form = CclientForm()
        elif person_type == "supplier":
            form = SupplierForm()

    return render(request, "erp/person_new.html", {
        "form": form,
        "person_type": person_type,
    })


def person_edit(request, person_type):
    """Search and edit an existing client or suppleir"""
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


def sales_invoice(request, inv_pk):
    """Especific invoice webpage"""
    invoice = Sale_invoice.objects.get(pk=inv_pk)

    return render(request, "erp/sales_invoice.html", {
        "invoice": invoice,
    })