"""API Views from erp app"""
from rest_framework import generics

from .models import Company_client
from .serializers import CClientSerializer


class CompanyClientAPI(generics.ListAPIView):
    """Show API list of clients"""
    queryset = Company_client.objects.all()
    serializer_class = CClientSerializer


class DetailCompanyClientAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific client"""
    queryset = Company_client.objects.all()
    serializer_class = CClientSerializer