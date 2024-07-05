"""API Views from erp app"""
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Company_client, Supplier, Payment_method, Payment_term
from .serializers import (CClientSerializer, SupplierSerializer, 
    PaymentMethodSerializer, PaymentTermSerializer)


class CompanyClientAPI(generics.ListAPIView):
    """Show API list of clients"""
    queryset = Company_client.objects.all()
    serializer_class = CClientSerializer


class DetailCompanyClientAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific client"""
    queryset = Company_client.objects.all()
    serializer_class = CClientSerializer


class SupplierAPI(generics.ListAPIView):
    """Show API list of suppliers"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class DetailSupplierAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific supplier"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class PaymentMethodAPI(generics.ListCreateAPIView):
    """CRUD API of payment methods"""
    queryset = Payment_method.objects.all()
    serializer_class = PaymentMethodSerializer

    def create(self, request, *args, **kwargs):
        """Handle single or multiple instances in one request"""
        if isinstance(request.data, list):
            # Create serializer for multiple instances
            serializer = self.get_serializer(data=request.data, many=True)
            # Check if they're valid
            serializer.is_valid(raise_exception=True)
            # Save instances
            self.perform_create(serializer)
            # Add headers 
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                headers=headers)
        else:
            return super().create(request, *args, **kwargs)


class DetailPaymentMethodAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific payment method"""
    queryset = Payment_method.objects.all()
    serializer_class = PaymentMethodSerializer


class PaymentTermAPI(generics.ListCreateAPIView):
    """CRUD API of payment terms"""
    queryset = Payment_term.objects.all()
    serializer_class = PaymentTermSerializer

    def create(self, request, *args, **kwargs):
        """Handle single or multiple instances in one request"""
        if isinstance(request.data, list):
            # Create serializer for multiple instances
            serializer = self.get_serializer(data=request.data, many=True)
            # Check if they're valid
            serializer.is_valid(raise_exception=True)
            # Save instances
            self.perform_create(serializer)
            # Add headers 
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                headers=headers)
        else:
            return super().create(request, *args, **kwargs)


class DetailPaymentTermAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific payment term"""
    queryset = Payment_term.objects.all()
    serializer_class = PaymentTermSerializer