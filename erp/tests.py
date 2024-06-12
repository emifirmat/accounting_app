import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

# Create your tests here.
from .models import (Company_client, Supplier, Client_current_account,
    Supplier_current_account, Payment_method, Payment_term, Sale_invoice,
    Sale_receipt, Purchase_invoice, Purchase_receipt)
from company.models import Company, Calendar


# Create your tests here.
class ErpTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Populate DB for testing ERP models"""
        cls.company = Company.objects.create(
            tax_number = "20361382480",
            name = "Test Company SRL",
            address = "fake street 123, fakycity, Argentina",
            email = "testcompany@email.com",
            phone = "5493465406182",
            creation_date = datetime.date(1991, 3, 10),
            closing_date = datetime.date(2024, 6, 30),
        )

        cls.calendar = Calendar.objects.create(
            starting_date = cls.company,
        )

        cls.company_client = Company_client.objects.create(
            tax_number = "20361382481",
            name = "Client1 SRL",
            address = "Client street, Client city, Chile",
            email = "client1@email.com",
            phone = "1234567890",
        )

        cls.supplier = Supplier.objects.create(
            tax_number = "20361382482",
            name = "Supplier1 SA",
            address = "Supplier street, Supplier city, Chile",
            email = "Supplier1@email.com",
            phone = "0987654321",
        )

        cls.client_ca = Client_current_account.objects.create(
            client = cls.company_client,
        )

        cls.supplier_ca = Supplier_current_account.objects.create(
            supplier = cls.supplier,
            amount = "10999.99",
        )

        cls.payment_method = Payment_method.objects.create(
            pay_method = "cash",
        )

        cls.payment_method2 = Payment_method.objects.create(
            pay_method = "transfer",
        )

        cls.payment_term = Payment_term.objects.create(
            pay_term = "0",
        )

        cls.payment_term2 = Payment_term.objects.create(
            pay_term = "30",
        )

        cls.sale_invoice = Sale_invoice.objects.create(
            type = "A",
            point_of_sell = "00001",
            number = "00000001",
            description = "Test sale invoice",
            sender = cls.company,
            recipient = cls.company_client,
            payment_method = cls.payment_method,
            payment_term = cls.payment_term,
            taxable_amount = "1000",
            not_taxable_amount = "90.01",
            VAT_amount = "210",
        )

        cls.sale_receipt = Sale_receipt.objects.create(
            type = "A",
            point_of_sell = "00001",
            number = "00000001",
            description = "Test sale receipt",
            related_invoice = cls.sale_invoice,
            sender = cls.company,
            recipient = cls.company_client,
            total_amount = "1300.01",
        )

        cls.purchase_invoice = Purchase_invoice.objects.create(
            type = "B",
            point_of_sell = "00231",
            number = "00083051",
            description = "Test purchase invoice",
            sender = cls.supplier,
            recipient = cls.company,
            payment_method = cls.payment_method2,
            payment_term = cls.payment_term2,
            taxable_amount = "200",
            not_taxable_amount = "0",
            VAT_amount = "42",
        )

        cls.purchase_receipt = Purchase_receipt.objects.create(
            type = "B",
            point_of_sell = "00231",
            number = "00000023",
            description = "Test purchase receipt",
            related_invoice = cls.purchase_invoice,
            sender = cls.supplier,
            recipient = cls.company,
            total_amount = "242",
        )

    def test_company_client_content(self):
        company_clients = Company_client.objects.all()
        self.assertEqual(company_clients.count(), 1)
        self.assertEqual(self.company_client.tax_number, "20361382481")
        self.assertEqual(self.company_client.name, "Client1 SRL")
        self.assertEqual(self.company_client.email, "client1@email.com")
        self.assertEqual(self.company_client.phone, "1234567890")
        self.assertEqual(self.company_client.address, "Client street, Client city, Chile")
        self.assertEqual(str(self.company_client), "Client1 SRL | 20361382481")

    def test_supplier_content(self):
        suppliers = Supplier.objects.all()
        self.assertEqual(suppliers.count(), 1)
        self.assertEqual(self.supplier.tax_number, "20361382482")
        self.assertEqual(self.supplier.name, "Supplier1 SA")
        self.assertEqual(self.supplier.email, "Supplier1@email.com")
        self.assertEqual(self.supplier.phone, "0987654321")
        self.assertEqual(self.supplier.address, "Supplier street, Supplier city, Chile")
        self.assertEqual(str(self.supplier), "Supplier1 SA | 20361382482")

    def test_client_current_account_content(self):
        client_ca_all = Client_current_account.objects.all()
        self.assertEqual(client_ca_all.count(), 1)
        self.assertEqual(self.client_ca.client, self.company_client)
        self.assertEqual(self.client_ca.amount, 0)

    def test_supplier_current_account_content(self):
        supplier_ca_all = Client_current_account.objects.all()
        self.assertEqual(supplier_ca_all.count(), 1)
        self.assertEqual(self.supplier_ca.supplier, self.supplier)
        self.assertEqual(self.supplier_ca.amount, "10999.99")

    def test_payment_method_content(self):
        payment_methods = Payment_method.objects.all()
        self.assertEqual(payment_methods.count(), 2)
        self.assertEqual(self.payment_method2.pay_method, "transfer")
        self.assertEqual(str(self.payment_method2), "transfer")

    def test_payment_term_content(self):
        payment_terms = Payment_term.objects.all()
        self.assertEqual(payment_terms.count(), 2)
        self.assertEqual(self.payment_term2.pay_term, "30")
        self.assertEqual(str(self.payment_term2), "30 days")
    
    def test_sale_invoice_content(self):
        invoices = Sale_invoice.objects.all()
        self.assertEqual(invoices.count(), 1)
        self.assertEqual(self.sale_invoice.type, "A")
        self.assertEqual(self.sale_invoice.point_of_sell, "00001")
        self.assertEqual(self.sale_invoice.number, "00000001")
        self.assertEqual(self.sale_invoice.description, "Test sale invoice")
        self.assertEqual(self.sale_invoice.sender, self.company)
        self.assertEqual(self.sale_invoice.recipient, self.company_client)
        self.assertEqual(self.sale_invoice.payment_method, self.payment_method)
        self.assertEqual(self.sale_invoice.payment_term, self.payment_term)
        self.assertEqual(self.sale_invoice.taxable_amount, "1000")
        self.assertEqual(self.sale_invoice.not_taxable_amount, "90.01")
        self.assertEqual(self.sale_invoice.VAT_amount, "210")
        self.assertEqual(
            str(self.sale_invoice),
            f"00001-00000001 | A | {self.sale_invoice.issue_date}"
        )

    def test_sale_invoice_constraint(self):
        sale_invoice2 = Sale_invoice.objects.create(
            type = "A",
            point_of_sell = "1",
            number = "2",
            description = "Test 2 sale invoice",
            sender = self.company,
            recipient = self.company_client,
            payment_method = self.payment_method2,
            payment_term = self.payment_term2,
            taxable_amount = "1010",
            not_taxable_amount = "90.01",
            VAT_amount = "212.10",
        )

        invoices = Sale_invoice.objects.all()
        self.assertEqual(invoices.count(), 2)

        with self.assertRaises(IntegrityError):
            sale_invoice3 = Sale_invoice.objects.create(
                type = "A",
                point_of_sell = "00001",
                number = "00000002",
                description = "Test 2 sale invoice",
                sender = self.company,
                recipient = self.company_client,
                payment_method = self.payment_method2,
                payment_term = self.payment_term2,
                taxable_amount = "1010",
                not_taxable_amount = "90.01",
                VAT_amount = "212.10",
            )

    def test_sale_invoice_decimal_places(self):
        # 1 digit
        self.sale_invoice.taxable_amount = "1.1"
        self.sale_invoice.save()
        self.assertEqual(self.sale_invoice.taxable_amount, "1.1")
        # 3 digits
        with self.assertRaises(ValidationError):
            self.sale_invoice.VAT_amount = "0.564"
            self.sale_invoice.full_clean()

    def test_sale_receipt_content(self):
        sale_receipts = Sale_receipt.objects.all()
        self.assertEqual(sale_receipts.count(), 1)
        self.assertEqual(self.sale_receipt.type, "A")
        self.assertEqual(self.sale_receipt.point_of_sell, "00001")
        self.assertEqual(self.sale_receipt.number, "00000001")
        self.assertEqual(self.sale_receipt.description, "Test sale receipt")
        self.assertEqual(self.sale_receipt.related_invoice, self.sale_invoice)
        self.assertEqual(self.sale_receipt.sender, self.company)
        self.assertEqual(self.sale_receipt.recipient, self.company_client)
        self.assertEqual(self.sale_receipt.total_amount, "1300.01")
        self.assertEqual(
            str(self.sale_receipt),
            f"00001-00000001 | A | {self.sale_receipt.issue_date}"
        )
        

    def test_sale_receipt_constraint(self):
        sale_receipt2 = Sale_receipt.objects.create(
            type = "A",
            point_of_sell = "1",
            number = "2",
            description = "Test 2 sale receipt",
            sender = self.company,
            recipient = self.company_client,
            related_invoice = self.sale_invoice,
            total_amount = "1312.11",
 
        )

        receipts = Sale_receipt.objects.all()
        self.assertEqual(receipts.count(), 2)

        with self.assertRaises(IntegrityError):
            sale_receipt3 = Sale_receipt.objects.create(
                type = "A",
                point_of_sell = "00001",
                number = "00000001",
                description = "Test 3 sale receipt",
                sender = self.company,
                recipient = self.company_client,
                related_invoice = self.sale_invoice,
                total_amount = "4000.11",
            )

    
    def test_purchase_invoice_content(self):
        invoices = Purchase_invoice.objects.all()
        self.assertEqual(invoices.count(), 1)
        self.assertEqual(self.purchase_invoice.type, "B")
        self.assertEqual(self.purchase_invoice.point_of_sell, "00231")
        self.assertEqual(self.purchase_invoice.number, "00083051")
        self.assertEqual(self.purchase_invoice.description, "Test purchase invoice")
        self.assertEqual(self.purchase_invoice.sender, self.supplier)
        self.assertEqual(self.purchase_invoice.recipient, self.company)
        self.assertEqual(self.purchase_invoice.payment_method, self.payment_method2)
        self.assertEqual(self.purchase_invoice.payment_term, self.payment_term2)
        self.assertEqual(self.purchase_invoice.taxable_amount, "200")
        self.assertEqual(self.purchase_invoice.not_taxable_amount, "0")
        self.assertEqual(self.purchase_invoice.VAT_amount, "42")
        self.assertEqual(
            str(self.purchase_invoice),
            f"00231-00083051 | B | {self.purchase_invoice.issue_date}"
        )

    def test_purchase_invoice_constraint(self):
        purchase_invoice2 = Purchase_invoice.objects.create(
            type = "B",
            point_of_sell = "231",
            number = "99992",
            description = "Test 2 purchase invoice",
            sender = self.supplier,
            recipient = self.company,
            payment_method = self.payment_method2,
            payment_term = self.payment_term2,
            taxable_amount = "1010",
            not_taxable_amount = "90.01",
            VAT_amount = "212.10",
        )

        invoices = Purchase_invoice.objects.all()
        self.assertEqual(invoices.count(), 2)

        with self.assertRaises(IntegrityError):
            purhcase_invoice3 = Purchase_invoice.objects.create(
                type = "B",
                point_of_sell = "00231",
                number = "00083051",
                description = "Test 3 purchase invoice",
                sender = self.supplier,
                recipient = self.company,
                payment_method = self.payment_method,
                payment_term = self.payment_term,
                taxable_amount = "1010",
                not_taxable_amount = "90.01",
                VAT_amount = "212.10",
            )

    def test_purchase_receipt_content(self):
        purchase_receipts = Purchase_receipt.objects.all()
        self.assertEqual(purchase_receipts.count(), 1)
        self.assertEqual(self.purchase_receipt.type, "B")
        self.assertEqual(self.purchase_receipt.point_of_sell, "00231")
        self.assertEqual(self.purchase_receipt.number, "00000023")
        self.assertEqual(self.purchase_receipt.description, "Test purchase receipt")
        self.assertEqual(self.purchase_receipt.related_invoice, self.purchase_invoice)
        self.assertEqual(self.purchase_receipt.sender, self.supplier)
        self.assertEqual(self.purchase_receipt.recipient, self.company)
        self.assertEqual(self.purchase_receipt.total_amount, "242")
        self.assertEqual(
            str(self.purchase_receipt),
            f"00231-00000023 | B | {self.purchase_receipt.issue_date}"
        )
    
    def test_purchase_receipt_constraint(self):
        purchase_receipt2 = Purchase_receipt.objects.create(
            type = "B",
            point_of_sell = "231",
            number = "2",
            description = "Test 2 purchase receipt",
            sender = self.supplier,
            recipient = self.company,
            related_invoice = self.purchase_invoice,
            total_amount = "1312.11",
        )

        receipts = Purchase_receipt.objects.all()
        self.assertEqual(receipts.count(), 2)

        with self.assertRaises(IntegrityError):
            purchase_receipt3 = Purchase_receipt.objects.create(
                type = "B",
                point_of_sell = "00231",
                number = "00000023",
                description = "Test 3 purchase receipt",
                sender = self.supplier,
                recipient = self.company,
                related_invoice = self.purchase_invoice,
                total_amount = "4000.11",
            )