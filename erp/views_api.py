"""API Views from erp app"""
from rest_framework import generics

from .models import Company_client, Supplier
from .serializers import CClientSerializer, SupplierSerializer


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