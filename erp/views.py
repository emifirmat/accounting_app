from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from company.models import FinancialYear
from .forms import CclientForm
from .models import Company, Company_client


# Create your views here.
def client_index(request):
    """Client's overview page"""
    try:
        financial_year = FinancialYear.objects.get(current=True)
    except ObjectDoesNotExist:
        financial_year = None
    clients = Company_client.objects.all()
    return render(request, "erp/client_index.html", {
        "financial_year": financial_year,
        "clients": clients,
    })


def client_new(request):
    """Add a new client page"""
    if request.method == "POST":
        form = CclientForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("erp:client_new"))
    else:
        form = CclientForm()

    return render(request, "erp/client_new.html", {
        "form": form,
    })


def client_edit(request):
    """Search and edit an existing client"""
    if request.method == "GET":
        clients = Company_client.objects.all()
        form = CclientForm()
        return render(request, "erp/client_edit.html", {
            "clients": clients,
            "form": form,
        })


def client_delete(request):
    """Search and delete an existing client"""
    clients = Company_client.objects.all()
    form = CclientForm()
    return render(request, "erp/client_delete.html", {
        "clients": clients,
        "form": form,
    })