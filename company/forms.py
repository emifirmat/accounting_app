from django import forms

from .models import Company, FinancialYear

class CompanyForm(forms.ModelForm):
    """Company Settings"""
    class Meta:
        model = Company
        fields = ["name", "address", "email", "phone", "tax_number", 
            "creation_date", "closing_date"]
        help_texts = {
            "tax_number": "Only numbers",
            "creation_date": "Company's starting date",
            "closing_date": "Ending date of each financial year",
        } 
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "example@email.com"}),
            "tax_number": forms.NumberInput(attrs={"placeholder": "XXXXXXXXXX"}),
            "creation_date": forms.DateInput(format="%d/%m/%Y", attrs={
                "class": "datepicker",
                "placeholder": "dd/mm/yyyy",
            }),
            "closing_date": forms.DateInput(format="%d/%m/%Y", attrs={
                "class": "datepicker",
                "placeholder": "dd/mm/yyyy",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['creation_date'].input_formats = ['%d/%m/%Y']
        self.fields['closing_date'].input_formats = ['%d/%m/%Y']

class FinancialYearForm(forms.ModelForm):
    """Financial year of the company"""
    class Meta:
        model = FinancialYear
        fields = ["year"]
        labels = {"year": "Add a new year"}
        widgets = {
            "year": forms.NumberInput(attrs={"placeholder": "XXXX"}),
        }