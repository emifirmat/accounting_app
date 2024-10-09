"""Selenium tests for erp app"""
import datetime, time
from decimal import Decimal
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select


from company.models import Company, FinancialYear
from ..models import (Company_client, Supplier, Payment_method, Payment_term,
    Point_of_sell, Document_type, Sale_invoice, Sale_invoice_line, Sale_receipt)
from utils.utils_tests import (go_to_section, element_has_selected_option, 
    edit_person_click_on_person, edit_person_click_on_edit, fill_field,
    delete_person_click_on_delete, pay_conditions_click_default,
    pay_conditions_delete_confirm_button, pick_option_by_index, search_fill_field,
    search_clear_field, create_extra_pay_terms, create_extra_pay_methods,
    get_columns_data, manual_explicit_wait, click_and_wait, first_input_search)


class FrontBaseTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        """Start Selenium webdriver"""
        super().setUpClass()
        """
        # Set console log to see browser errors
        options = Options()
        options.log.level = "trace"
        # Iniciar GeckoDriver con las opciones configuradas
        path = Path.home() / ".local" / "bin" / "geckodriver"
        service = Service(executable_path=path)
        """
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        """Close selenium webdriver"""
        cls.driver.quit()
        super().tearDownClass()

    # Common Set Up
    def setUp(self):
        """Populate db and load index page"""
        self.company = Company.objects.create(
            tax_number = "20361382480",
            name = "Test Company SRL",
            address = "fake street 123, fakycity, Argentina",
            email = "testcompany@email.com",
            phone = "5493465406182",
            creation_date = datetime.date(1991, 3, 10),
            closing_date = datetime.date(2024, 6, 30),
        )
        
        self.c_client1 = Company_client.objects.create(
            tax_number = "20361382481",
            name = "Client1 SRL",
            address = "Client street, Client city, Chile",
            email = "client1@email.com",
            phone = "1234567890",
        )

        self.c_client2 = Company_client.objects.create(
            tax_number = "99999999999",
            name = "Client2 SA",
            address = "Client2 street, Client city, Chile",
            email = "client2@email.com",
            phone = "0987654321",
        )

        self.supplier1 = Supplier.objects.create(
            tax_number = "20361382482",
            name = "Supplier1 SA",
            address = "Supplier street, Supplier city, Chile",
            email = "Supplier1@email.com",
            phone = "0987654321",
        )

        self.supplier2 = Supplier.objects.create(
            tax_number = "30361382485",
            name = "Supplier2 SRL",
            address = "Supplier2 street, Supplier city, Chile",
            email = "supplier2@email.com",
            phone = "987654321",
        )

        self.pos1 = Point_of_sell.objects.create(pos_number = "00001")

        self.pay_method1 = Payment_method.objects.create(pay_method = "Cash")
        self.pay_method2 = Payment_method.objects.create(pay_method = "Transfer")

        self.pay_term1 = Payment_term.objects.create(pay_term = "0")
        self.pay_term2 = Payment_term.objects.create(pay_term = "30")


