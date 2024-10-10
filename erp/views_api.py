"""API Views from erp app"""
from rest_framework import generics, status
from rest_framework.response import Response

from .models import (CompanyClient, Supplier, PaymentMethod, PaymentTerm,
    PointOfSell, DocumentType, SaleInvoice, SaleReceipt)
from .serializers import (CClientSerializer, SupplierSerializer, 
    PaymentMethodSerializer, PaymentTermSerializer, PointOfSellSerializer,
    DocTypesSerializer, SaleInvoicesSerializer, SaleReceiptsSerializer)


class CompanyClientAPI(generics.ListAPIView):
    """Show API list of clients"""
    queryset = CompanyClient.objects.all()
    serializer_class = CClientSerializer


class DetailCompanyClientAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific client"""
    queryset = CompanyClient.objects.all()
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
    queryset = PaymentMethod.objects.all()
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
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer


class PaymentTermAPI(generics.ListCreateAPIView):
    """CRUD API of payment terms"""
    queryset = PaymentTerm.objects.all()
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
    queryset = PaymentTerm.objects.all()
    serializer_class = PaymentTermSerializer


class PointOfSellAPI(generics.ListCreateAPIView):
    """CRUD API of Point of sells"""
    queryset = PointOfSell.objects.all()
    serializer_class = PointOfSellSerializer


class DetailPointOfSellAPI(generics.RetrieveUpdateAPIView):
    """CRUD API of specific POS"""
    queryset = PointOfSell.objects.all()
    serializer_class = PointOfSellSerializer


class DocTypesAPI(generics.ListAPIView):
    """View API of doc types"""
    queryset = DocumentType.objects.all()
    serializer_class = DocTypesSerializer


class DocTypeAPI(generics.RetrieveUpdateAPIView):
    """Vies API of especific doc type"""
    queryset = DocumentType.objects.all()
    serializer_class = DocTypesSerializer


class SaleInvoicesAPI(generics.ListCreateAPIView):
    """CRUD API of sale invoices"""
    queryset = SaleInvoice.objects.all()
    serializer_class = SaleInvoicesSerializer


class SaleInvoiceAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific sale invoice"""
    queryset = SaleInvoice.objects.all()
    serializer_class = SaleInvoicesSerializer

class SaleReceiptsAPI(generics.ListCreateAPIView):
    """CRUD API of sale receipts"""
    queryset = SaleReceipt.objects.all()
    serializer_class = SaleReceiptsSerializer


class SaleReceiptAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific sale receipt"""
    queryset = SaleReceipt.objects.all()
    serializer_class = SaleReceiptsSerializer