"""API tests for ERP app"""
import datetime
from decimal import Decimal
from django.urls import reverse
from django.test import tag
from rest_framework import status
from rest_framework.test import APITestCase

from company.models import Company
from .models import (Company_client, Supplier, Payment_method, Payment_term,
    Point_of_sell, Document_type, Sale_invoice)


@tag("erp_api")
class APIErpTests(APITestCase):
    """Test ERP's apis"""
    @classmethod
    def setUpTestData(cls):
        """Populate DB"""
        cls.company = Company.objects.create(
            tax_number = "20361382480",
            name = "Test Company SRL",
            address = "fake street 123, fakycity, Argentina",
            email = "testcompany@email.com",
            phone = "5493465406182",
            creation_date = datetime.date(1991, 3, 10),
            closing_date = datetime.date(2024, 6, 30),
        )
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
        cls.pay_method2 = Payment_method.objects.create(
            pay_method = "Transfer",
        )
        cls.pay_term1 = Payment_term.objects.create(
            pay_term = "30",
        )
        cls.pay_term2 = Payment_term.objects.create(
            pay_term = "0",
        )
        cls.pos1 = Point_of_sell.objects.create(
            pos_number = "00001",
        )
        cls.pos2 = Point_of_sell.objects.create(
            pos_number = "00002",
        )
        cls.pos3 = Point_of_sell.objects.create(
            pos_number = "00003",
        )
        cls.doc_type1 = Document_type.objects.create(
            code = "1",
            type = "FA",
            type_description = "FACTURAS A",
            hide = False,
        )
        cls.doc_type2 = Document_type.objects.create(
            code = "2",
            type = "FB",
            type_description = "FACTURAS B",
        )
        cls.sale_invoice = Sale_invoice.objects.create(
            type = cls.doc_type1,
            point_of_sell = cls.pos1,
            number = "00000001",
            description = "Test sale invoice",
            sender = cls.company,
            recipient = cls.client1,
            payment_method = cls.pay_method1,
            payment_term = cls.pay_term1,
            taxable_amount = Decimal("1000"),
            not_taxable_amount = Decimal("90.01"),
            VAT_amount = Decimal("210"),
        )
        cls.sale_invoice2 = Sale_invoice.objects.create(
            type = cls.doc_type1,
            point_of_sell = cls.pos1,
            number = "2",
            description = "Some products",
            sender = cls.company,
            recipient = cls.client2,
            payment_method = cls.pay_method2,
            payment_term = cls.pay_term2,
            taxable_amount = Decimal("2000"),
            not_taxable_amount = Decimal("180.02"),
            VAT_amount = Decimal("420"),
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

    def test_payment_methods_api(self):
        response = self.client.get(reverse("erp:payment_methods_api"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Payment_method.objects.count(), 2)
        self.assertContains(response, "Transfer")
    
    def test_payment_method_api(self):
        response = self.client.get(reverse("erp:payment_method_api",
            kwargs={"pk": self.pay_method1.pk}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Cash")
        self.assertNotContains(response, "Transfer")

    def test_payment_terms_api(self):
        response = self.client.get(reverse("erp:payment_terms_api"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Payment_term.objects.count(), 2)
        self.assertContains(response, "30")

    def test_payment_term_api(self):
        response = self.client.get(reverse("erp:payment_term_api",
            kwargs={"pk": self.pay_term2.pk}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "0")
        self.assertNotContains(response, "30")

    def test_points_of_sell_api(self):
        response = self.client.get(reverse("erp:pos_api"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Point_of_sell.objects.count(), 3)
        self.assertContains(response, "00003")

    def test_point_of_sell_api(self):
        response = self.client.get(reverse("erp:detail_pos_api",
            kwargs={"pk": self.pos3.pk}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "00003")
        self.assertNotContains(response, "00002")

    def test_doc_types_api(self):
        response = self.client.get(reverse("erp:doc_types_api"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Document_type.objects.count(), 2)
        self.assertContains(response, "FACTURAS A")

    def test_doc_type_api(self):
        response = self.client.get(reverse("erp:doc_type_api",
            kwargs={"pk": self.doc_type2.pk}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "FACTURAS B")
        self.assertNotContains(response, "FACTURAS A")

    def test_sale_invoices_api(self):
        response = self.client.get(reverse("erp:sale_invoices_api"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Sale_invoice.objects.count(), 2)
        self.assertContains(response, "90.01")
        self.assertContains(response, "00000002")

    def test_sale_invoice_api(self):
        response = self.client.get(reverse("erp:sale_invoice_api",
            kwargs={"pk": self.sale_invoice.pk}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "00000001")
        self.assertNotContains(response, "Some products")