"""Selenium tests for erp app"""
import datetime
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from company.models import Company
from .models import Company_client, Supplier


@tag("erp_front")
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

        self.driver.get(f"{self.live_server_url}")

    def test_client_edit(self):
        # Get to edit client page
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
        # Get to delete client page
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
        # Get to edit supplier page
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
        # Get to delete supplier page
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