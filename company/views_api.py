"""API views for Company app"""
from rest_framework import generics

from .models import FinancialYear
from .serializers import FinancialYearSerializer 

class CompanyYearAPI(generics.ListAPIView):
    """Show list of created years"""
    queryset = FinancialYear.objects.all()
    serializer_class = FinancialYearSerializer
    

class DetailCompanyYearAPI(generics.RetrieveUpdateDestroyAPIView):
    """CRUD API of specific year"""
    queryset = FinancialYear.objects.all()
    serializer_class = FinancialYearSerializer