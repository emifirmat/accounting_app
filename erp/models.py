from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Sum, Q
from django.urls import reverse

from .validators import (validate_is_digit, validate_in_current_year, 
    validate_invoices_date_number_correlation, validate_receipt_date_number_correlation,
    validate_receipt_total_amount)
from company.models import PersonModel, Company

# Create your models here.
class CurrentAccountModel(models.Model):
    """Base model for a person's current account"""
    """Amount is the amount of a transaction, not the total"""
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class CommercialDocumentModel(models.Model):
    """Base model for commercial documents"""
    issue_date = models.DateField(validators=[
        validate_in_current_year,
    ])
    number = models.CharField(max_length=8, validators=[
        validate_is_digit
    ]) 

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.issue_date} | {self.point_of_sell}-{self.number}"
    
    def save(self, *args, **kwargs):
        # Complete numbers with 0
        self.number = self.number.zfill(8)
        return super(CommercialDocumentModel, self).save(*args, **kwargs)
    

class CommercialDocumentLineModel(models.Model):
    """Base model for commercial documents lines"""
    description = models.CharField(max_length=280)
    taxable_amount = models.DecimalField(max_digits=15, decimal_places=2)
    not_taxable_amount = models.DecimalField(max_digits=15, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.description} | $ {self.total_amount}"
    
    def save(self, *args, **kwargs):
        # Get total amount field
        self.total_amount = (self.taxable_amount + self.not_taxable_amount +
            self.vat_amount)
        return super(CommercialDocumentLineModel, self).save(*args, **kwargs)


class Company_client(PersonModel):
    """Create a company's client"""
    pass

class Supplier(PersonModel):
    """Create a company's supplier"""
    pass    

class Client_current_account(CurrentAccountModel):
    """Track client's current account"""
    client = models.ForeignKey(Company_client, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.client}: $ {self.amount}"
    

class Supplier_current_account(CurrentAccountModel):
    """Track suppliers's current account"""
    """Amount is the amount of a transaction, not the total"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.supplier}: $ {self.amount}"
    

class Point_of_sell(models.Model):
    """Company's point of sell"""
    pos_number = models.CharField(max_length=5, unique=True, validators=[
        validate_is_digit
    ])
    # Delete is now allowed in POS
    disabled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Complete numbers with 0
        self.pos_number = self.pos_number.zfill(5)
        return super(Point_of_sell, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.pos_number}"


class Document_type(models.Model):
    """Type of the document"""
    code = models.CharField(max_length=3, unique=True, validators=[
        validate_is_digit,
    ])
    type = models.CharField(max_length=5, validators= [
            RegexValidator(
                regex=r'[a-zA-Z]',
                message="Insert letters only",
                code="Invalid doc type"
            )
    ])
    type_description = models.CharField(max_length=20)
    hide = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} | {self.type}"
    
    def save(self, *args, **kwargs):
        # Format fields
        self.code = self.code.zfill(3)
        self.type = self.type.upper()
        self.type_description = self.type_description.upper()
        return super(Document_type, self).save(*args, **kwargs)


class Payment_method(models.Model):
    """Establish payment methods for invoices"""
    pay_method = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.pay_method}"
    
    def save(self, *args, **kwargs):
        # Format fields
        self.type = self.pay_method.capitalize()
        return super(Payment_method, self).save(*args, **kwargs)
    

class Payment_term(models.Model):
    """Establish payment terms for invoices"""
    pay_term = models.CharField(max_length=3, unique=True, validators=[
        validate_is_digit
    ])

    def __str__(self):
        return f"{self.pay_term} days"


