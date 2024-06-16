"""API tests for ERP app"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Company_client


class APIErpTests(APITestCase):
    """Test ERP's apis"""
    @classmethod
    def setUpTestData(cls):
        """Populate DB"""
        cls.client1 = Company_client.objects.create(
            tax_number = "20361382481",
            name = "Client1 SRL",
            address = "Client street, Client city, Chile",
            email = "client1@email.com",
            phone = "1234567890",
        )
        cls.client2 = Company_client.objects.create(
            tax_number = "20361382482",
            name = "Client2 SRL",
            address = "Client street 2, Client city, Chile",
            email = "client2@email.com",
            phone = "0987654321",
        )
    
    def test_company_client_api(self):
        response = self.client.get(reverse("erp:clients_api"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Company_client.objects.count(), 2)
        self.assertContains(response, "20361382481")

    def test_detail_company_client_api(self):
        response = self.client.get(reverse("erp:client_api",
            kwargs={"pk": self.client2.pk}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Client street 2, Client city, Chile")
        self.assertNotContains(response, "20361382481")