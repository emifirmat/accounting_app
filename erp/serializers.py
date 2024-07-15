"""Serializers for ERP app"""
from rest_framework import serializers

from company.models import Company
from .models import (Company_client, Supplier, Payment_method, Payment_term,
    Point_of_sell, Document_type)


class CClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company_client
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
        model = Payment_method
        fields = "__all__"


class PaymentTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment_term
        fields = "__all__"


class PointOfSellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point_of_sell
        fields = "__all__"


class DocTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document_type
        fields = "__all__"