"""Tests"""
@tag("erp_front_simple_models")
class ErpFrontTestCase(FrontBaseTest):

    def test_navigation(self):
        # Index
        self.driver.get(f"{self.live_server_url}")
        self.assertEqual(self.driver.title, "Index")

        # Client
        go_to_section(self.driver, "client", 0)
        self.assertEqual(self.driver.title, "Clients")
        go_to_section(self.driver, "client", 1)
        self.assertEqual(self.driver.title, "New Client")
        go_to_section(self.driver, "client", 2)
        self.assertEqual(self.driver.title, "Edit Client")
        go_to_section(self.driver, "client", 3)
        self.assertEqual(self.driver.title, "Delete Client")
        
        # TODO
        """
        go_to_section(self.driver, "client", 4)
        self.assertEqual(self.driver.title, "Client Current Account")
        """

        # Supplier
        go_to_section(self.driver, "supplier", 0)
        self.assertEqual(self.driver.title, "Suppliers")
        go_to_section(self.driver, "supplier", 1)
        self.assertEqual(self.driver.title, "New Supplier")
        go_to_section(self.driver, "supplier", 2)
        self.assertEqual(self.driver.title, "Edit Supplier")
        go_to_section(self.driver, "supplier", 3)
        self.assertEqual(self.driver.title, "Delete Supplier")
        
        # TODO
        """
        go_to_section(self.driver, "supplier", 4)
        self.assertEqual(self.driver.title, "Supplier Current Account")
        """

    def test_client_edit(self):
        # Go to edit client page
        self.driver.get(f"{self.live_server_url}/erp/client/edit")

        """Test edition"""
        # click on 2nd client
        edit_person_click_on_person(self.driver, 1)
        edit_person_click_on_edit(self.driver)
        
        # Alter data, add company's tax number
        path = self.driver.find_element(By.ID, "person-edit-form")
        fill_field(path, "tax_number", "20361382480")
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "edit-message"),
                "The tax number you're trying to add belongs to the company."
            )
        )
        # Alter data again, add a correct id 
        path = self.driver.find_element(By.ID, "person-edit-form")
        fill_field(path, "tax_number", "12345678901")
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "person-list"),
                "12345678901"
            )
        )
       
    def test_client_delete(self):
        # Go to delete client page
        self.driver.get(f"{self.live_server_url}/erp/client/delete")

        # Click on 1st client and delete
        edit_person_click_on_person(self.driver, 0)
        delete_person_click_on_delete(self.driver)

        # Cancel alert
        self.driver.switch_to.alert.dismiss()

        # Click again on delete and accept
        delete_person_click_on_delete(self.driver)
        self.driver.switch_to.alert.accept()

        # Check that client disappeared
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(path[1])
        )
        # Path changed, I have to reassing it
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        self.assertNotIn("20361382480", path[0].text)
        self.assertEqual(len(path), 1)
        
    def test_supplier_edit(self):
        # Go to edit supplier page
        self.driver.get(f"{self.live_server_url}/erp/supplier/edit")

        """Test edition"""
        # click on 1st supplier
        edit_person_click_on_person(self.driver, 0)
        edit_person_click_on_edit(self.driver)

        # Alter data, add company's tax number
        path = self.driver.find_element(By.ID, "person-edit-form")
        fill_field(path, "tax_number", "20361382480")
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "edit-message"),
                "The tax number you're trying to add belongs to the company."
            )
        )
        # Alter data again, add a correct id 
        fill_field(path, "tax_number", "12345678901")
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "person-list"),
                "12345678901"
            )
        )
    
    @tag("erp_supplier_delete")
    def test_supplier_delete(self):
        # Go to delete supplier page
        self.driver.get(f"{self.live_server_url}/erp/supplier/delete")

        # Click on supplier2 and delete (note, 0= sup2, 1=sup1)
        edit_person_click_on_person(self.driver, 1)
        delete_person_click_on_delete(self.driver)

        # Cancel alert
        self.driver.switch_to.alert.dismiss()

        # Click again on delete and accept
        delete_person_click_on_delete(self.driver)
        self.driver.switch_to.alert.accept()

        # Check that supplier2 disappeared
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(path[1])
        )
        # Path changed, I have to reassign it
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        self.assertNotIn("30361382485", path[0].text)
        self.assertEqual(len(path), 1)

    @tag("erp_payment_term_d")
    def test_payment_conditions_term_default(self):
        # Clean payment cond instances and go to Payment Conditions page.
        Payment_term.objects.all().delete()
        Payment_method.objects.all().delete()
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Click on default
        pay_conditions_click_default(self.driver, 0)

        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message-section"),
                "Default for term loaded successfully."
            )
        )

    @tag("erp_payment_method_d")
    def test_payment_conditions_method_default(self):
        # Clean payment cond instances and go to Payment Conditions page.
        Payment_term.objects.all().delete()
        Payment_method.objects.all().delete()
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Click on default
        pay_conditions_click_default(self.driver, 1)

        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message-section"),
                "Default for method loaded successfully."
            )
        )

    @tag("erp_payment_term_n")
    def test_payment_conditions_term_new(self):
        # Go to Payment Conditions page.
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Click on new
        self.driver.find_elements(By.CLASS_NAME, "add-button")[0].click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "new-term"),
                "New payment term"
            )
        )
        
        # Add and submit data in form
        path = self.driver.find_element(By.ID, "new-term")
        fill_field(path, "pay_term",180)
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        
        self.driver.switch_to.alert.accept()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message-section"),
                "New term added successfully"
            )
        )


    @tag("erp_payment_method_n")
    def test_payment_conditions_method_new(self):
        # Go to Payment Conditions page.
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Click on new
        self.driver.find_elements(By.CLASS_NAME, "add-button")[1].click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "new-method"),
                "New payment method"
            )
        )
        
        # Add and submit data in form
        path = self.driver.find_element(By.ID, "new-method")
        fill_field(path, "pay_method", "Hand")
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())

        self.driver.switch_to.alert.accept()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message-section"),
                "New method added successfully"
            )
        )

    @tag("erp_payment_term_v")
    def test_payment_terms_view_list_and_delete(self):
        # Create data
        create_extra_pay_terms()
        self.assertEqual(Payment_term.objects.all().count(), 5)

        # Go to Payment Conditions page.
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Click on show methods
        self.driver.find_elements(By.CLASS_NAME, "view-button")[0].click()

        # Check title and list
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "view-title"),
                "Payment terms"
            )
        )
        path = self.driver.find_element(By.ID, "view-list")
        self.assertIn("180", path.text)

        # Delete an entry
        pay_conditions_delete_confirm_button(self.driver, path)
        self.assertEqual(Payment_term.objects.all().count(), 4)

    @tag("erp_payment_method_v")
    def test_payment_methods_view_list_and_delete(self):
        # Create data
        create_extra_pay_methods()
        self.assertEqual(Payment_method.objects.all().count(), 4)
    

        # Go to Payment Conditions page.
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Click on show methods
        self.driver.find_elements(By.CLASS_NAME, "view-button")[1].click()

        # Check title and list
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "view-title"),
                "Payment methods"
            )
        )
        path = self.driver.find_element(By.ID, "view-list")
        self.assertIn("Transfer", path.text)

        # Delete an entry
        pay_conditions_delete_confirm_button(self.driver, path)
        self.assertEqual(Payment_method.objects.all().count(), 3)


    @tag("erp_pos_n")
    def test_pos_new(self):
        # Go to POS page.
        self.driver.get(f"{self.live_server_url}/erp/points_of_sell")

        # Write new pos in form
        path = self.driver.find_element(By.ID, "new-pos-form")
        fill_field(path, "pos_number", "00003")
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        
        self.driver.switch_to.alert.accept()
        # Check if it was added
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message-section"),
                "Point of Sell added succesfully."
            )
        )

    @tag("erp_pos_v")
    def test_pos_view(self):
        # Go to POS page.
        self.driver.get(f"{self.live_server_url}/erp/points_of_sell")
        
        # click on show all POS
        self.driver.find_element(By.ID, "show-pos-button").click()
        
        # Check that list appears
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "show-pos-title"),
                "Points of Sell"
            )
        )
        path = self.driver.find_element(By.ID, "pos-list")
        self.assertIn("00001", path.text)
    
    @tag("erp_pos_d")
    def test_pos_disable(self):
        # Go to POS page.
        self.driver.get(f"{self.live_server_url}/erp/points_of_sell")

        # click on disable a pos
        self.driver.find_element(By.ID, "dropdown-disable-menu").click()
        
        self.driver.find_elements(By.CSS_SELECTOR, ".dropdown-item.pos")[0].click()
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        
        # Confirm
        self.driver.switch_to.alert.accept()
        # Check if it was disabled
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message-section"),
                "Point of Sell 00001 disabled."
            )
        )
        
        # Check new page with no pos
        path = self.driver.find_element(By.ID, "no-pos")
        self.assertIn("No Point of Sell has been created yet.", path.text)

    @tag("erp_doc_types")
    def test_doc_types_visibility(self):
        # Go to Document Types page.
        self.driver.get(f"{self.live_server_url}/erp/document_types")
        
        # Click on unhide on docs 001 and 002
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "invisible-list"), "002")
        )
        path = self.driver.find_element(By.ID, "invisible-list")
        unhide_buttons = path.find_elements(By.TAG_NAME, "button")
        # User JS click as regular click doesn't work
        self.driver.execute_script("arguments[0].click();", unhide_buttons[1])
        self.driver.execute_script("arguments[0].click();", unhide_buttons[0])
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "visible-list"),
                "001"
            )
        )
        
        # Check that docs are not in invisible list
        self.assertNotIn("002", path.text)
        self.assertNotIn("001", path.text)
        # Check that doc 001 is in visible list
        path = self.driver.find_element(By.ID, "visible-list")
        self.assertIn("001", path.text)
        
        # Move back doc 002 to invisible list
        hide_buttons = path.find_elements(By.TAG_NAME, "button")
        hide_buttons[1].click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "invisible-list"),
                "NOTAS DE DEBITO A"
            )
        )
        # Check that doc 002 is not in visible list
        self.assertNotIn("NOTAS DE DEBITO A", path.text)


