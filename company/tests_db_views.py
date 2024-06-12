import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .models import Company, Calendar, FinancialYear

# Create your tests here.
class CompanyTestCase(TestCase):
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

        cls.financial_year = FinancialYear.objects.create(
            year = "2024",
            current = True,
        )

        cls.calendar = Calendar.objects.create(
            starting_date = cls.company,
        )

    def test_company_model_content(self):
        self.assertEqual(self.company.id, 1)
        self.assertEqual(self.company.tax_number, "20361382480")
        self.assertEqual(self.company.name, "Test Company SRL")
        self.assertEqual(self.company.address, "fake street 123, fakycity, Argentina")
        self.assertEqual(self.company.email, "testcompany@email.com")
        self.assertEqual(self.company.phone, "5493465406182")
        self.assertEqual(self.company.creation_date, datetime.date(1991, 3, 10))
        self.assertEqual(self.company.closing_date, datetime.date(2024, 6, 30))
        self.assertEqual(str(self.company), "Test Company SRL | 20361382480")
    
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
    
    def test_calendar__model_content(self):
        calendars = Calendar.objects.all()
        self.assertEqual(calendars.count(), 1)
        self.assertEqual(self.calendar.starting_date, self.company)
        self.assertEqual(
            str(self.calendar),
            f"From {self.company.creation_date} to {self.calendar.ending_date}."
        )

    """Web Pages"""
    def test_company_settings_webpage_get(self):
        response = self.client.get("/company/settings")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "company/settings.html")
        # Company already exists
        self.assertContains(response, "20361382480")
        
        self.company.delete()
        response = self.client.get(reverse("company:settings"))
        # Company doesn't exist
        self.assertNotContains(response, "20361382480")

    def test_company_settings_webpage_post(self):
        # Modify existing company
        response = self.client.post(reverse("company:settings"), {
            "tax_number": "20361382482",
            "name": "New Test Company SRL",
            "address": "fake street 123, fakycity, Argentina",
            "email": "testcompany@email.com",
            "phone": "5493465406182",
            "creation_date": "03/10/1991",
            "closing_date": "30/06/2024",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Company.objects.all().count(), 1)
        company = Company.objects.all().first()
        self.assertEqual(company.tax_number, "20361382482")
        
        # Create new company
        self.company.delete()
        response = self.client.post(reverse("company:settings"), {
            "tax_number": "20346936115",
            "name": "Other Test Company SRL",
            "address": "Other fake street 123, fakycity, Argentina",
            "email": "othertestcompany@email.com",
            "phone": "5493465406182",
            "creation_date": "15/09/2000",
            "closing_date": "31/12/2024",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Company.objects.all().count(), 1)
        new_company = Company.objects.all().first()
        self.assertEqual(new_company.name, "Other Test Company SRL")
        self.assertNotEqual(new_company.tax_number, "20361382482")

    def test_company_settings_webpage_post_wrong_data(self):
        response = self.client.post(reverse("company:settings"), {
            "tax_number": "20a61382482",
            "name": "New Test Company SRL",
            "address": "fake street 123, fakycity, Argentina",
            "email": "testcompany@email.com",
            "phone": "5493465406182",
            "creation_date": "03/10/1991",
            "closing_date": "30/06/2024",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "20a61382482 must be only digits.")
        self.assertEqual(Company.objects.all().count(), 1)
        company = Company.objects.all().first()
        self.assertEqual(company.tax_number, "20361382480")

    def test_company_year_webpage_get(self):
        response = self.client.get("/company/year")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "company/year.html")
        # A year already exists
        self.assertContains(response, "Financial year")
        self.assertNotContains(response, "Please, create and/or select a year")
        
        self.financial_year.delete()
        response = self.client.get(reverse("company:year"))
        # Year doesn't exist
        self.assertContains(response, "Please, create and/or select a year")

    def test_company_year_webpage_post(self):
        self.financial_year.delete()
        
        # Add a year
        response = self.client.post(reverse("company:year"), {
            "year": "2025",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FinancialYear.objects.all().count(), 1)
        new_year = FinancialYear.objects.get(year="2025")
        self.assertEqual(new_year.year, "2025")
        self.assertEqual(new_year.current, True)
        # Add a second year
        response = self.client.post(reverse("company:year"), {
            "year": "2026",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FinancialYear.objects.all().count(), 2)
        second_year = FinancialYear.objects.get(year="2026")
        self.assertEqual(second_year.year, "2026")
        self.assertEqual(second_year.current, False)
