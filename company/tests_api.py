"""Tests for company api"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import FinancialYear
from utils.base_tests import APIBaseTest


class APICompanyTests(APIBaseTest):
    """Test company's app API"""
    @classmethod
    def setUpTestData(cls):
        cls.year1 = FinancialYear.objects.create(year = "2024", current = True)
        cls.year2 = FinancialYear.objects.create(year = "2023")
    
    def test_company_years_api(self):
        self.check_api_get_response(
            "/company/api/years",
            "company:years_api",
            page_content=[self.year1, "true", "false"],
            count=2,
        )

    def test_detail_company_year_api(self):
        self.check_api_get_response(
            f"/company/api/years/{self.year2.pk}",
            ["company:year_api", {"pk": self.year2.pk}],
            page_content=[self.year2],
            wrong_content=self.year1,
        )
        
        