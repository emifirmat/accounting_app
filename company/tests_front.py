"""Tests for company app"""
import datetime
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .models import Company, FinancialYear

class CompanyFrontTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        """Initiate selenium server"""
        super().setUpClass()
        cls.driver = WebDriver()
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        """Close selenium server"""
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        """Populate db and open index page"""
        self.company = Company.objects.create(
            tax_number = "20361382480",
            name = "Test Company SRL",
            address = "fake street 123, fakycity, Argentina",
            email = "testcompany@email.com",
            phone = "5493465406182",
            creation_date = datetime.date(1991, 3, 10),
            closing_date = datetime.date(2024, 6, 30),
        )
        self.f_year1 = FinancialYear.objects.create(year = "2023")
        self.f_year2 = FinancialYear.objects.create(year = "2024")
        
        self.driver.get(f"{self.live_server_url}")


    def test_company_settings_loads(self):
        self.assertEqual(self.driver.title, "Index")
        self.driver.find_element(By.ID, "company-menu-link").click()
        path = self.driver.find_element(By.ID, "company-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[0].click()
        self.assertEqual(self.driver.title, "Settings")

    def test_company_year_changeYear(self):
        # Test page loads
        self.driver.find_element(By.ID, "company-menu-link").click()
        path = self.driver.find_element(By.ID, "company-menu")
        path.find_elements(By.CLASS_NAME, "dropdown-item")[1].click()
        self.assertEqual(self.driver.title, "Financial Year")

        # Test there is no current year
        current_year = self.driver.find_element(By.ID, "current-year")
        self.assertEqual(current_year.text[-21:], "and/or select a year.")
        
        # Select new current year
        self.driver.find_element(By.ID, "year-dropdown").click()
        path = self.driver.find_element(By.ID, "change-year-menu")
        path.find_elements(By.CSS_SELECTOR, ".dropdown-item.year")[0].click()
        # Confirm that current year of 2023 is true. If it is false it will 
        # raise an error.
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "current-year"), "2023")
        )


