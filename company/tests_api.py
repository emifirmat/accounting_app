"""Tests for company api"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import FinancialYear


class APICompanyTests(APITestCase):
    """Test company's app API"""
    @classmethod
    def setUpTestData(cls):
        cls.year = FinancialYear.objects.create(year = "2023")
        cls.year2 = FinancialYear.objects.create(year = "2024")
    
    def test_company_years_api(self):
        response = self.client.get(reverse("company:years_api"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FinancialYear.objects.count(), 2)
        self.assertContains(response, self.year)

    def test_detail_company_year_api(self):
        response = self.client.get(reverse("company:year_api",
            kwargs={"pk": self.year2.pk}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.year2)
        