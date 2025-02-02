from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import (CompanyClient, SaleInvoice, ClientCurrentAccount, Company,
    SaleReceipt)
from .utils import update_invoice_collected_status


@receiver(post_save, sender=CompanyClient)
def create_current_account(sender, instance, created, **kwargs):
    """
    Create ClientCurrentAccount after a client is created.
    """
    if created:
        ClientCurrentAccount.objects.create(
            client = instance,
            date = Company.objects.first().creation_date   
        )

@receiver(post_save, sender=SaleReceipt)
def update_current_account(sender, instance, created, **kwargs):
    """Update current account after doing a CRUD operation with a receipt"""
    ClientCurrentAccount.objects.update_or_create(
        receipt = instance, defaults= {
            "date": instance.issue_date,
            "client": instance.recipient,
            "amount": -instance.total_amount
        }    
    )

@receiver([post_save, post_delete], sender=SaleReceipt)
def update_collected_invoice(sender, instance, **kwargs):
    """Update invoice collected status after doing a CRUD operation with a receipt"""
    # Check and update invoice's collected attribute
    invoice = instance.related_invoice
    invoice.collected = update_invoice_collected_status(invoice)
    invoice.save()