"""Serializers for ERP app"""
from rest_framework import serializers

from company.models import Company
from .models import Company_client, Supplier

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