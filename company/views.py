from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from .forms import CompanyForm
from .models import Company


# Create your views here.
def index(request):
    """Index page"""
    company = Company.objects.first()
    return render(request, "company/index.html", {
        "company": company,
    })


def company_settings(request):
    """Create or modify company settings"""
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            new_company = Company(form)
            new_company.save()
            return HttpResponseRedirect(reverse("company:index"))
    else:
        form = CompanyForm()
    
    return render(request, "company/settings.html", {
        "form": form
    })