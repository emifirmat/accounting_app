"""API tests for ERP app"""
import datetime
from decimal import Decimal
from django.urls import reverse
from django.test import tag
from rest_framework import status
from rest_framework.test import APITestCase

from company.models import Company
from utils.base_tests import APIBaseTest, CreateDbInstancesMixin
from ..models import (CompanyClient, Supplier, PaymentMethod, PaymentTerm,
    PointOfSell, DocumentType, SaleInvoice, SaleInvoiceLine, SaleReceipt)


@tag("erp_api")
class APIErpTests(CreateDbInstancesMixin, APIBaseTest):
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
        cls.c_client1 = CompanyClient.objects.create(
            tax_number = "20361382481",
            name = "Client1 SRL",
            address = "Client street, Client city, Chile",
            email = "c_client1@email.com",
            phone = "1234567890",
        )
        cls.c_client2 = CompanyClient.objects.create(
            tax_number = "99999999999",
            name = "Client2 SRL",
            address = "Client2 street, Client city, Argentina",
            email = "c_client2@email.com",
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
        
        cls.pos1 = PointOfSell.objects.create(pos_number = "00001")
        cls.pos2 = PointOfSell.objects.create(pos_number = "00002")
        cls.pos3 = PointOfSell.objects.create(pos_number = "00003")
        
        cls.doc_type1 = DocumentType.objects.create(
            type = "A",
            code = "1",
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
        cls.sale_invoice_line1 = SaleInvoiceLine.objects.create(
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

        cls.sale_invoice2 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 22),
            type = cls.doc_type2,
            point_of_sell = cls.pos1,
            number = "1",
            sender = cls.company,
            recipient = cls.c_client1,
            payment_method = cls.pay_method2,
            payment_term = cls.pay_term2,
        )

        cls.sale_invoice3 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 23),
            type = cls.doc_type1,
            point_of_sell = cls.pos1,
            number = "00000002",
            sender = cls.company,
            recipient = cls.c_client1,
            payment_method = cls.pay_method1,
            payment_term = cls.pay_term1,
        )

        cls.sale_invoice4 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 24),
            type = cls.doc_type1,
            point_of_sell = cls.pos1,
            number = "00000003",
            sender = cls.company,
            recipient = cls.c_client1,
            payment_method = cls.pay_method1,
            payment_term = cls.pay_term1,
        )

        cls.sale_receipt1 = SaleReceipt.objects.create(
            issue_date = datetime.date(2024, 1, 22),
            point_of_sell = cls.pos1,
            number = "00000001",
            description = "Test sale receipt",
            related_invoice = cls.sale_invoice1,
            sender = cls.company,
            recipient = cls.c_client1,
            total_amount = Decimal("2509.01"),
        )
        cls.sale_receipt2 = SaleReceipt.objects.create(
            issue_date = datetime.date(2024, 2, 22),
            point_of_sell = cls.pos1,
            number = "00000002",
            description = "Second receipt",
            related_invoice = cls.sale_invoice2,
            sender = cls.company,
            recipient = cls.c_client1,
            total_amount = Decimal("600.01"),
        )

    def test_company_client_api(self):
        self.check_api_get_response(
            "/erp/api/clients",
            "erp:clients_api",
            page_content=["20361382481", "99999999999"],
            count=2,
        )

    def test_company_client_delete_multiple_api(self):
        self.create_company_clients()
        delete_object = {"ids": [self.c_client3.pk, self.c_client5.pk, self.c_client7.pk]}
        
        self.check_api_delete_response(
            ["erp:clients_delete_api"],
            status.HTTP_204_NO_CONTENT,
            (CompanyClient, 4),
            delete_object,
        )

    def test_company_client_delete_multiple_conlfict_api(self):
        delete_object = {"ids": [self.c_client1.pk, self.c_client2.pk]}
        
        self.check_api_delete_response(
            ["erp:clients_delete_api"],
            status.HTTP_409_CONFLICT,
            (CompanyClient, 2),
            delete_object,
        )

    def test_detail_company_client_api(self):
        self.check_api_get_response(
            f"/erp/api/clients/{self.c_client2.pk}",
            ["erp:client_api", {"pk": self.c_client2.pk}],
            page_content=["Client2 Street", "99999999999"],
            wrong_content=["20361382481"]
        )
    
    def test_detail_company_client_delete_api(self):
        self.check_api_delete_response(
            ["erp:client_api", {"pk": self.c_client2.pk}],
            status.HTTP_204_NO_CONTENT,
            (CompanyClient, 1)
        )

    def test_detail_company_client_delete_conflict_api(self):
        self.check_api_delete_response(
            ["erp:client_api", {"pk": self.c_client1.pk}],
            status.HTTP_409_CONFLICT,
            (CompanyClient, 2)
        )

    def test_detail_company_client_dynamic_serializer_api(self):
        url = f"/erp/api/clients/{self.c_client2.pk}"
        self.check_api_get_response(
            f"{url}?fields=id,name,tax_number",
            # page content includes display_name
            page_content=["CLIENT2 SRL", "99999999999"],
            wrong_content=["12443131241"],
            count=3, # Number of fields in the object
        )

    def test_supplier_api(self):
        self.check_api_get_response(
           "/erp/api/suppliers",
            "erp:suppliers_api",
            page_content=["SUPPLIER1 SA", "SUPPLIER2 SRL"],
            count=2,
        )

    def test_supplier_delete_multiple_api(self):
        delete_object = {"ids": [self.supplier1.pk, self.supplier2.pk]}

        self.check_api_delete_response(
            ["erp:suppliers_delete_api"],
            status.HTTP_204_NO_CONTENT,
            (Supplier, 0),
            delete_object,
        )

    # TODO add multiple delete conflict after adding purhcase invoices
    """
    def test_supplier_delete_multiple_api(self):
        delete_object = {"ids": [self.supplier1.pk, self.supplier2.pk]}

        self.check_api_delete_response(
            ["erp:suppliers_delete_api"],
            status.HTTP_204_NO_CONTENT,
            (Supplier, 0),
            delete_object,
        )
    """

    def test_detail_supplier_api(self):
        self.check_api_get_response(
            f"/erp/api/suppliers/{self.supplier1.pk}",
            ["erp:supplier_api", {"pk": self.supplier1.pk}],
            page_content=["Supplier1@email.com", "20361382482"],
            wrong_content=["30361382485"]
        )

    def test_detail_supplier_delete_api(self):
        self.check_api_delete_response(
            ["erp:supplier_api", {"pk": self.supplier2.pk}],
            status.HTTP_204_NO_CONTENT,
            (Supplier, 1)
        )

    # TODO: Delete comment once I have a purchase invoice that generate conflict
    """
    def test_detail_supplier_delete_conflict_api(self):
        self.check_api_delete_response(
            ["erp:supplier_api", {"pk": self.supplier1.pk}],
            status.HTTP_409_CONFLICT,
            (Supplier, 2)
        )
    """

    def test_payment_methods_api(self):
        self.check_api_get_response(
           "/erp/api/payment_conditions/methods",
            "erp:payment_methods_api",
            page_content=["Cash", "Transfer"],
            count=2,
        )
    
    def test_payment_methods_create_multiple_api(self):
        post_object = [{"pay_method": "check"}, {"pay_method": "crypto"}]
        
        self.check_api_post_response(
            "erp:payment_methods_api", post_object, (PaymentMethod, 4)
        )
    
    def test_payment_method_api(self):
        self.check_api_get_response(
            f"/erp/api/payment_conditions/methods/{self.pay_method1.pk}",
            ["erp:payment_method_api", {"pk": self.pay_method1.pk}],
            page_content=["Cash"],
            wrong_content=["Transfer"]
        )

    def test_payment_method_delete_conflict_api(self):
        self.check_api_delete_response(
            ["erp:payment_method_api", {"pk": self.pay_method1.pk}],
            status.HTTP_409_CONFLICT,
            (PaymentMethod, 2)
        )

    def test_payment_terms_api(self):
        self.check_api_get_response(
           "/erp/api/payment_conditions/terms",
            "erp:payment_terms_api",
            page_content=["30"],
            count=2,
        )
    
    def test_payment_terms_create_multiple_api(self):
        post_object = [{"pay_term": "15"}, {"pay_term": "45"}, {"pay_term": "60"}]
        
        self.check_api_post_response(
            "erp:payment_terms_api", post_object, (PaymentTerm, 5)
        )

    def test_payment_term_api(self):
        self.check_api_get_response(
            f"/erp/api/payment_conditions/terms/{self.pay_term2.pk}",
            ["erp:payment_term_api", {"pk": self.pay_term2.pk}],
            page_content=["30"],
            wrong_content=["1"] # pay_term1.pk
        )

    def test_payment_term_delete_conflict_api(self):
        self.check_api_delete_response(
            ["erp:payment_term_api", {"pk": self.pay_term1.pk}],
            status.HTTP_409_CONFLICT,
            (PaymentTerm, 2)
        )

    def test_points_of_sell_api(self):
        self.check_api_get_response(
           "/erp/api/points_of_sell",
            "erp:pos_api",
            page_content=["00001","00002", "00003"],
            count=3,
        )

    def test_point_of_sell_api(self):
        self.check_api_get_response(
            f"/erp/api/points_of_sell/{self.pos3.pk}",
            ["erp:detail_pos_api", {"pk": self.pos3.pk}],
            page_content=["00003"],
            wrong_content=["00001", "00002"]
        )

    def test_point_of_sell_dynamic_serializer_api(self):
        url = f"/erp/api/points_of_sell/{self.pos3.pk}"
        self.check_api_get_response(
            f"{url}?fields=id,pos_number",
            # page content includes display_name
            page_content=["00003"],
            count=2, # Number of fields in the object
        )


    def test_doc_types_api(self):
        self.check_api_get_response(
           "/erp/api/document_types",
            "erp:doc_types_api",
            page_content=["A","INVOICE B", "19"],
            count=3,
        )

    def test_doc_type_api(self):
        self.check_api_get_response(
            f"/erp/api/document_types/{self.doc_type2.pk}",
            ["erp:doc_type_api", {"pk": self.doc_type2.pk}],
            page_content=["B", "false"],
            wrong_content=["00001", "INVOICE E"]
        )

    def test_doc_type_dynamic_serializer_api(self):
        url = f"/erp/api/document_types/{self.doc_type2.pk}"
        self.check_api_get_response(
            f"{url}?fields=type",
            # page content includes display_name
            page_content=["B"],
            wrong_content=["2"],
            count=1, # Number of fields in the object
        )
        
    def test_sale_invoices_api(self):
        self.check_api_get_response(
           "/erp/api/sale_invoices",
            "erp:sale_invoices_api",
            # page content includes display_name
            page_content=["00000001","B 00001-00000001", "00000002"],
            count=4,
        )

    def test_sale_invoices_collected_api(self):
        self.check_api_get_response(
           "/erp/api/sale_invoices?collected=True",
            # page content includes display_name
            page_content=["00000001","A 00001-00000001"],
            wrong_content=["00000002"],
            count=1,
        )
        self.check_api_get_response(
           "/erp/api/sale_invoices?collected=False",
            # page content includes display_name
            page_content=["A 00001-00000002"],
            wrong_content=["A 00001-00000001"],
            count=3,
        )
        self.check_api_get_response(
           "/erp/api/sale_invoices?collected=nope",
            count=4,
        )

    def test_sale_invoices_exclusion_api(self):
        self.check_api_get_response(
            f"/erp/api/sale_invoices?exclude_inv_pk={self.sale_invoice2.pk}",
            # page content includes display_name
            page_content=["A 00001-00000002","A 00001-00000001"],
            wrong_content=["B 00001-00000001"],
            count=3,
        )
  
    def test_sale_invoices_collected_exclusion_api(self):
        self.check_api_get_response(
            f"/erp/api/sale_invoices?collected=false&exclude_inv_pk={self.sale_invoice2.pk}",
            # page content includes display_name
            page_content=["A 00001-00000002", "A 00001-00000003"],
            wrong_content=["B 00001-00000001", "A 00001-00000001"],
            count=2,
        )

    def test_sale_invoices_dynamic_serializer_api(self):
        self.check_api_get_response(
            f"/erp/api/sale_invoices?fields=issue_date,number&collected=true",
            page_content=["2024-01-21", "00000001"],
            wrong_content=["A 00001-00000001"],
            count=1,
        )

    def test_sale_invoices_delete_multiple_api(self):
        delete_object = {"ids": [self.sale_invoice3.pk, self.sale_invoice4.pk]}
        
        self.check_api_delete_response(
            ["erp:sale_invoices_delete_api"],
            status.HTTP_204_NO_CONTENT,
            (SaleInvoice, 2),
            delete_object,
        )

    def test_sale_invoices_delete_multiple_conflict_api(self):
        delete_object = {"ids": [self.sale_invoice1.pk, self.sale_invoice2.pk,
            self.sale_invoice3.pk]}
        
        self.check_api_delete_response(
            ["erp:sale_invoices_delete_api"],
            status.HTTP_409_CONFLICT,
            (SaleInvoice, 4),
            delete_object,
        )

    def test_sale_invoice_api(self):
        self.check_api_get_response(
            f"/erp/api/sale_invoices/{self.sale_invoice1.pk}",
            ["erp:sale_invoice_api", {"pk": self.sale_invoice1.pk}],
            page_content=["2024-01-21", "true"],
            # Particular apis don't have display_name
            wrong_content=["A 00001-00000001", "00000002"]
        )

    def test_sale_invoice_delete_api(self):
        self.check_api_delete_response(
            ["erp:sale_invoice_api", {"pk": self.sale_invoice3.pk}],
            status.HTTP_204_NO_CONTENT,
            (SaleInvoice, 3)
        )

    def test_sale_invoice_delete_conflict_api(self):
        self.check_api_delete_response(
            ["erp:sale_invoice_api", {"pk": self.sale_invoice1.pk}],
            status.HTTP_409_CONFLICT,
            (SaleInvoice, 4)
        )

    def test_sale_invoice_dynamic_serializer_api(self):
        url = f"/erp/api/sale_invoices/{self.sale_invoice1.pk}"
        self.check_api_get_response(
            f"{url}?fields=issue_date,number",
            # page content includes display_name
            page_content=["2024-01-21", "00000001"],
            wrong_content=["A 00001-00000001"],
            count=2, # Number of fields in the object
        )

    def test_sale_receipts_api(self):
        self.check_api_get_response(
           "/erp/api/sale_receipts",
            "erp:sale_receipts_api",
            # page content includes display_name
            page_content=["00000001","600.01"],
            count=2,
        )

    def test_sale_receipts_delete_multiple_api(self):
        delete_object = {"ids": [self.sale_receipt1.pk, self.sale_receipt2.pk]}
        
        self.check_api_delete_response(
            ["erp:sale_receipts_delete_api"],
            status.HTTP_204_NO_CONTENT,
            (SaleReceipt, 0),
            delete_object,
        )

    def test_sale_receipt_api(self):
        self.check_api_get_response(
            f"/erp/api/sale_receipts/{self.sale_receipt1.pk}",
            ["erp:sale_receipt_api", {"pk": self.sale_receipt1.pk}],
            # page content includes display_name
            page_content=["00000001","2509.01"],
            wrong_content=["00000002", "2024-02-22"],
        )

    def test_sale_receipt_dynamic_serializer_api(self):
        url = f"/erp/api/sale_receipts/{self.sale_receipt2.pk}"
        url += f"?fields=total_amount,related_invoice"

        self.check_api_get_response(
            url,
            page_content=["600.01", f"{self.sale_invoice2.pk}"],
            wrong_content=["Second receipt"],
            count=2,
        )

 