"""Serializers for ERP app"""
from rest_framework import serializers

from company.models import Company
from .models import (CompanyClient, Supplier, PaymentMethod, PaymentTerm,
    PointOfSell, DocumentType, SaleInvoice, SaleReceipt)


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


class DocTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = "__all__"


class SaleInvoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleInvoice
        fields = "__all__"

class SaleReceiptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleReceipt
        fields = "__all__"