@tag("erp_front_documents")
class ErpFrontDocumentsTestCase(FrontBaseTest):
    
    def setUp(self):
        """Populate db and load index page"""
        super().setUp()

        FinancialYear.objects.create(year="2024", current=True)
        
        self.pos2 = Point_of_sell.objects.create(pos_number = "00002")

        self.doc_type1 = Document_type.objects.create(
            type = "A",
            code = "001",
            type_description = "Invoice A",
            hide = False,
        )
        
        self.doc_type2 = Document_type.objects.create(
            type = "B",
            code = "002",
            type_description = "Invoice B",
            hide = False,
        )

        self.sale_invoice1 = Sale_invoice.objects.create(
            issue_date = datetime.date(2024, 1, 21), 
            type = self.doc_type1, 
            point_of_sell = self.pos1,
            number = "00000001", 
            sender = self.company,
            recipient = self.c_client1,
            payment_method = self.pay_method1,
            payment_term = self.pay_term1,
            # Set collected manually, as this attribute is modified in views.
            collected = True, 
        )
        
        self.sale_invoice1_line1 = Sale_invoice_line.objects.create(
            sale_invoice = self.sale_invoice1,
            description = "Test sale invoice",
            taxable_amount = Decimal("1000"),
            not_taxable_amount = Decimal("90.01"),
            vat_amount = Decimal("210"),
        )
        self.sale_invoice1_line2 = Sale_invoice_line.objects.create(
            sale_invoice = self.sale_invoice1,
            description = "Other products",
            taxable_amount = Decimal("999"),
            not_taxable_amount = Decimal("00.01"),
            vat_amount = Decimal("209.99"),
        )

        self.sale_receipt1 = Sale_receipt.objects.create(
            issue_date = datetime.date(2024, 2, 21),
            point_of_sell = self.pos1,
            number = "00000001",
            description = "Test sale receipt",
            related_invoice = self.sale_invoice1,
            sender = self.company,
            recipient = self.c_client1,
            total_amount = Decimal("2509.01"),
        )

        
    def create_extra_invoices(self):
        """Add extra invoices in necessary tests"""
        self.sale_invoice2 = Sale_invoice.objects.create(
            issue_date = datetime.date(2024, 1, 22),
            type = self.doc_type2,
            point_of_sell = self.pos1,
            number = "00000001",
            sender = self.company,
            recipient = self.c_client1,
            payment_method = self.pay_method2,
            payment_term = self.pay_term2,
        )

        self.sale_invoice3 = Sale_invoice.objects.create(
            issue_date = datetime.date(2024, 1, 23),
            type = self.doc_type1,
            point_of_sell = self.pos1,
            number ="00000002", 
            sender = self.company,
            recipient = self.c_client1, 
            payment_method = self.pay_method1,
            payment_term = self.pay_term1
        )
        self.sale_invoice4 = Sale_invoice.objects.create(
            issue_date = datetime.date(2024, 1, 23),
            type=self.doc_type1,
            point_of_sell = self.pos1,
            number="00000003",
            sender=self.company,
            recipient = self.c_client2,
            payment_method=self.pay_method2, 
            payment_term = self.pay_term1
        )
        self.sale_invoice5 = Sale_invoice.objects.create(
            issue_date = datetime.date(2024, 1, 24),
            type = self.doc_type2,
            point_of_sell = self.pos1,
            number = "00000002",
            sender = self.company,
            recipient = self.c_client1,
            payment_method = self.pay_method1, 
            payment_term = self.pay_term1
        )
        self.sale_invoice6 = Sale_invoice.objects.create(
            issue_date=datetime.date(2024, 1, 24),
            type=self.doc_type2,
            point_of_sell=self.pos1,
            number="00000003",
            sender=self.company,
            recipient=self.c_client2,
            payment_method=self.pay_method2, 
            payment_term=self.pay_term1
        )
        self.sale_invoice7 = Sale_invoice.objects.create(
            issue_date=datetime.date(2024, 1, 25),
            type=self.doc_type1,
            point_of_sell=self.pos2,
            number="00000001",
            sender=self.company,
            recipient=self.c_client1,
            payment_method=self.pay_method1, 
            payment_term=self.pay_term1
        )
        self.sale_invoice8 = Sale_invoice.objects.create(
            issue_date=datetime.date(2024, 1, 25),
            type=self.doc_type1,
            point_of_sell=self.pos2,
            number="00000002",
            sender=self.company,
            recipient=self.c_client1,
            payment_method=self.pay_method2,
            payment_term=self.pay_term1
        )
        self.sale_invoice9 = Sale_invoice.objects.create(
            issue_date=datetime.date(2024, 1, 26),
            type=self.doc_type2,
            point_of_sell=self.pos2,
            number="00000001",
            sender=self.company,
            recipient=self.c_client2,
            payment_method=self.pay_method1,
            payment_term=self.pay_term1
        )
        self.sale_invoice10 = Sale_invoice.objects.create(
            issue_date=datetime.date(2024, 1, 26),
            type=self.doc_type2,
            point_of_sell=self.pos2,
            number="00000002",
            sender=self.company,
            recipient=self.c_client2,
            payment_method=self.pay_method2,
            payment_term=self.pay_term1
        )
        
        self.sale_invoice2_line1 = Sale_invoice_line.objects.create(
            sale_invoice = self.sale_invoice2,
            description = "Second sale invoice",
            taxable_amount = Decimal("999.99"),
            not_taxable_amount = Decimal("0.02"),
            vat_amount = Decimal("209.09"),
        )
        self.sale_invoice3_line1 = Sale_invoice_line.objects.create(
            sale_invoice = self.sale_invoice3,
            description = "Third sale invoice",
            taxable_amount = Decimal("3"),
            not_taxable_amount = Decimal("3"),
            vat_amount = Decimal("3"),
        )
        self.sale_invoice4_line1 = Sale_invoice_line.objects.create(
            sale_invoice = self.sale_invoice4,
            description = "Forth sale invoice",
            taxable_amount = Decimal("4"),
            not_taxable_amount = Decimal("4"),
            vat_amount = Decimal("4"),
        )
        self.sale_invoice5_line1 = Sale_invoice_line.objects.create(
            sale_invoice = self.sale_invoice5,
            description = "Fifth sale invoice",
            taxable_amount = Decimal("5"),
            not_taxable_amount = Decimal("5"),
            vat_amount = Decimal("5"),
        )
        self.sale_invoice6_line1 = Sale_invoice_line.objects.create(
            sale_invoice = self.sale_invoice6,
            description = "Sixth sale invoice",
            taxable_amount = Decimal("6"),
            not_taxable_amount = Decimal("6"),
            vat_amount = Decimal("6"),
        )
        self.sale_invoice7_line1 = Sale_invoice_line.objects.create(
            sale_invoice = self.sale_invoice7,
            description = "Seventh sale invoice",
            taxable_amount = Decimal("7"),
            not_taxable_amount = Decimal("7"),
            vat_amount = Decimal("7"),
        )
        self.sale_invoice8_line1 = Sale_invoice_line.objects.create(
            sale_invoice = self.sale_invoice8,
            description = "Eighth sale invoice",
            taxable_amount = Decimal("8"),
            not_taxable_amount = Decimal("8"),
            vat_amount = Decimal("8"),
        )
        self.sale_invoice9_line1 = Sale_invoice_line.objects.create(
            sale_invoice = self.sale_invoice9,
            description = "Ninth sale invoice",
            taxable_amount = Decimal("9"),
            not_taxable_amount = Decimal("9"),
            vat_amount = Decimal("9"),
        )
        self.sale_invoice10_line1 = Sale_invoice_line.objects.create(
            sale_invoice = self.sale_invoice10,
            description = "Tenth sale invoice",
            taxable_amount = Decimal("10"),
            not_taxable_amount = Decimal("10"),
            vat_amount = Decimal("10"),
        )
        
    def create_extra_receipts(self): 
        """Create extra receipts if it's necessary """
        self.create_extra_invoices() # Function dependant
        self.sale_invoice2.collected = True # Update imvoice 2 status
        
        self.sale_receipt2 = Sale_receipt.objects.create(
            issue_date = datetime.date(2024, 2, 22),
            point_of_sell = self.pos1,
            number = "00000002",
            description = "Second receipt",
            related_invoice = self.sale_invoice2,
            sender = self.company,
            recipient = self.c_client1,
            total_amount = Decimal("600.01"),
        )
        self.sale_receipt3 = Sale_receipt.objects.create(
            issue_date = datetime.date(2024, 2, 23),
            point_of_sell = self.pos1,
            number = "00000003",
            description = "Third receipt",
            related_invoice = self.sale_invoice2,
            sender = self.company,
            recipient = self.c_client1,
            total_amount = Decimal("609"),
        )
        self.sale_receipt4 = Sale_receipt.objects.create(
            issue_date = datetime.date(2024, 3, 24),
            point_of_sell = self.pos2,
            number = "00000001",
            description = "Fourth receipt",
            related_invoice = self.sale_invoice5,
            sender = self.company,
            recipient = self.c_client1,
            total_amount = Decimal("5"),
        )
        self.sale_receipt5 = Sale_receipt.objects.create(
            issue_date = datetime.date(2024, 3, 24),
            point_of_sell = self.pos2,
            number = "00000002",
            description = "Fifth receipt",
            related_invoice = self.sale_invoice5,
            sender = self.company,
            recipient = self.c_client1,
            total_amount = Decimal("5"),
        )
        self.sale_receipt6 = Sale_receipt.objects.create(
            issue_date = datetime.date(2024, 3, 24),
            point_of_sell = self.pos1,
            number = "00000004",
            description = "Sixth receipt",
            related_invoice = self.sale_invoice6,
            sender = self.company,
            recipient = self.c_client2,
            total_amount = Decimal("8"),
        )

    def test_navigation(self):
        # Test different sections of com documents
        self.driver.get(f"{self.live_server_url}")
        go_to_section(self.driver, "sales", 0)    
        self.assertEqual(self.driver.title, "Sales")
        go_to_section(self.driver, "sales", 1)    
        self.assertEqual(self.driver.title, "New Invoice")
        go_to_section(self.driver, "sales", 2)    
        self.assertEqual(self.driver.title, "New Massive Invoices")
        go_to_section(self.driver, "sales", 3)    
        self.assertEqual(self.driver.title, "Search Invoice")
        go_to_section(self.driver, "sales", 4)    
        self.assertEqual(self.driver.title, "Invoice List")
        go_to_section(self.driver, "receivables", 0)    
        self.assertEqual(self.driver.title, "Receivables")
        go_to_section(self.driver, "receivables", 1)    
        self.assertEqual(self.driver.title, "New Receipt")
        go_to_section(self.driver, "receivables", 2)    
        self.assertEqual(self.driver.title, "New Massive Receipts")
        go_to_section(self.driver, "receivables", 3)    
        self.assertEqual(self.driver.title, "Search Receipt")
        go_to_section(self.driver, "receivables", 4)    
        self.assertEqual(self.driver.title, "Receipt List")

    def test_sales_new_invoice_numbers(self):
        # Go to Sales new invoice page.
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/new")
        
        # Check sender field is the company
        sender_field = Select(self.driver.find_element(By.ID, "id_sender"))
        selected_option = sender_field.first_selected_option
        self.assertIn("TEST COMPANY SRL", selected_option.text)
        
        # Check number field is ""
        number_field = self.driver.find_element(By.ID, "id_number")
        self.assertEqual(number_field.get_attribute('value'), "")

        # Pick type and check number field doesn't change
        pick_option_by_index(self.driver, "id_type", 1, "001 | A")
        self.assertEqual(number_field.get_attribute('value'), "")
        
        # Pick pos and check number field changes
        pick_option_by_index(self.driver, "id_point_of_sell", 1, "00001")
        self.assertEqual(number_field.get_attribute('value'), "4")

        # Pick another pos and check number field changes again
        pick_option_by_index(self.driver, "id_point_of_sell", 2, "00002")
        self.assertEqual(number_field.get_attribute("value"), "3")

    def test_sales_new_invoice_link_type(self):
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/new")

        # Click on Go to type link
        path = self.driver.find_element(By.ID, "invoice-form")
        path.find_elements(By.TAG_NAME, "a")[0].click()
        WebDriverWait(self.driver, 20).until(
            EC.url_changes(f"{self.live_server_url}/erp/sales/invoices/new")
        )
        self.assertEqual(self.driver.title, "Document Types")

    def test_sales_new_invoice_link_pos(self):
        # Go to Sales new invoice page.
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/new")

        # Click on Go to type link
        path = self.driver.find_element(By.ID, "invoice-form")
        path.find_elements(By.TAG_NAME, "a")[1].click()
        WebDriverWait(self.driver, 20).until(
            EC.url_changes(f"{self.live_server_url}/erp/sales/invoices/new")
        )
        self.assertEqual(self.driver.title, "Points of Sell")
        
    @tag("erp_new_invoice_line")
    def test_sales_new_invoice_add_line(self):
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/new")

        # Click on New line
        path = self.driver.find_element(By.ID, "invoice-form")
        button = path.find_element(By.ID, "new-line")
        # JS click as regular one doesn't work.
        self.driver.execute_script("arguments[0].click();", button)
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(
                (By.ID, "id_s_invoice_lines-1-description")
            )
        )

        # Click again. JS click as regular one doesn't work.
        self.driver.execute_script("arguments[0].click();", button)
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(
                (By.ID, "id_s_invoice_lines-2-description")
            )
        )

    @tag("erp_front_search")
    def test_sales_new_search_invoice_one_field_part_1(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_type", 3)
        
        # Search by type
        search_fill_field(self.driver, "id_type", "a")
        path = self.driver.find_element(By.ID, "invoice-list")
        invoice_list = first_input_search(self.driver, path, "id_type", "a", 5)

        self.assertIn("A | ", invoice_list[0].text)
        
        search_clear_field(self.driver, "id_type")
        WebDriverWait(self.driver, 20).until(EC.staleness_of(invoice_list[0]))
        
        # Test Pos
        search_fill_field(self.driver, "id_pos", " 2")
        # Web driver gives fake error, I use manual wait
        invoice_list = manual_explicit_wait(self.driver, path, 4)
        
        self.assertIn("B | 00002-", invoice_list[0].text)
        
        search_clear_field(self.driver, "id_pos")
        WebDriverWait(self.driver, 20).until(EC.staleness_of(invoice_list[0]))
        
        
    @tag("erp_front_search_2")
    def test_sales_new_search_invoice_one_field_part_2(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")
        
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_pos")

        # Test Number
        search_fill_field(self.driver, "id_number", "1 ")
        WebDriverWait(self.driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.ID, "invoice-list"),"00001-00000001")
        )

        path = self.driver.find_element(By.ID, "invoice-list")
        invoice_list = path.find_elements(By.TAG_NAME, "li")
        self.assertEqual(len(invoice_list), 4)
        
        search_clear_field(self.driver, "id_number")
        WebDriverWait(self.driver, 20).until(EC.staleness_of(invoice_list[0]))

        # Test Client tax number
        search_fill_field(self.driver, "id_client_tax_number", "13 ")
        WebDriverWait(self.driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.ID, "invoice-list"), "00002-00000002")
        )
        
        invoice_list = path.find_elements(By.TAG_NAME, "li")
        last_invoice_in_list = invoice_list[-1]
        first_invoice_in_list = invoice_list[0]
        self.assertEqual(len(invoice_list), 6)
        
        search_clear_field(self.driver, "id_client_tax_number")
        # Check all invoices disappeared
        WebDriverWait(self.driver, 20).until(EC.staleness_of(last_invoice_in_list))
        WebDriverWait(self.driver, 20).until(EC.staleness_of(first_invoice_in_list))
        
        # Test Client name
        search_fill_field(self.driver, "id_client_name", "cLiEnT2 SA")
        WebDriverWait(self.driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.ID, "invoice-list"),"CLIENT2 SA")
        )

        invoice_list = path.find_elements(By.TAG_NAME, "li")
        self.assertEqual(len(invoice_list), 4)

    @tag("erp_front_search_3")
    def test_sales_new_search_invoice_one_field_part_3(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")
        
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_number")

        # Test Year
        search_fill_field(self.driver, "id_year", "20")
        WebDriverWait(self.driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.ID, "invoice-list"),"CLIENT1 SRL")
        )

        path = self.driver.find_element(By.ID, "invoice-list")
        invoice_list = path.find_elements(By.TAG_NAME, "li")
        self.assertEqual(len(invoice_list), 10)
        
        search_clear_field(self.driver, "id_year")
        WebDriverWait(self.driver, 20).until(EC.staleness_of(invoice_list[0]))
        
        # Test month
        search_fill_field(self.driver, "id_month", "13")
        invoice_list = manual_explicit_wait(self.driver, path, 0)
        
        path = self.driver.find_element(By.ID, "invoice-list")
        self.assertIn("Couldn't match any invoice.", path.text)

    @tag("erp_front_search_multiple")
    def test_sales_new_search_invoice_multiple_field(self):       
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_client_tax_number")

        # Test multiple fields
        # Type
        search_fill_field(self.driver, "id_type", "a ")
        WebDriverWait(self.driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.ID, "invoice-list"), "00002-00000002")
        )

        path = self.driver.find_element(By.ID, "invoice-list")
        invoice_list = path.find_elements(By.TAG_NAME, "li")
        self.assertEqual(len(invoice_list), 5)
        last_invoice_in_list = path.find_elements(By.TAG_NAME, "li")[-1]
        
        # POS
        search_fill_field(self.driver, "id_pos", " 2")
        WebDriverWait(self.driver, 20).until(
            EC.staleness_of(last_invoice_in_list)
        )
        last_invoice_in_list = path.find_elements(By.TAG_NAME, "li")[-1]
        
        # Number
        search_fill_field(self.driver, "id_number", "1 ")
        WebDriverWait(self.driver, 20).until(
            EC.staleness_of(last_invoice_in_list)
        )

        invoice_list = path.find_elements(By.TAG_NAME, "li")
        first_invoice_in_list = invoice_list[0]
        self.assertEqual(len(invoice_list), 1)
        
        # Clear all fields
        for field_id in ["id_type", "id_pos", "id_number"]:
            search_clear_field(self.driver, field_id)
        WebDriverWait(self.driver, 20).until(
            EC.staleness_of(first_invoice_in_list)
        )

    @tag("erp_front_search_multiple_2")
    def test_sales_new_search_invoice_multiple_field_2(self): 
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_client_name")

        # Client tax field
        search_fill_field(self.driver, "id_client_tax_number", "99999")
        WebDriverWait(self.driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.ID, "invoice-list"),"CLIENT2 SA")
        )
        
        path = self.driver.find_element(By.ID, "invoice-list")
        invoice_list = path.find_elements(By.TAG_NAME, "li")
        self.assertEqual(len(invoice_list), 4)

        # Client name
        search_fill_field(self.driver, "id_client_name", "cLiEnT1 Srl")
        WebDriverWait(self.driver, 20).until(
            EC.staleness_of(invoice_list[-1])
        )

        path = self.driver.find_element(By.ID, "invoice-list")
        self.assertIn("Couldn't match any invoice.", path.text)

    @tag("erp_front_search_edit")
    def test_sales_new_search_invoice_edit(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_year")

        # Search invoice 1
        # type
        search_fill_field(self.driver, "id_type", "a ")
        path = self.driver.find_element(By.ID, "invoice-list")
        
        invoice_list = first_input_search(self.driver, path, "id_type", "a", 5)
        self.assertIn("A | ", invoice_list[0].text)
   
        # pos
        search_fill_field(self.driver, "id_pos", "1")
        WebDriverWait(self.driver, 20).until(
            EC.staleness_of(invoice_list[-1])
        )
        
        path = self.driver.find_element(By.ID, "invoice-list")
        
        # Click on edit button
        edit_button = path.find_element(By.CLASS_NAME, "edit-button")
        ActionChains(self.driver).move_to_element(edit_button).click(edit_button).perform()
        WebDriverWait(self.driver, 20).until(
            EC.url_changes(f"{self.live_server_url}/erp/sales/invoices/search")
        )
        self.assertEqual(self.driver.title, "Edit Invoice")
        
    @tag("erp_front_search_delete")
    def test_sales_new_search_invoice_delete(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_month")

        # Search invoice A | 00001-00000003
        # Type
        search_fill_field(self.driver, "id_type", "a ")
        WebDriverWait(self.driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.ID, "invoice-list"), "A | 00001-00000001")
        )
        
        path = self.driver.find_element(By.ID, "invoice-list")
        invoice_list = path.find_elements(By.TAG_NAME, 'li')
        
        # POS
        search_fill_field(self.driver, "id_pos", "1")
        invoice_list = manual_explicit_wait(self.driver, path, 3)
        self.assertIn("A | 00001", invoice_list[0].text)
        
        # Click on delete button   
        path = self.driver.find_element(By.ID, "invoice-list")     
        delete_button = path.find_elements(By.CLASS_NAME, "delete-button")[1]
        self.driver.execute_script('arguments[0].click();', delete_button)
        # Accept emergent alert
        WebDriverWait(self.driver, 20).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        # Wait for invoice list to disappear
        WebDriverWait(self.driver, 20).until(
            EC.staleness_of(path)
        )
        self.assertEqual(Sale_invoice.objects.all().count(), 9)

    @tag("erp_front_invoice_edit")
    def test_sales_invoice_edit(self):
        # Go to invoice 2 webpage.
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/{self.sale_invoice2.pk}")
        self.assertEqual(self.driver.title, "Invoice 00001-00000001")

        # Click on edit button
        self.driver.find_element(By.ID, "edit-button").click()
        WebDriverWait(self.driver, 15).until(
            EC.url_changes(f"{self.live_server_url}/erp/sales/invoices/{self.sale_invoice2.pk}")
        )
        self.assertEqual(self.driver.title, "Edit Invoice")

        # Add line
        new_line_button = self.driver.find_element(By.ID, "new-line")
        # Regular click doesn't work, I use JS click
        self.driver.execute_script("arguments[0].click();", new_line_button)
        # There are 2 lines, so there should be a third one
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.ID, "id_s_invoice_lines-1-description")
            )
        )

        # Go back to invoice detail
        invoice_link = self.driver.find_element(By.ID, "invoice-link")
        ActionChains(self.driver).move_to_element(invoice_link).click(invoice_link).perform()
        WebDriverWait(self.driver, 10).until(
            EC.url_changes(f"{self.live_server_url}/erp/sales/invoices/{self.sale_invoice2.pk}/edit")
        )
        self.assertEqual(self.driver.title, "Invoice 00001-00000001")

    @tag("erp_front_edit_invoice_number")
    def test_sales_invoice_edit_numbers(self):
        # Go to Sales new invoice page.
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/{self.sale_invoice1.pk}/edit")
       
        # Check number field is 1
        number_field = self.driver.find_element(By.ID, "id_number")
        self.assertEqual(number_field.get_attribute('value'), "00000001")

        # Pick type and check new number field
        type_field = Select(self.driver.find_element(By.ID, "id_type"))
        type_field.select_by_index(2)
        WebDriverWait(self.driver, 10).until(
            element_has_selected_option((By.ID, "id_type"), "002 | B")
        )
        self.assertEqual(number_field.get_attribute('value'), "4")

    @tag("erp_front_invoice_delete")
    def test_sales_invoice_delete(self):
        # Go to invoice 1 webpage.
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/{self.sale_invoice7.pk}")
        self.assertEqual(self.driver.title, "Invoice 00002-00000001")

        # Click on delete button
        self.driver.find_element(By.ID, "delete-button").click()
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        
        # Wait 
        WebDriverWait(self.driver, 15).until(
            EC.url_changes(f"{self.live_server_url}/erp/sales/invoices/{self.sale_invoice7.pk}")
        )
        self.assertEqual(self.driver.title, "Sales")

    @tag("erp_front_show_list_tabs")
    def test_sales_show_list_tabs(self):
        # Go to show list page
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/list")

        # Click on year tab
        self.driver.find_element(By.ID, "year-tab").click()
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(
                (By.ID, "id_year")
            )
        )
        
        # Click on date tab
        self.driver.find_element(By.ID, "date-tab").click()
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(
                (By.ID, "id_date_from")
            )
        )


    @tag("erp_front_show_list_original_order")
    def test_sales_show_list_original_order(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/list")
        
        # Test original sort
        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        
        first_row = rows[0]
        date, type, pos, number = get_columns_data(first_row, end=4)
        self.assertEqual(date.text, "26/01/2024")
        self.assertEqual(type.text, "002 | B")
        self.assertEqual(pos.text, "00002")
        self.assertEqual(number.text, "00000001")

        third_row = rows[2]
        date, type, pos, number = get_columns_data(third_row, end=4)
        self.assertEqual(date.text, "25/01/2024")
        self.assertEqual(type.text, "001 | A")
        self.assertEqual(pos.text, "00002")
        self.assertEqual(number.text, "00000001")

        last_row = rows[-1]
        date, type, pos, number = get_columns_data(last_row, end=4)
        self.assertEqual(date.text, "21/01/2024")
        self.assertEqual(type.text, "001 | A")
        self.assertEqual(pos.text, "00001")
        self.assertEqual(number.text, "00000001")
        
    @tag("erp_front_show_list_date_reverse")
    def test_sales_show_list_date_reverse_order(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/list")

        # Test date reverse sort
        headers = self.driver.find_elements(By.TAG_NAME, "th")
        headers[0].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.01)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        date, type, pos, number = get_columns_data(first_row, end=4)
        self.assertEqual(date.text, "21/01/2024")
        self.assertEqual(type.text, "001 | A")
        self.assertEqual(pos.text, "00001")
        self.assertEqual(number.text, "00000001")

        third_row = rows[2]
        date, type, pos, number = get_columns_data(third_row, end=4)
        self.assertEqual(date.text, "23/01/2024")
        self.assertEqual(type.text, "001 | A")
        self.assertEqual(pos.text, "00001")
        self.assertEqual(number.text, "00000002")

        last_row = rows[-1]
        date, type, pos, number = get_columns_data(last_row, end=4)
        self.assertEqual(date.text, "26/01/2024")
        self.assertEqual(type.text, "002 | B")
        self.assertEqual(pos.text, "00002")
        self.assertEqual(number.text, "00000002")

    @tag("erp_front_show_list_type")
    def test_sales_show_list_type_order(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/list")

        # Test type asc sort
        headers = self.driver.find_elements(By.TAG_NAME, "th")
        headers[1].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.01)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        point_of_sell = first_row.find_elements(By.TAG_NAME, "td")[2]
        pay_term = first_row.find_elements(By.TAG_NAME, "td")[-2]
        i_type = first_row.find_elements(By.TAG_NAME, "td")[1]
        self.assertEqual(point_of_sell.text, "00002")
        self.assertEqual(pay_term.text, "0 days")    
        self.assertEqual(i_type.text, "001 | A")            

        last_row = rows[-1]
        point_of_sell = last_row.find_elements(By.TAG_NAME, "td")[2]
        pay_term = last_row.find_elements(By.TAG_NAME, "td")[-2]
        i_type = last_row.find_elements(By.TAG_NAME, "td")[1]
        self.assertEqual(point_of_sell.text, "00001")
        self.assertEqual(pay_term.text, "30 days")        
        self.assertEqual(i_type.text, "002 | B")            

        # Test client name desc sort
        headers[1].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.01)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        point_of_sell = first_row.find_elements(By.TAG_NAME, "td")[2]
        pay_term = first_row.find_elements(By.TAG_NAME, "td")[-2]
        i_type = first_row.find_elements(By.TAG_NAME, "td")[1]
        self.assertEqual(point_of_sell.text, "00002")
        self.assertEqual(pay_term.text, "0 days")   
        self.assertEqual(i_type.text, "002 | B")     

        last_row = rows[-1]
        point_of_sell = last_row.find_elements(By.TAG_NAME, "td")[2]
        pay_term = last_row.find_elements(By.TAG_NAME, "td")[-2]
        i_type = last_row.find_elements(By.TAG_NAME, "td")[1]
        self.assertEqual(point_of_sell.text, "00001")
        self.assertEqual(pay_term.text, "0 days") 
        self.assertEqual(i_type.text, "001 | A")         
    
    
    @tag("erp_front_show_list_client_name")
    def test_sales_show_list_client_name_order(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/list")

        # Test client name asc sort
        headers = self.driver.find_elements(By.TAG_NAME, "th")
        headers[5].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.01)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        client_name = first_row.find_elements(By.TAG_NAME, "td")[5]
        self.assertEqual(client_name.text, "CLIENT1 SRL")

        last_row = rows[-1]
        client_name = last_row.find_elements(By.TAG_NAME, "td")[5]
        self.assertEqual(client_name.text, "CLIENT2 SA")

        # Test client name desc sort
        headers[5].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.01)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        client_name = first_row.find_elements(By.TAG_NAME, "td")[5]
        self.assertEqual(client_name.text, "CLIENT2 SA")

        last_row = rows[-1]
        client_name = last_row.find_elements(By.TAG_NAME, "td")[5]
        self.assertEqual(client_name.text, "CLIENT1 SRL")

    @tag("erp_front_show_list_total")
    def test_sales_show_list_total_order(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/list")

        # Test total amount asc sort
        headers = self.driver.find_elements(By.TAG_NAME, "th")
        headers[-1].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.01)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        client_name = first_row.find_elements(By.TAG_NAME, "td")[5]
        total_amount = first_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(client_name.text, "CLIENT1 SRL")
        self.assertEqual(total_amount.text, "$ 9.00")

        last_row = rows[-1]
        client_name = last_row.find_elements(By.TAG_NAME, "td")[5]
        total_amount = last_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(client_name.text, "CLIENT1 SRL")
        self.assertEqual(total_amount.text, "$ 2509.01")

        # Test client name desc sort
        headers[-1].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.01)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        number = first_row.find_elements(By.TAG_NAME, "td")[3]
        total_amount = first_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(number.text, "00000001")
        self.assertEqual(total_amount.text, "$ 2509.01")

        last_row = rows[-1]
        number = last_row.find_elements(By.TAG_NAME, "td")[3]
        total_amount = last_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(number.text, "00000002")
        self.assertEqual(total_amount.text, "$ 9.00")

    def test_receivables_new_receipt_numbers(self):
        # Go to Receivables new receipt page.
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/new")

        # Check sender field is the company
        sender_field = Select(self.driver.find_element(By.ID, "id_sender"))
        selected_option = sender_field.first_selected_option
        self.assertIn("TEST COMPANY SRL", selected_option.text)
        
        # Check number field is ""
        number_field = self.driver.find_element(By.ID, "id_number")
        self.assertEqual(number_field.get_attribute('value'), "")
        
        # Pick pos and check number field changes
        pick_option_by_index(self.driver, "id_point_of_sell", 1, "00001")
        self.assertEqual(number_field.get_attribute('value'), "2")

        # Pick another pos and check number field changes again
        pick_option_by_index(self.driver, "id_point_of_sell", 2, "00002")      
        self.assertEqual(number_field.get_attribute("value"), "1")

    @tag("erp_receipt_recipient")
    def test_receivables_new_receipt_recipient(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/new")

        # Check recipient field is empty
        recipient_field = self.driver.find_element(By.ID, "id_recipient")
        self.assertEqual(recipient_field.get_attribute('value'), "")
                
        # Pick related invoice and check recipient field changes
        rel_invoice_field = Select(self.driver.find_element(By.ID, "id_related_invoice"))
        rel_invoice_field.select_by_index(1)
        WebDriverWait(self.driver, 10).until(
            # Rel invoices are ordered from newest to oldest
            element_has_selected_option((By.ID, "id_related_invoice"),
                "2024-01-26 | B 00002-00000001")
        )
        self.assertEqual(recipient_field.get_attribute('value'), str(self.c_client2.pk))

        # Pick another rel invoice and check recipient field changes again
        rel_invoice_field.select_by_index(3)
        WebDriverWait(self.driver, 10).until(
            element_has_selected_option((By.ID, "id_related_invoice"),
                "2024-01-25 | A 00002-00000001")
        )        
        self.assertEqual(recipient_field.get_attribute("value"), str(self.c_client1.pk))

    def test_receivables_new_receipt_link_pos(self):
        # Go to Receivables new receipt page.
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/new")

        # Click on Go to type link
        path = self.driver.find_element(By.ID, "receipt-form")
        path.find_element(By.TAG_NAME, "a").click()
        WebDriverWait(self.driver, 10).until(
            EC.url_changes(f"{self.live_server_url}/erp/sales/invoices/new")
        )
        self.assertEqual(self.driver.title, "Points of Sell")
    
    @tag("erp_front_receipt_search")
    def test_receivables_new_search_receipt_one_field_part_1(self):
        self.create_extra_receipts()
        
        # Go to search page.
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")
      
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_related_invoice", 3)

        # Search related invoice.
        search_fill_field(self.driver, "id_related_invoice", "3")
        path = self.driver.find_element(By.ID, "receipt-list")
        
        receipt_list = first_input_search(self.driver, path, "id_related_invoice",
            "3", 1)
        self.assertIn("00001-00000004", receipt_list[0].text)

        search_clear_field(self.driver, "id_related_invoice")
        WebDriverWait(self.driver, 20).until(EC.staleness_of(receipt_list[0]))
        
        # Search Pos
        search_fill_field(self.driver, "id_pos", " 2")
        receipt_list = path.find_elements(By.TAG_NAME, "li")
        # Sometime it loads the space but not the 2, so I wait more.
        receipt_list = manual_explicit_wait(self.driver, path, 2)

        self.assertIn("00002", receipt_list[0].text)
        
        search_clear_field(self.driver, "id_pos")
        WebDriverWait(self.driver, 20).until(EC.staleness_of(receipt_list[0]))
        
      
    @tag("erp_front_receipt_search_2")
    def test_receivables_new_search_receipt_one_field_part_2(self):
        self.create_extra_receipts()
        # Go to Sales search receipt page.
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")
        
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_pos")

        # Test Number
        search_fill_field(self.driver, "id_number", "1 ")
        
        path = self.driver.find_element(By.ID, "receipt-list")
        receipt_list = first_input_search(self.driver, path, "id_number", "1", 2)
     
        self.assertIn("00002-00000001", receipt_list[0].text)

        search_clear_field(self.driver, "id_number")
        WebDriverWait(self.driver, 20).until(EC.staleness_of(receipt_list[0]))

        # Test Client tax number
        search_fill_field(self.driver, "id_client_tax_number", "13 ")
        WebDriverWait(self.driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.ID, "receipt-list"), "00002-00000002")
        )

        receipt_list = path.find_elements(By.TAG_NAME, "li")
        last_receipt_in_list = receipt_list[-1]
        first_receipt_in_list = receipt_list[0]
        self.assertEqual(len(receipt_list), 5)
        
        search_clear_field(self.driver, "id_client_tax_number")
        # Check if all invoices disappeared
        WebDriverWait(self.driver, 20).until(EC.staleness_of(last_receipt_in_list))
        WebDriverWait(self.driver, 20).until(EC.staleness_of(first_receipt_in_list))
        
        # Test Client name
        search_fill_field(self.driver, "id_client_name", "cLiEnT2 SA")
        WebDriverWait(self.driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.ID, "receipt-list"),"CLIENT2 SA")
        )

        receipt_list = path.find_elements(By.TAG_NAME, "li")
        self.assertEqual(len(receipt_list), 1)

   

    @tag("erp_front_receipt_search_3")
    def test_receivables_new_search_receipt_one_field_part_3(self):
        self.create_extra_receipts()
        # Go to Sales search receipt page.
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")
    
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_number")
        
        # Search Year
        search_fill_field(self.driver, "id_year", "20")
        
        path = self.driver.find_element(By.ID, "receipt-list")
        receipt_list = first_input_search(self.driver, path, "id_year", "20", 6)
      
        self.assertIn("2024", receipt_list[0].text)
        
        search_clear_field(self.driver, "id_year")
        WebDriverWait(self.driver, 20).until(EC.staleness_of(receipt_list[0]))
        
        # Search month
        search_fill_field(self.driver, "id_month", "13")
        receipt_list = manual_explicit_wait(self.driver, path, 0)

        path = self.driver.find_element(By.ID, "receipt-list")
        self.assertIn("Couldn't match any receipt.", path.text)

    @tag("erp_front_receipt_search_multiple")
    def test_receivables_new_search_receipt_multiple_field(self): 
        self.create_extra_receipts()
        # Go to Sales search receipt page.
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")
        
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_client_tax_number")

        # Search multiple fields
        # Related Invoice
        search_fill_field(self.driver, "id_related_invoice", "1 ")
        path = self.driver.find_element(By.ID, "receipt-list")
        receipt_list = first_input_search(self.driver, path, "id_related_invoice",
            "1", 6)

        self.assertIn("00001", receipt_list[0].text)
        
        # POS
        search_fill_field(self.driver, "id_pos", " 1")
        # WebDriver doesn't work, I use manual explicit wait.
        receipt_list = manual_explicit_wait(self.driver, path, 4)
        
        # Number
        search_fill_field(self.driver, "id_number", "2 ")
        # Let list update again
        WebDriverWait(self.driver, 20).until(
            EC.staleness_of(receipt_list[-1])
        )
        
        receipt_list = path.find_elements(By.TAG_NAME, "li")
        self.assertEqual(len(receipt_list), 1)
        
        # Clear all fields
        for field_id in ["id_related_invoice", "id_pos", "id_number"]:
            search_clear_field(self.driver, field_id)
        WebDriverWait(self.driver, 20).until(
            EC.staleness_of(receipt_list[0])
        )

    

    @tag("erp_front_receipt_search_multiple_2")
    def test_receivables_new_search_receipt_multiple_field_2(self): 
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")
        
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_client_name")

        # Client tax field
        search_fill_field(self.driver, "id_client_tax_number", "99999")
        
        path = self.driver.find_element(By.ID, "receipt-list")
        receipt_list = first_input_search(self.driver, path, 
            "id_client_tax_number", "99999", 1)

        self.assertIn("CLIENT2 SA", receipt_list[0].text)
        
        # Client name
        search_fill_field(self.driver, "id_client_name", "cLiEnT1 SA")
        receipt_list = manual_explicit_wait(self.driver, path, 0)
        
        path = self.driver.find_element(By.ID, "receipt-list")
        self.assertIn("Couldn't match any receipt.", path.text)

    @tag("erp_front_receipt_search_edit")
    def test_receivables_new_search_receipt_edit(self):
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_year")

        # Search receipt 1
        # search related invoice
        search_fill_field(self.driver, "id_related_invoice", "3 ")
        
        path = self.driver.find_element(By.ID, "receipt-list")
        receipt_list = first_input_search(self.driver, path, "id_related_invoice",
            "3", 1)
        
        self.assertIn("00001-00000004", receipt_list[0].text)        

        # Click on edit button
        edit_button = path.find_element(By.CLASS_NAME, "edit-button")
        self.driver.execute_script("arguments[0].click()", edit_button)
        WebDriverWait(self.driver, 20).until(
            EC.url_changes(f"{self.live_server_url}/erp/receivables/receipts/search")
        )
        self.assertEqual(self.driver.title, "Edit Receipt") 

    @tag("erp_front_receipt_search_delete")
    def test_receivables_new_search_receipt_delete(self):
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_month")

        # Search receipt 00001-00000002
        # Related invoice
        search_fill_field(self.driver, "id_related_invoice", "00001-00000001")
        
        path = self.driver.find_element(By.ID, "receipt-list")
        receipt_list = first_input_search(self.driver, path, "id_related_invoice",
            "00001-00000001", 3)
        
        self.assertIn("00001-00000001", receipt_list[0].text)
        
        # number
        search_fill_field(self.driver, "id_number", "2")
        # WebDriver doesn't work, I use manual explicit wait.
        receipt_list = manual_explicit_wait(self.driver, path, 1)
  
        # Click on delete button   
        delete_button = path.find_element(By.CLASS_NAME, "delete-button")
        self.driver.execute_script('arguments[0].click();', delete_button)
        # Accept emergent alert
        WebDriverWait(self.driver, 20).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        # Wait for receipt list to disappear
        WebDriverWait(self.driver, 20).until(
            EC.staleness_of(path)
        )
        self.assertEqual(Sale_receipt.objects.all().count(), 5)
        self.sale_invoice2.refresh_from_db()
        time.sleep(0.5)
        self.assertEqual(self.sale_invoice2.collected, False)

    @tag("erp_front_receipt_edit")
    def test_receivable_receipt_edit(self):
        # Go to receipt 1 webpage.
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/{self.sale_receipt1.pk}")
        WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.ID, "edit-button"))
        )
        self.assertEqual(self.driver.title, "Receipt 00001-00000001")

        # Click on edit button
        self.driver.find_element(By.ID, "edit-button").click()
        WebDriverWait(self.driver, 15).until(
            EC.url_changes(f"{self.live_server_url}/erp/receivables/receipts/{self.sale_receipt1.pk}")
        )
        self.assertEqual(self.driver.title, "Edit Receipt")

        # Go back to receipt detail
        receipt_link = self.driver.find_element(By.ID, "receipt-link")
        ActionChains(self.driver).move_to_element(receipt_link).click(receipt_link).perform()
        # I don't use url changes as sometimes new page's DOM isn't loaded
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "delete-button"))
        )
        self.assertEqual(self.driver.title, "Receipt 00001-00000001")

    @tag("erp_front_edit_receipt_number")
    def test_receivables_receipt_edit_numbers(self):
        # Go to Sales new receipt page.
        self.driver.get(
            f"{self.live_server_url}/erp/receivables/receipts/{self.sale_receipt1.pk}/edit"
        )
       
        # Check number field is 1
        number_field = self.driver.find_element(By.ID, "id_number")
        self.assertEqual(number_field.get_attribute('value'), "00000001")

        # Pick pos and check new number field
        pos_field = Select(self.driver.find_element(By.ID, "id_point_of_sell"))
        pos_field.select_by_index(2)
        WebDriverWait(self.driver, 10).until(
            element_has_selected_option((By.ID, "id_point_of_sell"), "00002")
        )
        self.assertEqual(number_field.get_attribute('value'), "1")

    @tag("erp_front_receipt_delete")
    def test_sales_receipt_delete(self):
        # Go to receipt 1 webpage.
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/{self.sale_receipt1.pk}")
        self.assertEqual(self.driver.title, "Receipt 00001-00000001")
        
        # Check initial invoice collected status is true for later test
        self.assertEqual(self.sale_invoice1.collected, True)

        # Click on delete button
        self.driver.find_element(By.ID, "delete-button").click()
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        
        # Wait 
        WebDriverWait(self.driver, 15).until(
            EC.url_changes(f"{self.live_server_url}/erp/receivables/receipts/{self.sale_receipt1.pk}")
        )
        self.assertEqual(self.driver.title, "Receivables")
        
        # Check DB update
        self.assertEqual(Sale_receipt.objects.all().count(), 0)
        self.sale_invoice1.refresh_from_db()
        self.assertEqual(self.sale_invoice1.collected, False) 
        
    @tag("erp_front_receipt_show_list_tabs")
    def test_receivables_show_list_tabs(self):
        # Go to show list page
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/list")

        # Click on year tab
        self.driver.find_element(By.ID, "year-tab").click()
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(
                (By.ID, "id_year")
            )
        )
        
        # Click on date tab
        self.driver.find_element(By.ID, "date-tab").click()
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(
                (By.ID, "id_date_from")
            )
        )
    

    @tag("erp_front_receipt_show_list_original_order")
    def test_receivables_show_list_original_order(self):
        # Go to show list page
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/list")
        
        # Test original sort
        rows = self.driver.find_elements(By.CLASS_NAME, "receipt")
        
        first_row = rows[0]
        date, pos, number = get_columns_data(first_row, end=3)
        self.assertEqual(date.text, "24/03/2024")
        self.assertEqual(pos.text, "00001")
        self.assertEqual(number.text, "00000004")

        third_row = rows[2]
        date, pos, number = get_columns_data(third_row, end=3)
        self.assertEqual(date.text, "24/03/2024")
        self.assertEqual(pos.text, "00002")
        self.assertEqual(number.text, "00000002")

        last_row = rows[-1]
        date, pos, number = get_columns_data(last_row, end=3)
        self.assertEqual(date.text, "21/02/2024")
        self.assertEqual(pos.text, "00001")
        self.assertEqual(number.text, "00000001")
    
    @tag("erp_front_receipt_show_list_date_reverse")
    def test_receivables_show_list_date_reverse_order(self):
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/list")

        # Test date reverse sort
        headers = self.driver.find_elements(By.TAG_NAME, "th")
        headers[0].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.01)

        rows = self.driver.find_elements(By.CLASS_NAME, "receipt")
        first_row = rows[0]
        date, pos, number = get_columns_data(first_row, end=3)
        self.assertEqual(date.text, "21/02/2024")
        self.assertEqual(pos.text, "00001")
        self.assertEqual(number.text, "00000001")

        third_row = rows[2]
        date, pos, number = get_columns_data(third_row, end=3)
        self.assertEqual(date.text, "23/02/2024")
        self.assertEqual(pos.text, "00001")
        self.assertEqual(number.text, "00000003")

        last_row = rows[-1]
        date, pos, number = get_columns_data(last_row, end=3)
        self.assertEqual(date.text, "24/03/2024")
        self.assertEqual(pos.text, "00002")
        self.assertEqual(number.text, "00000002")
   
    @tag("erp_front_receipt_show_list_related_invoice")
    def test_receivables_show_list_related_invoice_order(self):
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/list")

        # Test related invoice asc sort
        headers = self.driver.find_elements(By.TAG_NAME, "th")
        headers[5].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.01)

        rows = self.driver.find_elements(By.CLASS_NAME, "receipt")
        first_row = rows[0]
        point_of_sell = first_row.find_elements(By.TAG_NAME, "td")[1]
        related_invoice = first_row.find_elements(By.TAG_NAME, "td")[5]
        self.assertEqual(point_of_sell.text, "00001")
        self.assertEqual(related_invoice.text, "A 00001-00000001")        

        last_row = rows[-1]
        point_of_sell = last_row.find_elements(By.TAG_NAME, "td")[1]
        related_invoice = last_row.find_elements(By.TAG_NAME, "td")[5]
        self.assertEqual(point_of_sell.text, "00001")
        self.assertEqual(related_invoice.text, "B 00001-00000003")        

        # Test related invoice desc sort
        headers[5].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.01)

        rows = self.driver.find_elements(By.CLASS_NAME, "receipt")
        first_row = rows[0]
        point_of_sell = first_row.find_elements(By.TAG_NAME, "td")[1]
        related_invoice = first_row.find_elements(By.TAG_NAME, "td")[5]
        self.assertEqual(point_of_sell.text, "00001")
        self.assertEqual(related_invoice.text, "B 00001-00000003")        

        last_row = rows[-1]
        point_of_sell = last_row.find_elements(By.TAG_NAME, "td")[1]
        related_invoice = last_row.find_elements(By.TAG_NAME, "td")[5]
        self.assertEqual(point_of_sell.text, "00001")
        self.assertEqual(related_invoice.text, "A 00001-00000001")        

    
    @tag("erp_front_receipt_show_list_total")
    def test_receivables_show_list_total_order(self):
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/list")

        # Test total amount asc sort
        headers = self.driver.find_elements(By.TAG_NAME, "th")
        headers[-1].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.01)

        rows = self.driver.find_elements(By.CLASS_NAME, "receipt")
        first_row = rows[0]
        client_name = first_row.find_elements(By.TAG_NAME, "td")[4]
        total_amount = first_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(client_name.text, "CLIENT1 SRL")
        self.assertEqual(total_amount.text, "$ 5.00")

        last_row = rows[-1]
        client_name = last_row.find_elements(By.TAG_NAME, "td")[4]
        total_amount = last_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(client_name.text, "CLIENT1 SRL")
        self.assertEqual(total_amount.text, "$ 2509.01")

        # Test client name desc sort
        headers[-1].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.01)

        rows = self.driver.find_elements(By.CLASS_NAME, "receipt")
        first_row = rows[0]
        number = first_row.find_elements(By.TAG_NAME, "td")[2]
        total_amount = first_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(number.text, "00000001")
        self.assertEqual(total_amount.text, "$ 2509.01")

        last_row = rows[-1]
        number = last_row.find_elements(By.TAG_NAME, "td")[2]
        total_amount = last_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(number.text, "00000002")
        self.assertEqual(total_amount.text, "$ 5.00")
  