"""Selenium tests for erp app"""
import datetime
from decimal import Decimal
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from company.models import Company
from .models import (Company_client, Supplier, Payment_method, Payment_term,
    Point_of_sell, Document_type, Sale_invoice)


"""Selenium custom functions"""
def element_has_selected_option(locator, option_text):
    def _predicate(driver):
        # Search and add class to select element
        select_element = Select(driver.find_element(*locator))
        # Pick selected option
        selected_option = select_element.first_selected_option
        # Return True if text is in selected option
        return selected_option.text == option_text
        # Return function to be used by webdriver
    return _predicate


"""Tests"""
@tag("erp_front_simple_models")
class ErpFrontTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        """Start Selenium webdriver"""
        super().setUpClass()
        cls.driver = WebDriver()
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        """Close selenium webdriver"""
        cls.driver.quit()
        super().tearDownClass()

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
        
        self.client1 = Company_client.objects.create(
            tax_number = "20361382481",
            name = "Client1 SRL",
            address = "Client street, Client city, Chile",
            email = "client1@email.com",
            phone = "1234567890",
        )

        self.client2 = Company_client.objects.create(
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

        self.pos1 = Point_of_sell.objects.create(
            pos_number = "00001",
        )

        self.driver.get(f"{self.live_server_url}")

    def test_client_edit(self):
        # Go to edit client page
        self.assertEqual(self.driver.title, "Index")
        self.driver.find_element(By.ID, "client-menu-link").click()
        path = self.driver.find_element(By.ID, "client-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[2].click()
        self.assertEqual(self.driver.title, "Edit Client")

        """Test edition"""
        # click on 2nd client
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        path[1].click()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "person-details"))
        )
        # Click on edit
        path = self.driver.find_element(By.ID, "person-details")
        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "person-edit-form"))
        )
        # Alter data, add company's tax number
        path = self.driver.find_element(By.ID, "person-edit-form")
        field_tax_number = path.find_element(By.NAME, "tax_number")
        self.assertEqual(field_tax_number.get_attribute("value"), "99999999999")
        field_tax_number.clear()
        field_tax_number.send_keys("20361382480")
        self.assertEqual(field_tax_number.get_attribute("value"), "20361382480")
        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "edit-message"),
                "The tax number you're trying to add belongs to the company."
            )
        )
        # Alter data, add a correct id 
        self.assertEqual(field_tax_number.get_attribute("value"), "20361382480")
        field_tax_number.clear()
        field_tax_number.send_keys("12345678901")
        self.assertEqual(field_tax_number.get_attribute("value"), "12345678901")
        path.find_element(By.TAG_NAME, "button").click()
        # Check new data
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "person-list"),
                "12345678901"
            )
        )
       
    def test_client_delete(self):
        # Go to delete client page
        self.driver.find_element(By.ID, "client-menu-link").click()
        path = self.driver.find_element(By.ID, "client-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[3].click()
        self.assertEqual(self.driver.title, "Delete Client")

        # Click on 1st client
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        self.assertIn("20361382481", path[0].text)
        path[0].click()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "person-details"))
        )
        # Click on delete
        path = self.driver.find_element(By.ID, "person-details")

        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())

        # Cancel alert
        alert_element = self.driver.switch_to.alert
        alert_element.dismiss()

        # Click again on delete
        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        
        # Accept alert and check that client1 disappeared
        alert_element = self.driver.switch_to.alert
        alert_element.accept()
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(path[1])
        )
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        self.assertNotIn("20361382480", path[0].text)
        
    def test_supplier_edit(self):
        # Go to edit supplier page
        self.driver.find_element(By.ID, "supplier-menu-link").click()
        path = self.driver.find_element(By.ID, "supplier-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[2].click()
        self.assertEqual(self.driver.title, "Edit Supplier")

        """Test edition"""
        # click on 1st supplier
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        path[0].click()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "person-details"))
        )
        # Click on edit
        path = self.driver.find_element(By.ID, "person-details")
        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "person-edit-form"))
        )
        # Alter data, add company's tax number
        path = self.driver.find_element(By.ID, "person-edit-form")
        field_tax_number = path.find_element(By.NAME, "tax_number")
        self.assertEqual(field_tax_number.get_attribute("value"), "20361382482")
        field_tax_number.clear()
        field_tax_number.send_keys("20361382480")
        self.assertEqual(field_tax_number.get_attribute("value"), "20361382480")
        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "edit-message"),
                "The tax number you're trying to add belongs to the company."
            )
        )
        # Alter data, add a correct id 
        self.assertEqual(field_tax_number.get_attribute("value"), "20361382480")
        field_tax_number.clear()
        field_tax_number.send_keys("12345678901")
        self.assertEqual(field_tax_number.get_attribute("value"), "12345678901")
        path.find_element(By.TAG_NAME, "button").click()
        # Check new data
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "person-list"),
                "12345678901"
            )
        )
       
    def test_supplier_delete(self):
        # Go to delete supplier page
        self.driver.find_element(By.ID, "supplier-menu-link").click()
        path = self.driver.find_element(By.ID, "supplier-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[3].click()
        self.assertEqual(self.driver.title, "Delete Supplier")

        # Click on 2nd supplier
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        self.assertIn("30361382485", path[1].text)
        path[1].click()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "person-details"))
        )
        # Click on delete
        path = self.driver.find_element(By.ID, "person-details")

        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())

        # Cancel alert
        alert_element = self.driver.switch_to.alert
        alert_element.dismiss()

        # Click again on delete
        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        
        # Accept alert and check that supplier2 disappeared
        alert_element = self.driver.switch_to.alert
        alert_element.accept()
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(path[1])
        )
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        self.assertNotIn("30361382485", path[0].text)
        self.assertEqual(len(path), 1)

    @tag("erp_payment_term_d")
    def test_payment_conditions_term_default(self):
        # Go to Payment Conditions page.
        self.driver.find_element(By.ID, "company-menu-link").click()
        path = self.driver.find_element(By.ID, "company-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[3].click()
        self.assertEqual(self.driver.title, "Payment Conditions")

        # Click on default
        path = self.driver.find_elements(By.CLASS_NAME, "default-button")
        path[0].click()
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message-section"),
                "Default for term loaded successfully."
            )
        )

    @tag("erp_payment_method_d")
    def test_payment_conditions_method_default(self):
        # Go to Payment Conditions page.
        self.driver.find_element(By.ID, "company-menu-link").click()
        path = self.driver.find_element(By.ID, "company-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[3].click()
        self.assertEqual(self.driver.title, "Payment Conditions")

        # Click on default
        path = self.driver.find_elements(By.CLASS_NAME, "default-button")
        path[1].click()
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message-section"),
                "Default for method loaded successfully."
            )
        )

    @tag("erp_payment_term_n")
    def test_payment_conditions_term_new(self):
        # Go to Payment Conditions page.
        self.driver.find_element(By.ID, "company-menu-link").click()
        path = self.driver.find_element(By.ID, "company-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[3].click()

        # Click on new
        path = self.driver.find_elements(By.CLASS_NAME, "add-button")
        path[0].click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "new-term"),
                "New payment term"
            )
        )
        
        # Add and submit data in form
        path = self.driver.find_element(By.ID, "new-term")
        field_pay_term = path.find_element(By.NAME, "pay_term")
        field_pay_term.send_keys("180")
        self.assertEqual(field_pay_term.get_attribute("value"), "180")
        path.find_element(By.TAG_NAME, "button").click()
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
        self.driver.find_element(By.ID, "company-menu-link").click()
        path = self.driver.find_element(By.ID, "company-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[3].click()

        # Click on new
        path = self.driver.find_elements(By.CLASS_NAME, "add-button")
        path[1].click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "new-method"),
                "New payment method"
            )
        )
        # Add and submit data in form
        path = self.driver.find_element(By.ID, "new-method")
        field_pay_term = path.find_element(By.NAME, "pay_method")
        field_pay_term.send_keys("Hand")
        self.assertEqual(field_pay_term.get_attribute("value"), "Hand")
        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message-section"),
                "New method added successfully"
            )
        )

    @tag("erp_payment_term_v")
    def test_payment_terms_view_and_delete_list(self):
        # Create data
        Payment_term.objects.bulk_create([
            Payment_term(pay_term="90"),
            Payment_term(pay_term="180"),
            Payment_term(pay_term="360"),
        ])
        self.assertTrue(Payment_term.objects.all().count(), 4)
        self.driver.implicitly_wait(5)

        # Go to Payment Conditions page.
        self.driver.find_element(By.ID, "company-menu-link").click()
        path = self.driver.find_element(By.ID, "company-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[3].click()

        # Click on show methods
        path = self.driver.find_elements(By.CLASS_NAME, "view-button")
        path[0].click()

        # Check title and list
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "view-title"),
                "Payment terms"
            )
        )
        path = self.driver.find_element(By.ID, "view-list")
        self.assertIn("360", path.text)

        # Delete an entry
        delete_button = path.find_elements(By.CLASS_NAME, "delete-item")[-1]
        delete_button.click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "view-list"),
                "Confirm"
            )
        )
        # Click in confirm
        delete_button.click()
        WebDriverWait(self.driver, 10).until(EC.staleness_of(delete_button))


    @tag("erp_payment_method_v")
    def test_payment_methods_view_list(self):
        # Create data
        Payment_method.objects.bulk_create([
            Payment_method(pay_method="Transfer"),
            Payment_method(pay_method="Check"),
        ])
        self.assertTrue(Payment_method.objects.all().count(), 3)
        self.driver.implicitly_wait(5)

        # Go to Payment Conditions page.
        self.driver.find_element(By.ID, "company-menu-link").click()
        path = self.driver.find_element(By.ID, "company-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[3].click()

        # Click on show methods
        path = self.driver.find_elements(By.CLASS_NAME, "view-button")
        path[0].click()

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
        delete_button = path.find_elements(By.CLASS_NAME, "delete-item")[1]
        delete_button.click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "view-list"),
                "Confirm"
            )
        )
        # Click in confirm
        delete_button.click()
        WebDriverWait(self.driver, 10).until(EC.staleness_of(delete_button))

    @tag("erp_pos_n")
    def test_pos_new(self):
        # Go to POS page.
        self.driver.find_element(By.ID, "company-menu-link").click()
        path = self.driver.find_element(By.ID, "company-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[2].click()
        self.assertEqual(self.driver.title, "Points of Sell")
        # Write new pos in form
        path = self.driver.find_element(By.ID, "new-pos-form")
        pos_number_field = path.find_element(By.NAME, "pos_number")
        pos_number_field.send_keys("00003")
        self.assertEqual(pos_number_field.get_attribute("value"), "00003")
        # Click on add, and confirm 
        self.driver.find_element(By.ID, "new-pos").click()
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        # Check it was added
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message-section"),
                "Point of Sell added succesfully."
            )
        )

    @tag("erp_pos_v")
    def test_pos_view(self):
        # Go to POS page.
        self.driver.find_element(By.ID, "company-menu-link").click()
        path = self.driver.find_element(By.ID, "company-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[2].click()
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
        self.driver.find_element(By.ID, "company-menu-link").click()
        path = self.driver.find_element(By.ID, "company-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[2].click()
        # click on disable a pos
        path = self.driver.find_element(By.ID, "dropdown-disable-menu")
        path.click()
        self.driver.find_elements(By.CSS_SELECTOR, ".dropdown-item.pos")[0].click()
        # Confirm
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        # Check it was disabled
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
        self.driver.find_element(By.ID, "company-menu-link").click()
        path = self.driver.find_element(By.ID, "company-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[4].click()
        self.assertEqual(self.driver.title, "Document Types")
        
        # Click on unhide on docs 001 and 002
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "invisible-list"), "002")
        )
        path = self.driver.find_element(By.ID, "invisible-list")
        unhide_buttons = path.find_elements(By.TAG_NAME, "button")
        unhide_buttons[1].click()
        unhide_buttons[0].click()
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
class ErpFrontDocumentsTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        """Start Selenium webdriver"""
        super().setUpClass()
        cls.driver = WebDriver()
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        """Close selenium webdriver"""
        cls.driver.quit()
        super().tearDownClass()

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
        
        self.client1 = Company_client.objects.create(
            tax_number = "20361382481",
            name = "Client1 SRL",
            address = "Client street, Client city, Chile",
            email = "client1@email.com",
            phone = "1234567890",
        )

        self.client2 = Company_client.objects.create(
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

        self.pos1 = Point_of_sell.objects.create(
            pos_number = "00001",
        )

        self.pos2 = Point_of_sell.objects.create(
            pos_number = "00002",
        )

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

        self.pay_method = Payment_method.objects.create(
            pay_method = "Cash",
        )
        self.pay_method2 = Payment_method.objects.create(
            pay_method = "Transfer",
        )

        self.pay_term = Payment_term.objects.create(
            pay_term = "0",
        )
        self.pay_term2 = Payment_term.objects.create(
            pay_term = "30",
        )

        self.sale_invoice1 = Sale_invoice.objects.create(
            type = self.doc_type1,
            point_of_sell = self.pos1,
            number = "00000001",
            description = "Test sale invoice",
            sender = self.company,
            recipient = self.client1,
            payment_method = self.pay_method,
            payment_term = self.pay_term,
            taxable_amount = Decimal("1000"),
            not_taxable_amount = Decimal("90.01"),
            VAT_amount = Decimal("210"),
        )

        self.sale_invoice2 = Sale_invoice.objects.create(
            type = self.doc_type2,
            point_of_sell = self.pos1,
            number = "00000001",
            description = "Second sale invoice",
            sender = self.company,
            recipient = self.client1,
            payment_method = self.pay_method2,
            payment_term = self.pay_term2,
            taxable_amount = Decimal("999.99"),
            not_taxable_amount = Decimal("0.02"),
            VAT_amount = Decimal("209.09"),
        )

        self.driver.get(f"{self.live_server_url}")

    def test_sales_overview(self):
        # Go to Sales overview page.
        self.driver.find_element(By.ID, "sales-menu-link").click()
        path = self.driver.find_element(By.ID, "sales-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[0].click()
        self.assertEqual(self.driver.title, "Sales")

    def test_sales_new_invoice_numbers(self):
        # Go to Sales new invoice page.
        self.driver.find_element(By.ID, "sales-menu-link").click()
        path = self.driver.find_element(By.ID, "sales-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[1].click()
        self.assertEqual(self.driver.title, "New Sale")

        # Check sender field is the company
        sender_field = Select(self.driver.find_element(By.ID, "id_sender"))
        selected_option = sender_field.first_selected_option
        self.assertIn("Test Company SRL", selected_option.text)
        
        # Check number field is ""
        number_field = self.driver.find_element(By.ID, "id_number")
        self.assertEqual(number_field.get_attribute('value'), "")

        # Pick type and check number field doesn't change
        type_field = Select(self.driver.find_element(By.ID, "id_type"))
        selected_option = type_field.select_by_index(1)
        WebDriverWait(self.driver, 10).until(
            element_has_selected_option((By.ID, "id_type"), "001 | A")
        )
        self.assertEqual(number_field.get_attribute('value'), "")
        
        # Pick pos and check number field changes
        pos_field = Select(self.driver.find_element(By.ID, "id_point_of_sell"))
        selected_option = pos_field.select_by_index(1)
        WebDriverWait(self.driver, 10).until(
            element_has_selected_option((By.ID, "id_point_of_sell"), "00001")
        )
        self.assertEqual(number_field.get_attribute('value'), "2")

        # Pick another pos and check number field changes again
        pos_field.select_by_index(2)
        WebDriverWait(self.driver, 10).until(
            element_has_selected_option((By.ID, "id_point_of_sell"), "00002")
        )        
        self.assertEqual(number_field.get_attribute("value"), "1")

    def test_sales_new_invoice_link_type(self):
        # Go to Sales new invoice page.
        self.driver.find_element(By.ID, "sales-menu-link").click()
        path = self.driver.find_element(By.ID, "sales-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[1].click()

        # Click on Go to type link
        path = self.driver.find_element(By.ID, "invoice-form")
        type_link = path.find_elements(By.TAG_NAME, "a")[0]
        type_link.click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "visible-list"),
                "Invoice A"
            )
        )

    def test_sales_new_invoice_link_pos(self):
        # Go to Sales new invoice page.
        self.driver.find_element(By.ID, "sales-menu-link").click()
        path = self.driver.find_element(By.ID, "sales-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[1].click()

        # Click on Go to type link
        path = self.driver.find_element(By.ID, "invoice-form")
        type_link = path.find_elements(By.TAG_NAME, "a")[1]
        type_link.click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "new-pos"),
                "Add"
            )
        )