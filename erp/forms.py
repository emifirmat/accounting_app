"""Forms for ERP app"""
from django import forms
from django.core.exceptions import ValidationError

from company.models import Company
from .models import Company_client, Supplier



class CclientForm(forms.ModelForm):
    """Form for a client"""
    class Meta:
        model = Company_client
        fields = ["name", "address", "email", "phone", "tax_number"]
        help_texts = {
            "tax_number": "Only numbers.",
        } 
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "example@email.com"}),
            "tax_number": forms.NumberInput(attrs={"placeholder": "XXXXXXXXXX"}),
        }

    def clean_tax_number(self):
        tax_number = self.cleaned_data.get("tax_number")
        company = Company.objects.only("tax_number").first()
        
        if tax_number == company.tax_number:
            raise ValidationError(
                "The tax number you're trying to add belongs to the company."
            )
        return tax_number
    

class SupplierForm(forms.ModelForm):
    """Form for a supplier"""
    class Meta:
        model = Supplier
        fields = ["name", "address", "email", "phone", "tax_number"]
        help_texts = {
            "tax_number": "Only numbers.",
        } 
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "example@email.com"}),
            "tax_number": forms.NumberInput(attrs={"placeholder": "XXXXXXXXXX"}),
        }

    def clean_tax_number(self):
        tax_number = self.cleaned_data.get("tax_number")
        company = Company.objects.only("tax_number").first()
        
        if tax_number == company.tax_number:
            raise ValidationError(
                "The tax number you're trying to add belongs to the company."
            )
        return tax_number
        
