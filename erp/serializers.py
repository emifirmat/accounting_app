"""Serializers for ERP app"""
from rest_framework import serializers

from company.models import Company
from .models import (CompanyClient, Supplier, PaymentMethod, PaymentTerm,
    PointOfSell, DocumentType, SaleInvoice, SaleReceipt)

class baseDynamicSerializer(serializers.ModelSerializer):
    """Create a dynamic serializer model where it only adds the 
    fields I need of each instance.
    """
    display_name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        
        # Delete fields in case then I have another parameter
        fields = kwargs.pop('fields', None)

        super(baseDynamicSerializer, self).__init__(*args, **kwargs)
        
        # Add fields in Meta class
        if fields is not None:
            self.Meta.fields = fields

    def get_display_name(self, instance):
        return str(instance)

class CClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyClient
        fields = "__all__"

    def validate_tax_number(self, value):
        company = Company.objects.only("tax_number").first()
        
        if value == company.tax_number:
            raise serializers.ValidationError(
                "The tax number you're trying to add belongs to the company."
            )
        return value
    
class CClientDynamicSerializer(baseDynamicSerializer):
    """Create a dynamic serializer for clients where it only adds the 
    fields I need of each instance.
    """
    class Meta:
        model = CompanyClient
        fields = []
    
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"

    def validate_tax_number(self, value):
        company = Company.objects.only("tax_number").first()
        
        if value == company.tax_number:
            raise serializers.ValidationError(
                "The tax number you're trying to add belongs to the company."
            )
        return value
    
class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


class PaymentTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTerm
        fields = "__all__"


class PointOfSellSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointOfSell
        fields = "__all__"

class POSDynamicSerializer(baseDynamicSerializer):
    """Create a dynamic serializer for clients where it only adds the 
    fields I need of each instance.
    """
    class Meta:
        model = PointOfSell
        fields = []


class DocTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = "__all__"

    
class DocTypeDynamicSerializer(baseDynamicSerializer):
    """Create a dynamic serializer for document types where it only adds the 
    fields I need of each instance.
    """
    class Meta:
        model = DocumentType
        fields = []


class SaleInvoicesSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SaleInvoice
        fields = "__all__"

    def get_display_name(self, instance):
        return str(instance)
    
class SInvoiceDynamicSerializer(baseDynamicSerializer):
    """Create a dynamic serializer for sale invoices where it only adds the 
    fields I need of each instance.
    """
    class Meta:
        model = SaleInvoice
        fields = []
       
class SaleReceiptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleReceipt
        fields = "__all__"

class SaleReceiptsDynamicSerializer(baseDynamicSerializer):
    """Create a dynamic serializer for particular sale receipt where it only adds 
    the fields I need of each instance.
    """
    class Meta:
        model = SaleReceipt
        fields = []