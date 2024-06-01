from django.db import models

from .validators import validate_is_digit
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
    issue_date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=2)
    point_of_sell = models.CharField(max_length=5, validators=[
        validate_is_digit
    ])
    number = models.CharField(max_length=8, validators=[
        validate_is_digit
    ]) 
    description = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.point_of_sell}-{self.number} | {self.type} | {self.issue_date}"
    
    def save(self, *args, **kwargs):
        # Complete numbers with 0
        self.point_of_sell = self.point_of_sell.zfill(5)
        self.number = self.number.zfill(8)
        return super(CommercialDocumentModel, self).save(*args, **kwargs)


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
    

class Payment_method(models.Model):
    """Establish payment methods for invoices"""
    pay_method = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.pay_method}"
    

class Payment_term(models.Model):
    """Establish payment terms for invoices"""
    pay_term = models.CharField(max_length=3, validators=[
        validate_is_digit
    ])

    def __str__(self):
        return f"{self.pay_term} days"


class Sale_invoice(CommercialDocumentModel):
    """Create a sale invoice"""
    sender = models.ForeignKey(Company, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Company_client, on_delete=models.PROTECT)
    payment_method = models.ForeignKey(Payment_method, on_delete=models.PROTECT)
    payment_term = models.ForeignKey(Payment_term, on_delete=models.PROTECT)
    taxable_amount = models.DecimalField(max_digits=15, decimal_places=2)
    not_taxable_amount = models.DecimalField(max_digits=15, decimal_places=2)
    VAT_amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["point_of_sell", "number", "type"],
                name="unique_sale_invoice_complete_number")
        ]


class Sale_receipt(CommercialDocumentModel):
    """Create a sale receipt"""
    related_invoice = models.ForeignKey(Sale_invoice, on_delete=models.RESTRICT)
    sender = models.ForeignKey(Company, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Company_client, on_delete=models.PROTECT)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["point_of_sell", "number", "type"],
                name="unique_sale_receipt_complete_number")
        ]

class Purchase_invoice(CommercialDocumentModel):
    """Record a purchase invoice"""
    sender = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Company, on_delete=models.PROTECT)
    payment_method = models.ForeignKey(Payment_method, on_delete=models.PROTECT)
    payment_term = models.ForeignKey(Payment_term, on_delete=models.PROTECT)
    taxable_amount = models.DecimalField(max_digits=15, decimal_places=2)
    not_taxable_amount = models.DecimalField(max_digits=15, decimal_places=2)
    VAT_amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["sender", "point_of_sell", "number",
                "type"], name="unique_purchase_invoice_per_supplier")
        ]


class Purchase_receipt(CommercialDocumentModel):
    """Record a purchase receipt"""
    related_invoice = models.ForeignKey(Purchase_invoice, on_delete=models.RESTRICT)
    sender = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Company, on_delete=models.PROTECT)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["sender", "point_of_sell", "number",
                "type"], name="unique_purchase_receipt_per_supplier")
        ]
