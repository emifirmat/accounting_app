"""Test for bookkeeping app"""
from django.test import TestCase
from django.db import IntegrityError

from .models import Chart_category, Chart_account, Entry


class BookkeepingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Populate DB"""
        cls.chart_assets = Chart_category.objects.create(
            code = "1",
            name = "Assets",
        )
        cls.chart_liabilities = Chart_category.objects.create(
            code = "02",
            name = "Liabilities",
        )
        
        cls.chart_account_current_assets = Chart_account.objects.create(
            code = "010000",
            name = "Current Assets",
            category = cls.chart_assets,
            allocable = False,
        )
        
        cls.chart_account_cash = Chart_account.objects.create(
            code = "010101",
            name = "Cash",
            category = cls.chart_assets,
            allocable = True,
        )

        cls.chart_account_supplier = Chart_account.objects.create(
            code = "010101",
            name = "Supplier1",
            category = cls.chart_liabilities,
            allocable = True,
        )

        cls.entry_line_1 = Entry.objects.create(
            number = "1",
            account = cls.chart_account_supplier,
            description = "Payment to a supplier",
            debit = "9999.99",
            credit = "0",
            last_line = False,
        )

        cls.entry_line_2 = Entry.objects.create(
            number = "1",
            account = cls.chart_account_cash,
            description = "Payment to a supplier",
            debit = "0",
            credit = "9999.99",
            last_line = True,  
        )
    
    def test_chart_category_model_content(self):
        chart_categories = Chart_category.objects.all()
        self.assertEqual(chart_categories.count(), 2)

        self.assertEqual(self.chart_assets.code, "01")
        self.assertEqual(self.chart_assets.name, "Assets")
        self.assertEqual(str(self.chart_assets), "01 Assets")
        self.assertEqual(self.chart_liabilities.code, "02")
        self.assertEqual(self.chart_liabilities.name, "Liabilities")
        self.assertEqual(str(self.chart_liabilities), "02 Liabilities")

    def test_chart_category_unique(self):
        with self.assertRaises(IntegrityError):
            Chart_category.objects.create(
                code = "02",
                name = "Equity",
            )

    def test_chart_account_model_content(self):
        chart_accounts = Chart_account.objects.all()
        self.assertEqual(chart_accounts.count(), 3)

        self.assertEqual(self.chart_account_current_assets.code, "010000")
        self.assertEqual(self.chart_account_current_assets.name, "Current Assets")
        self.assertEqual(self.chart_account_current_assets.category,
            self.chart_assets)
        self.assertEqual(self.chart_account_current_assets.allocable, False)
        self.assertEqual(str(self.chart_account_current_assets),
            "01010000 Current Assets")
        self.assertEqual(self.chart_account_cash.code, "010101")
        self.assertEqual(self.chart_account_cash.name, "Cash")
        self.assertEqual(self.chart_account_cash.category,
            self.chart_assets)
        self.assertEqual(self.chart_account_cash.allocable, True)
        self.assertEqual(str(self.chart_account_cash), "01010101 Cash") 

    def test_chart_account_unique(self):
        with self.assertRaises(IntegrityError):
            Chart_account.objects.create(
                code = "010101",
                name = "Bank",
                category = self.chart_assets,
                allocable = True,
            )

    def test_entry_content(self):
        entry = Entry.objects.all()
        self.assertEqual(entry.count(), 2)

        self.assertEqual(self.entry_line_1.number, "1")
        self.assertEqual(self.entry_line_1.account, self.chart_account_supplier)
        self.assertEqual(self.entry_line_1.description, "Payment to a supplier")
        self.assertEqual(self.entry_line_1.debit, "9999.99")
        self.assertEqual(self.entry_line_1.credit, "0")
        self.assertEqual(self.entry_line_1.last_line, False)
        self.assertEqual(self.entry_line_1.locked, False)
        self.assertEqual(str(self.entry_line_1), f"1 | {self.entry_line_1.date}")

        self.assertEqual(self.entry_line_2.number, "1")
        self.assertEqual(self.entry_line_2.account, self.chart_account_cash)
        self.assertEqual(self.entry_line_2.description, "Payment to a supplier")
        self.assertEqual(self.entry_line_2.debit, "0")
        self.assertEqual(self.entry_line_2.credit, "9999.99")
        self.assertEqual(self.entry_line_2.last_line, True)
        self.assertEqual(self.entry_line_2.locked, True)
        self.assertEqual(str(self.entry_line_2), f"1 | {self.entry_line_2.date}")

    def test_entry_new_valid_entry(self):
        self.entry_2_line_1 = Entry.objects.create(
            number = "2",
            account = self.chart_account_supplier,
            description = "Payment to another supplier",
            debit = "100",
            credit = "0",
            last_line = False,
        )

        self.entry_2_line_2 = Entry.objects.create(
            number = "2",
            account = self.chart_account_cash,
            description = "Payment to another supplier",
            debit = "0",
            credit = "100",
            last_line = True,  
        )
        entry = Entry.objects.all()
        self.assertEqual(entry.count(), 4)

    def test_entry_new_invalid_entry(self):
        self.entry_2_line_1 = Entry.objects.create(
            number = "2",
            account = self.chart_account_supplier,
            description = "Payment to another supplier",
            debit = "50",
            credit = "0",
            last_line = False,
        )

        with self.assertRaises(IntegrityError, msg="Debit must be equal to credit"):
            self.entry_2_line_2 = Entry.objects.create(
                number = "2",
                account = self.chart_account_cash,
                description = "Payment to another supplier",
                debit = "0",
                credit = "100",
                last_line = True,  
            )
        entry = Entry.objects.all()
        self.assertEqual(entry.count(), 2)
