"""API Views from erp app"""
from django.db.models.deletion import RestrictedError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import (CompanyClient, Supplier, PaymentMethod, PaymentTerm,
    PointOfSell, DocumentType, SaleInvoice, SaleReceipt)
from .serializers import (CClientSerializer, SupplierSerializer, 
    PaymentMethodSerializer, PaymentTermSerializer, PointOfSellSerializer,
    DocTypesSerializer, SaleInvoicesSerializer, SaleReceiptsSerializer, 
    SInvoiceDynamicSerializer, DocTypeDynamicSerializer, CClientDynamicSerializer,
    POSDynamicSerializer)

from .utils_api import (handle_multiple_instances, return_conflict_status, 
    SerializerMixin, BulkDeleteMixin)


class CompanyClientAPI(generics.ListAPIView):
    """Show API list of clients"""
    queryset = CompanyClient.objects.all()
    serializer_class = CClientSerializer
    
class CompanyClientDeleteAPI(BulkDeleteMixin, generics.GenericAPIView):
    """API delete a list of clients"""
    queryset = CompanyClient.objects.all()

class DetailCompanyClientAPI(SerializerMixin, generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific client"""
    queryset = CompanyClient.objects.all()

    def destroy(self, request, *args, **kwargs):
        # Identify when there is RestrictError (FK) with 409 status.
        try:
            return super().destroy(request, *args, **kwargs)
        except RestrictedError:
            return return_conflict_status(RestrictedError)
        
    def get_serializer_class(self):
        # Pick serializer acording to request
        fields = self.request.query_params.get("fields", None)
        if fields:
            return CClientDynamicSerializer
        # Default Serializer
        else:
            return CClientSerializer 

class SupplierAPI(generics.ListAPIView):
    """Show API list of suppliers"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class SupplierDeleteAPI(BulkDeleteMixin, generics.GenericAPIView):
    """API delete a list of suppliers"""
    queryset = Supplier.objects.all()

class DetailSupplierAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific supplier"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except RestrictedError:
            return return_conflict_status(RestrictedError)


class PaymentMethodAPI(generics.ListCreateAPIView):
    """CRUD API of payment methods"""
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer

    def create(self, request, *args, **kwargs):
        """Handle single or multiple instances in one request"""
        if isinstance(request.data, list):
            return handle_multiple_instances(self, request)
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
            return handle_multiple_instances(self, request)
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


class DetailPointOfSellAPI(SerializerMixin, generics.RetrieveUpdateAPIView):
    """CRUD API of specific POS"""
    queryset = PointOfSell.objects.all()

    def get_serializer_class(self):
        # Pick serializer acording to request
        fields = self.request.query_params.get("fields", None)
        if fields:
            return POSDynamicSerializer
        # Default Serializer
        else:
            return PointOfSellSerializer 


class DocTypesAPI(generics.ListAPIView):
    """View API of doc types"""
    queryset = DocumentType.objects.all()
    serializer_class = DocTypesSerializer


class DocTypeAPI(SerializerMixin, generics.RetrieveUpdateAPIView):
    """Vies API of especific doc type"""
    queryset = DocumentType.objects.all()

    def get_serializer_class(self):
        # Pick serializer acording to request
        fields = self.request.query_params.get("fields", None)
        if fields:
            return DocTypeDynamicSerializer
        # Default Serializer
        else:
            return DocTypesSerializer


class SaleInvoicesAPI(SerializerMixin, generics.ListCreateAPIView):
    """CRUD API of sale invoices"""
    def get_queryset(self):
        # Get full list or only collected invoices.
        collected = self.request.query_params.get("collected", None)
        exclude_inv_pk = self.request.query_params.get("exclude_inv_pk", None)
        
        queryset = SaleInvoice.objects.all()

        # Apply filters and exclusions
        if collected:
            if collected.lower() == "true":
                queryset = queryset.filter(collected=True)
            elif collected.lower() == "false":
                queryset = queryset.filter(collected=False)
    
        if exclude_inv_pk and exclude_inv_pk.isdigit():
            queryset = queryset.exclude(pk=int(exclude_inv_pk))
   
        return queryset
    
    def get_serializer_class(self):
        # Pick serializer acording to request
        fields = self.request.query_params.get("fields", None)
        if fields:
            return SInvoiceDynamicSerializer
        # Default Serializer
        else:
            return SaleInvoicesSerializer

class SaleInvoiceAPI(SerializerMixin, generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific sale invoice"""
    queryset = SaleInvoice.objects.all()
    serializer_class = SaleInvoicesSerializer
 
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except RestrictedError as e:
            return return_conflict_status(
                "The invoice you're trying to delete has related receipts."
            )
        
    def get_serializer_class(self):
        # Pick serializer acording to request
        fields = self.request.query_params.get("fields", None)
        if fields:
            return SInvoiceDynamicSerializer
        # Default Serializer
        else:
            return SaleInvoicesSerializer
    
class SaleReceiptsAPI(generics.ListCreateAPIView):
    """CRUD API of sale receipts"""
    queryset = SaleReceipt.objects.all()
    serializer_class = SaleReceiptsSerializer

class SaleReceiptAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific sale receipt"""
    queryset = SaleReceipt.objects.all()
    serializer_class = SaleReceiptsSerializer
