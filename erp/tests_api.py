"""API tests for ERP app"""
from django.urls import reverse
from django.test import tag
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Company_client, Supplier, Payment_method, Payment_term


@tag("erp_api")
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

        cls.supplier1 = Supplier.objects.create(
            tax_number = "20361382482",
            name = "Supplier1 SA",
            address = "Supplier street, Supplier city, Chile",
            email = "Supplier1@email.com",
            phone = "0987654321",
        )
        cls.supplier2 = Supplier.objects.create(
            tax_number = "20202020202",
            name = "Supplier2 SRL",
            address = "Supplier street 2, Supplier city, Chile",
            email = "supplier2@email.com",
            phone = "22222222222",
        )
        cls.pay_method1 = Payment_method.objects.create(
            pay_method = "Cash",
        )
        cls.pay_term1 = Payment_term.objects.create(
            pay_term = "30",
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

    def test_supplier_api(self):
        response = self.client.get(reverse("erp:suppliers_api"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Supplier.objects.count(), 2)
        self.assertContains(response, "Supplier2 SRL")

    def test_detail_supplier_api(self):
        response = self.client.get(reverse("erp:supplier_api",
            kwargs={"pk": self.supplier1.pk}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Supplier street, Supplier city, Chile")
        self.assertNotContains(response, "22222222222")

    def test_payment_method_api(self):
        response = self.client.get(reverse("erp:payment_method_api"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Payment_method.objects.count(), 1)
        self.assertContains(response, "Cash")

    def test_payment_term_api(self):
        response = self.client.get(reverse("erp:payment_term_api"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Payment_term.objects.count(), 1)
        self.assertContains(response, 30)