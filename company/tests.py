import datetime
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Company, Calendar

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
            financial_year = "2024",
        )

        cls.calendar = Calendar.objects.create(
            starting_date = cls.company,
        )

    def test_company_model_content(self):
        self.assertEqual(self.company.tax_number, "20361382480")
        self.assertEqual(self.company.name, "Test Company SRL")
        self.assertEqual(self.company.address, "fake street 123, fakycity, Argentina")
        self.assertEqual(self.company.email, "testcompany@email.com")
        self.assertEqual(self.company.phone, "5493465406182")
        self.assertEqual(self.company.creation_date, datetime.date(1991, 3, 10))
        self.assertEqual(self.company.closing_date, datetime.date(2024, 6, 30))
        self.assertEqual(self.company.financial_year, "2024")
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
                financial_year = "2025",
            )

        # Test digit validator
        with self.assertRaises(
            ValidationError, 
            msg="1234abd must have only digits."
        ):
            self.company.tax_number = "1234abd"
            self.company.full_clean()

    def test_calendar_content(self):
        calendars = Calendar.objects.all()
        self.assertEqual(calendars.count(), 1)
        self.assertEqual(self.calendar.starting_date, self.company)
        self.assertEqual(
            str(self.calendar),
            f"From {self.company.creation_date} to {self.calendar.ending_date}."
        )