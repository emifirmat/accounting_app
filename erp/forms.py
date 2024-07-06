"""Forms for ERP app"""
from django import forms
from django.core.exceptions import ValidationError

from company.models import Company
from .models import (Company_client, Supplier, Sale_invoice, Payment_method,
    Payment_term)



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
    

class SaleInvoiceForm(forms.ModelForm):
    """Create a new invoice"""
    class Meta:
        model = Sale_invoice
        fields = ["type", "point_of_sell", "number", "sender", "recipient",
            "payment_method", "payment_term", "description", "not_taxable_amount",
            "taxable_amount", "VAT_amount"]
        help_texts = {
            "payment_method": "How will you collect the sale?",
            "payment_term": "In how many days will you collect the sale?",
            "description": "Description of the product or service you are selling.",
            "not_taxable_amount": "Total amount.",
            "taxable_amount": "Total amount.",
            "VAT_amount": "Total amount.",
        } 


class PaymentTermForm(forms.ModelForm):
    class Meta:
        model = Payment_term
        fields = "__all__"
        labels = {
            "pay_term": "New payment term",
        }


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = Payment_method
        fields = "__all__"
        labels = {
            "pay_method": "New payment method",
        }
        
