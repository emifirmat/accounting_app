"""Forms for ERP app"""
from datetime import datetime
from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError

from company.models import Company
from .models import (CompanyClient, Supplier, PaymentMethod, PaymentTerm,
    PointOfSell, DocumentType, SaleInvoice, SaleInvoiceLine, SaleReceipt)
from .validators import validate_is_digit, validate_file_extension



class CclientForm(forms.ModelForm):
    """Form for a client"""
    class Meta:
        model = CompanyClient
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
        model = PaymentTerm
        fields = "__all__"
        labels = {
            "pay_term": "",
        }


class PaymentMethodForm(forms.ModelForm):
    "Add a new payment method"
    class Meta:
        model = PaymentMethod
        fields = "__all__"
        labels = {
            "pay_method": "",
        }
        

class PointOfSellForm(forms.ModelForm):
    """Add a new company's point of sell"""
    class Meta:
        model = PointOfSell
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
        model = SaleInvoice
        fields = ["issue_date", "type", "point_of_sell", "number", "sender", "recipient",
            "payment_method", "payment_term"]
        help_texts = {
            "issue_date": "The date should be in the current financial year. Format=DD/MM/YYYY",
            "type": "Can't find the type you need? <a href=\"/erp/document_types\">Click Here</a>",
            "number": "The number you see is the next in sequence after the last invoice created in the system.",
            "point_of_sell": "Can't find the point of sell you need? <a href=\"/erp/points_of_sell\">Click Here</a>",
            "payment_method": "How will you collect the sale?",
            "payment_term": "In how many days will you collect the sale?",
        } 
        labels = {"issue_date": "Date"}
        widgets = {
            "issue_date": forms.DateInput(format="%d/%m/%Y", attrs={
                "class": "datepicker",
            }),
            "number": forms.NumberInput(attrs={"placeholder": "XXXXXXXX"}),
        }
    
    def __init__(self, *args, **kwargs):
        """Customize intitial fields"""
        super().__init__(*args, **kwargs)
        
        # Customize issue_date field
        self.fields["issue_date"].input_formats = ["%d/%m/%Y"]
        self.fields["issue_date"].initial = datetime.now()

        # Type field, show only visible types
        self.fields["type"].queryset = DocumentType.objects.filter(hide=False)
        
        # Point of sell field, show only enabled POS
        self.fields["point_of_sell"].queryset = PointOfSell.objects.filter(disabled=False)

        # Define sender as the company
        sender = Company.objects.first()
        if sender:
            self.fields["sender"].initial = sender
            self.fields["sender"].disabled = True

    
class SaleInvoiceLineForm(forms.ModelForm):
    """Create a new line of products details for an especific invoice"""
    class Meta:
        model = SaleInvoiceLine
        fields = ["description", "not_taxable_amount", "taxable_amount",
            "vat_amount"]
        help_texts = {
            "description": "Description of the product or service you are selling.",
            "not_taxable_amount": "Total amount.",
            "taxable_amount": "Total amount.",
            "vat_amount": "Total amount.",
        }

SaleInvoiceLineFormSet = inlineformset_factory(
    SaleInvoice, SaleInvoiceLine, form=SaleInvoiceLineForm, extra=1, 
    can_delete=True, min_num=1, validate_min=True
)

class SearchInvoiceForm(forms.Form):
    """Fields for the invoice search"""
    collected = forms.ChoiceField(choices=[
        ('op1', 'All'), ('op2', 'Uncollected'), ('op3', 'Collected')
    ], label='Show invoices')
    type = forms.CharField(max_length=5)
    pos = forms.CharField(max_length=5, label="Point of sell")
    number = forms.CharField(max_length=8)
    client_tax_number = forms.CharField(max_length=11)
    client_name = forms.CharField(max_length=40)
    year = forms.CharField(max_length=4)
    month = forms.CharField(max_length=2, help_text="Only numbers.")

    def __init__(self, *args, **kwargs):
        """Customize intitial fields"""
        super().__init__(*args, **kwargs)
        
        # Customize issue_date field
        self.fields["collected"].initial = 'op2'
        self.fields['collected'].widget.attrs.update({'data-status': ''})

class AddPersonFileForm(forms.Form):
    """Add file for new clients or suppliers"""
    file = forms.FileField(label="", help_text=
    """Format:
    tax_number=number, 11 char;
    name=text;
    address=text;
    email=xx@email.com;
    phone=number, max 25 char;""",
    validators=[validate_file_extension])

