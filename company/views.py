from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from .forms import CompanyForm, FinancialYearForm
from .models import Company, FinancialYear


# Create your views here.
def index(request):
    """Index page"""
    company = Company.objects.first()
    try:
        financial_year = FinancialYear.objects.get(current=True)
    except ObjectDoesNotExist:
        financial_year = None
    return render(request, "company/index.html", {
        "company": company,
        "financial_year": financial_year,
    })


def company_settings(request):
    """Create or modify company settings"""
    company = Company.objects.all().first()
    if request.method == "POST":
        # Modify data of existing company
        if company:    
            form = CompanyForm(instance=company, data=request.POST)
        # Create new company
        else:
            form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("company:index"))
    else:
        # Get form with company's data
        if company:
            form = CompanyForm(instance=company)
        # Get a blank form
        else:
            form = CompanyForm()
    
    return render(request, "company/settings.html", {
        "form": form
    })


def company_year(request):
    """Create or select current year"""
    years = FinancialYear.objects.all()
    try:
        current_year = FinancialYear.objects.get(current=True)
    except ObjectDoesNotExist:
        current_year = None
    if request.method == "POST":
        form = FinancialYearForm(request.POST)
        if form.is_valid():
            new_year = FinancialYear(year=form.cleaned_data["year"])
            # If it's first time adding a year, make it current.
            if not years.count():
                new_year.current = True
            new_year.save()
            return HttpResponseRedirect(reverse("company:index"))
    else:
        form = FinancialYearForm()
    
    return render(request, "company/year.html", {
        "form": form,
        "years": years,
        "current_year": current_year,
    })
