import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase, tag
from django.urls import reverse

from .models import Company, FinancialYear
from utils.base_tests import BackBaseTest

# Create your tests here.
@tag("company_db_views")
class CompanyTestCase(BackBaseTest):

    def test_company_model_content(self):
        self.assertEqual(self.company.id, 1)
        self.assertEqual(self.company.tax_number, "20361382480")
        self.assertEqual(self.company.name, "TEST COMPANY SRL")
        self.assertEqual(self.company.address, "Fake Street 123, Fakycity, Argentina")
        self.assertEqual(self.company.email, "testcompany@email.com")
        self.assertEqual(self.company.phone, "5493465406182")
        self.assertEqual(self.company.creation_date, datetime.date(1991, 3, 10))
        self.assertEqual(self.company.closing_date, datetime.date(2024, 6, 30))
        self.assertEqual(str(self.company), "TEST COMPANY SRL | 20361382480")
    
    def test_company_constraints(self):
        # Check number of companies
        companies = Company.objects.all()
        self.assertEqual(companies.count(), 1)

        # Test singleton pattern
        with self.assertRaises(
            ValidationError,
            msg="An instance of Company already exits"
        ):
            company2 = Company.objects.create(
                tax_number = "20361382481",
                name = "Test Company 2 SRL",
                address = "fake street 345, fakycity, Argentina",
                email = "testcompany2@email.com",
                phone = "5493465406180",
                creation_date = datetime.date(1992, 3, 10),
                closing_date = datetime.date(2023, 6, 30),
            )

        # Test digit validator
        with self.assertRaises(
            ValidationError, 
            msg="1234abd must have only digits."
        ):
            self.company.tax_number = "1234abd"
            self.company.full_clean()

    def test_financialYear_model_content(self):
        # Check number of companies
        years = FinancialYear.objects.all()
        self.assertEqual(years.count(), 1)
        self.assertEqual(self.financial_year.year, "2024")
        self.assertEqual(str(self.financial_year), "2024")
        self.assertEqual(self.financial_year.current, True)

    def test_financialYear_model_new_instance(self):
        # Check number of companies
        new_year = FinancialYear.objects.create(year = "2025")
        years = FinancialYear.objects.all()
        self.assertEqual(years.count(), 2)
        self.assertEqual(new_year.year, "2025")
        self.assertEqual(new_year.current, False)

    def test_financialYear_model_constraint(self):
        with self.assertRaises(IntegrityError):
            FinancialYear.objects.create(year = "2025", current = True)

    """Web Pages"""
    def test_company_settings_webpage_get(self):
        self.check_page_get_response(
            "/company/settings",
            "company:settings",
            "company/settings.html",
            "20361382480"
        )
        
    def test_company_settings_webpage_get_no_company(self):
        self.company.delete()
        self.check_page_get_response(
            "/company/settings",
            "company:settings",
            "company/settings.html",
            wrong_content="20361382480" # Company doesn't exist
        )

    def test_company_settings_webpage_post_create(self):  
        # Create new company
        self.company.delete()
        post_object = {
            "tax_number": "20346936115",
            "name": "Other Test Company SRL",
            "address": "Other fake street 123, fakycity, Argentina",
            "email": "othertestcompany@email.com",
            "phone": "5493465406182",
            "creation_date": "15/09/2000",
            "closing_date": "31/12/2024",
        }
        
        self.check_page_post_response(
            "company:settings",post_object, 302, (Company, 1)
        )
 
        new_company = Company.objects.all().first()
        self.assertEqual(new_company.name, "OTHER TEST COMPANY SRL")
        self.assertNotEqual(new_company.tax_number, "20361382482")    

    def test_company_settings_webpage_post_edit(self):
        # Modify existing company
        post_object = {
            "tax_number": "20361382482",
            "name": "New Test Company SRL",
            "address": "fake street 123, fakycity, Argentina",
            "email": "testcompany@email.com",
            "phone": "5493465406182",
            "creation_date": "03/10/1991",
            "closing_date": "30/06/2024",
        }
        
        self.check_page_post_response(
            "company:settings",post_object, 302, (Company, 1)
        )
        
        company = Company.objects.all().first()
        self.assertEqual(company.tax_number, "20361382482")
        
    def test_company_settings_webpage_post_wrong_data(self):
        post_object = {
            "tax_number": "20a61382482",
            "name": "New Test Company SRL",
            "address": "fake street 123, fakycity, Argentina",
            "email": "testcompany@email.com",
            "phone": "5493465406182",
            "creation_date": "03/10/1991",
            "closing_date": "30/06/2024",
        }
        
        response = self.check_page_post_response(
            "company:settings",post_object, 200, (Company, 1)
        )

        self.assertContains(response, "20a61382482 must be only digits.")
        company = Company.objects.first()
        self.assertEqual(company.tax_number, "20361382480")

    def test_company_year_webpage_get(self):
        self.check_page_get_response(
            "/company/year",
            "company:year",
            "company/year.html",
            # A year already exists
            "Financial year" ,
            "Please, create and/or select a year",
        )
        
    def test_company_year_webpage_get_no_year(self):
        self.financial_year.delete()
        
        self.check_page_get_response(
            "/company/year",
            "company:year",
            "company/year.html",
            # Year doesn't exist
            "Please, create and/or select a year"
        )
        
    def test_company_year_webpage_post(self):
        self.financial_year.delete()
        
        # Add a year
        self.check_page_post_response(
            "company:year", {"year": "2025"}, 302, (FinancialYear, 1)
        )

        new_year = FinancialYear.objects.get(year="2025")
        self.assertEqual(new_year.year, "2025")
        self.assertEqual(new_year.current, True)
        
        # Add a second year
        self.check_page_post_response(
            "company:year", {"year": "2026"}, 302, (FinancialYear, 2)
        )
        
        second_year = FinancialYear.objects.get(year="2026")
        self.assertEqual(second_year.year, "2026")
        self.assertEqual(second_year.current, False)

    def test_company_year_wrong_year(self):
        response = self.check_page_post_response(
            "company:year", {"year": "1990"}, 200, (FinancialYear, 1)
        )

        self.assertContains(response, "1990 is older than 1991")