class AddSaleInvoicesFileForm(forms.Form):
    """Add file for new sale invoices"""
    file = forms.FileField(label="", help_text=
    """Format:
    issue_date=DD/MM/YYYY; type=code, number, max 3 char; point_of_sell=number,
    max 5 char; number=number, max 8 char; sender=tax_number, max 11 char; 
    recipient=tax_number, max 11 char; payment_method=text; payment_term=number,
    max 3 char; description=text, max 280 char; taxable_amount=decimal(2); 
    not_taxable_amount=decimal(2); VAT_amount=decimal(2);""",
    validators=[validate_file_extension])

class SearchByYearForm(forms.Form):
    """Year form for searching"""
    year = forms.CharField(
        max_length=4, 
        widget=forms.TextInput(
            attrs={
                "placeholder": "XXXX",
            }
        ),
        validators = [validate_is_digit]
    )


class SearchByDateForm(forms.Form):
    """From date to date form for searching"""
    date_from = forms.DateField(
        label="From",
        input_formats=["%d/%m/%Y"],
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={
                "class": "datepicker",
            }
        )
    )
    
    date_to = forms.DateField(
        label="To",
        input_formats=["%d/%m/%Y"],
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={
                "class": "datepicker",
            }
        )
    )

class cutOffDateForm(forms.Form):
    """A form to complete with day and month"""
    day = forms.IntegerField( 
        min_value=0,
        max_value=31,
        required =True
    )
    month = forms.IntegerField(
        min_value=0,
        max_value=12,
        required=True
    )
  
class SaleReceiptForm(forms.ModelForm):
    """Create a new receipt"""
    class Meta:
        model = SaleReceipt
        fields = ["issue_date", "point_of_sell", "number", "related_invoice",
                "sender", "recipient", "description", "total_amount"]
        help_texts = {
            "issue_date": "The date should be in the current financial year. Format=DD/MM/YYYY",
            "number": "The number you see is the next in sequence after the last invoice created in the system.",
            "related_invoice": "You can only add one invoice per receipt.",
            "point_of_sell": "Can't find the point of sell you need? <a href=\"/erp/points_of_sell\">Click Here</a>",
            "total_amount": "Total amount collected.",
        } 
        labels = {
            "issue_date": "Date",        
        }
        widgets = {
            "issue_date": forms.DateInput(format="%d/%m/%Y", attrs={
                "class": "datepicker",
            }),
            "number": forms.NumberInput(attrs={"placeholder": "XXXXXXXX"}),
        }

    def __init__(self, *args, **kwargs):
        """Customize intitial fields"""
        super().__init__(*args, **kwargs)
        
        # Customize issue_date field
        self.fields["issue_date"].input_formats = ["%d/%m/%Y"]
        self.fields["issue_date"].initial = datetime.now()
        
        # Point of sell: show only enabled pos
        self.fields["point_of_sell"].queryset = PointOfSell.objects.filter(disabled=False)

        # Define sender as the company
        sender = Company.objects.first()
        if sender:
            self.fields["sender"].initial = sender
            self.fields["sender"].disabled = True

        # In related invoice field, show only uncollected invoices + edited invoice
        receipt = kwargs.get("instance")

        if receipt:
            related_invoices = SaleInvoice.objects.filter(
                Q(collected=False) | Q(pk=receipt.related_invoice.pk)
            )
            
            self.fields["related_invoice"].queryset = related_invoices
        else:
            self.fields["related_invoice"].queryset = SaleInvoice.objects.filter(
                collected=False
            )

        


class SearchReceiptForm(forms.Form):
    """Fields for the receipt search"""
    related_invoice = forms.CharField(max_length=14, widget=forms.TextInput(
            attrs={
                "placeholder": "XX XXXXX-XXXXXXXX",
            }
        ), help_text="Invoice type, POS and number.")
    pos = forms.CharField(max_length=5, label="Point of sell")
    number = forms.CharField(max_length=8)
    client_tax_number = forms.CharField(max_length=11)
    client_name = forms.CharField(max_length=40)
    year = forms.CharField(max_length=4)
    month = forms.CharField(max_length=2, help_text="Only numbers.")

class AddSaleReceiptsFileForm(forms.Form):
    """Add file for new sale receipts"""
    file = forms.FileField(label="", help_text=
    """Format:
    issue_date=DD/MM/YYYY; point_of_sell=number, max 5 char; number=number, max 8 char;
    sender=tax_number, max 11 char; recipient=tax_number, max 11 char; 
    description=text, max 280char; total_amount=decimal(2); ri_type=code, number,
    max 3char; ri_pos=number, max 5 char; ri_number=number, max 8 char;
    """,
    validators=[validate_file_extension])