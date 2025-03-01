from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Sum, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from .validators import (validate_is_digit, validate_in_current_year, 
    validate_invoices_date_number_correlation, validate_receipt_date_number_correlation,
    validate_receipt_total_amount, validate_not_disabled_pos)
from company.models import PersonModel, Company

# Create your models here.
class CurrentAccountModel(models.Model):
    """Base model for a person's current account"""
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

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


class CompanyClient(PersonModel):
    """Create a company's client"""
    pass

class Supplier(PersonModel):
    """Create a company's supplier"""
    pass    

class ClientCurrentAccount(CurrentAccountModel):
    """Track client's current account"""
    client = models.ForeignKey(CompanyClient, on_delete=models.CASCADE, 
        related_name="current_account")
    
    invoice = models.ForeignKey("SaleInvoice", on_delete=models.CASCADE, 
        blank=True, null=True)
    receipt = models.ForeignKey("SaleReceipt", on_delete=models.CASCADE,
        blank=True, null=True)
    
    def __str__(self):
        return f"{self.client}: $ {self.amount}"


class SupplierCurrentAccount(CurrentAccountModel):
    """Track suppliers's current account"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE,
        related_name="current_account")
    
    invoice = models.ForeignKey("PurchaseInvoice", on_delete=models.CASCADE, 
        blank=True, null=True)
    receipt = models.ForeignKey("PurchaseReceipt", on_delete=models.CASCADE,
        blank=True, null=True)

    def __str__(self):
        return f"{self.supplier}: $ {self.amount}"
    

class PointOfSell(models.Model):
    """Company's point of sell"""
    pos_number = models.CharField(max_length=5, unique=True, validators=[
        validate_is_digit
    ])
    # Delete is not allowed in POS
    disabled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Fill numbers with 0
        self.pos_number = self.pos_number.zfill(5)
        return super(PointOfSell, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.pos_number}"


class DocumentType(models.Model):
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
    description = models.CharField(max_length=20)
    hide = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} | {self.type}"
    
    def save(self, *args, **kwargs):
        # Format fields
        self.code = self.code.zfill(3)
        self.type = self.type.upper()
        self.description = self.description.upper()
        return super(DocumentType, self).save(*args, **kwargs)


class PaymentMethod(models.Model):
    """Establish payment methods for invoices"""
    pay_method = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.pay_method}"
    
    def save(self, *args, **kwargs):
        # Format fields
        self.type = self.pay_method.capitalize()
        return super(PaymentMethod, self).save(*args, **kwargs)
    

class PaymentTerm(models.Model):
    """Establish payment terms for invoices"""
    pay_term = models.CharField(max_length=3, unique=True, validators=[
        validate_is_digit
    ])

    def __str__(self):
        return f"{self.pay_term} days"


class SaleInvoice(CommercialDocumentModel):
    """Create a sale invoice"""
    type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    point_of_sell = models.ForeignKey(PointOfSell, on_delete=models.PROTECT)
    sender = models.ForeignKey(Company, on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        CompanyClient, on_delete=models.RESTRICT, related_name="invoices")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.RESTRICT)
    payment_term = models.ForeignKey(PaymentTerm, on_delete=models.RESTRICT)
    collected = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["point_of_sell", "number", "type"],
                name="unique_sale_invoice_complete_number"),
        ]
        ordering = ["-issue_date", "type", "point_of_sell", "-number" ]

    def get_absolute_url(self):
        """Get object webpage"""
        return reverse("erp:sales_invoice", args=[self.pk])
    
    def total_lines_sum(self):
        """Get the sum of all invoice's line"""
        total_sum = self.s_invoice_lines.aggregate(
            lines_sum=Sum("total_amount")
        )["lines_sum"]
        return round(total_sum, 2)
    
    def update_current_account(self):
        """Update client's current account"""
        ClientCurrentAccount.objects.update_or_create(
            invoice = self, defaults= {
                "date": self.issue_date,
                "client": self.recipient,
                "amount": self.total_lines_sum()
            }    
        )
      
    def __str__(self):
        return f"{self.type.type} {self.point_of_sell}-{self.number}"
    
    def clean(self):
        """Add date and pos validators for invoice"""
        super().clean()
        validate_invoices_date_number_correlation(__class__, self)
        validate_not_disabled_pos(self)

        
class SaleInvoiceLine(CommercialDocumentLineModel):
    """Product/service detail of the sale invoice"""
    sale_invoice = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE,
        related_name="s_invoice_lines")

class SaleReceipt(CommercialDocumentModel):
    """Create a sale receipt"""
    point_of_sell = models.ForeignKey(PointOfSell, on_delete=models.PROTECT)
    related_invoice = models.ForeignKey(SaleInvoice, on_delete=models.RESTRICT)
    sender = models.ForeignKey(Company, on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        CompanyClient, on_delete=models.RESTRICT, related_name="receipts"
    )
    description = models.CharField(max_length=280)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["point_of_sell", "number"],
                name="unique_sale_receipt_complete_number"
            ),
        ]
        ordering = ["-issue_date", "point_of_sell", "-number"]

    def get_absolute_url(self):
        """Get object webpage"""
        return reverse("erp:receivables_receipt", args=[self.pk])
    
    def __str__(self):
        return f"{self.point_of_sell}-{self.number}"
    
    def clean(self):
        """Add date validator for receipt"""
        super().clean()
        validate_receipt_date_number_correlation(__class__, self)
        validate_receipt_total_amount(__class__, self)
        validate_not_disabled_pos(self)


class PurchaseInvoice(CommercialDocumentModel):
    """Record a purchase invoice"""
    # POS is different from Sale invoice, as dif suppliers have dif POS.
    type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    point_of_sell = models.CharField(max_length=5, validators=[
        validate_is_digit
    ])
    sender = models.ForeignKey(Supplier, on_delete=models.RESTRICT)
    recipient = models.ForeignKey(Company, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.RESTRICT)
    payment_term = models.ForeignKey(PaymentTerm, on_delete=models.RESTRICT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["sender", "point_of_sell", "number",
                "type"], name="unique_purchase_invoice_per_supplier")
        ]
        ordering = ["-issue_date", "sender", "type", "point_of_sell", "-number"]

    def __str__(self):
        return f"{self.type.type} {self.point_of_sell}-{self.number}"

class PurchaseInvoiceLine(CommercialDocumentLineModel):
    """Product/service detail of the purchase invoice"""
    purchase_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE,
        related_name="p_invoice_lines")


class PurchaseReceipt(CommercialDocumentModel):
    """Record a purchase receipt"""
    # POS is different from Sale invoice, as dif suppliers have dif POS.
    point_of_sell = models.CharField(max_length=5, validators=[
        validate_is_digit
    ])
    related_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.RESTRICT)
    sender = models.ForeignKey(Supplier, on_delete=models.RESTRICT)
    recipient = models.ForeignKey(Company, on_delete=models.CASCADE)
    description = models.CharField(max_length=280)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=[
                "sender", "point_of_sell", "number",
            ], name="unique_purchase_receipt_per_supplier"
            )
        ]
        ordering = ["-issue_date", "sender", "point_of_sell", "-number"]
    
    def __str__(self):
        return f"{self.point_of_sell}-{self.number}"
