import datetime, os
import pprint
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase, tag
from django.urls import reverse


# Create your tests here.
from ..models import (CompanyClient, Supplier, ClientCurrentAccount,
    SupplierCurrentAccount, PaymentMethod, PaymentTerm, SaleInvoice,
    SaleInvoiceLine, SaleReceipt, PurchaseInvoice, PurchaseInvoiceLine,
    PurchaseReceipt, PointOfSell, DocumentType)
from company.models import Company, FinancialYear

from utils.utils_tests import get_file
from utils.base_tests import BackBaseTest, CreateDbInstancesMixin


# Create your tests here.
@tag("erp_db_view")
class ErpTestCase(CreateDbInstancesMixin, BackBaseTest):
    @classmethod
    def setUpTestData(cls):
        """Populate DB for testing ERP models"""
        super().setUpTestData()

        cls.c_client1 = CompanyClient.objects.create(
            tax_number = "20361382481",
            name = "Client1 SRL",
            address = "Client street, Client city, Chile",
            email = "client1@email.com",
            phone = "1234567890",
        )
        cls.c_client2 = CompanyClient.objects.create(
            tax_number = "99999999999",
            name = "Client2 SA",
            address = "Client2 street, Client city, Argentina",
            email = "client2@email.com",
            phone = "12443131241",
        )

        cls.supplier1 = Supplier.objects.create(
            tax_number = "20361382482",
            name = "Supplier1 SA",
            address = "Supplier street, Supplier city, Chile",
            email = "Supplier1@email.com",
            phone = "0987654321",
        )

        cls.supplier2 = Supplier.objects.create(
            tax_number = "30361382485",
            name = "Supplier2 SRL",
            address = "Supplier2 street, Supplier city, Chile",
            email = "supplier2@email.com",
            phone = "987654321",
        )

        cls.client_ca = ClientCurrentAccount.objects.create(
            client = cls.c_client1,
        )

        cls.supplier_ca = SupplierCurrentAccount.objects.create(
            supplier = cls.supplier1,
            amount = "10999.99",
        )

        cls.pos1 = PointOfSell.objects.create(pos_number="1")
        cls.pos2 = PointOfSell.objects.create(pos_number="2")

        cls.doc_type1 = DocumentType.objects.create(
            type = "A",
            code = "001",
            type_description = "Invoice A",
            hide = False,
        )
        cls.doc_type2 = DocumentType.objects.create(
            type = "B",
            code = "2",
            type_description = "Invoice B",
            hide = False,
        )
        cls.doc_type3 = DocumentType.objects.create(
            type = "E",
            code = "19",
            type_description = "Invoice E",
        )

        cls.pay_method1 = PaymentMethod.objects.create(pay_method = "Cash")
        cls.pay_method2 = PaymentMethod.objects.create(pay_method = "Transfer")

        cls.pay_term1 = PaymentTerm.objects.create(pay_term = "0")
        cls.pay_term2 = PaymentTerm.objects.create(pay_term = "30")

        cls.sale_invoice1 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 21),
            type = cls.doc_type1,
            point_of_sell = cls.pos1,
            number = "00000001",
            sender = cls.company,
            recipient = cls.c_client1,
            payment_method = cls.pay_method1,
            payment_term = cls.pay_term1,
            # Set collected manually, as this attribute is modified in views.
            collected = True,
        )
        cls.sale_invoice1_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = cls.sale_invoice1,
            description = "Test sale invoice",
            taxable_amount = Decimal("1000"),
            not_taxable_amount = Decimal("90.01"),
            vat_amount = Decimal("210"),
        )
        cls.sale_invoice1_line2 = SaleInvoiceLine.objects.create(
            sale_invoice = cls.sale_invoice1,
            description = "Other products",
            taxable_amount = Decimal("999"),
            not_taxable_amount = Decimal("00.01"),
            vat_amount = Decimal("209.99"),
        )

        cls.sale_receipt1 = SaleReceipt.objects.create(
            issue_date = datetime.date(2024, 2, 21),
            point_of_sell = cls.pos1,
            number = "00000001",
            description = "Test sale receipt",
            related_invoice = cls.sale_invoice1,
            sender = cls.company,
            recipient = cls.c_client1,
            total_amount = Decimal("2509.01"),
        )

        cls.purchase_invoice1 = PurchaseInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 13),
            type = cls.doc_type2,
            point_of_sell = "00231",
            number = "00083051",
            sender = cls.supplier1,
            recipient = cls.company,
            payment_method = cls.pay_method2,
            payment_term = cls.pay_term2,
        )

        cls.purchase_invoice_line1 = PurchaseInvoiceLine.objects.create(
            purchase_invoice = cls.purchase_invoice1,
            description = "Test purchase invoice",
            taxable_amount = Decimal("200"),
            not_taxable_amount = Decimal("0"),
            vat_amount = Decimal("42"),
        )

        cls.purchase_receipt1 = PurchaseReceipt.objects.create(
            issue_date = datetime.date(2024, 2, 13),
            point_of_sell = "00231",
            number = "00000023",
            description = "Test purchase receipt",
            related_invoice = cls.purchase_invoice1,
            sender = cls.supplier1,
            recipient = cls.company,
            total_amount = Decimal("242"),
        )

    def create_extra_invoices(self):
        """Create extra invoices when a test demands it"""
        self.sale_invoice2 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 22),
            type = self.doc_type2,
            point_of_sell = self.pos1,
            number = "00000001",
            sender = self.company,
            recipient = self.c_client1,
            payment_method = self.pay_method2,
            payment_term = self.pay_term2,
        )
        SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice2,
            description = "Test 2 sale invoice",
            taxable_amount = Decimal("999.99"),
            not_taxable_amount = Decimal("0.02"),
            vat_amount = Decimal("209.09"),
        )

        self.sale_invoice3 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 23),
            type = self.doc_type1,
            point_of_sell = self.pos1,
            number = "00000002",
            sender = self.company,
            recipient = self.c_client1,
            payment_method = self.pay_method1,
            payment_term = self.pay_term1,
        )
        SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice3,
            description = "Test 2 sale invoice",
            taxable_amount = Decimal("500"),
            not_taxable_amount = Decimal("20.01"),
            vat_amount = Decimal("80"),
        )

        self.sale_invoice4 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 23),
            type = self.doc_type1,
            point_of_sell = self.pos1,
            number = "00000003",
            sender = self.company,
            recipient = self.c_client2,
            payment_method = self.pay_method2,
            payment_term = self.pay_term1,
        )
        SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice4,
            description = "Test 2 sale invoice",
            taxable_amount = Decimal("500"),
            not_taxable_amount = Decimal("20.01"),
            vat_amount = Decimal("80"),
        )

        self.sale_invoice5 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 24),
            type = self.doc_type2,
            point_of_sell = self.pos1,
            number = "00000002",
            sender = self.company,
            recipient = self.c_client1,
            payment_method = self.pay_method1,
            payment_term = self.pay_term1,
        )
        SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice5,
            description = "Test 2 sale invoice",
            taxable_amount = Decimal("5"),
            not_taxable_amount = Decimal("5"),
            vat_amount = Decimal("5"),
        )
        self.sale_invoice6 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 24),
            type = self.doc_type2,
            point_of_sell = self.pos1,
            number = "00000003",
            sender = self.company,
            recipient = self.c_client1,
            payment_method = self.pay_method2,
            payment_term = self.pay_term2,
        )
        SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice6,
            description = "Test a sale invoice",
            taxable_amount = Decimal("6"),
            not_taxable_amount = Decimal("6"),
            vat_amount = Decimal("6"),
        )
        self.sale_invoice7 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 25),
            type = self.doc_type1,
            point_of_sell = self.pos2,
            number = "00000001",
            sender = self.company,
            recipient = self.c_client1,
            payment_method = self.pay_method1,
            payment_term = self.pay_term1,
        )
        SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice7,
            description = "Test b sale invoice",
            taxable_amount = Decimal("7"),
            not_taxable_amount = Decimal("7"),
            vat_amount = Decimal("7"),
        )
        self.sale_invoice8 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 25),
            type = self.doc_type1,
            point_of_sell = self.pos2,
            number = "00000002",
            sender = self.company,
            recipient = self.c_client1,
            payment_method = self.pay_method2,
            payment_term = self.pay_term1,
        )
        SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice8,
            description = "Test c sale invoice",
            taxable_amount = Decimal("8"),
            not_taxable_amount = Decimal("8"),
            vat_amount = Decimal("8"),   
        )
        self.sale_invoice9 = SaleInvoice.objects.create(
            issue_date=datetime.date(2024, 1, 26),
            type=self.doc_type2,
            point_of_sell=self.pos2,
            number="00000001",
            sender=self.company,
            recipient=self.c_client2,
            payment_method=self.pay_method1,
            payment_term=self.pay_term1
        )
        self.sale_invoice9_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice9,
            description = "Ninth sale invoice",
            taxable_amount = Decimal("9"),
            not_taxable_amount = Decimal("9"),
            vat_amount = Decimal("9"),
        )
        self.sale_invoice10 = SaleInvoice.objects.create(
            issue_date=datetime.date(2024, 1, 26),
            type=self.doc_type2,
            point_of_sell=self.pos2,
            number="00000002",
            sender=self.company,
            recipient=self.c_client2,
            payment_method=self.pay_method2,
            payment_term=self.pay_term1
        )
        self.sale_invoice10_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice10,
            description = "Tenth sale invoice",
            taxable_amount = Decimal("10"),
            not_taxable_amount = Decimal("10"),
            vat_amount = Decimal("10"),
        )

        self.sale_invoice11 = SaleInvoice.objects.create(
            issue_date = datetime.date(2025, 6, 23),
            type = self.doc_type1,
            point_of_sell = self.pos1,
            number = "00000005",
            sender = self.company,
            recipient = self.c_client1,
            payment_method = self.pay_method1,
            payment_term = self.pay_term1,
        )
        SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice11,
            description = "Eleventh sale invoice",
            taxable_amount = Decimal("500"),
            not_taxable_amount = Decimal("20.01"),
            vat_amount = Decimal("80"),
        )

    def create_extra_receipts(self):
        """ Create extra receipts for some tests. """
        self.create_extra_invoices() # Function dependant
        self.sale_invoice2.collected = True # Update invoice 2 status
        
        self.sale_receipt2 = SaleReceipt.objects.create(
            issue_date = datetime.date(2024, 2, 22),
            point_of_sell = self.pos1,
            number = "00000002",
            description = "Second receipt",
            related_invoice = self.sale_invoice2,
            sender = self.company,
            recipient = self.c_client1,
            total_amount = Decimal("600.01"),
        )
        self.sale_receipt3 = SaleReceipt.objects.create(
            issue_date = datetime.date(2024, 2, 23),
            point_of_sell = self.pos1,
            number = "00000003",
            description = "Third receipt",
            related_invoice = self.sale_invoice2,
            sender = self.company,
            recipient = self.c_client1,
            total_amount = Decimal("609"),
        )
        self.sale_receipt4 = SaleReceipt.objects.create(
            issue_date = datetime.date(2024, 3, 24),
            point_of_sell = self.pos2,
            number = "00000001",
            description = "Fourth receipt",
            related_invoice = self.sale_invoice5,
            sender = self.company,
            recipient = self.c_client1,
            total_amount = Decimal("5"),
        )
        self.sale_receipt5 = SaleReceipt.objects.create(
            issue_date = datetime.date(2024, 3, 24),
            point_of_sell = self.pos2,
            number = "00000002",
            description = "Fifth receipt",
            related_invoice = self.sale_invoice5,
            sender = self.company,
            recipient = self.c_client1,
            total_amount = Decimal("5"),
        )
        self.sale_receipt6 = SaleReceipt.objects.create(
            issue_date = datetime.date(2024, 3, 24),
            point_of_sell = self.pos1,
            number = "00000004",
            description = "Sixth receipt",
            related_invoice = self.sale_invoice6,
            sender = self.company,
            recipient = self.c_client2,
            total_amount = Decimal("8"),
        )
        self.sale_receipt7 = SaleReceipt.objects.create(
            issue_date = datetime.date(2025, 7, 24),
            point_of_sell = self.pos1,
            number = "00000005",
            description = "Seventh receipt",
            related_invoice = self.sale_invoice11,
            sender = self.company,
            recipient = self.c_client1,
            total_amount = Decimal("300.99"),
        )


    def test_company_client_content(self):
        company_clients = CompanyClient.objects.all()
        self.assertEqual(company_clients.count(), 2)
        self.assertEqual(self.c_client1.tax_number, "20361382481")
        self.assertEqual(self.c_client1.name, "CLIENT1 SRL")
        self.assertEqual(self.c_client1.email, "client1@email.com")
        self.assertEqual(self.c_client1.phone, "1234567890")
        self.assertEqual(self.c_client1.address, "Client Street, Client City, Chile")
        self.assertEqual(str(self.c_client1), "CLIENT1 SRL | 20361382481")

    def test_supplier_content(self):
        suppliers = Supplier.objects.all()
        self.assertEqual(suppliers.count(), 2)
        self.assertEqual(self.supplier1.tax_number, "20361382482")
        self.assertEqual(self.supplier1.name, "SUPPLIER1 SA")
        self.assertEqual(self.supplier1.email, "Supplier1@email.com")
        self.assertEqual(self.supplier1.phone, "0987654321")
        self.assertEqual(self.supplier1.address, "Supplier Street, Supplier City, Chile")
        self.assertEqual(str(self.supplier1), "SUPPLIER1 SA | 20361382482")

    def test_client_current_account_content(self):
        client_ca_all = ClientCurrentAccount.objects.all()
        self.assertEqual(client_ca_all.count(), 1)
        self.assertEqual(self.client_ca.client, self.c_client1)
        self.assertEqual(self.client_ca.amount, 0)

    def test_supplier_current_account_content(self):
        supplier_ca_all = ClientCurrentAccount.objects.all()
        self.assertEqual(supplier_ca_all.count(), 1)
        self.assertEqual(self.supplier_ca.supplier, self.supplier1)
        self.assertEqual(self.supplier_ca.amount, "10999.99")

    def test_company_point_of_sell_content(self):
        pos_all = PointOfSell.objects.all()
        self.assertEqual(pos_all.count(), 2)
        self.assertEqual(self.pos1.pos_number, "00001")
        self.assertEqual(str(self.pos1), "00001")
    
    def test_document_type_content(self):
        doc_type_all = DocumentType.objects.all()
        self.assertEqual(doc_type_all.count(), 3)
        self.assertEqual(self.doc_type1.type, "A")
        self.assertEqual(self.doc_type1.code, "001")
        self.assertEqual(self.doc_type1.type_description, "INVOICE A")
        self.assertEqual(self.doc_type1.hide, False)
        self.assertEqual(str(self.doc_type1), "001 | A")

    def test_document_type_validator(self):
        with self.assertRaises(ValidationError):
            doc_3 = DocumentType.objects.create(
                type = "3",
                code = "003",
                type_description = "Invoice C",
            )
            doc_3.full_clean()
    
    def test_payment_method_content(self):
        payment_methods = PaymentMethod.objects.all()
        self.assertEqual(payment_methods.count(), 2)
        self.assertEqual(self.pay_method2.pay_method, "Transfer")
        self.assertEqual(str(self.pay_method2), "Transfer")

    def test_payment_term_content(self):
        payment_terms = PaymentTerm.objects.all()
        self.assertEqual(payment_terms.count(), 2)
        self.assertEqual(self.pay_term2.pay_term, "30")
        self.assertEqual(str(self.pay_term2), "30 days")
    
    def test_sale_invoice_content(self):
        invoices = SaleInvoice.objects.all()
        self.assertEqual(invoices.count(), 1)
        self.assertEqual(self.sale_invoice1.issue_date, datetime.date(2024, 1, 21))
        self.assertEqual(self.sale_invoice1.type, self.doc_type1)
        self.assertEqual(self.sale_invoice1.point_of_sell.pos_number, "00001")
        self.assertEqual(self.sale_invoice1.number, "00000001")
        self.assertEqual(self.sale_invoice1.sender, self.company)
        self.assertEqual(self.sale_invoice1.recipient, self.c_client1)
        self.assertEqual(self.sale_invoice1.payment_method, self.pay_method1)
        self.assertEqual(self.sale_invoice1.payment_term, self.pay_term1)
        self.assertEqual(self.sale_invoice1.collected, True)
        self.assertEqual(
            str(self.sale_invoice1), f"A 00001-00000001"
        )

    def test_sale_invoice_get_abosulte_url(self):
        response = self.client.get(self.sale_invoice1.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_sale_invoice_total_sum(self):
        self.assertAlmostEqual(self.sale_invoice1.total_lines_sum(),
            Decimal(2509.01))

    def test_sale_invoice_constraint(self):
        sale_invoice2 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 21),
            type = self.doc_type1,
            point_of_sell = self.pos1,
            number = "2",
            sender = self.company,
            recipient = self.c_client1,
            payment_method = self.pay_method2,
            payment_term = self.pay_term2,
        )

        invoices = SaleInvoice.objects.all()
        self.assertEqual(invoices.count(), 2)

        with self.assertRaises(IntegrityError):
            sale_invoice3 = SaleInvoice.objects.create(
                issue_date = datetime.date(2024, 1, 22),
                type = self.doc_type1,
                point_of_sell = self.pos1,
                number = "00000002",
                sender = self.company,
                recipient = self.c_client1,
                payment_method = self.pay_method2,
                payment_term = self.pay_term2,
            )

    def test_sale_invoice_line_content(self):
        invoice_lines = SaleInvoiceLine.objects.all()
        self.assertEqual(invoice_lines.count(), 2)
        self.assertEqual(self.sale_invoice1_line1.sale_invoice, self.sale_invoice1)
        self.assertEqual(self.sale_invoice1_line1.description, "Test sale invoice")
        self.assertEqual(self.sale_invoice1_line1.taxable_amount, Decimal("1000"))
        self.assertEqual(self.sale_invoice1_line1.not_taxable_amount, 
            Decimal("90.01"))
        self.assertEqual(self.sale_invoice1_line1.vat_amount, Decimal("210"))
        self.assertEqual(self.sale_invoice1_line1.total_amount, Decimal("1300.01"))
        self.assertEqual(
            str(self.sale_invoice1_line1), f"Test sale invoice | $ 1300.01"
        )

    def test_sale_invoice_line_decimal_places(self):
        # 1 digit
        self.sale_invoice1_line1.taxable_amount = Decimal("1.1")
        self.sale_invoice1_line1.save()
        self.assertEqual(self.sale_invoice1_line1.taxable_amount, Decimal("1.1"))
        # 3 digits
        with self.assertRaises(ValidationError):
            self.sale_invoice1_line1.vat_amount = Decimal("0.564")
            self.sale_invoice1_line1.full_clean()

    def test_sale_receipt_content(self):
        sale_receipts = SaleReceipt.objects.all()
        self.assertEqual(sale_receipts.count(), 1)
        self.assertEqual(self.sale_receipt1.issue_date, datetime.date(2024, 2, 21))
        self.assertEqual(self.sale_receipt1.point_of_sell.pos_number, "00001")
        self.assertEqual(self.sale_receipt1.number, "00000001")
        self.assertEqual(self.sale_receipt1.description, "Test sale receipt")
        self.assertEqual(self.sale_receipt1.related_invoice, self.sale_invoice1)
        self.assertEqual(self.sale_receipt1.sender, self.company)
        self.assertEqual(self.sale_receipt1.recipient, self.c_client1)
        self.assertEqual(self.sale_receipt1.total_amount, Decimal("2509.01"))
        self.assertEqual(
            str(self.sale_receipt1), f"00001-00000001"
        )

    def test_sale_receipt_constraint(self):
        sale_receipt2 = SaleReceipt.objects.create(
            issue_date = datetime.date(2024, 2, 21),
            point_of_sell = self.pos1,
            number = "2",
            description = "Test 2 sale receipt",
            sender = self.company,
            recipient = self.c_client1,
            related_invoice = self.sale_invoice1,
            total_amount = "1312.11",
        )

        receipts = SaleReceipt.objects.all()
        self.assertEqual(receipts.count(), 2)

        with self.assertRaises(IntegrityError):
            sale_receipt3 = SaleReceipt.objects.create(
                issue_date = datetime.date(2024, 2, 22),
                point_of_sell = self.pos1,
                number = "00000001",
                description = "Test 3 sale receipt",
                sender = self.company,
                recipient = self.c_client1,
                related_invoice = self.sale_invoice1,
                total_amount = "4000.11",
            )

    def test_purchase_invoice_content(self):
        invoices = PurchaseInvoice.objects.all()
        self.assertEqual(invoices.count(), 1)
        self.assertEqual(self.purchase_invoice1.issue_date, datetime.date(2024, 1, 13))
        self.assertEqual(self.purchase_invoice1.type, self.doc_type2)
        self.assertEqual(self.purchase_invoice1.point_of_sell, "00231")
        self.assertEqual(self.purchase_invoice1.number, "00083051")
        self.assertEqual(self.purchase_invoice1.sender, self.supplier1)
        self.assertEqual(self.purchase_invoice1.recipient, self.company)
        self.assertEqual(self.purchase_invoice1.payment_method, self.pay_method2)
        self.assertEqual(self.purchase_invoice1.payment_term, self.pay_term2)
        self.assertEqual(
            str(self.purchase_invoice1), f"B 00231-00083051"
        )

    def test_purchase_invoice_constraint(self):
        purchase_invoice2 = PurchaseInvoice.objects.create(
            issue_date=datetime.date(2024, 1, 13),
            type = self.doc_type2,
            point_of_sell = "231",
            number = "99992",
            sender = self.supplier1,
            recipient = self.company,
            payment_method = self.pay_method2,
            payment_term = self.pay_term2,
        )

        invoices = PurchaseInvoice.objects.all()
        self.assertEqual(invoices.count(), 2)

        with self.assertRaises(IntegrityError):
            purhcase_invoice3 = PurchaseInvoice.objects.create(
                issue_date=datetime.date(2024, 1, 14),
                type = self.doc_type2,
                point_of_sell = "00231",
                number = "00083051",
                sender = self.supplier1,
                recipient = self.company,
                payment_method = self.pay_method1,
                payment_term = self.pay_term1,
            )

    def test_purchase_invoice_line_content(self):
        invoice_lines = PurchaseInvoice.objects.all()
        self.assertEqual(invoice_lines.count(), 1)
        self.assertEqual(self.purchase_invoice_line1.purchase_invoice, 
            self.purchase_invoice1)
        self.assertEqual(self.purchase_invoice_line1.description, 
            "Test purchase invoice")
        self.assertEqual(self.purchase_invoice_line1.taxable_amount, 
            Decimal("200"))
        self.assertEqual(self.purchase_invoice_line1.not_taxable_amount, 
            Decimal("0"))
        self.assertEqual(self.purchase_invoice_line1.vat_amount, Decimal("42"))
        self.assertEqual(self.purchase_invoice_line1.total_amount, 242)
        self.assertEqual(
            str(self.purchase_invoice_line1), f"Test purchase invoice | $ 242"
        )

    def test_purchase_receipt_content(self):
        purchase_receipts = PurchaseReceipt.objects.all()
        self.assertEqual(purchase_receipts.count(), 1)
        self.assertEqual(self.purchase_receipt1.issue_date, datetime.date(2024, 2, 13))
        self.assertEqual(self.purchase_receipt1.point_of_sell, "00231")
        self.assertEqual(self.purchase_receipt1.number, "00000023")
        self.assertEqual(self.purchase_receipt1.description, "Test purchase receipt")
        self.assertEqual(self.purchase_receipt1.related_invoice, self.purchase_invoice1)
        self.assertEqual(self.purchase_receipt1.sender, self.supplier1)
        self.assertEqual(self.purchase_receipt1.recipient, self.company)
        self.assertEqual(self.purchase_receipt1.total_amount, Decimal("242"))
        self.assertEqual(
            str(self.purchase_receipt1), f"00231-00000023"
        )
    
    def test_purchase_receipt_constraint(self):
        purchase_receipt2 = PurchaseReceipt.objects.create(
            issue_date = datetime.date(2024, 2, 13),
            point_of_sell = "231",
            number = "2",
            description = "Test 2 purchase receipt",
            sender = self.supplier1,
            recipient = self.company,
            related_invoice = self.purchase_invoice1,
            total_amount = "1312.11",
        )

        receipts = PurchaseReceipt.objects.all()
        self.assertEqual(receipts.count(), 2)

        with self.assertRaises(IntegrityError):
            purchase_receipt3 = PurchaseReceipt.objects.create(
                issue_date = datetime.date(2024, 2, 14),
                point_of_sell = "00231",
                number = "00000023",
                description = "Test 3 purchase receipt",
                sender = self.supplier1,
                recipient = self.company,
                related_invoice = self.purchase_invoice1,
                total_amount = "4000.11",
            )

    def test_client_index_webpage(self):
        self.check_page_get_response(
            "/erp/client", 
            "erp:client_index", 
            "erp/client_index.html", 
            "Clients Overview"
        )
        
    def test_client_new_get(self):
        self.check_page_get_response(
            "/erp/client/new", 
            ["erp:person_new", {"person_type": "supplier"}], 
            "erp/person_new.html", 
            "Address:"
        )
        
    def test_client_new_post(self):    
        post_object = {
            "tax_number": "30361382485",
            "name": "Client2 SRL",
            "address": "Client2 street, Client city, Chile",
            "email": "client2@email.com",
            "phone": "987654321",
        }
        
        self.check_page_post_response(["erp:person_new",
            {"person_type": "client"}], post_object, 302, (CompanyClient, 3)
        )
        
    def test_client_new_post_error(self):
        post_object = {
            "tax_number": "20361382480",
            "name": "Client2 SRL",
            "address": "Client2 street, Client city, Chile",
            "email": "client2@email.com",
            "phone": "987654321",
        }
        
        response = self.check_page_post_response(["erp:person_new",
            {"person_type": "client"}], post_object, 200, (CompanyClient, 2)
        )
    
        # Check if error is displayed.
        self.assertEqual(response.context["form"].errors["tax_number"],
            ["The tax number you're trying to add belongs to the company."]
        )

    def test_client_new_multiple_post_csv(self):
        # Get file dir to test
        file = get_file("erp/tests/files/clients/clients.csv")

        self.check_page_post_response(["erp:person_new_multiple",
            {"person_type": "client"}], {"file": file}, 302, (CompanyClient, 8)
        )
            
        # Test DB was updated correctly
        client_great = CompanyClient.objects.get(tax_number="20123456780")
        self.assertEqual(client_great.tax_number, "20123456780")
        self.assertEqual(client_great.name, "GREAT SUGAR SA")
        self.assertEqual(client_great.address, "Mutiple Street 1, Dublin, Ireland")
        self.assertEqual(client_great.email, "mclient1@email.com")
        self.assertEqual(client_great.phone, "3412425841")
    
    def test_client_new_multiple_post_xls(self):
        file = get_file("erp/tests/files/clients/clients.xls")
        
        self.check_page_post_response(["erp:person_new_multiple",
            {"person_type": "client"}], {"file": file}, 302, (CompanyClient, 8)
        )
        
        # Test DB was updated correctly
        client_great = CompanyClient.objects.get(tax_number="20123456780")
        self.assertEqual(client_great.tax_number, "20123456780")
        self.assertEqual(client_great.name, "GREAT SUGAR SA")
        self.assertEqual(client_great.address, "Mutiple Street 1, Dublin, Ireland")
        self.assertEqual(client_great.email, "mclient1@email.com")
        self.assertEqual(client_great.phone, "3412425841")

    def test_client_new_multiple_post_xlsx(self):
        file = get_file("erp/tests/files/clients/clients.xlsx")
   
        self.check_page_post_response(["erp:person_new_multiple",
            {"person_type": "client"}], {"file": file}, 302, (CompanyClient, 8)
        )
    
        # Test DB was updated correctly
        client_great = CompanyClient.objects.get(tax_number="20123456780")
        self.assertEqual(client_great.tax_number, "20123456780")
        self.assertEqual(client_great.name, "GREAT SUGAR SA")
        self.assertEqual(client_great.address, "Mutiple Street 1, Dublin, Ireland")
        self.assertEqual(client_great.email, "mclient1@email.com")
        self.assertEqual(client_great.phone, "3412425841")

    @tag("erp_db_view_client_multiple_post_pdf")
    def test_client_new_multiple_post_pdf(self):
        file = get_file("erp/tests/files/clients/clients.pdf")

        page_content = self.check_page_post_response(["erp:person_new_multiple",
            {"person_type": "client"}], {"file": file}, 400, (CompanyClient, 2)
        )
        
        self.assertIn("Invalid file", page_content)        

    def test_client_new_multiple_post_repeated_client(self):
        # Get file dir to test
        file = get_file("erp/tests/files/clients/clientsbad2.csv")
      
        page_content = self.check_page_post_response(["erp:person_new_multiple",
            {"person_type": "client"}], {"file": file}, 400, (CompanyClient, 2)
        )
        
        self.assertIn("tax number already exists", page_content)

    def test_client_new_multiple_post_wrong_columns(self):
        # Get file dir to test
        file = get_file("erp/tests/files/sales/invoice_one_line.csv")
   
        page_content = self.check_page_post_response(["erp:person_new_multiple",
            {"person_type": "client"}], {"file": file}, 400, (CompanyClient, 2)
        )
        
        self.assertIn("The columns in your file don't match", page_content)

    def test_client_new_multiple_post_wrong_data(self):
        # Get file dir to test
        file = get_file("erp/tests/files/clients/clientsbad.csv")
   
        page_content = self.check_page_post_response(["erp:person_new_multiple",
            {"person_type": "client"}], {"file": file}, 400, (CompanyClient, 2)
        )
        
        for text in ["must be only digits", "value has at most", 
            "field cannot be blank"]:
            self.assertIn(text, page_content)
        

    def test_client_edit_get(self):
        self.check_page_get_response(
            "/erp/client/edit", 
            ["erp:person_edit", {"person_type": "client"}],
            "erp/person_edit.html", 
            ["CLIENT1 SRL", "20361382481", "Tax Number"],
            "Select"
        )

    def test_client_delete_get(self):
        self.check_page_get_response(
            "/erp/client/delete", 
            ["erp:person_delete", {"person_type": "client"}],
            "erp/person_delete.html", 
            ["CLIENT1 SRL", "20361382481", "Select"]
        )

    def test_client_related_documents(self):
        self.check_page_get_response(
            f"/erp/client/{self.c_client1.pk}/related_documents", 
            ["erp:person_rel_docs", {
                "person_type": "client",
                "person_pk": self.c_client1.pk
            }],
            "erp/person_related_docs.html", 
            ["Related Documents", "Receipt N° 00001-00000001", 
             "Invoice N° A 00001-00000001", "client N° 1"]
        )

    def test_client_related_documents_no(self):
        self.check_page_get_response(
            f"/erp/client/{self.c_client2.pk}/related_documents", 
            ["erp:person_rel_docs", {
                "person_type": "client",
                "person_pk": self.c_client2.pk
            }],
            "erp/person_related_docs.html", 
            ["Related Documents", "There isn't any related receipt.",
                "client N° 2", "There isn't any related invoice."]
        )

    def test_supplier_index_webpage(self):
        self.check_page_get_response(
            "/erp/supplier", 
            "erp:supplier_index", 
            "erp/supplier_index.html", 
            "Suppliers Overview"
        )
        
    def test_supplier_new_get(self):
        self.check_page_get_response(
            "/erp/supplier/new",
            ["erp:person_new", {"person_type": "supplier"}], 
            "erp/person_new.html",
            "Tax number:"
        )
        
    @tag("test")
    def test_supplier_new_post(self):    
        post_object = {
                "tax_number": "30361382486",
                "name": "Supplier3 SRL",
                "address": "Supplier3 street, Supplier city, Chile",
                "email": "supplier3@email.com",
                "phone": "987654321",
            }

        self.check_page_post_response(["erp:person_new",
            {"person_type": "supplier"}], post_object, 302, (Supplier, 3)
        )  
        
    def test_supplier_new_post_error(self):
        post_object = {
            "tax_number": "20361382480",
            "name": "Supplier3 SRL",
            "address": "Supplier3 street, Supplier city, Chile",
            "email": "supplier3@email.com",
            "phone": "987654321",
        }
        
        response = self.check_page_post_response(["erp:person_new",
            {"person_type": "supplier"}], post_object, 200, (Supplier, 2)
        )  

        # Check if an error is displayed.
        self.assertEqual(response.context["form"].errors["tax_number"],
            ["The tax number you're trying to add belongs to the company."]
        )
        

    def test_supplier_new_multiple_post_csv(self):
        # Note: As I use same view and template as clients, I only do one test to
        # check that suppliers db is update correctly
        # Get file dir to test
        file = get_file("erp/tests/files/suppliers/suppliers.csv")
        
        self.check_page_post_response(["erp:person_new_multiple",
            {"person_type": "supplier"}], {"file": file}, 302, (Supplier, 8)
        )  

        # Test DB was updated correctly
        supplier_great = Supplier.objects.get(tax_number="20123456780")
        self.assertEqual(supplier_great.tax_number, "20123456780")
        self.assertEqual(supplier_great.name, "GREAT SUGAR SA")
        self.assertEqual(supplier_great.address, "Mutiple Street 1, Dublin, Ireland")
        self.assertEqual(supplier_great.email, "mclient1@email.com")
        self.assertEqual(supplier_great.phone, "3412425841")

    def test_supplier_edit_get(self):
        self.check_page_get_response(
            "/erp/supplier/edit",
            ["erp:person_edit", {"person_type": "supplier"}], 
            "erp/person_edit.html",
            ["SUPPLIER1 SA", "20361382482", "Name"],
            "Select"
        )
        
    def test_supplier_delete_get(self):
        self.check_page_get_response(
            "/erp/supplier/delete",
            ["erp:person_delete", {"person_type": "supplier"}], 
            "erp/person_delete.html",
            ["SUPPLIER1 SA", "20361382482", "Select"]
        )
        
    def test_payment_conditions_webpage(self):
        self.check_page_get_response(
            "/erp/payment_conditions",
            "erp:payment_conditions", 
            "company/payment_conditions.html",
            "Payment Conditions"
        )

    def test_points_of_sell_webpage(self):
        self.check_page_get_response(
            "/erp/points_of_sell", 
            "erp:points_of_sell", 
            "company/points_of_sell.html", 
            "Points of Sell"
        )

    def test_doc_types_webpage(self):
        self.check_page_get_response(
            "/erp/document_types", 
            "erp:doc_types", 
            "company/doc_types.html", 
            "Document Types"
        )

    def test_sales_overview_webpage(self):
        self.check_page_get_response(
            "/erp/sales", 
            "erp:sales_index", 
            "erp/sales_index.html", 
            ["Sales Overview", "00001-00000001"]
        )

    def test_sales_new_invoice_get_webpage(self):
        self.create_extra_pos()
        self.assertEqual(PointOfSell.objects.count(), 4)
        
        # type 019 | E and pos 00003 must be hidden, so it shouldn't appear in 
        # the webpage
        self.check_page_get_response(
            "/erp/sales/invoices/new", 
            "erp:sales_new", 
            "erp/sales_new.html", 
            ["Create a new invoice", "002 | B", "00001", "00002", "00004"],
            ["019 | E", "00003"]
        )

    def test_sales_new_invoice_post_single_line_webpage(self):
        post_object = {
            # Invoice form
            "issue_date": "29/01/2024",
            "type": self.doc_type2.id,
            "point_of_sell": self.pos2.id,
            "number": "1",
            "sender": self.company.id,
            "recipient": self.c_client1.id,
            "payment_method": self.pay_method1.id,
            "payment_term": self.pay_term2.id,
            # line-setform 
            "s_invoice_lines-0-description": "Random products",
            "s_invoice_lines-0-taxable_amount": Decimal("2000"),
            "s_invoice_lines-0-not_taxable_amount": Decimal("180.02"),
            "s_invoice_lines-0-vat_amount": Decimal("420"),
            # line-setform-management
            "s_invoice_lines-TOTAL_FORMS": "1",
            "s_invoice_lines-INITIAL_FORMS": "0",
            "s_invoice_lines-MIN_NUM_FORMS": "0",
            "s_invoice_lines-MAX_NUM_FORMS": "1000",
        }

        self.check_page_post_response("erp:sales_new", post_object, 302, 
            (SaleInvoice, 2))  
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 3)


    def test_sales_new_invoice_post_triple_line_webpage(self):
        post_object = {
            # Invoice form
            "issue_date": "29/01/2024",
            "type": self.doc_type2.id,
            "point_of_sell": self.pos2.id,
            "number": "1",
            "sender": self.company.id,
            "recipient": self.c_client1.id,
            "payment_method": self.pay_method1.id,
            "payment_term": self.pay_term2.id,
            # line-setform-management
            "s_invoice_lines-TOTAL_FORMS": "3",
            "s_invoice_lines-INITIAL_FORMS": "0",
            "s_invoice_lines-MIN_NUM_FORMS": "0",
            "s_invoice_lines-MAX_NUM_FORMS": "1000",
            # line-1-setform 
            "s_invoice_lines-0-description": "Random products",
            "s_invoice_lines-0-taxable_amount": Decimal("2000"),
            "s_invoice_lines-0-not_taxable_amount": Decimal("180.02"),
            "s_invoice_lines-0-vat_amount": Decimal("420"),
            # line-2-setform 
            "s_invoice_lines-1-description": "Custom products",
            "s_invoice_lines-1-taxable_amount": Decimal("1000"),
            "s_invoice_lines-1-not_taxable_amount": Decimal("80.02"),
            "s_invoice_lines-1-vat_amount": Decimal("20"),
            # line-3-setform 
            "s_invoice_lines-2-description": "A few products",
            "s_invoice_lines-2-taxable_amount": Decimal("333"),
            "s_invoice_lines-2-not_taxable_amount": Decimal("33.32"),
            "s_invoice_lines-2-vat_amount": Decimal("33"),
        }      
        self.check_page_post_response("erp:sales_new", post_object, 302, 
            (SaleInvoice, 2))  
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 5)

    def test_sales_new_invoice_post_wrong_year_webpage(self):
        post_object = {
            # Invoice form
            "issue_date": "29/01/2025",
            "type": self.doc_type2.id,
            "point_of_sell": self.pos2.id,
            "number": "1",
            "sender": self.company.id,
            "recipient": self.c_client1.id,
            "payment_method": self.pay_method1.id,
            "payment_term": self.pay_term2.id,
            # line-setform 
            "s_invoice_lines-0-description": "Random products",
            "s_invoice_lines-0-taxable_amount": Decimal("2000"),
            "s_invoice_lines-0-not_taxable_amount": Decimal("180.02"),
            "s_invoice_lines-0-vat_amount": Decimal("420"),
            # line-setform-management
            "s_invoice_lines-TOTAL_FORMS": "1",
            "s_invoice_lines-INITIAL_FORMS": "0",
            "s_invoice_lines-MIN_NUM_FORMS": "0",
            "s_invoice_lines-MAX_NUM_FORMS": "1000",
        }      
        response = self.check_page_post_response("erp:sales_new", post_object, 200, 
            (SaleInvoice, 1))  

        self.assertEqual(SaleInvoiceLine.objects.all().count(), 2)
        self.assertIn("The selected date is not within the current year.", 
            response.context["form"].errors["issue_date"])

    def test_sales_new_invoice_post_wrong_date_correlation_webpage(self):
        post_object = {
            # Invoice form
            "issue_date": "20/01/2024",
            "type": self.doc_type1.id,
            "point_of_sell": self.pos1.id,
            "number": "2",
            "sender": self.company.id,
            "recipient": self.c_client1.id,
            "payment_method": self.pay_method1.id,
            "payment_term": self.pay_term1.id,
            # line-setform 
            "s_invoice_lines-0-description": "Random products",
            "s_invoice_lines-0-taxable_amount": Decimal("2000"),
            "s_invoice_lines-0-not_taxable_amount": Decimal("180.02"),
            "s_invoice_lines-0-vat_amount": Decimal("420"),
            # line-setform-management
            "s_invoice_lines-TOTAL_FORMS": "1",
            "s_invoice_lines-INITIAL_FORMS": "0",
            "s_invoice_lines-MIN_NUM_FORMS": "0",
            "s_invoice_lines-MAX_NUM_FORMS": "1000",
        }       
        
        response = self.check_page_post_response("erp:sales_new", post_object, 200, 
            (SaleInvoice, 1))
    
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 2)
        self.assertContains(response, "be older than previous invoice.")

    def test_sales_new_invoice_post_blank_line_webpage(self):
        post_object = {
            # Invoice form
            "issue_date": "29/01/2024",
            "type": self.doc_type2.id,
            "point_of_sell": self.pos2.id,
            "number": "1",
            "sender": self.company.id,
            "recipient": self.c_client1.id,
            "payment_method": self.pay_method1.id,
            "payment_term": self.pay_term2.id,
            # line-setform 
            "s_invoice_lines-0-description": "",
            "s_invoice_lines-0-taxable_amount": "",
            "s_invoice_lines-0-not_taxable_amount": "",
            "s_invoice_lines-0-vat_amount": "",
            # line-setform-management
            "s_invoice_lines-TOTAL_FORMS": "1",
            "s_invoice_lines-INITIAL_FORMS": "0",
            "s_invoice_lines-MIN_NUM_FORMS": "0",
            "s_invoice_lines-MAX_NUM_FORMS": "1000",
        }       
        response = self.check_page_post_response("erp:sales_new", post_object, 
            200, (SaleInvoice, 1))  
        
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 2)

    def test_sales_new_massive_invoice_get(self):
        self.check_page_get_response(
            "/erp/sales/invoices/new_massive", 
            "erp:sales_new_massive", "erp/sales_new_massive.html",
            ["Create new massive invoices", "Upload"]
        )

    def test_sales_new_massive_invoice_post_csv(self):
        file = get_file("erp/tests/files/sales/invoice_one_line.csv")

        self.check_page_post_response("erp:sales_new_massive", {"file": file}, 
            302, (SaleInvoice, 2))

        # Test DB was updated correctly
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 3)
        new_invoice = SaleInvoice.objects.get(
            type=self.doc_type1, point_of_sell=self.pos2, number="00000001")
        invoice_line = SaleInvoiceLine.objects.get(sale_invoice = new_invoice)
        self.assertEqual(new_invoice.issue_date, datetime.date(2024, 3, 15))
        self.assertEqual(new_invoice.type, self.doc_type1)
        self.assertEqual(new_invoice.point_of_sell, self.pos2)
        self.assertEqual(new_invoice.number, "00000001")
        self.assertEqual(new_invoice.sender, self.company)
        self.assertEqual(new_invoice.recipient, self.c_client1)
        self.assertEqual(new_invoice.payment_term, self.pay_term2)
        self.assertEqual(new_invoice.payment_method, self.pay_method1)
        self.assertEqual(invoice_line.description, "A mouse")
        self.assertEqual(invoice_line.taxable_amount, Decimal("1000"))
        self.assertEqual(invoice_line.not_taxable_amount, Decimal("50"))
        self.assertEqual(invoice_line.vat_amount, Decimal("105"))
        self.assertEqual(invoice_line.total_amount, Decimal("1155"))

    def test_sales_new_massive_invoice_post_xls(self):
        file = get_file("erp/tests/files/sales/invoice_one_line.xls")

        self.check_page_post_response("erp:sales_new_massive", {"file": file}, 
            302, (SaleInvoice, 2))
        
        # Test DB was updated correctly
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 3)
        new_invoice = SaleInvoice.objects.get(
        type=self.doc_type1, point_of_sell=self.pos2, number="00000001")
        invoice_line = SaleInvoiceLine.objects.get(sale_invoice = new_invoice)
        self.assertEqual(new_invoice.issue_date, datetime.date(2024, 3, 15))
        self.assertEqual(new_invoice.type, self.doc_type1)
        self.assertEqual(new_invoice.point_of_sell, self.pos2)
        self.assertEqual(new_invoice.number, "00000001")
        self.assertEqual(new_invoice.sender, self.company)
        self.assertEqual(new_invoice.recipient, self.c_client1)
        self.assertEqual(new_invoice.payment_term, self.pay_term2)
        self.assertEqual(new_invoice.payment_method, self.pay_method1)
        self.assertEqual(invoice_line.description, "A mouse")
        self.assertEqual(invoice_line.taxable_amount, Decimal("1000"))
        self.assertEqual(invoice_line.not_taxable_amount, Decimal("50"))
        self.assertEqual(invoice_line.vat_amount, Decimal("105"))
        self.assertEqual(invoice_line.total_amount, Decimal("1155"))

    def test_sales_new_massive_invoice_post_xlsx(self):
        file = get_file("erp/tests/files/sales/invoice_one_line.xlsx")
    
        self.check_page_post_response("erp:sales_new_massive", {"file": file}, 
            302, (SaleInvoice, 2))
        
        # Test DB was updated correctly
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 3)
        new_invoice = SaleInvoice.objects.get(
        type=self.doc_type1, point_of_sell=self.pos2, number="00000001")
        invoice_line = SaleInvoiceLine.objects.get(sale_invoice = new_invoice)
        self.assertEqual(new_invoice.issue_date, datetime.date(2024, 3, 15))
        self.assertEqual(new_invoice.type, self.doc_type1)
        self.assertEqual(new_invoice.point_of_sell, self.pos2)
        self.assertEqual(new_invoice.number, "00000001")
        self.assertEqual(new_invoice.sender, self.company)
        self.assertEqual(new_invoice.recipient, self.c_client1)
        self.assertEqual(new_invoice.payment_term, self.pay_term2)
        self.assertEqual(new_invoice.payment_method, self.pay_method1)
        self.assertEqual(invoice_line.description, "A mouse")
        self.assertEqual(invoice_line.taxable_amount, Decimal("1000"))
        self.assertEqual(invoice_line.not_taxable_amount, Decimal("50"))
        self.assertEqual(invoice_line.vat_amount, Decimal("105"))
        self.assertEqual(invoice_line.total_amount, Decimal("1155"))

    def test_sales_new_massive_invoice_pdf(self):
        file = get_file("erp/tests/files/sales/invoice_one_line.pdf")
        
        page_content = self.check_page_post_response("erp:sales_new_massive", 
            {"file": file}, 400, (SaleInvoice, 1))
        
        self.assertIn("Invalid file", page_content)
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 2)
        
    def test_sales_new_massive_invoice_multiple_lines_post_xlsx(self):
        file = get_file("erp/tests/files/sales/invoice_multiple_lines.xlsx")
  
        self.check_page_post_response("erp:sales_new_massive", 
            {"file": file}, 302, (SaleInvoice, 2))
        
        # Test DB was updated correctly
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 5)
        new_invoice = SaleInvoice.objects.get(
        type=self.doc_type1, point_of_sell=self.pos2, number="00000001")
        invoice_lines = SaleInvoiceLine.objects.filter(sale_invoice=new_invoice)
        self.assertEqual(new_invoice.issue_date, datetime.date(2024, 3, 15))
        self.assertEqual(new_invoice.type, self.doc_type1)
        self.assertEqual(new_invoice.point_of_sell, self.pos2)
        self.assertEqual(new_invoice.number, "00000001")
        self.assertEqual(new_invoice.sender, self.company)
        self.assertEqual(new_invoice.recipient, self.c_client1)
        self.assertEqual(new_invoice.payment_term, self.pay_term2)
        self.assertEqual(new_invoice.payment_method, self.pay_method1)
        self.assertEqual(invoice_lines[0].description, "A mouse")
        self.assertEqual(invoice_lines[0].taxable_amount, Decimal("1000"))
        self.assertEqual(invoice_lines[0].not_taxable_amount, Decimal("50"))
        self.assertEqual(invoice_lines[0].vat_amount, Decimal("105"))
        self.assertEqual(invoice_lines[0].total_amount, Decimal("1155"))
        self.assertEqual(invoice_lines[1].description, "A monitor")
        self.assertEqual(invoice_lines[1].taxable_amount, Decimal("100.22"))
        self.assertEqual(invoice_lines[1].not_taxable_amount, Decimal("0"))
        self.assertEqual(invoice_lines[1].vat_amount, Decimal("10.52"))
        self.assertEqual(invoice_lines[1].total_amount, Decimal("110.74"))
        self.assertEqual(invoice_lines[2].taxable_amount, Decimal("2000"))
        self.assertEqual(invoice_lines[2].not_taxable_amount, Decimal("50.50"))
        self.assertEqual(invoice_lines[2].vat_amount, Decimal("210"))
        self.assertEqual(invoice_lines[2].total_amount, Decimal("2260.50"))

    def test_sales_new_massive_invoices_multiple_lines_post_xlsx(self):
        file = get_file("erp/tests/files/sales/invoices_mixed.xlsx")
    
        self.check_page_post_response("erp:sales_new_massive", 
            {"file": file}, 302, (SaleInvoice, 6))
            
        # Test DB was updated correctly
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 10)
        new_invoice = SaleInvoice.objects.get(
        type=self.doc_type1, point_of_sell=self.pos2, number="00000004")
        invoice_lines = SaleInvoiceLine.objects.filter(sale_invoice=new_invoice)
        self.assertEqual(new_invoice.issue_date, datetime.date(2024, 3, 16))
        self.assertEqual(new_invoice.type, self.doc_type1)
        self.assertEqual(new_invoice.point_of_sell, self.pos2)
        self.assertEqual(new_invoice.number, "00000004")
        self.assertEqual(new_invoice.sender, self.company)
        self.assertEqual(new_invoice.recipient, self.c_client1)
        self.assertEqual(new_invoice.payment_term, self.pay_term2)
        self.assertEqual(new_invoice.payment_method, self.pay_method1)
        self.assertEqual(invoice_lines[0].description, "A monitor")
        self.assertEqual(invoice_lines[0].taxable_amount, Decimal("100.22"))
        self.assertEqual(invoice_lines[0].not_taxable_amount, Decimal("0"))
        self.assertEqual(invoice_lines[0].vat_amount, Decimal("10.52"))
        self.assertEqual(invoice_lines[0].total_amount, Decimal("110.74"))

    def test_sales_new_massive_invoice_post_repeated(self):
        file = get_file("erp/tests/files/sales/invoice_one_line_repeated.csv")
     
        page_content = self.check_page_post_response("erp:sales_new_massive", 
            {"file": file}, 400, (SaleInvoice, 1))
        
        self.assertIn("Invoice A 00001-00000001 already exists or repeated",
            page_content
        )
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 2)
    
    def test_sales_new_massive_invoice_post_wrong_columns(self):
        file = get_file("erp/tests/files/receivables/receipt_one.csv")

        page_content = self.check_page_post_response("erp:sales_new_massive", 
            {"file": file}, 400, (SaleInvoice, 1))
        
        self.assertIn("The columns in your file don't match", page_content)
    
    def test_sales_new_massive_invoice_post_wrong_data(self):
        file = get_file("erp/tests/files/sales/invoice_one_line_wrong.csv")

        page_content = self.check_page_post_response("erp:sales_new_massive", 
            {"file": file}, 400, (SaleInvoice, 1)) 
        
        self.assertIn("must be only digits", page_content)
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 2)

    def test_sales_new_massive_invoice_post_wrong_sender(self):
        file = get_file("erp/tests/files/sales/invoice_one_line_wrong2.csv")

        page_content = self.check_page_post_response("erp:sales_new_massive", 
            {"file": file}, 400, (SaleInvoice, 1))
        
        self.assertIn("The input in row 2 and column sender doesn't exist",
            page_content)
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 2)
    
    def test_sales_new_massive_invoice_post_wrong_data_3(self):
        file = get_file("erp/tests/files/sales/invoice_one_line_wrong3.csv")
    
        page_content = self.check_page_post_response("erp:sales_new_massive", 
            {"file": file}, 400, (SaleInvoice, 1)) 
        
        for text in ["must be a decimal number", "cannot be blank"]:
            self.assertIn(text, page_content)

        self.assertEqual(SaleInvoiceLine.objects.all().count(), 2)

    def test_sales_new_massive_invoice_post_wrong_date(self):
        file = get_file("erp/tests/files/sales/invoice_one_line_wrong_date.csv")
    
        page_content = self.check_page_post_response("erp:sales_new_massive", 
            {"file": file}, 400, (SaleInvoice, 1))
        
        self.assertIn("within the current year", page_content)
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 2)

    def test_sales_new_massive_invoices_multiple_lines_post_wrong_data(self):
        self.create_extra_pay_methods()
        self.create_extra_pay_terms()
        file = get_file("erp/tests/files/sales/invoices_mixed_wrong.csv")
  
        page_content = self.check_page_post_response("erp:sales_new_massive", 
            {"file": file}, 400, (SaleInvoice, 1))

        self.assertIn("Row 10: Your invoice's information doesn't match with row 9",
            page_content)
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 2)

    def test_sales_new_massive_invoices_disabled_pos(self):
        self.create_extra_pos()
        file = get_file("erp/tests/files/sales/invoices_disabled_pos.csv")
  
        page_content = self.check_page_post_response("erp:sales_new_massive", 
            {"file": file}, 400, (SaleInvoice, 1))

        self.assertIn("Row 2, general: You cannot include a disabled point of sell.",
            page_content)

    def test_sales_invoice_webpage(self):
        self.create_extra_invoices()
        self.check_page_get_response(
            f"/erp/sales/invoices/{self.sale_invoice1.pk}", 
            ["erp:sales_invoice", {"inv_pk": self.sale_invoice1.pk}],
            "erp/sales_invoice.html", 
            ["Invoice N° 00001-00000001", "$ 1300.01", "$ 2509.01", "Collected"]                   
        )

        # Check invoice2 doesn't have "collected".
        response = self.client.get(f"/erp/sales/invoices/{self.sale_invoice2.pk}")
        self.assertNotContains(response, "Collected")

        
    def test_sales_search_webpage(self):
        self.check_page_get_response(
            "/erp/sales/invoices/search", 
            "erp:sales_search", 
            "erp/document_search.html", 
            ["Search Invoice", "Year"]                   
        )
        
    def test_sales_edit_invoice_get_webpage(self):
        self.check_page_get_response(
            f"/erp/sales/invoices/{self.sale_invoice1.pk}/edit", 
            ["erp:sales_edit", {"inv_pk":f"{self.sale_invoice1.pk}"}],
            "erp/sales_edit.html", 
            ["Edit Invoice", "00000001", "209.99"]                   
        )
        
    def test_sales_edit_invoice_post_webpage(self):
        post_object = {
                # Invoice form
                "issue_date": "21/01/2024",
                "type": self.doc_type1.id,
                "point_of_sell": self.pos1.id,
                "number": "1",
                "sender": self.company.id,
                "recipient": self.c_client2.id,
                "payment_method": self.pay_method2.id,
                "payment_term": self.pay_term2.id,
                # line-setform-management. Modify 2 lines, add 1.
                "s_invoice_lines-TOTAL_FORMS": "3",
                "s_invoice_lines-INITIAL_FORMS": "2",
                "s_invoice_lines-MIN_NUM_FORMS": "0",
                "s_invoice_lines-MAX_NUM_FORMS": "1000",
                # line-1-setform / Modify all fields
                "s_invoice_lines-0-id": self.sale_invoice1.id,
                "s_invoice_lines-0-description": "Random products",
                "s_invoice_lines-0-taxable_amount": Decimal("2000"),
                "s_invoice_lines-0-not_taxable_amount": Decimal("180.02"),
                "s_invoice_lines-0-vat_amount": Decimal("420"),
                # line-2-setform / Modify all fields
                "s_invoice_lines-1-id": self.sale_invoice1.id,
                "s_invoice_lines-1-description": "Custom products",
                "s_invoice_lines-1-taxable_amount": Decimal("1000"),
                "s_invoice_lines-1-not_taxable_amount": Decimal("80.02"),
                "s_invoice_lines-1-vat_amount": Decimal("20"),
                # line-3-setform / New line added
                "s_invoice_lines-2-id": self.sale_invoice1.id,
                "s_invoice_lines-2-description": "A few products",
                "s_invoice_lines-2-taxable_amount": Decimal("333"),
                "s_invoice_lines-2-not_taxable_amount": Decimal("33.32"),
                "s_invoice_lines-2-vat_amount": Decimal("33")
            } 
        
        self.check_page_post_response(
            ["erp:sales_edit", {"inv_pk": self.sale_invoice1.pk}], 
            post_object, 302, (SaleInvoice, 1)
        ) 
        self.assertEqual(SaleInvoiceLine.objects.all().count(), 3)

    def test_sales_invoice_related_receipts(self):
        self.check_page_get_response(
            f"/erp/sales/invoices/{self.sale_invoice1.pk}/related_receipts", 
            ["erp:sales_rel_receipts", {"inv_pk": self.sale_invoice1.pk}],
            "erp/sales_related_receipts.html", 
            ["Related Receipts", "Receipt N° 00001-00000001", "A 00001-00000001"]
        )

    def test_sales_invoice_related_receipts_no(self):
        self.create_extra_invoices()
        self.check_page_get_response(
            f"/erp/sales/invoices/{self.sale_invoice2.pk}/related_receipts", 
            ["erp:sales_rel_receipts", {"inv_pk": self.sale_invoice2.pk}],
            "erp/sales_related_receipts.html", 
            ["Related Receipts", "There isn't any related receipt.",
                "B 00001-00000001"]
        )

    def test_sales_list_get_webpage(self):
        self.check_page_get_response(
            "/erp/sales/invoices/list", 
            "erp:invoice_list", 
            "erp/sales_list.html", 
            ["Invoice List", "Client Name", "21/01/2024", "Collected"] # Current year is 2024                   
        )

    def test_sales_list_post_year_webpage(self):
        # Add financial year and an invoice before testing
        FinancialYear.objects.create(year = "2025")
        self.create_extra_invoices()

        post_object = {"year": "2025", "form_type": "year",}

        response = self.check_page_post_response("erp:invoice_list", post_object,
            200) 

        for page_content in [ "23/06/2025", "20361382481", "600.01", "No"]:
            self.assertContains(response, page_content)
     
    def test_sales_list_post_year_no_financial_webpage(self):
        post_object = {"year": "2025", "form_type": "year"}
        
        response = self.check_page_post_response("erp:invoice_list", post_object,
            200) 
        
        # By default, current's year invoices should appear
        for page_content in ["The year 2025 doesn", "21/01/2024", "00000001"]:
            self.assertContains(response, page_content)
    
        
    def test_sales_list_post_year_no_invoice_webpage(self):
        FinancialYear.objects.create(year = "2025")
        post_object = {"year": "2025", "form_type": "year"}

        response = self.check_page_post_response("erp:invoice_list", post_object,
            200) 
        
        self.assertNotContains(response, "The year 2025 doesn't exist in the records.")
        self.assertContains(response, "There isn't any invoice in this period of time.")
        
    def test_sales_list_post_dates_webpage(self):
        self.create_extra_invoices()
        post_object = {
            "date_from": "23/01/2024",
            "date_to": "24/01/2024",
            "form_type": "date",
        }

        response = self.check_page_post_response("erp:invoice_list", post_object,
            200) 

        for page_content in ["00000002", "00000003", "CLIENT1 SRL", "CLIENT2 SA"]:
            self.assertContains(response, page_content)
        
        self.assertNotContains(response, "00000001")

    def test_sales_list_post_dates_same_webpage(self):
        self.create_extra_invoices()
        post_object = {
            "date_from": "23/01/2024",
            "date_to": "23/01/2024",
            "form_type": "date",
        }
        
        response = self.check_page_post_response("erp:invoice_list", post_object,
            200) 
        
        for page_content in ["00000002", "00000003"]:
            self.assertContains(response, page_content)
        
        self.assertNotContains(response, "00000004")
    
    def test_sales_list_post_dates_inverted_webpage(self):
        self.create_extra_invoices()
        post_object = {
            "date_from": "24/04/2024",
            "date_to": "23/04/2024",
            "form_type": "date",
        }
        
        response = self.check_page_post_response("erp:invoice_list", post_object,
            200) 
        
        self.assertContains(response, "should be older")
        self.assertNotContains(response, "00000002")
        self.assertNotContains(response, "00000004")

   
    def test_receivables_overview_webpage(self):    
        self.check_page_get_response(
            "/erp/receivables", 
            "erp:receivables_index",
            "erp/receivables_index.html", 
            ["Amount collected:", "Last Receipts"]                   
        )

    def test_receivables_new_receipt_get_webpage(self):
        self.create_extra_pos()
        self.assertEqual(PointOfSell.objects.count(), 4)
        
        # 00003 should be hidden as it disabled
        self.check_page_get_response(
            "/erp/receivables/receipts/new", 
            "erp:receivables_new",
            "erp/receivables_new.html", 
            ["Create a new receipt", "Related invoice", "Number", "00001",
                "00002", "00004"],
            "00003"

        )        

    @tag("erp_db_view_receivables_new_post")
    def test_receivables_new_receipt_post_webpage(self):
        self.create_extra_invoices()
        post_object = {
            # Receipt form
            "issue_date": "29/03/2024",
            "point_of_sell": self.pos1.id,
            "number": "2",
            "related_invoice": self.sale_invoice2.id,
            "sender": self.company.id,
            "recipient": self.c_client1.id,
            "description": "Something",
            "total_amount": "1209.10",
        }

        self.check_page_post_response("erp:receivables_new",post_object, 302,
            (SaleReceipt, 2)) 
        
        # Update sale invoice and test
        self.sale_invoice2.refresh_from_db()
        self.assertEqual(self.sale_invoice2.collected, True)

    def test_receivables_new_receipt_post_wrong_year_webpage(self):
        self.create_extra_invoices()
        post_object = {
            # Receipt form
            "issue_date": "29/01/2025",
            "point_of_sell": self.pos2.id,
            "number": "1",
            "sender": self.company.id,
            "recipient": self.c_client1.id,
            "related_invoice": self.sale_invoice2.id,
            "description": "Something",
            "total_amount": "600.01"
        }
        
        response = self.check_page_post_response("erp:receivables_new", 
            post_object, 200, (SaleReceipt, 1)) 

        self.assertContains(response, 
            "The selected date is not within the current year."
        )

    def test_receivables_new_receipt_post_wrong_date_correlation_webpage(self):
        post_object = {
            # Receipt form
            "issue_date": "29/01/2024",
            "point_of_sell": self.pos1.id,
            "number": "2",
            "sender": self.company.id,
            "recipient": self.c_client1.id,
            "related_invoice": self.sale_invoice1.id,
            "description": "Something",
            "total_amount": "600.01"
        }      
        response = self.check_page_post_response("erp:receivables_new", 
            post_object, 200, (SaleReceipt, 1)) 
        
        self.assertContains(response, "be older than previous receipt.")

    def test_receivables_new_receipt_post_wrong_amount_webpage(self):
        self.create_extra_invoices()
        post_object = {
            # Receipt form
            "issue_date": "24/04/2024",
            "point_of_sell": self.pos1.id,
            "number": "2",
            "sender": self.company.id,
            "recipient": self.c_client1.id,
            "related_invoice": self.sale_invoice2.id,
            "description": "Something",
            "total_amount": "1209.11" # Total from invoice is 1209.10
        }

        response = self.check_page_post_response("erp:receivables_new", 
            post_object, 200, (SaleReceipt, 1))
         
        self.assertContains(response, "Receipt total amount cannot be higher")

    def test_receivables_new_receipt_post_wrong_second_amount_webpage(self):
        self.create_extra_receipts()
        post_object = {
            # Receipt form
            "issue_date": "25/07/2025",
            "point_of_sell": self.pos1.id,
            "number": "6",
            "sender": self.company.id,
            "recipient": self.c_client1.id,
            "related_invoice": self.sale_invoice2.id,
            "description": "Something",
            "total_amount": "1209.10" # Total from invoice is $1209.10,
        }
        response = self.check_page_post_response("erp:receivables_new", 
            post_object, 200, (SaleReceipt, 7))     

        self.assertContains(response, 
            "The sum of your receipts cannot be higher"
        )
    
    def test_receivables_new_massive_receipt_get(self):
        self.check_page_get_response(
            "/erp/receivables/receipts/new_massive", 
            "erp:receivables_new_massive",
            "erp/receivables_new_massive.html", 
            ["Create new massive receipts", "Upload"]
        )  

    def test_receivables_new_massive_receipt_post_csv(self):
        self.create_extra_invoices()
        file = get_file("erp/tests/files/receivables/receipt_one.csv")

        self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 302, (SaleReceipt, 2))  


        # Test DB was updated correctly
        new_receipt = SaleReceipt.objects.get(
            point_of_sell=self.pos1, number="00000002")
        self.assertEqual(new_receipt.issue_date, datetime.date(2024, 2, 22))
        self.assertEqual(new_receipt.point_of_sell, self.pos1)
        self.assertEqual(new_receipt.number, "00000002")
        self.assertEqual(new_receipt.sender, self.company)
        self.assertEqual(new_receipt.recipient, self.c_client1)
        self.assertEqual(new_receipt.description, "test import receipt")
        self.assertEqual(new_receipt.total_amount, Decimal("1209.10"))

        self.sale_invoice2.refresh_from_db()
        self.assertEqual(self.sale_invoice1.collected, True)

    def test_receivables_new_massive_receipt_post_xls(self):
        self.create_extra_invoices()
        file = get_file("erp/tests/files/receivables/receipt_one.xls")

        self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 302, (SaleReceipt, 2))
        
        # Test DB was updated correctly
        new_receipt = SaleReceipt.objects.get(
            point_of_sell=self.pos1, number="00000002")
        self.assertEqual(new_receipt.issue_date, datetime.date(2024, 2, 22))
        self.assertEqual(new_receipt.point_of_sell, self.pos1)
        self.assertEqual(new_receipt.number, "00000002")
        self.assertEqual(new_receipt.sender, self.company)
        self.assertEqual(new_receipt.recipient, self.c_client1)
        self.assertEqual(new_receipt.description, "test import receipt")
        self.assertEqual(new_receipt.total_amount, Decimal("1209.10"))

        self.sale_invoice1.refresh_from_db()
        self.assertEqual(self.sale_invoice1.collected, True)
    
    def test_receivables_new_massive_receipt_post_xlsx(self):
        self.create_extra_invoices()
        file = get_file("erp/tests/files/receivables/receipt_one.xlsx")

        self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 302, (SaleReceipt, 2))
        
        # Test DB was updated correctly
        new_receipt = SaleReceipt.objects.get(
            point_of_sell=self.pos1, number="00000002")
        self.assertEqual(new_receipt.issue_date, datetime.date(2024, 2, 22))
        self.assertEqual(new_receipt.point_of_sell, self.pos1)
        self.assertEqual(new_receipt.number, "00000002")
        self.assertEqual(new_receipt.sender, self.company)
        self.assertEqual(new_receipt.recipient, self.c_client1)
        self.assertEqual(new_receipt.description, "test import receipt")
        self.assertEqual(new_receipt.total_amount, Decimal("1209.10"))

        self.sale_invoice2.refresh_from_db()
        self.assertEqual(self.sale_invoice2.collected, True)
    
    def test_receivables_new_massive_receipt_pdf(self):
        file = get_file("erp/tests/files/receivables/receipt_one.pdf")
 
        page_content = self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 400, (SaleReceipt, 1))

        self.assertIn("Invalid file", page_content)

    def test_receivables_new_massive_receipt_multiple_receipts_post_xlsx(self):
        self.create_extra_invoices()
        file = get_file("erp/tests/files/receivables/receipt_multiple.xlsx")
        
        self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 302, (SaleReceipt, 6))

        # Test DB was updated correctly
        new_receipt = SaleReceipt.objects.get(
        point_of_sell=self.pos1, number="00000003")
        self.assertEqual(new_receipt.issue_date, datetime.date(2024, 2, 23))
        self.assertEqual(new_receipt.point_of_sell, self.pos1)
        self.assertEqual(new_receipt.number, "00000003")
        self.assertEqual(new_receipt.sender, self.company)
        self.assertEqual(new_receipt.recipient, self.c_client1)
        self.assertEqual(new_receipt.description, "test import receipt 2")
        self.assertEqual(new_receipt.total_amount, Decimal("609"))
       
        for sale_invoice in [self.sale_invoice1, self.sale_invoice5]:
            sale_invoice.refresh_from_db()
            self.assertEqual(sale_invoice.collected, True)

        for sale_invoice in [self.sale_invoice2, self.sale_invoice6]:
            sale_invoice.refresh_from_db()
            self.assertEqual(sale_invoice.collected, False)
    
    def test_receivables_new_massive_receipt_post_repeated(self):
        self.create_extra_invoices()
        
        file = get_file("erp/tests/files/receivables/receipt_repeated.xlsx")

        page_content = self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 400, (SaleReceipt, 1))
        
        self.assertIn("Receipt 00001-00000002 already exists or repeated",
            page_content
        )

        self.sale_invoice1.refresh_from_db()
        self.assertEqual(self.sale_invoice1.collected, True)

    def test_receivables_new_massive_receipt_post_wrong_columns(self):
        file = get_file(
            "erp/tests/files/sales/invoice_one_line.xlsx"
        )
        
        page_content = self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 400, (SaleReceipt, 1))

        self.assertIn("The columns in your file don't match", page_content)
    
    def test_receivables_new_massive_receipt_post_wrong_number_descripcion(self):
        self.create_extra_invoices()

        file = get_file(
            "erp/tests/files/receivables/receipt_one_wrong_number_blank.xlsx"
        )
        
        page_content = self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 400, (SaleReceipt, 1))

        for text in ["must be only digits", "cannot be blank"]:
            self.assertIn(text, page_content)
        
    def test_receivables_new_massive_receipt_post_wrong_amount(self):
        self.create_extra_invoices()
        file = get_file(
            "erp/tests/files/receivables/receipt_one_wrong_amount.xlsx"
        )
        
        page_content = self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 400, (SaleReceipt, 1))
       
        self.assertIn("higher than invoice total", page_content)

    def test_receivables_new_massive_receipt_post_wrong_invoice(self):
        self.create_extra_invoices()
        file = get_file(
            "erp/tests/files/receivables/receipt_one_wrong_invoice.xlsx"
        )
        
        page_content = self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 400, (SaleReceipt, 1))

        self.assertIn("column ri_pos doesn't exist in the records.", 
            page_content
        )

    def test_receivables_new_massive_receipt_post_wrong_date(self):
        self.create_extra_invoices()
        file = get_file(
            "erp/tests/files/receivables/receipt_one_wrong_date.xlsx"
        )
        
        page_content = self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 400, (SaleReceipt, 1))
    
        self.assertIn("selected date is not within the current year.",
            page_content
        )
        
    def test_receivables_new_massive_receipt_post_wrong_client(self):
        self.create_extra_invoices()
        file = get_file(
            "erp/tests/files/receivables/receipt_one_wrong_client.xlsx"
        )
        
        page_content = self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 400, (SaleReceipt, 1))
        
        self.assertIn("column recipient doesn't exist in the records.",
            page_content)

    
    def test_receivables_new_massive_receipt_disabled_pos(self):
        self.create_extra_pos()
        self.create_extra_invoices()
        file = get_file("erp/tests/files/receivables/receipt_one_disabled_pos.csv")
  
        page_content = self.check_page_post_response("erp:receivables_new_massive", 
            {"file": file}, 400, (SaleReceipt, 1))

        self.assertIn("Row 2, general: You cannot include a disabled point of sell.",
            page_content)

    
    def test_receivables_receipt_webpage(self):
        self.check_page_get_response(
            f"/erp/receivables/receipts/{self.sale_receipt1.pk}", 
            ["erp:receivables_receipt", {"rec_pk": self.sale_receipt1.pk}],
            "erp/receivables_receipt.html", 
            ["Receipt N° 00001-00000001", "Related Invoice", "$ 2509.01", "X"]
        )  
        
    def test_receivables_edit_receipt_get_webpage(self):
        self.check_page_get_response(
            f"/erp/receivables/receipts/{self.sale_receipt1.pk}/edit", 
            ["erp:receivables_edit", {"rec_pk": self.sale_receipt1.pk}],
            "erp/receivables_edit.html", 
            ["Edit Receipt", "00000001", "2509.01"]
        )  

    def test_receivables_edit_receipt_post_webpage(self):
        post_object = {
                # Receipt form
                "issue_date": "21/02/2024",
                "point_of_sell": self.pos1.id,
                "number": "1",
                "description": "Test sale receipt edited.",
                "related_invoice": self.sale_invoice1.pk,
                "sender": self.company.id,
                "recipient": self.c_client1.id,
                "total_amount": Decimal("150"),
            }

        self.check_page_post_response(["erp:receivables_edit", {
            "rec_pk": self.sale_receipt1.pk}], post_object, 302, (SaleReceipt, 
            1)
        )
        
        self.sale_receipt1.refresh_from_db()
        self.sale_invoice1.refresh_from_db()
        self.assertEqual(self.sale_receipt1.description, "Test sale receipt edited.")
        self.assertEqual(self.sale_invoice1.collected, False)
    
    def test_receivables_edit_receipt_ri_post_webpage(self):
        # As I need 2 invoices, I add more
        self.create_extra_invoices()

        post_object = {
                # Receipt form
                "issue_date": "21/02/2024",
                "point_of_sell": self.pos1.id,
                "number": "1",
                "description": "Test modified rel inv.",
                "related_invoice": self.sale_invoice2.id,
                "sender": self.company.id,
                "recipient": self.c_client1.id,
                "total_amount": Decimal("1209.10"),
            }
           
        self.check_page_post_response(["erp:receivables_edit", {
            "rec_pk": self.sale_receipt1.pk}], post_object, 302, (SaleReceipt, 
            1)
        )
        
        for com_doc in [self.sale_receipt1, self.sale_invoice1, self.sale_invoice2]:
            com_doc.refresh_from_db()
        
        self.assertEqual(self.sale_receipt1.description, "Test modified rel inv.")
        self.assertEqual(self.sale_invoice1.collected, False)
        self.assertEqual(self.sale_invoice2.collected, True)
        
    def test_receivables_search_webpage(self):
        self.check_page_get_response(
            "/erp/receivables/receipts/search", 
            "erp:receivables_search",
            "erp/document_search.html", 
            ["Search Receipt", "Related invoice"]
        )  

    def test_receivables_list_get_webpage(self):
        self.check_page_get_response(
            "/erp/receivables/receipts/list", 
            "erp:receipt_list",
            "erp/receivables_list.html", 
            # Reminder: Current year is 2024
            ["Receipt List", "Related Invoice", "21/02/2024"] 
        ) 

    def test_receivables_list_post_year_webpage(self):
        # Add financial year and an invoice before testing
        FinancialYear.objects.create(year = "2025")
        self.create_extra_receipts()
        post_object = {"year": "2025", "form_type": "year"}

        # Note: Response is 200 as there is no redirect
        response = self.check_page_post_response("erp:receipt_list",
            post_object, 200)
        
        for text in ["24/07/2025", "20361382481", "300.99"]:
            self.assertContains(response, text)
    
    def test_receivables_list_post_year_no_financial_webpage(self):
        self.create_extra_receipts()
        post_object = {"year": "2025", "form_type": "year"}
        
        response = self.check_page_post_response("erp:receipt_list",
            post_object, 200)
        
        # By default, current's year invoices should appear
        for page_content in ["The year 2025 doesn", "24/03/2024", "00000003"]:
            self.assertContains(response, page_content)
    
        
    def test_receivables_list_post_year_no_invoice_webpage(self):
        FinancialYear.objects.create(year = "2025")
        post_object = {"year": "2025", "form_type": "year"}

        response = self.check_page_post_response("erp:receipt_list", post_object,
            200) 
        
        self.assertNotContains(response, "The year 2025 doesn't exist in the records.")
        self.assertContains(response, "There isn't any receipt in this period of time.")
        
    def test_receivables_list_post_dates_webpage(self):
        self.create_extra_receipts()
        post_object = {
            "date_from": "21/02/2024",
            "date_to": "23/02/2024",
            "form_type": "date",
        }

        response = self.check_page_post_response("erp:receipt_list", post_object,
            200) 

        for page_content in ["00000001", "00000002", "00000003", "600.01"]:
            self.assertContains(response, page_content)
        
        self.assertNotContains(response, "00000004")
   
    def test_receivables_list_post_dates_same_webpage(self):
        self.create_extra_receipts()
        post_object = {
            "date_from": "24/03/2024",
            "date_to": "24/03/2024",
            "form_type": "date",
        }
        
        response = self.check_page_post_response("erp:receipt_list", post_object,
            200) 
        
        for page_content in ["00000001", "00000002", "00000004"]:
            self.assertContains(response, page_content)
        
        self.assertNotContains(response, "00000005")
    
    def test_receivables_list_post_dates_inverted_webpage(self):
        self.create_extra_receipts()
        post_object = {
            "date_from": "24/04/2024",
            "date_to": "23/04/2024",
            "form_type": "date",
        }
        
        response = self.check_page_post_response("erp:receipt_list", post_object,
            200) 
        
        self.assertContains(response, "should be older")
        self.assertNotContains(response, "00000002")
        self.assertNotContains(response, "00000004")
   