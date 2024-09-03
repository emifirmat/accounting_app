import datetime, os
import pprint
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase, tag
from django.urls import reverse

# Create your tests here.
from ..models import (Company_client, Supplier, Client_current_account,
    Supplier_current_account, Payment_method, Payment_term, Sale_invoice,
    Sale_invoice_line, Sale_receipt, Purchase_invoice, Purchase_invoice_line,
    Purchase_receipt, Point_of_sell, Document_type)
from company.models import Company, Calendar, FinancialYear


# Create your tests here.
@tag("erp_db_view")
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

        cls.current_year = FinancialYear.objects.create(
            year = "2024",
            current = True,
        )

        cls.company_client = Company_client.objects.create(
            tax_number = "20361382481",
            name = "Client1 SRL",
            address = "Client street, Client city, Chile",
            email = "client1@email.com",
            phone = "1234567890",
        )
        cls.company_client2 = Company_client.objects.create(
            tax_number = "20999999999",
            name = "Client2 SA",
            address = "Client2 street, Client city, Argentina",
            email = "client2@email.com",
            phone = "12443131241",
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

        cls.pos1 = Point_of_sell.objects.create(pos_number="1")
        cls.pos2 = Point_of_sell.objects.create(pos_number="2")

        cls.doc_type1 = Document_type.objects.create(
            type = "A",
            code = "001",
            type_description = "Invoice A",
            hide = False,
        )
        cls.doc_type2 = Document_type.objects.create(
            type = "B",
            code = "2",
            type_description = "Invoice B",
            hide = False,
        )
        cls.doc_type3 = Document_type.objects.create(
            type = "E",
            code = "19",
            type_description = "Invoice E",
        )

        cls.payment_method = Payment_method.objects.create(
            pay_method = "Cash",
        )

        cls.payment_method2 = Payment_method.objects.create(
            pay_method = "Transfer",
        )

        cls.payment_term = Payment_term.objects.create(
            pay_term = "0",
        )

        cls.payment_term2 = Payment_term.objects.create(
            pay_term = "30",
        )

        cls.sale_invoice = Sale_invoice.objects.create(
            issue_date = datetime.date(2024, 1, 21),
            type = cls.doc_type1,
            point_of_sell = cls.pos1,
            number = "00000001",
            sender = cls.company,
            recipient = cls.company_client,
            payment_method = cls.payment_method,
            payment_term = cls.payment_term,
        )

        cls.sale_invoice_line1 = Sale_invoice_line.objects.create(
            sale_invoice = cls.sale_invoice,
            description = "Test sale invoice",
            taxable_amount = Decimal("1000"),
            not_taxable_amount = Decimal("90.01"),
            vat_amount = Decimal("210"),
        )
        cls.sale_invoice_line2 = Sale_invoice_line.objects.create(
            sale_invoice = cls.sale_invoice,
            description = "Other products",
            taxable_amount = Decimal("999"),
            not_taxable_amount = Decimal("00.01"),
            vat_amount = Decimal("209.99"),
        )

        cls.sale_receipt = Sale_receipt.objects.create(
            issue_date = datetime.date(2024, 2, 21),
            type = cls.doc_type1,
            point_of_sell = cls.pos1,
            number = "00000001",
            description = "Test sale receipt",
            related_invoice = cls.sale_invoice,
            sender = cls.company,
            recipient = cls.company_client,
            total_amount = Decimal("1300.01"),
        )

        cls.purchase_invoice = Purchase_invoice.objects.create(
            issue_date = datetime.date(2024, 1, 13),
            type = cls.doc_type2,
            point_of_sell = "00231",
            number = "00083051",
            sender = cls.supplier,
            recipient = cls.company,
            payment_method = cls.payment_method2,
            payment_term = cls.payment_term2,
        )

        cls.purchase_invoice_line1 = Purchase_invoice_line.objects.create(
            purchase_invoice = cls.purchase_invoice,
            description = "Test purchase invoice",
            taxable_amount = Decimal("200"),
            not_taxable_amount = Decimal("0"),
            vat_amount = Decimal("42"),
        )

        cls.purchase_receipt = Purchase_receipt.objects.create(
            issue_date = datetime.date(2024, 2, 13),
            type = cls.doc_type2,
            point_of_sell = "00231",
            number = "00000023",
            description = "Test purchase receipt",
            related_invoice = cls.purchase_invoice,
            sender = cls.supplier,
            recipient = cls.company,
            total_amount = Decimal("242"),
        )

    def create_extra_invoices(self):
        """Create extra invoices when a test demands it"""
        new_sale_invoice = Sale_invoice.objects.create(
            issue_date = datetime.date(2024, 4, 23),
            type = self.doc_type1,
            point_of_sell = self.pos1,
            number = "00000002",
            sender = self.company,
            recipient = self.company_client,
            payment_method = self.payment_method,
            payment_term = self.payment_term,
        )
        Sale_invoice_line.objects.create(
            sale_invoice = new_sale_invoice,
            description = "Test 2 sale invoice",
            taxable_amount = Decimal("500"),
            not_taxable_amount = Decimal("20.01"),
            vat_amount = Decimal("80"),
        )

        new_sale_invoice = Sale_invoice.objects.create(
            issue_date = datetime.date(2024, 4, 23),
            type = self.doc_type1,
            point_of_sell = self.pos1,
            number = "00000003",
            sender = self.company,
            recipient = self.company_client,
            payment_method = self.payment_method,
            payment_term = self.payment_term,
        )
        Sale_invoice_line.objects.create(
            sale_invoice = new_sale_invoice,
            description = "Test 2 sale invoice",
            taxable_amount = Decimal("500"),
            not_taxable_amount = Decimal("20.01"),
            vat_amount = Decimal("80"),
        )

        new_sale_invoice = Sale_invoice.objects.create(
            issue_date = datetime.date(2024, 4, 24),
            type = self.doc_type1,
            point_of_sell = self.pos1,
            number = "00000004",
            sender = self.company,
            recipient = self.company_client,
            payment_method = self.payment_method,
            payment_term = self.payment_term,
        )
        Sale_invoice_line.objects.create(
            sale_invoice = new_sale_invoice,
            description = "Test 2 sale invoice",
            taxable_amount = Decimal("500"),
            not_taxable_amount = Decimal("20.01"),
            vat_amount = Decimal("80"),
        )

        new_sale_invoice = Sale_invoice.objects.create(
            issue_date = datetime.date(2025, 6, 23),
            type = self.doc_type1,
            point_of_sell = self.pos1,
            number = "00000005",
            sender = self.company,
            recipient = self.company_client,
            payment_method = self.payment_method,
            payment_term = self.payment_term,
        )
        Sale_invoice_line.objects.create(
            sale_invoice = new_sale_invoice,
            description = "Test 2 sale invoice",
            taxable_amount = Decimal("500"),
            not_taxable_amount = Decimal("20.01"),
            vat_amount = Decimal("80"),
        )


    def test_company_client_content(self):
        company_clients = Company_client.objects.all()
        self.assertEqual(company_clients.count(), 2)
        self.assertEqual(self.company_client.tax_number, "20361382481")
        self.assertEqual(self.company_client.name, "CLIENT1 SRL")
        self.assertEqual(self.company_client.email, "client1@email.com")
        self.assertEqual(self.company_client.phone, "1234567890")
        self.assertEqual(self.company_client.address, "Client Street, Client City, Chile")
        self.assertEqual(str(self.company_client), "CLIENT1 SRL | 20361382481")

    def test_supplier_content(self):
        suppliers = Supplier.objects.all()
        self.assertEqual(suppliers.count(), 1)
        self.assertEqual(self.supplier.tax_number, "20361382482")
        self.assertEqual(self.supplier.name, "SUPPLIER1 SA")
        self.assertEqual(self.supplier.email, "Supplier1@email.com")
        self.assertEqual(self.supplier.phone, "0987654321")
        self.assertEqual(self.supplier.address, "Supplier Street, Supplier City, Chile")
        self.assertEqual(str(self.supplier), "SUPPLIER1 SA | 20361382482")

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

    def test_company_point_of_sell_content(self):
        pos_all = Point_of_sell.objects.all()
        self.assertEqual(pos_all.count(), 2)
        self.assertEqual(self.pos1.pos_number, "00001")
        self.assertEqual(str(self.pos1), "00001")
    
    def test_document_type_content(self):
        doc_type_all = Document_type.objects.all()
        self.assertEqual(doc_type_all.count(), 3)
        self.assertEqual(self.doc_type1.type, "A")
        self.assertEqual(self.doc_type1.code, "001")
        self.assertEqual(self.doc_type1.type_description, "Invoice A")
        self.assertEqual(self.doc_type1.hide, False)
        self.assertEqual(str(self.doc_type1), "001 | A")

    def test_document_type_validator(self):
        with self.assertRaises(ValidationError):
            doc_3 = Document_type.objects.create(
                type = "3",
                code = "003",
                type_description = "Invoice C",
            )
            doc_3.full_clean()
    
    def test_payment_method_content(self):
        payment_methods = Payment_method.objects.all()
        self.assertEqual(payment_methods.count(), 2)
        self.assertEqual(self.payment_method2.pay_method, "Transfer")
        self.assertEqual(str(self.payment_method2), "Transfer")

    def test_payment_term_content(self):
        payment_terms = Payment_term.objects.all()
        self.assertEqual(payment_terms.count(), 2)
        self.assertEqual(self.payment_term2.pay_term, "30")
        self.assertEqual(str(self.payment_term2), "30 days")
    
    def test_sale_invoice_content(self):
        invoices = Sale_invoice.objects.all()
        self.assertEqual(invoices.count(), 1)
        self.assertEqual(self.sale_invoice.issue_date, datetime.date(2024, 1, 21))
        self.assertEqual(self.sale_invoice.type, self.doc_type1)
        self.assertEqual(self.sale_invoice.point_of_sell.pos_number, "00001")
        self.assertEqual(self.sale_invoice.number, "00000001")
        self.assertEqual(self.sale_invoice.sender, self.company)
        self.assertEqual(self.sale_invoice.recipient, self.company_client)
        self.assertEqual(self.sale_invoice.payment_method, self.payment_method)
        self.assertEqual(self.sale_invoice.payment_term, self.payment_term)
        self.assertEqual(
            str(self.sale_invoice),
            f"00001-00000001 | A | 2024-01-21"
        )

    def test_sale_invoice_get_abosulte_url(self):
        response = self.client.get(self.sale_invoice.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_sale_invoice_total_sum(self):
        self.assertAlmostEqual(self.sale_invoice.total_lines_sum(),
            Decimal(2509.01))

    def test_sale_invoice_constraint(self):
        sale_invoice2 = Sale_invoice.objects.create(
            issue_date = datetime.date(2024, 1, 21),
            type = self.doc_type1,
            point_of_sell = self.pos1,
            number = "2",
            sender = self.company,
            recipient = self.company_client,
            payment_method = self.payment_method2,
            payment_term = self.payment_term2,
        )

        invoices = Sale_invoice.objects.all()
        self.assertEqual(invoices.count(), 2)

        with self.assertRaises(IntegrityError):
            sale_invoice3 = Sale_invoice.objects.create(
                issue_date = datetime.date(2024, 1, 22),
                type = self.doc_type1,
                point_of_sell = self.pos1,
                number = "00000002",
                sender = self.company,
                recipient = self.company_client,
                payment_method = self.payment_method2,
                payment_term = self.payment_term2,
            )

    def test_sale_invoice_line_content(self):
        invoice_lines = Sale_invoice_line.objects.all()
        self.assertEqual(invoice_lines.count(), 2)
        self.assertEqual(self.sale_invoice_line1.sale_invoice, self.sale_invoice)
        self.assertEqual(self.sale_invoice_line1.description, "Test sale invoice")
        self.assertEqual(self.sale_invoice_line1.taxable_amount, Decimal("1000"))
        self.assertEqual(self.sale_invoice_line1.not_taxable_amount, 
            Decimal("90.01"))
        self.assertEqual(self.sale_invoice_line1.vat_amount, Decimal("210"))
        self.assertEqual(self.sale_invoice_line1.total_amount, Decimal("1300.01"))
        self.assertEqual(
            str(self.sale_invoice_line1), f"Test sale invoice | $ 1300.01"
        )

    def test_sale_invoice_line_decimal_places(self):
        # 1 digit
        self.sale_invoice_line1.taxable_amount = Decimal("1.1")
        self.sale_invoice_line1.save()
        self.assertEqual(self.sale_invoice_line1.taxable_amount, Decimal("1.1"))
        # 3 digits
        with self.assertRaises(ValidationError):
            self.sale_invoice_line1.vat_amount = Decimal("0.564")
            self.sale_invoice_line1.full_clean()

    def test_sale_receipt_content(self):
        sale_receipts = Sale_receipt.objects.all()
        self.assertEqual(sale_receipts.count(), 1)
        self.assertEqual(self.sale_receipt.issue_date, datetime.date(2024, 2, 21))
        self.assertEqual(self.sale_receipt.type, self.doc_type1)
        self.assertEqual(self.sale_receipt.point_of_sell.pos_number, "00001")
        self.assertEqual(self.sale_receipt.number, "00000001")
        self.assertEqual(self.sale_receipt.description, "Test sale receipt")
        self.assertEqual(self.sale_receipt.related_invoice, self.sale_invoice)
        self.assertEqual(self.sale_receipt.sender, self.company)
        self.assertEqual(self.sale_receipt.recipient, self.company_client)
        self.assertEqual(self.sale_receipt.total_amount, Decimal("1300.01"))
        self.assertEqual(
            str(self.sale_receipt),
            f"00001-00000001 | A | 2024-02-21"
        )
        

    def test_sale_receipt_constraint(self):
        sale_receipt2 = Sale_receipt.objects.create(
            issue_date = datetime.date(2024, 2, 21),
            type = self.doc_type1,
            point_of_sell = self.pos1,
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
                issue_date = datetime.date(2024, 2, 22),
                type = self.doc_type1,
                point_of_sell = self.pos1,
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
        self.assertEqual(self.purchase_invoice.issue_date, datetime.date(2024, 1, 13))
        self.assertEqual(self.purchase_invoice.type, self.doc_type2)
        self.assertEqual(self.purchase_invoice.point_of_sell, "00231")
        self.assertEqual(self.purchase_invoice.number, "00083051")
        self.assertEqual(self.purchase_invoice.sender, self.supplier)
        self.assertEqual(self.purchase_invoice.recipient, self.company)
        self.assertEqual(self.purchase_invoice.payment_method, self.payment_method2)
        self.assertEqual(self.purchase_invoice.payment_term, self.payment_term2)
        self.assertEqual(
            str(self.purchase_invoice),
            f"00231-00083051 | B | 2024-01-13"
        )

    def test_purchase_invoice_constraint(self):
        purchase_invoice2 = Purchase_invoice.objects.create(
            issue_date=datetime.date(2024, 1, 13),
            type = self.doc_type2,
            point_of_sell = "231",
            number = "99992",
            sender = self.supplier,
            recipient = self.company,
            payment_method = self.payment_method2,
            payment_term = self.payment_term2,
        )

        invoices = Purchase_invoice.objects.all()
        self.assertEqual(invoices.count(), 2)

        with self.assertRaises(IntegrityError):
            purhcase_invoice3 = Purchase_invoice.objects.create(
                issue_date=datetime.date(2024, 1, 14),
                type = self.doc_type2,
                point_of_sell = "00231",
                number = "00083051",
                sender = self.supplier,
                recipient = self.company,
                payment_method = self.payment_method,
                payment_term = self.payment_term,
            )

    def test_purchase_invoice_line_content(self):
        invoice_lines = Purchase_invoice.objects.all()
        self.assertEqual(invoice_lines.count(), 1)
        self.assertEqual(self.purchase_invoice_line1.purchase_invoice, 
            self.purchase_invoice)
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
        purchase_receipts = Purchase_receipt.objects.all()
        self.assertEqual(purchase_receipts.count(), 1)
        self.assertEqual(self.purchase_receipt.issue_date, datetime.date(2024, 2, 13))
        self.assertEqual(self.purchase_receipt.type, self.doc_type2)
        self.assertEqual(self.purchase_receipt.point_of_sell, "00231")
        self.assertEqual(self.purchase_receipt.number, "00000023")
        self.assertEqual(self.purchase_receipt.description, "Test purchase receipt")
        self.assertEqual(self.purchase_receipt.related_invoice, self.purchase_invoice)
        self.assertEqual(self.purchase_receipt.sender, self.supplier)
        self.assertEqual(self.purchase_receipt.recipient, self.company)
        self.assertEqual(self.purchase_receipt.total_amount, Decimal("242"))
        self.assertEqual(
            str(self.purchase_receipt),
            f"00231-00000023 | B | 2024-02-13"
        )
    
    def test_purchase_receipt_constraint(self):
        purchase_receipt2 = Purchase_receipt.objects.create(
            issue_date = datetime.date(2024, 2, 13),
            type = self.doc_type2,
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
                issue_date = datetime.date(2024, 2, 14),
                type = self.doc_type2,
                point_of_sell = "00231",
                number = "00000023",
                description = "Test 3 purchase receipt",
                sender = self.supplier,
                recipient = self.company,
                related_invoice = self.purchase_invoice,
                total_amount = "4000.11",
            )

    def test_client_index_webpage(self):
        response = self.client.get("/erp/client")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/client_index.html")
        self.assertContains(response, "Clients Overview")
    
    def test_client_new_get(self):
        response = self.client.get("/erp/client/new")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/person_new.html")
        self.assertContains(response, "Address:")
        
    def test_client_new_post(self):    
        response = self.client.post(
            reverse("erp:person_new", kwargs={"person_type": "client"}
        ),{
            "tax_number": "30361382485",
            "name": "Client2 SRL",
            "address": "Client2 street, Client city, Chile",
            "email": "client2@email.com",
            "phone": "987654321",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Company_client.objects.all().count(), 3)
        
    def test_client_new_post_error(self):
        response = self.client.post(
            reverse("erp:person_new", kwargs={"person_type": "client"}
        ), {
            "tax_number": "20361382480",
            "name": "Client2 SRL",
            "address": "Client2 street, Client city, Chile",
            "email": "client2@email.com",
            "phone": "987654321",
        })
        # Check an error is displayed.
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors["tax_number"],
            ["The tax number you're trying to add belongs to the company."]
        )

    def test_client_new_multiple_post_csv(self):
        # Get file dir to test
        file_path = os.path.join(os.path.dirname(__file__), "files", "clients",
            "clients.csv")
        
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(), 
            content_type="text/csv")
            response = self.client.post(reverse(
                "erp:person_new_multiple", kwargs={"person_type": "client"}
            ), {"file": uploaded_file})
            self.assertEqual(response.status_code, 302)
            
        # Test DB was updated correctly
        self.assertEqual(Company_client.objects.all().count(), 8)
        client_great = Company_client.objects.get(tax_number="20123456780")
        self.assertEqual(client_great.tax_number, "20123456780")
        self.assertEqual(client_great.name, "GREAT SUGAR SA")
        self.assertEqual(client_great.address, "Mutiple Street 1, Dublin, Ireland")
        self.assertEqual(client_great.email, "mclient1@email.com")
        self.assertEqual(client_great.phone, "3412425841")
    
    def test_client_new_multiple_post_xls(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "clients",
            "clients.xls")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="application/vnd.ms-excel")
            response = self.client.post(reverse(
                "erp:person_new_multiple", kwargs={"person_type": "client"}
            ), {"file": uploaded_file})
            self.assertEqual(response.status_code, 302)
        
        # Test DB was updated correctly
        self.assertEqual(Company_client.objects.all().count(), 8)
        client_great = Company_client.objects.get(tax_number="20123456780")
        self.assertEqual(client_great.tax_number, "20123456780")
        self.assertEqual(client_great.name, "GREAT SUGAR SA")
        self.assertEqual(client_great.address, "Mutiple Street 1, Dublin, Ireland")
        self.assertEqual(client_great.email, "mclient1@email.com")
        self.assertEqual(client_great.phone, "3412425841")

    def test_client_new_multiple_post_xlsx(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "clients",
            "clients.xlsx")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response = self.client.post(reverse(
                "erp:person_new_multiple", kwargs={"person_type": "client"}
            ), {"file": uploaded_file})
            self.assertEqual(response.status_code, 302)
        
        # Test DB was updated correctly
        self.assertEqual(Company_client.objects.all().count(), 8)
        client_great = Company_client.objects.get(tax_number="20123456780")
        self.assertEqual(client_great.tax_number, "20123456780")
        self.assertEqual(client_great.name, "GREAT SUGAR SA")
        self.assertEqual(client_great.address, "Mutiple Street 1, Dublin, Ireland")
        self.assertEqual(client_great.email, "mclient1@email.com")
        self.assertEqual(client_great.phone, "3412425841")

    def test_client_new_multiple_post_pdf(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "clients",
            "clients.pdf")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="application/pdf")
            response = self.client.post(reverse(
                "erp:person_new_multiple", kwargs={"person_type": "client"}
            ), {"file": uploaded_file})
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid file", response.content.decode("utf-8"))
            self.assertEqual(Company_client.objects.all().count(), 2)

    def test_client_new_multiple_post_repeated_client(self):
        # Get file dir to test
        file_path = os.path.join(os.path.dirname(__file__), "files", "clients",
            "clientsbad2.csv")
        
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(), 
            content_type="text/csv")
            response = self.client.post(reverse(
                "erp:person_new_multiple", kwargs={"person_type": "client"}
            ), {"file": uploaded_file})
            
            self.assertEqual(response.status_code, 400)
            self.assertIn("tax number already exists", response.content.decode("utf-8"))
            self.assertEqual(Company_client.objects.all().count(), 2)

    def test_client_new_multiple_post_wrong_data(self):
        # Get file dir to test
        file_path = os.path.join(os.path.dirname(__file__), "files", "clients",
            "clientsbad.csv")
        
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(), 
            content_type="text/csv")
            response = self.client.post(reverse(
                "erp:person_new_multiple", kwargs={"person_type": "client"}
            ), {"file": uploaded_file})
            
            self.assertEqual(response.status_code, 400)
            self.assertIn("must be only digits", response.content.decode("utf-8"))
            self.assertIn("value has at most", response.content.decode("utf-8"))
            self.assertIn("field cannot be blank", response.content.decode("utf-8"))
            self.assertEqual(Company_client.objects.all().count(), 2)

    def test_client_edit_get(self):
        response = self.client.get("/erp/client/edit")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/person_edit.html")
        self.assertContains(response, "CLIENT1 SRL | 20361382481")

    def test_client_delete_get(self):
        response = self.client.get("/erp/client/delete")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/person_delete.html")
        self.assertContains(response, "CLIENT1 SRL | 20361382481")

    def test_supplier_index_webpage(self):
        response = self.client.get("/erp/supplier")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/supplier_index.html")
        self.assertContains(response, "Suppliers Overview")
    
    def test_supplier_new_get(self):
        response = self.client.get("/erp/supplier/new")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/person_new.html")
        self.assertContains(response, "Tax number:")
        
    def test_supplier_new_post(self):    
        response = self.client.post(reverse("erp:person_new", kwargs={"person_type": "supplier"}
        ), {
            "tax_number": "30361382485",
            "name": "Supplier2 SRL",
            "address": "Supplier2 street, Supplier city, Chile",
            "email": "supplier2@email.com",
            "phone": "987654321",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Supplier.objects.all().count(), 2)
        
    def test_supplier_new_post_error(self):
        response = self.client.post(reverse("erp:person_new", kwargs={"person_type": "supplier"}
        ), {
            "tax_number": "20361382480",
            "name": "Supplier2 SRL",
            "address": "Supplier2 street, Supplier city, Chile",
            "email": "supplier2@email.com",
            "phone": "987654321",
        })
        # Check an error is displayed.
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(form.errors["tax_number"],
            ["The tax number you're trying to add belongs to the company."]
        )

    def test_supplier_new_multiple_post_csv(self):
        # Note: As I use same view and template as clients, I only do one test to
        # check that suppliers db is update correctly
        # Get file dir to test
        file_path = os.path.join(os.path.dirname(__file__), "files", "suppliers",
            "suppliers.csv")
        
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(), 
            content_type="text/csv")
            response = self.client.post(reverse(
                "erp:person_new_multiple", kwargs={"person_type": "supplier"}
            ), {"file": uploaded_file})
            self.assertEqual(response.status_code, 302)

        # Test DB was updated correctly
        self.assertEqual(Supplier.objects.all().count(), 7)
        supplier_great = Supplier.objects.get(tax_number="20123456780")
        self.assertEqual(supplier_great.tax_number, "20123456780")
        self.assertEqual(supplier_great.name, "GREAT SUGAR SA")
        self.assertEqual(supplier_great.address, "Mutiple Street 1, Dublin, Ireland")
        self.assertEqual(supplier_great.email, "mclient1@email.com")
        self.assertEqual(supplier_great.phone, "3412425841")

    def test_supplier_edit_get(self):
        response = self.client.get("/erp/supplier/edit")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/person_edit.html")
        self.assertContains(response, "SUPPLIER1 SA | 20361382482")

    def test_supplier_delete_get(self):
        response = self.client.get("/erp/supplier/delete")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/person_delete.html")
        self.assertContains(response, "SUPPLIER1 SA | 20361382482")

    def test_payment_conditions_webpage(self):
        response = self.client.get("/erp/payment_conditions")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "company/payment_conditions.html")
        self.assertContains(response, "Payment Conditions")

    def test_points_of_sell_webpage(self):
        response = self.client.get("/erp/points_of_sell")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "company/points_of_sell.html")
        self.assertContains(response, "Points of Sell")

    def test_doc_types_webpage(self):
        response = self.client.get("/erp/document_types")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "company/doc_types.html")
        self.assertContains(response, "Document Types")

    def test_sales_overview_webpage(self):
        response = self.client.get("/erp/sales")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/sales_index.html")
        self.assertContains(response, "Sales Overview")
        self.assertContains(response, "00001-00000001")

    def test_sales_new_invoice_get_webpage(self):
        response = self.client.get("/erp/sales/invoices/new")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/sales_new.html")
        self.assertContains(response, "Create a new invoice")
        self.assertContains(response, "002 | B")
        # Hidden invoice types are not in the webpage
        self.assertNotContains(response, "019 | E")

    def test_sales_new_invoice_post_single_line_webpage(self):
        response = self.client.post(reverse("erp:sales_new"), {
            # Invoice form
            "issue_date": "29/01/2024",
            "type": self.doc_type2.id,
            "point_of_sell": self.pos2.id,
            "number": "1",
            "sender": self.company.id,
            "recipient": self.company_client.id,
            "payment_method": self.payment_method.id,
            "payment_term": self.payment_term2.id,
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
        })       
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Sale_invoice.objects.all().count(), 2)
        self.assertEqual(Sale_invoice_line.objects.all().count(), 3)

    def test_sales_new_invoice_post_triple_line_webpage(self):
        response = self.client.post(reverse("erp:sales_new"), {
            # Invoice form
            "issue_date": "29/01/2024",
            "type": self.doc_type2.id,
            "point_of_sell": self.pos2.id,
            "number": "1",
            "sender": self.company.id,
            "recipient": self.company_client.id,
            "payment_method": self.payment_method.id,
            "payment_term": self.payment_term2.id,
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
        })       
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Sale_invoice.objects.all().count(), 2)
        self.assertEqual(Sale_invoice_line.objects.all().count(), 5)

    def test_sales_new_invoice_post_wrong_date_webpage(self):
        response = self.client.post(reverse("erp:sales_new"), {
            # Invoice form
            "issue_date": "29/01/2025",
            "type": self.doc_type2.id,
            "point_of_sell": self.pos2.id,
            "number": "1",
            "sender": self.company.id,
            "recipient": self.company_client.id,
            "payment_method": self.payment_method.id,
            "payment_term": self.payment_term2.id,
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
        })       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Sale_invoice.objects.all().count(), 1)
        self.assertEqual(Sale_invoice_line.objects.all().count(), 2)
        self.assertContains(response, "The selected date is not within the current year.")

    def test_sales_new_invoice_post_blank_line_webpage(self):
        response = self.client.post(reverse("erp:sales_new"), {
            # Invoice form
            "issue_date": "29/01/2024",
            "type": self.doc_type2.id,
            "point_of_sell": self.pos2.id,
            "number": "1",
            "sender": self.company.id,
            "recipient": self.company_client.id,
            "payment_method": self.payment_method.id,
            "payment_term": self.payment_term2.id,
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
        })       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Sale_invoice.objects.all().count(), 1)
        self.assertEqual(Sale_invoice_line.objects.all().count(), 2)

    def test_sales_new_massive_invoice_get(self):
        response = self.client.get("/erp/sales/invoices/new_massive")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/sales_new_massive.html")
        self.assertContains(response, "Create massive new invoices")
        self.assertContains(response, "Upload")

    def test_sales_new_massive_invoice_post_csv(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "sales",
            "invoice_one_line.csv")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="text/csv")
            response = self.client.post(reverse("erp:sales_new_massive"), {
                "file": uploaded_file
            })
            self.assertEqual(response.status_code, 302)

        # Test DB was updated correctly
        self.assertEqual(Sale_invoice.objects.all().count(), 2)
        self.assertEqual(Sale_invoice_line.objects.all().count(), 3)
        new_invoice = Sale_invoice.objects.get(
            type=self.doc_type1, point_of_sell=self.pos2, number="00000001")
        invoice_line = Sale_invoice_line.objects.get(sale_invoice = new_invoice)
        self.assertEqual(new_invoice.issue_date, datetime.date(2024, 3, 15))
        self.assertEqual(new_invoice.type, self.doc_type1)
        self.assertEqual(new_invoice.point_of_sell, self.pos2)
        self.assertEqual(new_invoice.number, "00000001")
        self.assertEqual(new_invoice.sender, self.company)
        self.assertEqual(new_invoice.recipient, self.company_client)
        self.assertEqual(new_invoice.payment_term, self.payment_term2)
        self.assertEqual(new_invoice.payment_method, self.payment_method)
        self.assertEqual(invoice_line.description, "A mouse")
        self.assertEqual(invoice_line.taxable_amount, Decimal("1000"))
        self.assertEqual(invoice_line.not_taxable_amount, Decimal("50"))
        self.assertEqual(invoice_line.vat_amount, Decimal("105"))
        self.assertEqual(invoice_line.total_amount, Decimal("1155"))

    def test_sales_new_massive_invoice_post_xls(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "sales",
            "invoice_one_line.xls")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="application/vnd.ms-excel")
            response = self.client.post(reverse("erp:sales_new_massive"), {
                "file": uploaded_file
            })
            self.assertEqual(response.status_code, 302)
        # Test DB was updated correctly
        self.assertEqual(Sale_invoice.objects.all().count(), 2)
        self.assertEqual(Sale_invoice_line.objects.all().count(), 3)
        new_invoice = Sale_invoice.objects.get(
        type=self.doc_type1, point_of_sell=self.pos2, number="00000001")
        invoice_line = Sale_invoice_line.objects.get(sale_invoice = new_invoice)
        self.assertEqual(new_invoice.issue_date, datetime.date(2024, 3, 15))
        self.assertEqual(new_invoice.type, self.doc_type1)
        self.assertEqual(new_invoice.point_of_sell, self.pos2)
        self.assertEqual(new_invoice.number, "00000001")
        self.assertEqual(new_invoice.sender, self.company)
        self.assertEqual(new_invoice.recipient, self.company_client)
        self.assertEqual(new_invoice.payment_term, self.payment_term2)
        self.assertEqual(new_invoice.payment_method, self.payment_method)
        self.assertEqual(invoice_line.description, "A mouse")
        self.assertEqual(invoice_line.taxable_amount, Decimal("1000"))
        self.assertEqual(invoice_line.not_taxable_amount, Decimal("50"))
        self.assertEqual(invoice_line.vat_amount, Decimal("105"))
        self.assertEqual(invoice_line.total_amount, Decimal("1155"))

    def test_sales_new_massive_invoice_post_xlsx(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "sales",
            "invoice_one_line.xlsx")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response = self.client.post(reverse("erp:sales_new_massive"), {
                "file": uploaded_file
            })
            self.assertEqual(response.status_code, 302)
        # Test DB was updated correctly
        self.assertEqual(Sale_invoice.objects.all().count(), 2)
        self.assertEqual(Sale_invoice_line.objects.all().count(), 3)
        new_invoice = Sale_invoice.objects.get(
        type=self.doc_type1, point_of_sell=self.pos2, number="00000001")
        invoice_line = Sale_invoice_line.objects.get(sale_invoice = new_invoice)
        self.assertEqual(new_invoice.issue_date, datetime.date(2024, 3, 15))
        self.assertEqual(new_invoice.type, self.doc_type1)
        self.assertEqual(new_invoice.point_of_sell, self.pos2)
        self.assertEqual(new_invoice.number, "00000001")
        self.assertEqual(new_invoice.sender, self.company)
        self.assertEqual(new_invoice.recipient, self.company_client)
        self.assertEqual(new_invoice.payment_term, self.payment_term2)
        self.assertEqual(new_invoice.payment_method, self.payment_method)
        self.assertEqual(invoice_line.description, "A mouse")
        self.assertEqual(invoice_line.taxable_amount, Decimal("1000"))
        self.assertEqual(invoice_line.not_taxable_amount, Decimal("50"))
        self.assertEqual(invoice_line.vat_amount, Decimal("105"))
        self.assertEqual(invoice_line.total_amount, Decimal("1155"))

    def test_sales_new_massive_invoice_pdf(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "sales",
            "invoice_one_line.pdf")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="application/pdf")
            response = self.client.post(reverse("erp:sales_new_massive"), {
                "file": uploaded_file
            })
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid file", response.content.decode("utf-8"))
            self.assertEqual(Sale_invoice.objects.all().count(), 1)

    def test_sales_new_massive_invoice_multiple_lines_post_xlsx(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "sales",
            "invoice_multiple_lines.xlsx")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response = self.client.post(reverse("erp:sales_new_massive"), {
                "file": uploaded_file
            })
            self.assertEqual(response.status_code, 302)
        # Test DB was updated correctly
        self.assertEqual(Sale_invoice.objects.all().count(), 2)
        self.assertEqual(Sale_invoice_line.objects.all().count(), 5)
        new_invoice = Sale_invoice.objects.get(
        type=self.doc_type1, point_of_sell=self.pos2, number="00000001")
        invoice_lines = Sale_invoice_line.objects.filter(sale_invoice=new_invoice)
        self.assertEqual(new_invoice.issue_date, datetime.date(2024, 3, 15))
        self.assertEqual(new_invoice.type, self.doc_type1)
        self.assertEqual(new_invoice.point_of_sell, self.pos2)
        self.assertEqual(new_invoice.number, "00000001")
        self.assertEqual(new_invoice.sender, self.company)
        self.assertEqual(new_invoice.recipient, self.company_client)
        self.assertEqual(new_invoice.payment_term, self.payment_term2)
        self.assertEqual(new_invoice.payment_method, self.payment_method)
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
        file_path = os.path.join(os.path.dirname(__file__), "files", "sales",
            "invoices_mixed.xlsx")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response = self.client.post(reverse("erp:sales_new_massive"), {
                "file": uploaded_file
            })
            self.assertEqual(response.status_code, 302)
        # Test DB was updated correctly
        self.assertEqual(Sale_invoice.objects.all().count(), 6)
        self.assertEqual(Sale_invoice_line.objects.all().count(), 10)
        new_invoice = Sale_invoice.objects.get(
        type=self.doc_type1, point_of_sell=self.pos2, number="00000004")
        invoice_lines = Sale_invoice_line.objects.filter(sale_invoice=new_invoice)
        self.assertEqual(new_invoice.issue_date, datetime.date(2024, 3, 16))
        self.assertEqual(new_invoice.type, self.doc_type1)
        self.assertEqual(new_invoice.point_of_sell, self.pos2)
        self.assertEqual(new_invoice.number, "00000004")
        self.assertEqual(new_invoice.sender, self.company)
        self.assertEqual(new_invoice.recipient, self.company_client)
        self.assertEqual(new_invoice.payment_term, self.payment_term2)
        self.assertEqual(new_invoice.payment_method, self.payment_method)
        self.assertEqual(invoice_lines[0].description, "A monitor")
        self.assertEqual(invoice_lines[0].taxable_amount, Decimal("100.22"))
        self.assertEqual(invoice_lines[0].not_taxable_amount, Decimal("0"))
        self.assertEqual(invoice_lines[0].vat_amount, Decimal("10.52"))
        self.assertEqual(invoice_lines[0].total_amount, Decimal("110.74"))

    def test_sales_new_massive_invoice_post_repeated(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "sales",
            "invoice_one_line_repeated.csv")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="text/csv")
            response = self.client.post(reverse("erp:sales_new_massive"), {
                "file": uploaded_file
            })
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invoice A 00001-00000001 already exists.",
                response.content.decode("utf-8")
            )
            self.assertEqual(Sale_invoice.objects.all().count(), 1)
            self.assertEqual(Sale_invoice_line.objects.all().count(), 2)
    
    def test_sales_new_massive_invoice_post_wrong_data(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "sales",
            "invoice_one_line_wrong.csv")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="text/csv")
            response = self.client.post(reverse("erp:sales_new_massive"), {
                "file": uploaded_file
            })
            self.assertEqual(response.status_code, 400)
            self.assertIn("must be only digits", response.content.decode("utf-8"))
            self.assertEqual(Sale_invoice.objects.all().count(), 1)
            self.assertEqual(Sale_invoice_line.objects.all().count(), 2)

    def test_sales_new_massive_invoice_post_wrong_data_2(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "sales",
            "invoice_one_line_wrong2.csv")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="text/csv")
            response = self.client.post(reverse("erp:sales_new_massive"), {
                "file": uploaded_file
            })
            self.assertEqual(response.status_code, 400)
            self.assertIn("The input in row 2 and column sender doesn't exist",
                response.content.decode("utf-8"))
            self.assertEqual(Sale_invoice.objects.all().count(), 1)
            self.assertEqual(Sale_invoice_line.objects.all().count(), 2)
    
    def test_sales_new_massive_invoice_post_wrong_data_3(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "sales",
            "invoice_one_line_wrong3.csv")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="text/csv")
            response = self.client.post(reverse("erp:sales_new_massive"), {
                "file": uploaded_file
            })
            self.assertEqual(response.status_code, 400)
            self.assertIn("must be a decimal number", response.content.decode("utf-8"))
            self.assertIn("cannot be blank", response.content.decode("utf-8"))
            self.assertEqual(Sale_invoice.objects.all().count(), 1)
            self.assertEqual(Sale_invoice_line.objects.all().count(), 2)

    def test_sales_new_massive_invoices_multiple_lines_post_wrong_data(self):
        file_path = os.path.join(os.path.dirname(__file__), "files", "sales",
            "invoices_mixed_wrong.csv")
        with open(file_path, "rb") as file:
            uploaded_file = SimpleUploadedFile(file.name, file.read(),
                content_type="text/csv")
            response = self.client.post(reverse("erp:sales_new_massive"), {
                "file": uploaded_file
            })
            self.assertEqual(response.status_code, 400)
            self.assertIn("Row 10: Your invoice's information doesn't match with row 9",
                response.content.decode("utf-8"))
            self.assertEqual(Sale_invoice.objects.all().count(), 1)
            self.assertEqual(Sale_invoice_line.objects.all().count(), 2)

    def test_sales_invoice_multiline_webpage(self):
        response = self.client.get("/erp/sales/invoices/1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/sales_invoice.html")
        self.assertContains(response, "Invoice N° 00001-00000001")
        self.assertContains(response, "$ 1300.01")
        self.assertContains(response, "$ 2509.01")
        
    def test_sales_search_webpage(self):
        response = self.client.get("/erp/sales/invoices/search")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/sales_search.html")
        self.assertContains(response, "Search Invoice")
        self.assertContains(response, "Year")
        
    def test_sales_edit_invoice_get_webpage(self):
        response = self.client.get("/erp/sales/invoices/1/edit")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/sales_edit.html")
        self.assertContains(response, "Edit Invoice")
        self.assertContains(response, "00000001")
        self.assertContains(response, "209.99")

    def test_sales_edit_invoice_post_webpage(self):
        response = self.client.post(reverse("erp:sales_edit", 
            args=[self.sale_invoice.pk]), {
                # Invoice form
                "issue_date": "21/01/2024",
                "type": self.doc_type1.id,
                "point_of_sell": self.pos1.id,
                "number": "1",
                "sender": self.company.id,
                "recipient": self.company_client2.id,
                "payment_method": self.payment_method2.id,
                "payment_term": self.payment_term2.id,
                # line-setform-management. Modify 2 lines, add 1.
                "s_invoice_lines-TOTAL_FORMS": "3",
                "s_invoice_lines-INITIAL_FORMS": "2",
                "s_invoice_lines-MIN_NUM_FORMS": "0",
                "s_invoice_lines-MAX_NUM_FORMS": "1000",
                # line-1-setform / Modify all fields
                "s_invoice_lines-0-id": self.sale_invoice.id,
                "s_invoice_lines-0-description": "Random products",
                "s_invoice_lines-0-taxable_amount": Decimal("2000"),
                "s_invoice_lines-0-not_taxable_amount": Decimal("180.02"),
                "s_invoice_lines-0-vat_amount": Decimal("420"),
                # line-2-setform / Modify all fields
                "s_invoice_lines-1-id": self.sale_invoice.id,
                "s_invoice_lines-1-description": "Custom products",
                "s_invoice_lines-1-taxable_amount": Decimal("1000"),
                "s_invoice_lines-1-not_taxable_amount": Decimal("80.02"),
                "s_invoice_lines-1-vat_amount": Decimal("20"),
                # line-3-setform / New line added
                "s_invoice_lines-2-id": self.sale_invoice.id,
                "s_invoice_lines-2-description": "A few products",
                "s_invoice_lines-2-taxable_amount": Decimal("333"),
                "s_invoice_lines-2-not_taxable_amount": Decimal("33.32"),
                "s_invoice_lines-2-vat_amount": Decimal("33")
            })   
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Sale_invoice.objects.all().count(), 1)
        self.assertEqual(Sale_invoice_line.objects.all().count(), 3)

    def test_sales_list_get_webpage(self):
        response = self.client.get("/erp/sales/invoices/list")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "erp/sales_list.html")
        self.assertContains(response, "Sales List")
        self.assertContains(response, "Client Name")
        # Reminder: Current year is 2024
        self.assertContains(response, "21/01/2024")

    def test_sales_list_post_year_webpage(self):
        # Add financial year and an invoice before testing
        FinancialYear.objects.create(year = "2025")
        self.create_extra_invoices()
        response = self.client.post(reverse("erp:sales_list"), {
            "year": "2025",
            "form_type": "year",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "23/06/2025")
        self.assertContains(response, "20361382481")
        self.assertContains(response, "600.01")

    def test_sales_list_post_year_no_financial_webpage(self):
        response = self.client.post(reverse("erp:sales_list"), {
            "year": "2025",
            "form_type": "year",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The year 2025 doesn")
        # By default, current's year invoices should appear
        self.assertContains(response, "21/01/2024")
        self.assertContains(response, "00000001")
        
    def test_sales_list_post_year_no_invoice_webpage(self):
        FinancialYear.objects.create(year = "2025")
        response = self.client.post(reverse("erp:sales_list"), {
            "year": "2025",
            "form_type": "year",
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "The year 2025 doesn't exist in the records.")
        self.assertContains(response, "There isn't any invoice in this period of time.")
        
    def test_sales_list_post_dates_webpage(self):
        self.create_extra_invoices()
        response = self.client.post(reverse("erp:sales_list"), {
            "date_from": "23/04/2024",
            "date_to": "24/04/2024",
            "form_type": "date",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "00000002")
        self.assertContains(response, "00000003")
        self.assertContains(response, "00000004")
        self.assertNotContains(response, "00000001")

    def test_sales_list_post_dates_same_webpage(self):
        self.create_extra_invoices()
        response = self.client.post(reverse("erp:sales_list"), {
            "date_from": "23/04/2024",
            "date_to": "23/04/2024",
            "form_type": "date",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "00000002")
        self.assertContains(response, "00000003")
        self.assertNotContains(response, "00000004")
    
    def test_sales_list_post_dates_inverted_webpage(self):
        self.create_extra_invoices()
        response = self.client.post(reverse("erp:sales_list"), {
            "date_from": "24/04/2024",
            "date_to": "23/04/2024",
            "form_type": "date",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "should be older")
        self.assertNotContains(response, "00000002")
        self.assertNotContains(response, "00000004")
        