"""Forms for ERP app"""
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError

from company.models import Company
from .models import (Company_client, Supplier, Payment_method, Payment_term,
    Point_of_sell, Document_type, Sale_invoice, Sale_invoice_line)
from .validators import validate_is_digit



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
    

class PaymentTermForm(forms.ModelForm):
    """Add a new payment term"""
    class Meta:
        model = Payment_term
        fields = "__all__"
        labels = {
            "pay_term": "New payment term",
        }


class PaymentMethodForm(forms.ModelForm):
    "Add a new payment method"
    class Meta:
        model = Payment_method
        fields = "__all__"
        labels = {
            "pay_method": "New payment method",
        }
        

class PointOfSellForm(forms.ModelForm):
    """Add a new company's point of sell"""
    class Meta:
        model = Point_of_sell
        fields = ["pos_number",]
        labels = {
            "pos_number": "Point of sell",
        }
        help_texts = {
            "pos_number": "I.E. 00001",
        }


class SaleInvoiceForm(forms.ModelForm):
    """Create a new invoice"""
    class Meta:
        model = Sale_invoice
        fields = ["type", "point_of_sell", "number", "sender", "recipient",
            "payment_method", "payment_term"]
        help_texts = {
            "type": "Can't find the type you need? <a href=\"/erp/document_types\">Click Here</a>",
            "number": "The number you see is the next in sequence after the last invoice created in the system.",
            "point_of_sell": "Can't find the point of sell you need? <a href=\"/erp/points_of_sell\">Click Here</a>",
            "payment_method": "How will you collect the sale?",
            "payment_term": "In how many days will you collect the sale?",
        } 
        widgets = {
            "number": forms.NumberInput(attrs={"placeholder": "XXXXXXXX"}),
        }
    
    def __init__(self, *args, **kwargs):
        """Customize intitial fields"""
        super().__init__(*args, **kwargs)
        # Define sender as the company
        sender = Company.objects.first()
        if sender:
            self.fields["sender"].initial = sender
            self.fields["sender"].disabled = True

        # In type field, show only visible types
        self.fields["type"].queryset = Document_type.objects.filter(hide=False)


class SaleInvoiceLineForm(forms.ModelForm):
    """Create a new line of products details for an especific invoice"""
    class Meta:
        model = Sale_invoice_line
        fields = ["description", "not_taxable_amount", "taxable_amount",
            "VAT_amount"]
        help_texts = {
            "description": "Description of the product or service you are selling.",
            "not_taxable_amount": "Total amount.",
            "taxable_amount": "Total amount.",
            "VAT_amount": "Total amount.",
        }


SaleInvoiceLineFormSet = inlineformset_factory(
    Sale_invoice, Sale_invoice_line, form=SaleInvoiceLineForm, extra=1, 
    can_delete=True
)

class SearchInvoiceForm(forms.Form):
    """Fields for the invoice search"""
    type = forms.CharField(max_length=5)
    pos = forms.CharField(max_length=5, label="Point of sell")
    number = forms.CharField(max_length=8)
    client_tax_number = forms.CharField(max_length=11)
    client_name = forms.CharField(max_length=40)
    year = forms.CharField(max_length=4)
    month = forms.CharField(max_length=2, help_text="Only numbers.")