class Sale_invoice(CommercialDocumentModel):
    """Create a sale invoice"""
    type = models.ForeignKey(Document_type, on_delete=models.PROTECT)
    point_of_sell = models.ForeignKey(Point_of_sell, on_delete=models.PROTECT)
    sender = models.ForeignKey(Company, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Company_client, on_delete=models.PROTECT)
    payment_method = models.ForeignKey(Payment_method, on_delete=models.PROTECT)
    payment_term = models.ForeignKey(Payment_term, on_delete=models.PROTECT)
    collected = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["point_of_sell", "number", "type"],
                name="unique_sale_invoice_complete_number"),
        ]
        ordering = ["-issue_date", "type", "point_of_sell", "number" ]

    def get_absolute_url(self):
        """Get object webpage"""
        return reverse("erp:sales_invoice", args=[self.pk])
    
    def total_lines_sum(self):
        """Get the sum of all invoice's line"""
        total_sum = self.s_invoice_lines.aggregate(
            lines_sum=Sum("total_amount")
        )["lines_sum"]
        return round(total_sum, 2)
    
    def __str__(self):
        return f"{self.issue_date} | {self.type.type} | {self.point_of_sell}-{self.number}"
    
    def clean(self):
        """Add date validator for invoice"""
        super().clean()
        validate_invoices_date_number_correlation(__class__, self)
        
class Sale_invoice_line(CommercialDocumentLineModel):
    """Product/service detail of the sale invoice"""
    sale_invoice = models.ForeignKey(Sale_invoice, on_delete=models.CASCADE,
        related_name="s_invoice_lines")

class Sale_receipt(CommercialDocumentModel):
    """Create a sale receipt"""
    point_of_sell = models.ForeignKey(Point_of_sell, on_delete=models.PROTECT)
    related_invoice = models.ForeignKey(Sale_invoice, on_delete=models.RESTRICT)
    sender = models.ForeignKey(Company, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Company_client, on_delete=models.PROTECT)
    description = models.CharField(max_length=280)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["point_of_sell", "number"],
                name="unique_sale_receipt_complete_number"
            ),
        ]
        ordering = ["-issue_date", "point_of_sell", "number"]

    def get_absolute_url(self):
        """Get object webpage"""
        return reverse("erp:receivables_receipt", args=[self.pk])
    
    def __str__(self):
        return f"{self.issue_date} | {self.point_of_sell}-{self.number}"
    
    def clean(self):
        """Add date validator for receipt"""
        super().clean()
        validate_receipt_date_number_correlation(__class__, self)
        validate_receipt_total_amount(__class__, self)

class Purchase_invoice(CommercialDocumentModel):
    """Record a purchase invoice"""
    # POS is different from Sale invoice, as dif suppliers have dif POS.
    type = models.ForeignKey(Document_type, on_delete=models.PROTECT)
    point_of_sell = models.CharField(max_length=5, validators=[
        validate_is_digit
    ])
    sender = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Company, on_delete=models.PROTECT)
    payment_method = models.ForeignKey(Payment_method, on_delete=models.PROTECT)
    payment_term = models.ForeignKey(Payment_term, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["sender", "point_of_sell", "number",
                "type"], name="unique_purchase_invoice_per_supplier")
        ]
        ordering = ["-issue_date", "sender", "type", "point_of_sell", "number"]

    def __str__(self):
        return f"{self.issue_date} | {self.type.type} | {self.point_of_sell}-{self.number}"

class Purchase_invoice_line(CommercialDocumentLineModel):
    """Product/service detail of the purchase invoice"""
    purchase_invoice = models.ForeignKey(Purchase_invoice, on_delete=models.CASCADE,
        related_name="p_invoice_lines")


class Purchase_receipt(CommercialDocumentModel):
    """Record a purchase receipt"""
    # POS is different from Sale invoice, as dif suppliers have dif POS.
    point_of_sell = models.CharField(max_length=5, validators=[
        validate_is_digit
    ])
    related_invoice = models.ForeignKey(Purchase_invoice, on_delete=models.RESTRICT)
    sender = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Company, on_delete=models.PROTECT)
    description = models.CharField(max_length=280)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=[
                "sender", "point_of_sell", "number",
            ], name="unique_purchase_receipt_per_supplier"
            )
        ]
        ordering = ["-issue_date", "sender", "point_of_sell", "number"]
    
    def __str__(self):
        return f"{self.issue_date} | {self.point_of_sell}-{self.number}"
