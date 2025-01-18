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
from ..models import (CompanyClient, Supplier, PaymentMethod, PaymentTerm,
    PointOfSell, DocumentType, SaleInvoice, SaleInvoiceLine, SaleReceipt)
from utils.utils_tests import (go_to_section, element_has_selected_option, 
    click_button_and_show, fill_field, webDriverWait_visible_element,
    click_button_and_answer_alert, pay_conditions_click_default, go_to_link,
    pay_conditions_delete_confirm_button, pick_option_by_index, search_fill_field,
    search_clear_field, click_and_redirect, multiple_driver_wait_count, 
    get_columns_data, web_driver_wait_count, click_and_wait, search_wait_first_input,
    find_visible_elements, filter_field, text_in_visible_element, scroll_page,
    load_new_collected_option, wait_visible_invisible, view_and_answer_popup)
from utils.base_tests import CreateDbInstancesMixin


class FrontBaseTest(CreateDbInstancesMixin, StaticLiveServerTestCase):
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
        
        self.c_client1 = CompanyClient.objects.create(
            tax_number = "20361382481",
            name = "Client1 SRL",
            address = "Client street, Client city, Chile",
            email = "client1@email.com",
            phone = "1234567890",
        )

        self.c_client2 = CompanyClient.objects.create(
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

        self.pos1 = PointOfSell.objects.create(pos_number = "00001")

        self.pay_method1 = PaymentMethod.objects.create(pay_method = "Cash")
        self.pay_method2 = PaymentMethod.objects.create(pay_method = "Transfer")

        self.pay_term1 = PaymentTerm.objects.create(pay_term = "0")
        self.pay_term2 = PaymentTerm.objects.create(pay_term = "30")

    def create_doc_types(self):
        self.doc_type1 = DocumentType.objects.create(
            type = "A",
            code = "001",
            type_description = "Invoice A",
            hide = False,
        )

        self.doc_type2 = DocumentType.objects.create(
            type = "B",
            code = "002",
            type_description = "Invoice B",
            hide = False,
        )

    def create_first_invoice_and_receipt(self):
        self.create_doc_types()
        self.sale_invoice1 = SaleInvoice.objects.create(
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
        
        self.sale_invoice1_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice1,
            description = "Test sale invoice",
            taxable_amount = Decimal("1000"),
            not_taxable_amount = Decimal("90.01"),
            vat_amount = Decimal("210"),
        )
        self.sale_invoice1_line2 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice1,
            description = "Other products",
            taxable_amount = Decimal("999"),
            not_taxable_amount = Decimal("00.01"),
            vat_amount = Decimal("209.99"),
        )

        self.sale_receipt1 = SaleReceipt.objects.create(
            issue_date = datetime.date(2024, 2, 21),
            point_of_sell = self.pos1,
            number = "00000001",
            description = "Test sale receipt",
            related_invoice = self.sale_invoice1,
            sender = self.company,
            recipient = self.c_client1,
            total_amount = Decimal("2509.01"),
        )


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

    @tag("erp_front_client_edit")
    def test_client_edit(self):
        # Go to edit client page
        self.driver.get(f"{self.live_server_url}/erp/client/edit")

        # click on 2nd client and edit
        self.driver.find_elements(By.CLASS_NAME, "specific-person")[1].click()
        webDriverWait_visible_element(self.driver, By.ID, "person-details")
        click_button_and_show(
            self.driver, By.ID, "person-details", By.ID, "person-edit-form"
        )
        
        path = self.driver.find_element(By.ID, "person-edit-form")
        
        # Alter data, add company's tax number
        fill_field(self.driver, path, "tax_number", "20361382480")
        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "edit-message"),
                "The tax number you're trying to add belongs to the company."
            )
        )
        
        # Alter data again, add a correct id 
        fill_field(self.driver, path, "tax_number", "12345678901")
        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "person-list"), "12345678901"
            )
        )
    
    @tag("erp_front_client_edit")
    def test_client_edit_filter(self):
        self.create_company_clients()
        # Go to edit client page
        self.driver.get(f"{self.live_server_url}/erp/client/edit")

        # Get original client's list 
        client_list = find_visible_elements(self.driver, By.CLASS_NAME, "specific-person")
        self.assertEqual(len(client_list), 7)
        
        # Filter the list
        filterField = self.driver.find_element(By.ID, "filter")
        filterField.send_keys("2745100")
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element(client_list[0])
        )
        path = self.driver.find_element(By.ID, "person-list")
        client_list = web_driver_wait_count(
            self.driver, path, 3, selector_value="specific-person", visible=True
        )
        
        # clean data and filter again
        search_clear_field(self.driver, "filter")
        filterField.send_keys("Client6 SRL")
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element(client_list[0])
        )
        
        # check quantity
        web_driver_wait_count(
            self.driver, path, 1, selector_value="specific-person", visible=True
        )
       
    @tag("erp_front_client_delete")
    def test_client_delete_single(self):
        # Go to delete client page
        self.driver.get(f"{self.live_server_url}/erp/client/delete")

        # Click on 1st client 
        self.driver.find_elements(By.CLASS_NAME, "specific-person")[0].click()
        webDriverWait_visible_element(self.driver, By.ID, "person-details")
        
        # Click on Delete and cancel alert
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "dismiss"
        )

        # Click again on delete and accept
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "accept"
        )

        # Check that client disappeared
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(path[1])
        )
        # Path changed, I have to reassing it
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        self.assertNotIn("20361382480", path[0].text)
        self.assertEqual(len(path), 1)

    @tag("erp_front_client_delete")
    def test_client_delete_multiple(self):
        self.create_company_clients()
        # Go to delete client page
        self.driver.get(f"{self.live_server_url}/erp/client/delete")

        # Click clients 2,4 outside the checkbox
        clients = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        clients[1].click()
        clients[3].click()
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "person-details"), "CLIENT4")
        )
        boxes = self.driver.find_elements(By.CLASS_NAME, "select-multiple")
        checked_boxes = [box for box in boxes if box.is_selected()]
        delete_button = self.driver.find_element(By.CLASS_NAME, "delete-button")

        self.assertEqual(len(checked_boxes), 2)
        self.assertIn("Delete All (2)", delete_button.text)

        # Click clients 5,7 inside the checkbox
        boxes[4].click()
        boxes[6].click()
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "person-details"), "CLIENT7")
        )
        checked_boxes = [box for box in boxes if box.is_selected()]
        delete_button = self.driver.find_element(By.CLASS_NAME, "delete-button")

        self.assertEqual(len(checked_boxes), 4)
        self.assertIn("Delete All (4)", delete_button.text)
        
        # Click checkbox of client 4 and container client 5
        boxes[3].click()
        clients[4].click()
        WebDriverWait(self.driver, 5).until(
            # Use delete button because client detail doesn't change
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "delete-button"), "Delete All (2)")
        )
        checked_boxes = [box for box in boxes if box.is_selected()]
        
        self.assertEqual(len(checked_boxes), 2)

        # Click on Delete All and cancel alert
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "dismiss"
        )
        # Click again and accept
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "accept"
        )

        # Check that clients 2 and 7 disappeared
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(path[-1])
        )
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person") # Refresh the list
        self.assertNotIn("33546921", path[-1].text)
        self.assertNotIn("CLIENT2 SA", path[1].text)
        self.assertEqual(len(path), 5)

    @tag("erp_front_client_delete")
    def test_client_delete_filter(self):
        self.create_company_clients()
        # Go to edit client page
        self.driver.get(f"{self.live_server_url}/erp/client/delete")

        # Get original client's list 
        client_list = find_visible_elements(self.driver, By.CLASS_NAME, "specific-person")
        self.assertEqual(len(client_list), 7)
        
        # Filter the list
        filter_field(self.driver, "09876", invisible_element=client_list[1])
        path = self.driver.find_element(By.ID, "person-list")
        client_list = web_driver_wait_count(
            self.driver, path, 0, selector_value="specific-person", visible=True
        )
        
        # clean data and filter again
        search_clear_field(self.driver, "filter")
        WebDriverWait(self.driver, 5).until(
            text_in_visible_element(
                (By.CLASS_NAME, "specific-person"), "CLIENT1"
            )
        )
        client_list = find_visible_elements(self.driver, By.CLASS_NAME, "specific-person")
        filter_field(self.driver, "client")
        
        # check quantity
        web_driver_wait_count(
            self.driver, path, 7, selector_value="specific-person", visible=True
        )

    @tag("erp_front_client_delete")
    def test_client_delete_conflict(self):
        # Go to client delete webpage.
        self.create_first_invoice_and_receipt()
        self.driver.get(f"{self.live_server_url}/erp/client/delete")
        
        # Click on 1st client and delete
        self.driver.find_elements(By.CLASS_NAME, "specific-person")[0].click()
        webDriverWait_visible_element(self.driver, By.ID, "person-details")
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "accept"
        )
    
        # Wait for popup to appear and accept
        view_and_answer_popup(self.driver, "The client couldn't be deleted")
       
        webDriverWait_visible_element(self.driver, By.ID, "rd-title")

        self.assertEqual(self.driver.title, "Related Documents")
        self.assertEqual(CompanyClient.objects.all().count(), 2)

    @tag("erp_front_client_delete")
    def test_client_delete_multiple_conflict_filter(self):
        self.create_company_clients()
        self.create_first_invoice_and_receipt()
        # Go to delete client page
        self.driver.get(f"{self.live_server_url}/erp/client/delete")

        # filter clients by SRL
        client_list = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        filter_field(self.driver, "srl", invisible_element=client_list[1])
        path = self.driver.find_element(By.ID, "person-list")
        client_list = web_driver_wait_count(
            self.driver, path, 3, selector_value="specific-person", visible=True
        )

        # Click clients 1 and 6 (first and third in filtered list)
        client_list[0].click()
        client_list[2].click()
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "person-details"), "CLIENT6")
        )
        boxes = self.driver.find_elements(By.CLASS_NAME, "select-multiple")
        checked_boxes = [box for box in boxes if box.is_selected()]
        delete_button = self.driver.find_element(By.CLASS_NAME, "delete-button")

        self.assertEqual(len(checked_boxes), 2)
        self.assertIn("Delete All (2)", delete_button.text)

        # Click on Delete All and cancel alert
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "dismiss"
        )
        # Click again and accept
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "accept"
        )

        # Accept popup
        view_and_answer_popup(self.driver, "Couldn't delete the selected clients")

        self.assertEqual(CompanyClient.objects.all().count(), 7)

    @tag("erp_front_supplier_edit")
    def test_supplier_edit(self):
        # Go to edit supplier page
        self.driver.get(f"{self.live_server_url}/erp/supplier/edit")

        # click on 1st supplier
        self.driver.find_elements(By.CLASS_NAME, "specific-person")[0].click()
        webDriverWait_visible_element(self.driver, By.ID, "person-details")
        click_button_and_show(
            self.driver, By.ID, "person-details", By.ID, "person-edit-form"
        )

        path = self.driver.find_element(By.ID, "person-edit-form")
        
        # Alter data, add company's tax number
        fill_field(self.driver, path, "tax_number", "20361382480")
        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "edit-message"),
                "The tax number you're trying to add belongs to the company."
            )
        )

        # Alter data again, add a correct id 
        fill_field(self.driver, path, "tax_number", "12345678901")
        path.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "person-list"), "12345678901"
            )
        )

    @tag("erp_front_supplier_edit")
    def test_supplier_edit_filter(self):
        self.create_suppliers()
        # Go to edit supplier page
        self.driver.get(f"{self.live_server_url}/erp/supplier/edit")

        # Get original supplier's list 
        supplier_list = find_visible_elements(self.driver, By.CLASS_NAME, "specific-person")
        self.assertEqual(len(supplier_list), 7)
        
        # Filter the list
        filterField = self.driver.find_element(By.ID, "filter")
        filterField.send_keys("13")
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element(supplier_list[-1])
        )
        path = self.driver.find_element(By.ID, "person-list")
        supplier_list = web_driver_wait_count(
            self.driver, path, 2, selector_value="specific-person", visible=True
        )
        
        # clean data and filter again
        search_clear_field(self.driver, "filter")
        filterField.send_keys("SA")
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element(supplier_list[1])
        )
        
        # check quantity
        web_driver_wait_count(
            self.driver, path, 4, selector_value="specific-person", visible=True
        )
    
    @tag("erp_front_supplier_delete")
    def test_supplier_delete_single(self):
        # Go to delete supplier page
        self.driver.get(f"{self.live_server_url}/erp/supplier/delete")

        # Click on supplier2, delete (note, 0= sup2, 1=sup1) and cancel alarm
        self.driver.find_elements(By.CLASS_NAME, "specific-person")[1].click()
        webDriverWait_visible_element(self.driver, By.ID, "person-details")
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "dismiss"
        )

        # Click again on delete and accept
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "accept"
        )

        # Check that supplier2 disappeared
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(path[1])
        )
        # Path changed, I have to reassign it
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        self.assertNotIn("30361382485", path[0].text)
        self.assertEqual(len(path), 1)

    @tag("erp_front_supplier_delete_multiple")
    def test_supplier_delete_multiple(self):
        self.create_suppliers()
        # Go to delete supplier page
        self.driver.get(f"{self.live_server_url}/erp/supplier/delete")

        # Click suppliers 3, 4, 1 outside the checkbox
        suppliers = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        suppliers[2].click()
        suppliers[3].click()
        suppliers[0].click()
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "person-details"), "20361382482")
        )
        boxes = self.driver.find_elements(By.CLASS_NAME, "select-multiple")
        checked_boxes = [box for box in boxes if box.is_selected()]
        delete_button = self.driver.find_element(By.CLASS_NAME, "delete-button")

        self.assertEqual(len(checked_boxes), 3)
        self.assertIn("Delete All (3)", delete_button.text)

        # Click suppliers 7,6 inside the checkbox
        boxes[6].click()
        boxes[5].click()
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "person-details"), "74639018254")
        )
        checked_boxes = [box for box in boxes if box.is_selected()]
        delete_button = self.driver.find_element(By.CLASS_NAME, "delete-button")

        self.assertEqual(len(checked_boxes), 5)
        self.assertIn("Delete All (5)", delete_button.text)
        
        # Click checkbox of supplier 1 and container supplier 6
        boxes[0].click()
        suppliers[5].click()
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.ID, "person-details"), "83092147563"
            )
        )
        checked_boxes = [box for box in boxes if box.is_selected()]
        delete_button = self.driver.find_element(By.CLASS_NAME, "delete-button")
        
        self.assertEqual(len(checked_boxes), 3)
        self.assertIn("Delete All (3)", delete_button.text)

        # Click on Delete All and cancel alert
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "dismiss"
        )
        # Click again and accept
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "accept"
        )

        # Check that suppliers 3, 4 and 7 disappeared
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(path[-1])
        )
        # Refresh the list
        path = self.driver.find_elements(By.CLASS_NAME, "specific-person") 
        
        for value, element in [("78493261547", path[2]), ("23984715680", path[3]),
            ("83092147563", path[-1])]:
            self.assertNotIn(value, element.text)
        
        self.assertEqual(len(path), 4)

    @tag("erp_front_supplier_delete")
    def test_supplier_delete_filter(self):
        self.create_suppliers()
        # Go to edit supplier page
        self.driver.get(f"{self.live_server_url}/erp/supplier/delete")

        # Get original supplier's list 
        supplier_list = find_visible_elements(self.driver, By.CLASS_NAME, "specific-person")
        self.assertEqual(len(supplier_list), 7)
        
        # Filter the list
        filterField = self.driver.find_element(By.ID, "filter")
        filterField.send_keys("13")
        # Double wait as sometime it shows false error.
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element(supplier_list[2]) 
        )
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element(supplier_list[-1]) 
        )
        path = self.driver.find_element(By.ID, "person-list")
        supplier_list = web_driver_wait_count(
            self.driver, path, 2, selector_value="specific-person", visible=True
        )
        
        # clean data and filter again
        search_clear_field(self.driver, "filter")
        filterField.send_keys("SRL")
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element(supplier_list[0])
        )
        
        # check quantity
        web_driver_wait_count(
            self.driver, path, 3, selector_value="specific-person", visible=True
        )

    # TODO when I add a purchase invoice
    """
    @tag("erp_front_supplier_delete")
    def test_client_delete_conflict(self):
        # Go to client delete webpage.
        self.create_first_invoice_and_receipt()
        self.driver.get(f"{self.live_server_url}/erp/client/delete")
        
        # Click on 1st client and delete
        self.driver.find_elements(By.CLASS_NAME, "specific-person")[0].click()
        webDriverWait_visible_element(self.driver, By.ID, "person-details")
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "accept"
        )
        
        # Wait for popup and cancel.
        webDriverWait_visible_element(self.driver, By.CLASS_NAME, "popup")
        path = self.driver.find_element(By.CLASS_NAME, "popup-footer")
        path.find_elements(By.TAG_NAME, "button")[1].click()

        #  Delete again  
        self.driver.find_elements(By.CLASS_NAME, "specific-person")[0].click()
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "accept"
        )
    
        # Wait for popup to appear and accept
        view_and_answer_popup(self.driver, "The client couldn't be deleted")
        
        webDriverWait_visible_element(self.driver, By.ID, "rd-title")

        self.assertEqual(self.driver.title, "Related Documents")
        self.assertEqual(CompanyClient.objects.all().count(), 2)

    @tag("erp_front_supplier_delete")
    def test_client_delete_multiple_conflict_filter(self):
        self.create_company_clients()
        self.create_first_invoice_and_receipt()
        # Go to delete client page
        self.driver.get(f"{self.live_server_url}/erp/client/delete")

        # filter clients by SRL
        client_list = self.driver.find_elements(By.CLASS_NAME, "specific-person")
        filter_field(self.driver, "srl", invisible_element=client_list[1])
        path = self.driver.find_element(By.ID, "person-list")
        client_list = web_driver_wait_count(
            self.driver, path, 3, selector_value="specific-person", visible=True
        )

        # Click clients 1 and 6 (first and third in filtered list)
        client_list[0].click()
        client_list[2].click()
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "person-details"), "CLIENT6")
        )
        boxes = self.driver.find_elements(By.CLASS_NAME, "select-multiple")
        checked_boxes = [box for box in boxes if box.is_selected()]
        delete_button = self.driver.find_element(By.CLASS_NAME, "delete-button")

        self.assertEqual(len(checked_boxes), 2)
        self.assertIn("Delete All (2)", delete_button.text)

        # Click on Delete All and cancel alert
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "dismiss"
        )
        # Click again and accept
        click_button_and_answer_alert(
            self.driver, By.ID, "person-details", "accept"
        )

        # Accept pop up 
        view_and_answer_popup(self.driver, "The client couldn't be deleted")

        self.assertEqual(self.driver.title, "Delete Client")
        self.assertEqual(CompanyClient.objects.all().count(), 7)
    """


    @tag("erp_front_client_rel_docs_links")
    def test_client_rel_docs_links_invoice(self):
        self.create_first_invoice_and_receipt()
        # Go to invoice 1 rel receipts webpage.
        url = f"{self.live_server_url}/erp/client/{self.c_client1.pk}"
        url += f"/related_documents"
        self.driver.get(url)
        self.assertEqual(self.driver.title, "Related Documents")

        # Check invoice link
        go_to_link(self.driver, By.CLASS_NAME, "inv-section", url, 0)
        self.assertEqual(self.driver.title, "Invoice A 00001-00000001")

    @tag("erp_front_client_rel_docs_links")
    def test_sales_invoice_rel_receipts_links_receipt(self):
        self.create_first_invoice_and_receipt()
        # Go to invoice 1 rel receipts webpage.
        url = f"{self.live_server_url}/erp/client/{self.c_client1.pk}"
        url += f"/related_documents"
        self.driver.get(url)
        self.assertEqual(self.driver.title, "Related Documents")

        # Check receipt link
        go_to_link(self.driver, By.CLASS_NAME, "rec-section", url, 0)
        self.assertEqual(self.driver.title, "Receipt 00001-00000001")

    @tag("erp_payment_conditions")
    def test_payment_conditions_tags(self):
        # Clean payment cond instances and try all the tabs.
        PaymentTerm.objects.all().delete()
        PaymentMethod.objects.all().delete()
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Se welcome message
        welcome_section = self.driver.find_element(By.ID, "welcome-section")
        self.assertIn("you can manage the payment", welcome_section.text)

        # Click on add default methods and change to terms
        methods_button = self.driver.find_element(By.ID, "method-tab")
        methods_button.click()
        default_button = self.driver.find_element(By.ID, "default-tab")
        wait_visible_invisible(self.driver,
            (By.ID, "default-tab"), (By.ID, "welcome-section")
        )
        
        default_button.click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "default-method"))
        )

        # Click on term and check changes
        terms_button = self.driver.find_element(By.ID, "term-tab")
        terms_button.click()
        wait_visible_invisible(self.driver,
            (By.ID, "default-term"), (By.ID, "default-method")
        )

        # Check new method and term buttons
        new_button = self.driver.find_element(By.ID, "new-tab")
        new_button.click()
        wait_visible_invisible(self.driver,
            (By.ID, "new-term"), (By.ID, "default-term")
        )

        methods_button.click()
        methods_button.click() # Check double click works well
        wait_visible_invisible(self.driver,
            (By.ID, "new-method"), (By.ID, "new-term")
        )

        # Check show method and term buttons
        show_button = self.driver.find_element(By.ID, "show-tab")
        show_button.click()
 
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "new-method"))
        )
        WebDriverWait(self.driver, 5).until(EC.text_to_be_present_in_element(
            (By.ID, "show-list"), "added any method")
        )

        terms_button.click()
        terms_button.click() # Double click check
        WebDriverWait(self.driver, 5).until(EC.text_to_be_present_in_element(
                (By.ID, "show-list"), "added any term")
        )
        
    
    @tag("erp_payment_cond_def")
    def test_payment_conditions_term_default(self):
        # Clean payment cond instances and go to Payment Conditions page.
        PaymentTerm.objects.all().delete()
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Click on terms < default < load
        self.driver.find_element(By.ID, "term-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "default-tab")
        self.driver.find_element(By.ID, "default-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "default-term")
        click_button_and_answer_alert(self.driver, By.ID, "default-term", "dismiss")
        click_button_and_answer_alert(self.driver, By.ID, "default-term", "accept")
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "popup"), "Default terms loaded successfully."
            )
        )

        # Check other default is disabled
        self.driver.find_element(By.ID, "method-tab").click()
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element_attribute(
                (By.ID, "default-tab"), "class", "disabled"
            )
        )
        def_section = self.driver.find_element(By.ID, "default-method")
        self.assertIn("payment method's", def_section.text)


    @tag("erp_payment_cond_def")
    def test_payment_conditions_method_default(self):
        # Clean payment cond instances and go to Payment Conditions page.
        PaymentMethod.objects.all().delete()
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Click on default
        self.driver.find_element(By.ID, "method-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "default-tab")
        self.driver.find_element(By.ID, "default-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "default-method")
        click_button_and_answer_alert(self.driver, By.ID, "default-method", "dismiss")
        click_button_and_answer_alert(self.driver, By.ID, "default-method", "accept")
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "popup"), "Default methods loaded successfully."
            )
        )

        # Check other default is disabled
        self.driver.find_element(By.ID, "term-tab").click()
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element_attribute(
                (By.ID, "default-tab"), "class", "disabled"
            )
        )
        def_section = self.driver.find_element(By.ID, "default-term")
        self.assertIn("payment term's", def_section.text)

    @tag("erp_payment_cond_def")
    def test_payment_conditions_term_default_multiple_clicks(self):
        # Clean payment cond instances and go to Payment Conditions page.
        PaymentTerm.objects.all().delete()
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")
 
        method_tab = self.driver.find_element(By.ID, "method-tab")
        term_tab = self.driver.find_element(By.ID, "term-tab")
        default_tab = self.driver.find_element(By.ID, "default-tab")
        
        # Click on term > default
        term_tab.click()
        webDriverWait_visible_element(self.driver, By.ID, "default-tab")
        default_tab.click()
        webDriverWait_visible_element(self.driver, By.ID, "default-term")

        # swap between method and term a few times
        for _ in range(4): 
            method_tab.click()
            webDriverWait_visible_element(self.driver, By.ID, "default-method")
            term_tab.click()
            webDriverWait_visible_element(self.driver, By.ID, "default-term")
        
        # Click and Dismiss alert
        click_button_and_answer_alert(self.driver, By.ID, "default-term", "dismiss")

        # If code works correctly, term tab can be clicked
        method_tab.click()
    
    @tag("erp_payment_cond_def")
    def test_payment_conditions_method_default_multiple_clicks(self):
        # Clean payment cond instances and go to Payment Conditions page.
        PaymentMethod.objects.all().delete()
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")
 
        method_tab = self.driver.find_element(By.ID, "method-tab")
        term_tab = self.driver.find_element(By.ID, "term-tab")
        default_tab = self.driver.find_element(By.ID, "default-tab")
        
        # Click on method > default
        method_tab.click()
        webDriverWait_visible_element(self.driver, By.ID, "default-tab")
        default_tab.click()
        webDriverWait_visible_element(self.driver, By.ID, "default-method")

        # swap between method and term a few times
        for _ in range(4): 
            term_tab.click()
            webDriverWait_visible_element(self.driver, By.ID, "default-term")
            method_tab.click()
            webDriverWait_visible_element(self.driver, By.ID, "default-method")
        
        # Click and Dismiss alert
        click_button_and_answer_alert(self.driver, By.ID, "default-method", "dismiss")

        # If code works correctly, term tab can be clicked
        term_tab.click()

    @tag("erp_payment_cond_new")
    def test_payment_conditions_term_new(self):
        # Go to Payment Conditions page.
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Click on new
        self.driver.find_element(By.ID, "term-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "new-tab")
        self.driver.find_element(By.ID, "new-tab").click()
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "new-term"), "Add Term")
        )

        # Fill field and confirm
        path = self.driver.find_element(By.ID, "new-term")
        fill_field(self.driver, path, "pay_term", "180")
        click_button_and_answer_alert(self.driver, By.ID, "new-term", "dismiss")
        click_button_and_answer_alert(self.driver, By.ID, "new-term", "accept")
       
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "popup"), "New term added successfully."
            )
        )

    @tag("erp_payment_cond_new")
    def test_payment_conditions_method_new(self):
        # Go to Payment Conditions page.
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Click on new
        self.driver.find_element(By.ID, "method-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "new-tab")
        self.driver.find_element(By.ID, "new-tab").click()
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "new-method"), "Add Method")
        )
        
         # Fill field and confirm
        path = self.driver.find_element(By.ID, "new-method")
        fill_field(self.driver, path, "pay_method", "Hand")
        click_button_and_answer_alert(self.driver, By.ID, "new-method", "dismiss")
        click_button_and_answer_alert(self.driver, By.ID, "new-method", "accept")
        
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "popup"), "New method added successfully."
            )
        )

    @tag("erp_payment_cond_view")
    def test_payment_terms_view_list_and_delete(self):
        # Create data
        self.create_extra_pay_terms()
        self.assertEqual(PaymentTerm.objects.all().count(), 5)
        
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Click on show methods
        self.driver.find_element(By.ID, "term-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "show-tab")
        self.driver.find_element(By.ID, "show-tab").click()
        WebDriverWait(self.driver, 5).until(EC.text_to_be_present_in_element(
                (By.ID, "show-section"), "Payment terms")
        )
        # Check list
        list_section = self.driver.find_element(By.ID, "show-list")
        for value in ["0", "30", "60", "90", "180"]:
            self.assertIn(value, list_section.text)

        # Delete an entry
        delete_buttons = list_section.find_elements(By.CLASS_NAME, "delete-item")
        delete_buttons[2].click()  
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.ID, "show-list"), "Confirm"
            )
        )
        # Click in confirm
        delete_buttons[2].click()
        WebDriverWait(self.driver, 10).until(EC.staleness_of(delete_buttons[2]))

        self.assertEqual(PaymentTerm.objects.all().count(), 4)
        self.assertNotIn("60", list_section.text)

    @tag("erp_payment_cond_view")
    def test_payment_methods_view_list_and_delete(self):
        # Create data
        self.create_extra_pay_methods()
        self.assertEqual(PaymentMethod.objects.all().count(), 4)
    
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")

        # Click on show methods
        self.driver.find_element(By.ID, "method-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "show-tab")
        self.driver.find_element(By.ID, "show-tab").click()
        WebDriverWait(self.driver, 5).until(EC.text_to_be_present_in_element(
                (By.ID, "show-section"), "Payment methods")
        )

        # Check list
        list_section = self.driver.find_element(By.ID, "show-list")
        for value in ["Cash", "Transfer", "Debit Card", "Check"]:
            self.assertIn(value, list_section.text)
        
        # Delete 2 entries
        for index in [-1, 0]:
            delete_buttons = list_section.find_elements(By.CLASS_NAME, "delete-item")
            delete_buttons[index].click()  
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element(
                    (By.ID, "show-list"), "Confirm"
                )
            )
            delete_buttons[index].click()
            WebDriverWait(self.driver, 10).until(EC.staleness_of(delete_buttons[index]))

        self.assertEqual(PaymentMethod.objects.all().count(), 2)
        self.assertNotIn("Cash", list_section.text)
        self.assertNotIn("Check", list_section.text)

    @tag("erp_payment_cond_delete_conflict")
    def test_payment_terms_delete_conflict(self):
        # Go to client delete webpage.
        self.create_first_invoice_and_receipt()
        self.assertEqual(PaymentTerm.objects.all().count(), 2)
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")
        
        # Click on show methods
        self.driver.find_element(By.ID, "term-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "show-tab")
        self.driver.find_element(By.ID, "show-tab").click()
        WebDriverWait(self.driver, 5).until(EC.text_to_be_present_in_element(
                (By.ID, "show-section"), "Payment terms")
        )
        
        # Delete an entry
        list_section = self.driver.find_element(By.ID, "show-list")
        delete_buttons = list_section.find_elements(By.CLASS_NAME, "delete-item")
        delete_buttons[0].click()  
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "show-list"), "Confirm")
        )
        # Click on confirm
        delete_buttons[0].click()
        
        # Wait for popup and cancel.
        view_and_answer_popup(self.driver, "invoices using this term")

        self.assertEqual(PaymentTerm.objects.all().count(), 2)
        self.assertIn("30", list_section.text)

    @tag("erp_payment_cond_delete_conflict")
    def test_payment_methods_delete_conflict(self):
        # Go to client delete webpage.
        self.create_first_invoice_and_receipt()
        self.assertEqual(PaymentMethod.objects.all().count(), 2)
        self.driver.get(f"{self.live_server_url}/erp/payment_conditions")
        
        # Click on show methods
        self.driver.find_element(By.ID, "method-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "show-tab")
        self.driver.find_element(By.ID, "show-tab").click()
        WebDriverWait(self.driver, 5).until(EC.text_to_be_present_in_element(
                (By.ID, "show-section"), "Payment methods")
        )
        
        # Delete an entry
        list_section = self.driver.find_element(By.ID, "show-list")
        delete_buttons = list_section.find_elements(By.CLASS_NAME, "delete-item")
        delete_buttons[0].click()  
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "show-list"), "Confirm")
        )
        # Click on confirm
        delete_buttons[0].click()
        
        # Wait for popup and cancel.
        view_and_answer_popup(self.driver, "invoices using this method")

        self.assertEqual(PaymentTerm.objects.all().count(), 2)
        self.assertIn("Cash", list_section.text)
        self.assertIn("Transfer", list_section.text)


    @tag("erp_front_pos")
    def test_pos_toggle(self):
        # Go to POS page.
        self.driver.get(f"{self.live_server_url}/erp/points_of_sell")

        # check sections are hidden
        new_section = self.driver.find_element(By.ID, "new-section")
        show_section = self.driver.find_element(By.ID, "show-section")
        disable_section = self.driver.find_element(By.ID, "disable-section")

        for section in [new_section, show_section, disable_section]:
            self.assertFalse(section.is_displayed())

        # Toggle tabs
        new_tab = self.driver.find_element(By.ID, "new-tab")
        show_tab = self.driver.find_element(By.ID, "show-tab")
        disable_tab = self.driver.find_element(By.ID, "disable-tab")

        # New POS
        click_and_wait(self.driver, "new-tab")
        WebDriverWait(self.driver, 5).until(
            text_in_visible_element((By.ID, "new-pos-form"), "Add a new POS")
        )
        for section in [show_section, disable_section]:
            self.assertFalse(section.is_displayed())

        # Show POS
        click_and_wait(self.driver, "show-tab", 0.2)
        WebDriverWait(self.driver, 5).until(
            text_in_visible_element((By.ID, "show-pos-title"), "Points of Sell")
        )
        for section in [new_section, disable_section]:
            self.assertFalse(section.is_displayed())

        # Disable Pos
        click_and_wait(self.driver, "disable-tab", 0.2)
        webDriverWait_visible_element(self.driver, By.ID, "dropdown-disable-menu")
        for section in [new_section, show_section]:
            self.assertFalse(section.is_displayed())

    @tag("erp_front_pos")
    def test_pos_new(self):
        self.driver.get(f"{self.live_server_url}/erp/points_of_sell")

        # Go to new POS section
        click_and_wait(self.driver, "new-tab", 0.2)
        webDriverWait_visible_element(self.driver, By.ID, "new-section")
        new_pos_form = self.driver.find_element(By.ID, "new-pos-form")
        
        # Write new pos in form   
        fill_field(self.driver, new_pos_form, "pos_number", "00003")
        click_button_and_answer_alert(self.driver, By.ID, "new-pos-form", "accept")
    
        # Check if it was added
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message-section"), "Point of Sell added succesfully."
            )
        )

    @tag("erp_front_pos")
    def test_pos_view(self):
        self.driver.get(f"{self.live_server_url}/erp/points_of_sell")
        
        # Go to show POS section
        click_and_wait(self.driver, "show-tab", 0.2)
        webDriverWait_visible_element(self.driver, By.ID, "show-section")
        
        # Check that list appears
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "show-pos-title"),
                "Points of Sell"
            )
        )
        pos_list = self.driver.find_element(By.ID, "pos-list")
        self.assertIn("00001", pos_list.text)

    @tag("erp_front_pos_n")
    def test_pos_view_empty(self):
        self.pos1.delete()
        self.driver.get(f"{self.live_server_url}/erp/points_of_sell")
        
        # Go to show POS section
        click_and_wait(self.driver, "show-tab")
        webDriverWait_visible_element(self.driver, By.ID, "show-section")
        
        # Check that text appears
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.ID, "pos-list"), "No Point of Sell has been"
            )
        )
        pos_list = self.driver.find_element(By.ID, "pos-list")
        self.assertNotIn("00001", pos_list.text)

    
    @tag("erp_front_pos")
    def test_pos_disable(self):
        url = f"{self.live_server_url}/erp/points_of_sell"
        self.driver.get(url)

        # Go to disable POS section
        click_and_wait(self.driver, "disable-tab", 1) # 0.8 is not enough
        webDriverWait_visible_element(self.driver, By.ID, "disable-section")

        # click on disable a pos
        self.driver.find_element(By.ID, "dropdown-disable-menu").click()
        self.driver.find_elements(By.CSS_SELECTOR, ".dropdown-item.pos")[0].click()
        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
        
        # Confirm and Check if it was disabled
        self.driver.switch_to.alert.accept()
        WebDriverWait(self.driver, 5).until(EC.text_to_be_present_in_element(
                (By.ID, "message-section"),
                "Point of Sell 00001 disabled."
            )
        )
        
        # Check disabled status 
        time.sleep(1.5) # Sleep 1.5 sec to let page reload
        self.driver.find_element(By.ID, "show-tab").click()
        webDriverWait_visible_element(self.driver, By.CLASS_NAME, "item-disabled")

        self.driver.find_element(By.ID, "disable-tab").click()
        disable_section = self.driver.find_element(By.ID, "disable-section")
        self.assertIn('No Point of Sell', disable_section.text)

    @tag("erp_doc_types")
    def test_doc_types_visibility(self):
        # Go to Document Types page.
        self.driver.get(f"{self.live_server_url}/erp/document_types")
        time.sleep(0.5)
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "invisible-list"), "002")
        )

        # Click on unhide on docs 001 and 002
        path = self.driver.find_element(By.ID, "invisible-list")
        unhide_buttons = path.find_elements(By.TAG_NAME, "button")
        # Use JS click as regular click doesn't work
        self.driver.execute_script("arguments[0].click();", unhide_buttons[1])
        self.driver.execute_script("arguments[0].click();", unhide_buttons[0])
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "visible-list"),
                "001"
            )
        )
        
        # Check that docs are not in invisible list
        for code in ["001", "002"]:
            self.assertNotIn(code, path.text)
        
        # Check that docs 001 and 002 are in visible list
        path = self.driver.find_element(By.ID, "visible-list")
        for code in ["001", "002"]:
            self.assertIn(code, path.text)
        
        # Move back doc 002 to invisible list
        path.find_elements(By.TAG_NAME, "button")[1].click()
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
        self.pos2 = PointOfSell.objects.create(pos_number = "00002")
        self.create_first_invoice_and_receipt()# FrontBaseTest function
        
    def create_extra_invoices(self):
        """Add extra invoices in necessary tests"""
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

        self.sale_invoice3 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 23),
            type = self.doc_type1,
            point_of_sell = self.pos1,
            number ="00000002", 
            sender = self.company,
            recipient = self.c_client1, 
            payment_method = self.pay_method1,
            payment_term = self.pay_term1
        )
        self.sale_invoice4 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 23),
            type=self.doc_type1,
            point_of_sell = self.pos1,
            number="00000003",
            sender=self.company,
            recipient = self.c_client2,
            payment_method=self.pay_method2, 
            payment_term = self.pay_term1
        )
        self.sale_invoice5 = SaleInvoice.objects.create(
            issue_date = datetime.date(2024, 1, 24),
            type = self.doc_type2,
            point_of_sell = self.pos1,
            number = "00000002",
            sender = self.company,
            recipient = self.c_client1,
            payment_method = self.pay_method1, 
            payment_term = self.pay_term1
        )
        self.sale_invoice6 = SaleInvoice.objects.create(
            issue_date=datetime.date(2024, 1, 24),
            type=self.doc_type2,
            point_of_sell=self.pos1,
            number="00000003",
            sender=self.company,
            recipient=self.c_client2,
            payment_method=self.pay_method2, 
            payment_term=self.pay_term1
        )
        self.sale_invoice7 = SaleInvoice.objects.create(
            issue_date=datetime.date(2024, 1, 25),
            type=self.doc_type1,
            point_of_sell=self.pos2,
            number="00000001",
            sender=self.company,
            recipient=self.c_client1,
            payment_method=self.pay_method1, 
            payment_term=self.pay_term1
        )
        self.sale_invoice8 = SaleInvoice.objects.create(
            issue_date=datetime.date(2024, 1, 25),
            type=self.doc_type1,
            point_of_sell=self.pos2,
            number="00000002",
            sender=self.company,
            recipient=self.c_client1,
            payment_method=self.pay_method2,
            payment_term=self.pay_term1
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
        
        self.sale_invoice2_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice2,
            description = "Second sale invoice",
            taxable_amount = Decimal("999.99"),
            not_taxable_amount = Decimal("0.02"),
            vat_amount = Decimal("209.09"),
        )
        self.sale_invoice3_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice3,
            description = "Third sale invoice",
            taxable_amount = Decimal("3"),
            not_taxable_amount = Decimal("3"),
            vat_amount = Decimal("3"),
        )
        self.sale_invoice4_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice4,
            description = "Forth sale invoice",
            taxable_amount = Decimal("4"),
            not_taxable_amount = Decimal("4"),
            vat_amount = Decimal("4"),
        )
        self.sale_invoice5_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice5,
            description = "Fifth sale invoice",
            taxable_amount = Decimal("5"),
            not_taxable_amount = Decimal("5"),
            vat_amount = Decimal("5"),
        )
        self.sale_invoice6_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice6,
            description = "Sixth sale invoice",
            taxable_amount = Decimal("6"),
            not_taxable_amount = Decimal("6"),
            vat_amount = Decimal("6"),
        )
        self.sale_invoice7_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice7,
            description = "Seventh sale invoice",
            taxable_amount = Decimal("7"),
            not_taxable_amount = Decimal("7"),
            vat_amount = Decimal("7"),
        )
        self.sale_invoice8_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice8,
            description = "Eighth sale invoice",
            taxable_amount = Decimal("8"),
            not_taxable_amount = Decimal("8"),
            vat_amount = Decimal("8"),
        )
        self.sale_invoice9_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice9,
            description = "Ninth sale invoice",
            taxable_amount = Decimal("9"),
            not_taxable_amount = Decimal("9"),
            vat_amount = Decimal("9"),
        )
        self.sale_invoice10_line1 = SaleInvoiceLine.objects.create(
            sale_invoice = self.sale_invoice10,
            description = "Tenth sale invoice",
            taxable_amount = Decimal("10"),
            not_taxable_amount = Decimal("10"),
            vat_amount = Decimal("10"),
        )
        
    def create_extra_receipts(self): 
        """Create extra receipts if it's necessary """
        self.create_extra_invoices() # Function dependant
        self.sale_invoice2.collected = True # Update invoice 2 status
        self.sale_invoice2.save()
        
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

    @tag("erp_new_invoice_link_t")
    def test_sales_new_invoice_link_type(self):
        url = f"{self.live_server_url}/erp/sales/invoices/new"
        self.driver.get(url)

        # Click on "Go to type" link-
        go_to_link(self.driver, By.ID, "invoice-form", url, 0)
        self.assertEqual(self.driver.title, "Document Types")

    def test_sales_new_invoice_link_pos(self):
        # Go to Sales new invoice page.
        url = f"{self.live_server_url}/erp/sales/invoices/new"
        self.driver.get(url)

        # Click on "Go to pos" link-
        go_to_link(self.driver, By.ID, "invoice-form", url, 1)
        self.assertEqual(self.driver.title, "Points of Sell")
        
    @tag("erp_new_invoice_line")
    def test_sales_new_invoice_add_line(self):
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/new")

        # Click on New line
        path = self.driver.find_element(By.ID, "invoice-form")
        button = path.find_element(By.ID, "new-line")
        # JS click as regular one doesn't work.
        self.driver.execute_script("arguments[0].click();", button)
        webDriverWait_visible_element(
            self.driver, By.ID, "id_s_invoice_lines-1-description"
        )

        # Click again. JS click as regular one doesn't work.
        self.driver.execute_script("arguments[0].click();", button)
        webDriverWait_visible_element(
            self.driver, By.ID, "id_s_invoice_lines-2-description"
        )

    @tag("erp_front_invoice_search_collected")
    def test_sales_search_invoice_collected(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")

        element_has_selected_option("id_collected", "Uncollected")
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_client_name")

        # Test initial list
        path = self.driver.find_element(By.ID, "invoice-list")
        invoice_list = path.find_elements(By.CLASS_NAME, "search-row")
        self.assertEqual(len(invoice_list), 0)
        
        # Add an imput to show all invoices
        search_fill_field(self.driver, "id_type", " ")
        invoice_list = multiple_driver_wait_count(self.driver, path, 9)

        # Test all invoices
        load_new_collected_option(self.driver, "All")
        invoice_list = web_driver_wait_count(self.driver, path, 10)
        
        # Test collected invoices
        load_new_collected_option(self.driver, "Collected")
        invoice_list = web_driver_wait_count(self.driver, path, 1)

    @tag("erp_front_invoice_search_fields")
    def test_sales_invoice_search_one_field_part_1(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_type", 3)
        
        path = self.driver.find_element(By.ID, "invoice-list")
        
        # Search by type
        search_fill_field(self.driver, "id_type", "a")
        invoice_list = search_wait_first_input(self.driver, path, "id_type", "a", 4)

        self.assertIn("A", invoice_list[0].text)
        
        search_clear_field(self.driver, "id_type", invoice_list[0])
        
        # Test Pos
        search_fill_field(self.driver, "id_pos", " 2")
        invoice_list = web_driver_wait_count(self.driver, path, 4, By.CLASS_NAME,
            "search-row")
        
        self.assertIn("00002-", invoice_list[0].text)
        
        search_clear_field(self.driver, "id_pos", invoice_list[0])
             
    @tag("erp_front_invoice_search_fields")
    def test_sales_invoice_search_one_field_part_2(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")
        
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_pos")

        path = self.driver.find_element(By.ID, "invoice-list")

        # Test Number
        search_fill_field(self.driver, "id_number", "1 ")
        invoice_list = search_wait_first_input(self.driver, path, "id_number", "1", 3)
        
        self.assertIn("-00000001", invoice_list[0].text)
        
        search_clear_field(self.driver, "id_number", invoice_list[0])

        # Test Client tax number
        search_fill_field(self.driver, "id_client_tax_number", "13 ")
        invoice_list = web_driver_wait_count(self.driver, path, 5, By.CLASS_NAME,
            "search-row")
        
        self.assertIn("20361382481", invoice_list[0].text)
        
        search_clear_field(self.driver, "id_client_tax_number", invoice_list[0])
        
        # Test Client name
        search_fill_field(self.driver, "id_client_name", "cLiEnT2 SA")
        invoice_list = web_driver_wait_count(self.driver, path, 4, By.CLASS_NAME,
            "search-row")

        self.assertIn("CLIENT2 SA", invoice_list[0].text)

    @tag("erp_front_invoice_search_fields")
    def test_sales_invoice_search_one_field_part_3(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")
        
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_number")

        path = self.driver.find_element(By.ID, "invoice-list")
        
        # Test Year
        search_fill_field(self.driver, "id_year", "20")
        invoice_list = search_wait_first_input(self.driver, path, "id_year", "20", 9)
       
        self.assertIn("2024", invoice_list[0].text)
        
        search_clear_field(self.driver, "id_year", invoice_list[0])
        
        # Test month
        search_fill_field(self.driver, "id_month", "13")
        invoice_list = web_driver_wait_count(self.driver, path, 0, By.CLASS_NAME,
            "search-row")
        
        path = self.driver.find_element(By.ID, "invoice-list")
        self.assertIn("Couldn't match any invoice.", path.text)

    @tag("erp_front_invoice_search_multiple")
    def test_sales_invoice_search_multiple_field(self):       
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_client_tax_number")

        path = self.driver.find_element(By.ID, "invoice-list")
        
        # Test multiple fields: 1) Type
        search_fill_field(self.driver, "id_type", "a ")
        invoice_list = search_wait_first_input(self.driver, path, "id_type", "a ", 4)
 
        self.assertIn("A", invoice_list[0].text)
        
        # 2) POS
        search_fill_field(self.driver, "id_pos", " 2")
        invoice_list = web_driver_wait_count(self.driver, path, 2, By.CLASS_NAME,
            "search-row")

        self.assertIn("00002", invoice_list[0].text)
        
        # Number
        search_fill_field(self.driver, "id_number", " 1 ")
        invoice_list = web_driver_wait_count(self.driver, path, 1, By.CLASS_NAME,
            "search-row")

        self.assertIn("00002-00000001", invoice_list[0].text)
        
        # Clear all fields
        for field_id in ["id_type", "id_pos", "id_number"]:
            search_clear_field(self.driver, field_id)
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(invoice_list[0])
        )

    @tag("erp_front_invoice_search_multiple")
    def test_sales_invoice_search_multiple_field_2(self): 
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_client_name")

        path = self.driver.find_element(By.ID, "invoice-list")

        # Client tax field
        search_fill_field(self.driver, "id_client_tax_number", "99999")
        invoice_list = search_wait_first_input(self.driver, path, "id_client_tax_number",
            "99999", 4)
        
        self.assertIn("99999999999", invoice_list[0].text)

        # Client name
        search_fill_field(self.driver, "id_client_name", "cLiEnT1 Srl")
        invoice_list = web_driver_wait_count(self.driver, path, 0, By.CLASS_NAME,
            "search-row")

        # No match
        path = self.driver.find_element(By.ID, "invoice-list")
        self.assertIn("Couldn't match any invoice.", path.text)

    @tag("erp_front_invoice_search_view")
    def test_sales_invoice_search_view(self):
        self.create_extra_invoices()
        url = f"{self.live_server_url}/erp/sales/invoices/search"
        self.driver.get(url)

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_year")

        path = self.driver.find_element(By.ID, "invoice-list")
        
        # Search invoice 1: 
        # collected
        load_new_collected_option(self.driver, "Collected")
        # type
        search_fill_field(self.driver, "id_type", "a ")
        invoice_list = search_wait_first_input(self.driver, path, "id_type", "a", 1)
        
        self.assertIn("A", invoice_list[0].text)
        
        # Click on edit button
        click_and_redirect(self.driver, By.CLASS_NAME, "view-button", url, path)
        self.assertEqual(self.driver.title, "Invoice A 00001-00000001")

    @tag("erp_front_invoice_search_edit")
    def test_sales_invoice_search_edit(self):
        self.create_extra_invoices()
        url = f"{self.live_server_url}/erp/sales/invoices/search"
        self.driver.get(url)

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_year")

        path = self.driver.find_element(By.ID, "invoice-list")
        
        # Search invoice 1: 
        # collected
        load_new_collected_option(self.driver, "All")
        # type
        search_fill_field(self.driver, "id_type", "a ")
        invoice_list = search_wait_first_input(self.driver, path, "id_type", "a", 5)
        
        self.assertIn("A", invoice_list[0].text)
   
        # pos
        search_fill_field(self.driver, "id_pos", "1")
        invoice_list = web_driver_wait_count(self.driver, path, 3, By.CLASS_NAME,
            "search-row")

        self.assertIn("00001", invoice_list[0].text)
        
        # Click on edit button
        click_and_redirect(self.driver, By.CLASS_NAME, "edit-button", url, path)
        self.assertEqual(self.driver.title, "Edit Invoice")
        
    @tag("erp_front_invoice_search_delete")
    def test_sales_invoice_search_delete(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_month")

        path = self.driver.find_element(By.ID, "invoice-list")

        # Search invoice A 00001-00000003
        # Collected
        load_new_collected_option(self.driver, "All")
        # Type
        search_fill_field(self.driver, "id_type", "a ")
        invoice_list = search_wait_first_input(self.driver, path, "id_type", "a ", 5)
        
        self.assertIn("A", invoice_list[0].text)
        
        # POS
        search_fill_field(self.driver, "id_pos", "1")
        invoice_list = web_driver_wait_count(self.driver, path, 3, By.CLASS_NAME,
            "search-row")
        self.assertIn("00001", invoice_list[0].text)
        
        # Click on delete button   
        path = self.driver.find_element(By.ID, "invoice-list")     
        delete_button = path.find_elements(By.CLASS_NAME, "delete-button")[1]
        self.driver.execute_script('arguments[0].click();', delete_button)
        # Accept emergent alert
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        # Wait for invoice list to disappear
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(path)
        )
        self.assertEqual(SaleInvoice.objects.all().count(), 9)

    @tag("erp_front_invoice_search_delete_conflict")
    def test_sales_invoice_search_delete_conflict(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_pos")

        path = self.driver.find_element(By.ID, "invoice-list")

        # Search invoice A 00001-00000001
        load_new_collected_option(self.driver, "All")
        # Type
        search_fill_field(self.driver, "id_type", " a")
        invoice_list = search_wait_first_input(self.driver, path, "id_type", " a", 5)       
        
        self.assertIn("A", invoice_list[0].text)
        
        # POS
        search_fill_field(self.driver, "id_pos", "1")
        invoice_list = web_driver_wait_count(self.driver, path, 3, By.CLASS_NAME,
            "search-row")
        self.assertIn("00001", invoice_list[0].text)

        # Number
        search_fill_field(self.driver, "id_number", "1")
        invoice_list = web_driver_wait_count(self.driver, path, 1, By.CLASS_NAME,
            "search-row")
        self.assertNotIn("00001-00000002", invoice_list[0].text)
        
        # Click on delete button
        # Accept emergent alert
        click_button_and_answer_alert(self.driver, By.CLASS_NAME, "search-row", 
            "accept", 2)
        # Wait for popup to appear and reject
        view_and_answer_popup(self.driver, "The invoice couldn't be deleted", 1)

        # Delete again     
        # Accept emergent alert
        click_button_and_answer_alert(self.driver, By.CLASS_NAME, "search-row",
            "accept", 2)
        # Accept pop up
        view_and_answer_popup(self.driver, "The invoice couldn't be deleted")
        webDriverWait_visible_element(self.driver, By.ID, "rr-title")

        self.assertEqual(self.driver.title, "Related Receipts")
        self.assertEqual(SaleInvoice.objects.all().count(), 10)


    @tag("erp_front_invoice_search_delete_multiple")
    def test_sales_invoice_search_delete_multiple(self):
        self.create_extra_invoices()
        url = f"{self.live_server_url}/erp/sales/invoices/search"
        self.driver.get(url)

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_month")

        path = self.driver.find_element(By.ID, "invoice-list")

        # Show all uncollected invoices
        search_fill_field(self.driver, "id_type", " ")
        invoice_list = search_wait_first_input(self.driver, path, "id_type", " ", 9)
        self.assertIn("00002-00000001", invoice_list[1].text) # Inv B
        self.assertIn("00002-00000001", invoice_list[3].text) # Inv A
        self.assertIn("00001-00000002", invoice_list[5].text) # Inv B

        # Click on 3 checkboxes
        checkboxes = self.driver.find_elements(By.CLASS_NAME, "checkbox")
        # Move to element to avoid MoveTargetOutOfBoundsException
        scroll_page(self.driver, "0.5") # Time needed to selenium to scroll
        for index in [1, 3, 5]:
            checkboxes[index].click()
   
        # Click on delete button and reject alert  
        click_button_and_answer_alert(self.driver, By.ID, "delete-all", 
            "dismiss")
        # Repeat and accept alert
        click_button_and_answer_alert(self.driver, By.ID, "delete-all", 
            "accept")
        
        # Check popup appears and wait for receipt list to disappear
        webDriverWait_visible_element(self.driver, By.CLASS_NAME, "popup")
        WebDriverWait(self.driver, 10).until(
            EC.url_changes(url)
        )
        
        self.assertEqual(SaleInvoice.objects.all().count(), 7)

        # Check invoices are not there anymore
        overview = self.driver.find_element(By.TAG_NAME, "main")
        for invoice in ["B 00002-00000001", "A 00002-00000001", "B 00001-00000002"]:
            self.assertNotIn(invoice, overview.text) 

    @tag("erp_front_invoice_search_delete_multiple")
    def test_sales_invoice_search_delete_multiple_conflict(self):
        self.create_extra_invoices()
        url = f"{self.live_server_url}/erp/sales/invoices/search"
        self.driver.get(url)

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_month")

        path = self.driver.find_element(By.ID, "invoice-list")

        # Show all invoices
        load_new_collected_option(self.driver, "All")
        search_fill_field(self.driver, "id_type", " ")
        search_wait_first_input(self.driver, path, "id_type", " ", 10)

        # Click on 3 checkboxes
        scroll_page(self.driver)
        checkboxes = self.driver.find_elements(By.CLASS_NAME, "checkbox")
        for index in range(-3, 0):
            checkboxes[index].click()
        
        # Click on delete button and accept alert
        click_button_and_answer_alert(self.driver, By.ID, "delete-all", 
            "accept")
        
        # Wait and accept popup 
        view_and_answer_popup(self.driver, "The selected invoices couldn't be deleted")
        self.assertEqual(SaleInvoice.objects.all().count(), 10)


    @tag("erp_front_invoice_edit")
    def test_sales_invoice_edit(self):
        # Go to invoice 2 webpage.
        self.create_extra_invoices()
        url = f"{self.live_server_url}/erp/sales/invoices/{self.sale_invoice2.pk}"
        self.driver.get(url)
        self.assertEqual(self.driver.title, "Invoice B 00001-00000001")

        # Click on edit button
        click_and_redirect(self.driver, By.ID, "edit-button", url)
        self.assertEqual(self.driver.title, "Edit Invoice")

        # Add line
        new_line_button = self.driver.find_element(By.ID, "new-line")
        # Regular click doesn't work, I use JS click
        self.driver.execute_script("arguments[0].click();", new_line_button)
        # There are 2 lines, so there should be a third one
        webDriverWait_visible_element(
            self.driver, By.ID, "id_s_invoice_lines-1-description"
        )

        # Go back to invoice detail
        url = f"{url}/edit"
        go_to_link(self.driver, By.ID, "invoice-link", url)
        self.assertEqual(self.driver.title, "Invoice B 00001-00000001")

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
        self.assertEqual(self.driver.title, "Invoice A 00002-00000001")

        # Click on delete button
        self.driver.find_element(By.ID, "delete-button").click()
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        
        # Wait 
        WebDriverWait(self.driver, 10).until(
            EC.url_changes(f"{self.live_server_url}/erp/sales/invoices/{self.sale_invoice7.pk}")
        )
        self.assertEqual(self.driver.title, "Sales")

    @tag("erp_front_invoice_delete")
    def test_sales_invoice_delete_conflict(self):
        # Go to invoice 1 webpage.
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/{self.sale_invoice1.pk}")
        self.assertEqual(self.driver.title, "Invoice A 00001-00000001")

        # Click on delete button
        click_button_and_answer_alert(self.driver, By.CLASS_NAME, "container", 
            "accept")

        # Wait for and cancel pop up
        view_and_answer_popup(self.driver, "The invoice couldn't be deleted", 1)

        #  Delete again 
        click_button_and_answer_alert(self.driver, By.CLASS_NAME, "container", 
            "accept")
    
        # Wait for popup to appear and accept
        view_and_answer_popup(self.driver, "The invoice couldn't be deleted")
        webDriverWait_visible_element(self.driver, By.ID, "rr-title")

        self.assertEqual(self.driver.title, "Related Receipts")
        self.assertEqual(SaleInvoice.objects.all().count(), 1)

    @tag("erp_front_invoice_rel_receipts_link")
    def test_sales_invoice_rel_receipts_links_invoice(self):
        # Go to invoice 1 rel receipts webpage.
        url = f"{self.live_server_url}/erp/sales/invoices/{self.sale_invoice1.pk}"
        url += f"/related_receipts"
        self.driver.get(url)
        self.assertEqual(self.driver.title, "Related Receipts")

        # Check invoice link
        go_to_link(self.driver, By.CLASS_NAME, "container", url, 0)
        self.assertEqual(self.driver.title, "Invoice A 00001-00000001")

    @tag("erp_front_invoice_rel_receipts_link")
    def test_sales_invoice_rel_receipts_links_receipt(self):
        # Go to invoice 1 rel receipts webpage.
        url = f"{self.live_server_url}/erp/sales/invoices/{self.sale_invoice1.pk}"
        url += f"/related_receipts"
        self.driver.get(url)
        self.assertEqual(self.driver.title, "Related Receipts")

        # Check receipt link
        go_to_link(self.driver, By.CLASS_NAME, "container", url, 1)
        self.assertEqual(self.driver.title, "Receipt 00001-00000001")

    @tag("erp_front_show_list_tabs")
    def test_sales_show_list_tabs(self):
        # Go to show list page
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/list")

        # Click on year tab
        self.driver.find_element(By.ID, "year-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "id_year")
      
        # Click on date tab
        self.driver.find_element(By.ID, "date-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "id_date_from")


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
        self.assertEqual(number.text, "00000002")

        third_row = rows[2]
        date, type, pos, number = get_columns_data(third_row, end=4)
        self.assertEqual(date.text, "25/01/2024")
        self.assertEqual(type.text, "001 | A")
        self.assertEqual(pos.text, "00002")
        self.assertEqual(number.text, "00000002")

        last_row = rows[-1]
        date, type, pos, number = get_columns_data(last_row, end=4)
        self.assertEqual(date.text, "21/01/2024")
        self.assertEqual(type.text, "001 | A")
        self.assertEqual(pos.text, "00001")
        self.assertEqual(number.text, "00000001")
        
    @tag("erp_front_show_list_date")
    def test_sales_show_list_date_reverse_order(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/list")

        # Test date reverse sort
        headers = self.driver.find_elements(By.TAG_NAME, "th")
        headers[0].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.005)

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
        self.assertEqual(number.text, "00000003")

        last_row = rows[-1]
        date, type, pos, number = get_columns_data(last_row, end=4)
        self.assertEqual(date.text, "26/01/2024")
        self.assertEqual(type.text, "002 | B")
        self.assertEqual(pos.text, "00002")
        self.assertEqual(number.text, "00000001")

    @tag("erp_front_show_list_type")
    def test_sales_show_list_type_order(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/list")

        # Test type asc sort
        headers = self.driver.find_elements(By.TAG_NAME, "th")
        headers[1].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.005)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        i_type = first_row.find_elements(By.TAG_NAME, "td")[1]
        point_of_sell = first_row.find_elements(By.TAG_NAME, "td")[2]
        pay_term = first_row.find_elements(By.TAG_NAME, "td")[7]
        self.assertEqual(i_type.text, "001 | A")
        self.assertEqual(point_of_sell.text, "00002")
        self.assertEqual(pay_term.text, "0 days")
        
        last_row = rows[-1]
        i_type = last_row.find_elements(By.TAG_NAME, "td")[1]
        point_of_sell = last_row.find_elements(By.TAG_NAME, "td")[2]
        pay_term = last_row.find_elements(By.TAG_NAME, "td")[7]
        self.assertEqual(i_type.text, "002 | B")
        self.assertEqual(point_of_sell.text, "00001")
        self.assertEqual(pay_term.text, "30 days")

        # Test client name desc sort
        headers[1].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.005)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        i_type = first_row.find_elements(By.TAG_NAME, "td")[1]
        point_of_sell = first_row.find_elements(By.TAG_NAME, "td")[2]
        pay_term = first_row.find_elements(By.TAG_NAME, "td")[7]
        self.assertEqual(i_type.text, "002 | B")
        self.assertEqual(point_of_sell.text, "00002")
        self.assertEqual(pay_term.text, "0 days")
        
        last_row = rows[-1]
        i_type = last_row.find_elements(By.TAG_NAME, "td")[1]
        point_of_sell = last_row.find_elements(By.TAG_NAME, "td")[2]
        pay_term = last_row.find_elements(By.TAG_NAME, "td")[7]
        self.assertEqual(i_type.text, "001 | A")
        self.assertEqual(point_of_sell.text, "00001")
        self.assertEqual(pay_term.text, "0 days")
    
    @tag("erp_front_show_list_client_name")
    def test_sales_show_list_client_name_order(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/list")

        # Test client name asc sort
        headers = self.driver.find_elements(By.TAG_NAME, "th")
        headers[5].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.005)

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
        time.sleep(0.005)

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
        headers[-2].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.005)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        client_name = first_row.find_elements(By.TAG_NAME, "td")[5]
        total_amount = first_row.find_elements(By.TAG_NAME, "td")[-2]
        self.assertEqual(client_name.text, "CLIENT1 SRL")
        self.assertEqual(total_amount.text, "$ 9.00")

        last_row = rows[-1]
        client_name = last_row.find_elements(By.TAG_NAME, "td")[5]
        total_amount = last_row.find_elements(By.TAG_NAME, "td")[-2]
        self.assertEqual(client_name.text, "CLIENT1 SRL")
        self.assertEqual(total_amount.text, "$ 2509.01")

        # Test total amount desc sort
        headers[-2].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.005)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        number = first_row.find_elements(By.TAG_NAME, "td")[3]
        total_amount = first_row.find_elements(By.TAG_NAME, "td")[-2]
        self.assertEqual(number.text, "00000001")
        self.assertEqual(total_amount.text, "$ 2509.01")

        last_row = rows[-1]
        number = last_row.find_elements(By.TAG_NAME, "td")[3]
        total_amount = last_row.find_elements(By.TAG_NAME, "td")[-2]
        self.assertEqual(number.text, "00000002")
        self.assertEqual(total_amount.text, "$ 9.00")

    @tag("erp_front_show_list_collected")
    def test_sales_show_list_collected(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/sales/invoices/list")

        # Test collected asc sort
        headers = self.driver.find_elements(By.TAG_NAME, "th")
        headers[-1].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.005)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        collected = first_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(collected.text, "No")

        last_row = rows[-1]
        collected = last_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(collected.text, "Yes")

        # Test client name desc sort
        headers[-1].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.005)

        rows = self.driver.find_elements(By.CLASS_NAME, "invoice")
        first_row = rows[0]
        collected = first_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(collected.text, "Yes")

        last_row = rows[-1]
        collected = last_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(collected.text, "No")

    @tag("erp_front_receipt_new")
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

    @tag("erp_front_receipt_new")
    def test_receivables_new_receipt_recipient(self):
        self.create_extra_invoices()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/new")

        # Check recipient field is empty
        recipient_field = self.driver.find_element(By.ID, "id_recipient")
        self.assertEqual(recipient_field.get_attribute('value'), "")
                
        # Pick related invoice and check recipient field changes
        pick_option_by_index(self.driver, "id_related_invoice",
            1, "B 00002-00000002")

        self.assertEqual(recipient_field.get_attribute('value'), str(self.c_client2.pk))

        # Pick another rel invoice and check recipient field changes again
        pick_option_by_index(self.driver, "id_related_invoice", 3, 
            "A 00002-00000002")
                
        self.assertEqual(recipient_field.get_attribute("value"), str(self.c_client1.pk))

    @tag("erp_front_receipt_new")
    def test_receivables_new_receipt_collected_ri(self):
        # Go to Receivables new receipt page.
        self.create_extra_invoices()
        url = f"{self.live_server_url}/erp/receivables/receipts/new"
        self.driver.get(url)

        ri_field = self.driver.find_element(By.ID, "id_related_invoice")
        options = ri_field.find_elements(By.TAG_NAME, "option")
        # 9 uncollected invoices + empty option[0]
        self.assertEqual(len(options), 10)
        
        # Click on "Include collected invoice"
        checkbox = self.driver.find_element(By.ID, "id-collected")
        checkbox.click()
        # 8 uncollected invoices + empty option[0] + 1 collected inv
        web_driver_wait_count(self.driver, ri_field, 11, By.TAG_NAME, "option")
        
        self.assertTrue(checkbox.is_selected())

        # Check collected invoice content
        collected_invs = self.driver.find_elements(By.CLASS_NAME, "collected-inv")
        self.assertEqual(collected_invs[0].text, "A 00001-00000001")

        # Click again and see if collected invs were removed
        checkbox.click()
        web_driver_wait_count(self.driver, ri_field, 10, By.TAG_NAME, "option")
        
        self.assertFalse(checkbox.is_selected())

    def test_receivables_new_receipt_link_pos(self):
        # Go to Receivables new receipt page.
        url = f"{self.live_server_url}/erp/receivables/receipts/new"
        self.driver.get(url)

        # Click on Go to type link
        go_to_link(self.driver, By.ID, "receipt-form", url)
        self.assertEqual(self.driver.title, "Points of Sell")
    
    @tag("erp_front_receipt_search")
    def test_receivables_receipt_search_one_field_part_1(self):
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")
      
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_related_invoice", 3)

        path = self.driver.find_element(By.ID, "receipt-list")

        # Search related invoice.
        search_fill_field(self.driver, "id_related_invoice", "3")
        receipt_list = search_wait_first_input(self.driver, path, "id_related_invoice",
            "3", 1)

        self.assertIn("00001-00000004", receipt_list[0].text)

        search_clear_field(self.driver, "id_related_invoice", receipt_list[0])
        
        # Search Pos
        search_fill_field(self.driver, "id_pos", " 2")
        receipt_list = web_driver_wait_count(self.driver, path, 2, By.CLASS_NAME,
            "search-row")

        self.assertIn("00002", receipt_list[0].text)
        
        search_clear_field(self.driver, "id_pos", receipt_list[0])     
        
      
    @tag("erp_front_receipt_search_2")
    def test_receivables_receipt_search_one_field_part_2(self):
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")
        
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_pos")

        path = self.driver.find_element(By.ID, "receipt-list")
        
        # Test Number
        search_fill_field(self.driver, "id_number", "1 ")
        receipt_list = search_wait_first_input(self.driver, path, "id_number", "1 ",
            2)
     
        self.assertIn("00002-00000001", receipt_list[0].text)

        search_clear_field(self.driver, "id_number", receipt_list[0])

        # Test Client tax number
        search_fill_field(self.driver, "id_client_tax_number", "13 ")
        receipt_list = web_driver_wait_count(self.driver, path, 5, By.CLASS_NAME,
            "search-row")
        
        self.assertIn("20361382481", receipt_list[0].text)
        
        search_clear_field(self.driver, "id_client_tax_number", receipt_list[0])
        
        # Test Client name
        search_fill_field(self.driver, "id_client_name", "cLiEnT2 SA")
        receipt_list = web_driver_wait_count(self.driver, path, 1, By.CLASS_NAME,
            "search-row")
        
        self.assertIn("99999999999", receipt_list[0].text)

    @tag("erp_front_receipt_search_3")
    def test_receivables_receipt_search_one_field_part_3(self):
        self.create_extra_receipts()
        # Go to Sales search receipt page.
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")
    
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_number")
        
        path = self.driver.find_element(By.ID, "receipt-list")

        # Search Year
        search_fill_field(self.driver, "id_year", "20")
        receipt_list = search_wait_first_input(self.driver, path, "id_year", "20", 6)
      
        self.assertIn("2024", receipt_list[0].text)
        
        search_clear_field(self.driver, "id_year", receipt_list[0])
        
        # Search month
        search_fill_field(self.driver, "id_month", "13")
        receipt_list = web_driver_wait_count(self.driver, path, 0, By.CLASS_NAME,
            "search-row")

        path = self.driver.find_element(By.ID, "receipt-list")
        self.assertIn("Couldn't match any receipt.", path.text)

    @tag("erp_front_receipt_search_multiple")
    def test_receivables_receipt_search_multiple_field(self): 
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")
        
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_client_tax_number")

        path = self.driver.find_element(By.ID, "receipt-list")

        # Search multiple fields
        # Related Invoice
        search_fill_field(self.driver, "id_related_invoice", "1 ")
        receipt_list = search_wait_first_input(self.driver, path, "id_related_invoice",
            "1 ", 6)

        self.assertIn("00001", receipt_list[0].text)
        
        # POS
        search_fill_field(self.driver, "id_pos", " 1")
        receipt_list = web_driver_wait_count(self.driver, path, 4,By.CLASS_NAME,
            "search-row")
        
        # Number
        search_fill_field(self.driver, "id_number", "2 ")
        receipt_list = web_driver_wait_count(self.driver, path, 1, By.CLASS_NAME,
            "search-row")

        self.assertIn("00001-00000002", receipt_list[0].text)
        
        # Clear all fields
        for field_id in ["id_related_invoice", "id_pos", "id_number"]:
            search_clear_field(self.driver, field_id)
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(receipt_list[0])
        )

    @tag("erp_front_receipt_search_multiple_2")
    def test_receivables_receipt_search_multiple_field_2(self): 
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")
        
        # Click to load invoices in js.
        click_and_wait(self.driver, "id_client_name")

        path = self.driver.find_element(By.ID, "receipt-list")
        
        # Client tax field
        search_fill_field(self.driver, "id_client_tax_number", "99999")
        receipt_list = search_wait_first_input(self.driver, path, 
            "id_client_tax_number", "99999", 1)

        self.assertIn("CLIENT2 SA", receipt_list[0].text)
        
        # Client name
        search_fill_field(self.driver, "id_client_name", "cLiEnT1 SA")
        receipt_list = web_driver_wait_count(self.driver, path, 0, By.CLASS_NAME,
            "search-row")
        
        path = self.driver.find_element(By.ID, "receipt-list")
        self.assertIn("Couldn't match any receipt.", path.text)

    @tag("erp_front_receipt_search_view")
    def test_receivables_receipt_search_view(self):
        self.create_extra_receipts()
        url = f"{self.live_server_url}/erp/receivables/receipts/search"
        self.driver.get(url)

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_year")

        path = self.driver.find_element(By.ID, "receipt-list")
        
        # Search invoice 1: 
        # related invoice
        search_fill_field(self.driver, "id_related_invoice", "3 ")
        receipt_list = search_wait_first_input(self.driver, path, "id_related_invoice",
            "3", 1)
        
        self.assertIn("00001-00000004", receipt_list[0].text)
        
        # Click on edit button
        click_and_redirect(self.driver, By.CLASS_NAME, "view-button", url, path)
        self.assertEqual(self.driver.title, "Receipt 00001-00000004")

    @tag("erp_front_receipt_search_edit")
    def test_receivables_search_receipt_edit(self):
        self.create_extra_receipts()
        url = f"{self.live_server_url}/erp/receivables/receipts/search"
        self.driver.get(url)

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_year")

        path = self.driver.find_element(By.ID, "receipt-list")

        # Search receipt 1
        # search related invoice
        search_fill_field(self.driver, "id_related_invoice", "3 ")
        receipt_list = search_wait_first_input(self.driver, path, "id_related_invoice",
            "3 ", 1)
        
        self.assertIn("00001-00000004", receipt_list[0].text)        

        # Click on edit button
        click_and_redirect(self.driver, By.CLASS_NAME, "edit-button", url)
        self.assertEqual(self.driver.title, "Edit Receipt") 

    @tag("erp_front_receipt_search_delete")
    def test_receivables_search_receipt_delete(self):
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/search")

        # Click to load invoices in js.
        click_and_wait(self.driver, "id_month")

        path = self.driver.find_element(By.ID, "receipt-list")
        
        # Search receipt 00001-00000002
        # Related invoice
        search_fill_field(self.driver, "id_related_invoice", "00001-00000001")
        receipt_list = search_wait_first_input(self.driver, path, "id_related_invoice",
            "00001-00000001", 3)
        
        self.assertIn("00001-00000001", receipt_list[0].text)
        
        # number
        search_fill_field(self.driver, "id_number", "2")
        receipt_list = web_driver_wait_count(self.driver, path, 1, By.CLASS_NAME,
            "search-row")
  
        # Click on delete button   
        delete_button = path.find_element(By.CLASS_NAME, "delete-button")
        self.driver.execute_script('arguments[0].click();', delete_button)
        # Accept emergent alert
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        # Wait for receipt list to disappear
        WebDriverWait(self.driver, 10).until(EC.staleness_of(path))
        
        self.assertEqual(SaleReceipt.objects.all().count(), 5)
        self.sale_invoice2.refresh_from_db()
        time.sleep(0.1)
        self.assertEqual(self.sale_invoice2.collected, False)

    @tag("erp_front_receipt_search_delete_multiple")
    def test_receivables_search_receipt_delete_multiple(self):
        self.create_extra_receipts()
        url = f"{self.live_server_url}/erp/receivables/receipts/search"
        self.driver.get(url)

        # Click to load receipts in js.
        click_and_wait(self.driver, "id_month")

        path = self.driver.find_element(By.ID, "receipt-list")

        # Show all receipts
        search_fill_field(self.driver, "id_related_invoice", " ")
        search_wait_first_input(self.driver, path, "id_related_invoice", " ", 6)

        # Click on all checkboxes
        checkboxes = self.driver.find_elements(By.CLASS_NAME, "checkbox")
        # Move to element to avoid MoveTargetOutOfBoundsException
        scroll_page(self.driver, "0.5")
        for index in range(6):
            checkboxes[index].click()
   
        # Click on delete button and reject alert  
        click_button_and_answer_alert(self.driver, By.ID, "delete-all", 
            "dismiss")
        # Repeat and accept alert
        click_button_and_answer_alert(self.driver, By.ID, "delete-all", 
            "accept")
        
        # Check popup appears and wait for receipt list to disappear
        view_and_answer_popup(self.driver, "receipts have been deleted", buttons=False)
        WebDriverWait(self.driver, 10).until(
            EC.url_changes(url)
        )
        
        self.assertEqual(SaleReceipt.objects.all().count(), 0)

        self.sale_invoice1.refresh_from_db()
        time.sleep(0.2) # 0.1 sometimes raise error
        self.assertEqual(self.sale_invoice1.collected, False)

        # Check invoices are not there anymore
        overview = self.driver.find_element(By.TAG_NAME, "main")
        self.assertIn("You haven't issued any receipt", overview.text) 

    @tag("erp_front_receipt_edit")
    def test_receivable_receipt_edit(self):
        # Go to receipt 1 webpage.
        url = f"{self.live_server_url}/erp/receivables/receipts/{self.sale_receipt1.pk}"
        self.driver.get(url)
        self.assertEqual(self.driver.title, "Receipt 00001-00000001")

        # Click on edit button
        click_and_redirect(self.driver, By.ID, "edit-button", url)
        self.assertEqual(self.driver.title, "Edit Receipt")

        # Go back to receipt detail
        url = f"{self.live_server_url}/erp/receivables/receipts/{self.sale_receipt1.pk}/edit"
        go_to_link(self.driver, By.ID, "receipt-link", url)
        self.assertEqual(self.driver.title, "Receipt 00001-00000001")

    @tag("erp_front_receipt_edit")
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

    @tag("erp_front_receipt_edit_ri")
    def test_receivables_receipt_edit_ri(self):
        self.create_extra_receipts()
    
        # Go to Sales new receipt page.
        self.driver.get(
            f"{self.live_server_url}/erp/receivables/receipts/{self.sale_receipt1.pk}/edit"
        )
       
        # Check number field is 1
        ri_field = self.driver.find_element(By.ID, "id_related_invoice")
        # Blank option + 8 uncollected invoices + edited invoice
        web_driver_wait_count(self.driver, ri_field, 10,By.TAG_NAME, "option")

        # Pick pos and check new number field
        checkbox = self.driver.find_element(By.ID, "id-collected")
        checkbox.click()

        # 8 uncollected invoices + empty option[0] + 1 collected inv
        web_driver_wait_count(self.driver, ri_field, 11, By.TAG_NAME, "option")
        self.assertTrue(checkbox.is_selected())

        # Check collected invoice content
        collected_invs = self.driver.find_elements(By.CLASS_NAME, "collected-inv")
        self.assertEqual(collected_invs[0].text, "B 00001-00000001")

        # Click again and see if collected invs were removed
        checkbox.click()
        web_driver_wait_count(self.driver, ri_field, 10, By.TAG_NAME, "option")
        
        self.assertFalse(checkbox.is_selected())

    @tag("erp_front_receipt_delete")
    def test_receivables_receipt_delete(self):
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
        WebDriverWait(self.driver, 10).until(
            EC.url_changes(f"{self.live_server_url}/erp/receivables/receipts/{self.sale_receipt1.pk}")
        )
        self.assertEqual(self.driver.title, "Receivables")
        
        # Check DB update
        self.assertEqual(SaleReceipt.objects.all().count(), 0)
        self.sale_invoice1.refresh_from_db()
        self.assertEqual(self.sale_invoice1.collected, False) 
        
    @tag("erp_front_receipt_show_list_tabs")
    def test_receivables_show_list_tabs(self):
        # Go to show list page
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/list")

        # Click on year tab
        self.driver.find_element(By.ID, "year-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "id_year")
        
        # Click on date tab
        self.driver.find_element(By.ID, "date-tab").click()
        webDriverWait_visible_element(self.driver, By.ID, "id_date_from")
    

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
        self.assertEqual(number.text, "00000001")

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
        time.sleep(0.005)

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
        self.assertEqual(number.text, "00000001")
   
    @tag("erp_front_receipt_show_list_related_invoice")
    def test_receivables_show_list_related_invoice_order(self):
        self.create_extra_receipts()
        self.driver.get(f"{self.live_server_url}/erp/receivables/receipts/list")

        # Test related invoice asc sort
        headers = self.driver.find_elements(By.TAG_NAME, "th")
        headers[5].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.005)

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
        time.sleep(0.005)

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
        time.sleep(0.005)

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

        # Test total desc sort
        headers[-1].click()
        # Elements only change location, so I use time sleep
        time.sleep(0.005)

        rows = self.driver.find_elements(By.CLASS_NAME, "receipt")
        first_row = rows[0]
        number = first_row.find_elements(By.TAG_NAME, "td")[2]
        total_amount = first_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(number.text, "00000001")
        self.assertEqual(total_amount.text, "$ 2509.01")

        last_row = rows[-1]
        number = last_row.find_elements(By.TAG_NAME, "td")[2]
        total_amount = last_row.find_elements(By.TAG_NAME, "td")[-1]
        self.assertEqual(number.text, "00000001")
        self.assertEqual(total_amount.text, "$ 5.00")
  