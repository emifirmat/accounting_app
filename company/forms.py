from django import forms

from .models import Company

class CompanyForm(forms.ModelForm):
    """Company Settings"""
    class Meta:
        model = Company
        fields = ["name", "address", "email", "phone", "tax_number", 
            "creation_date", "closing_date", "financial_year"]
        help_texts = {
            "tax_number": "Only numbers",
            "creation_date": "Company's starting date",
            "closing_date": "Ending date of each financial year",
        } 
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "example@email.com"}),
            "tax_number": forms.NumberInput(attrs={"placeholder": "XXXXXXXXXX"}),
            "creation_date": forms.DateInput(format="%d/%m/%Y", attrs={
                "class": "form-control",
                "placeholder": "dd/mm/yyyy",
            }),
            "closing_date": forms.DateInput(format="%d/%m/%Y", attrs={
                "class": "form-control",
                "placeholder": "dd/mm/yyyy",
            }),
            "financial_year": forms.NumberInput(attrs={"placeholder": "XXXX"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].input_formats = ['%d/%m/%Y']


