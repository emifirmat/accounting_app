from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from company.models import FinancialYear
from .forms import CclientForm, SupplierForm, SaleInvoiceForm
from .models import (Company, Company_client, Supplier, Sale_invoice, 
    Payment_method, Payment_term)


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
    form = SaleInvoiceForm
    return render(request, "erp/sales_new.html", {
        "form": form,
    })

def payment_conditions(request):
    """Payment conditions webpage"""
    payment_methods = Payment_method.objects.all()
    payment_terms = Payment_term.objects.all()
    return render(request, "company/payment_conditions.html", {
        "payment_methods": payment_methods,
        "payment_terms": payment_terms,
    })
