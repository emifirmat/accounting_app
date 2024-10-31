"""API Views from erp app"""
from django.db.models.deletion import RestrictedError
from rest_framework import generics, status
from rest_framework.response import Response


from .models import (CompanyClient, Supplier, PaymentMethod, PaymentTerm,
    PointOfSell, DocumentType, SaleInvoice, SaleReceipt)
from .serializers import (CClientSerializer, SupplierSerializer, 
    PaymentMethodSerializer, PaymentTermSerializer, PointOfSellSerializer,
    DocTypesSerializer, SaleInvoicesSerializer, SaleReceiptsSerializer, 
    SInvoiceDynamicSerializer)


def handle_multiple_instances(self, request):
    """
    Handle multiple instances in one request.
    Returns:
    - Response: status 201, headers, and serializer data. 
    """
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
 
def return_conflict_status(message):
    """
    When a RestrictedError is raised, return conflic_status.
    Parameters:
    - error: Restricted Error object.
    Returns:
    - response: Status 409 and error message.
    """
    return Response({
        "detail": str(message),
        "code": "restricted_error"
    }, status=status.HTTP_409_CONFLICT)


class CompanyClientAPI(generics.ListAPIView):
    """Show API list of clients"""
    queryset = CompanyClient.objects.all()
    serializer_class = CClientSerializer

class DetailCompanyClientAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific client"""
    queryset = CompanyClient.objects.all()
    serializer_class = CClientSerializer

    def destroy(self, request, *args, **kwargs):
        # Identify when there is RestrictError (FK) with 409 status.
        try:
            return super().destroy(request, *args, **kwargs)
        except RestrictedError as e:
            return return_conflict_status(RestrictedError)


class SupplierAPI(generics.ListAPIView):
    """Show API list of suppliers"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class DetailSupplierAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific supplier"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except RestrictedError as e:
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
    
    def get_serializer(self, *args, **kwargs):
        # Add 'fields' to serializer init if picked SIDynamicSerilizer.
        fields = self.request.query_params.get("fields", None)
        if fields:
            kwargs['fields'] = fields.split(",")
        
        # Return an instance of the selected serializer class
        return self.get_serializer_class()(*args, **kwargs)

    def get_serializer_class(self):
        # Pick serializer acording to request
        fields = self.request.query_params.get("fields", None)
        if fields:
            return SInvoiceDynamicSerializer
        # Default Serializer
        else:
            return SaleInvoicesSerializer

class SaleInvoiceAPI(generics.RetrieveUpdateDestroyAPIView):
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

class SaleReceiptsAPI(generics.ListCreateAPIView):
    """CRUD API of sale receipts"""
    queryset = SaleReceipt.objects.all()
    serializer_class = SaleReceiptsSerializer

class SaleReceiptAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific sale receipt"""
    queryset = SaleReceipt.objects.all()
    serializer_class = SaleReceiptsSerializer
