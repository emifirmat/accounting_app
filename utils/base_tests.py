"""Base classes for tests"""
import datetime
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from company.models import Company, FinancialYear
from erp.models import (PaymentTerm, PaymentMethod, CompanyClient, Supplier,
    PointOfSell)


class CreateDbInstancesMixin:
    """Create additional instances from DB for testing"""
    def create_extra_pay_terms(self):
        """Create additional payment terms for testing."""
        PaymentTerm.objects.bulk_create([
            PaymentTerm(pay_term="60"),
            PaymentTerm(pay_term="90"),
            PaymentTerm(pay_term="180"),
        ])

    def create_extra_pay_methods(self):
        """Create additional payment methods for testing."""
        PaymentMethod.objects.bulk_create([
            PaymentMethod(pay_method="Debit Card"),
            PaymentMethod(pay_method="Check"),
        ])

    def create_extra_pos(self):
        """Create additional points of sell for testing."""
        PointOfSell.objects.bulk_create([  
            PointOfSell(pos_number="00003", disabled=True),
            PointOfSell(pos_number="00004")
        ])

    def create_company_clients(self):
        self.c_client3 = CompanyClient.objects.create(
            tax_number = "27451008780",
            name = "Client3 SA",
            address = "Client3 street, Client city, Argentina",
            email = "client3@gmail.com",
            phone = "0981114322",
        )
        self.c_client4 = CompanyClient.objects.create(
            tax_number = "27451008781",
            name = "Client4 SA",
            address = "Client4 street, Client city, Brazil",
            email = "client4@gmail.com",
            phone = "0987656663",
        )
        self.c_client5 = CompanyClient.objects.create(
            tax_number = "27451008782",
            name = "Client5 SRL",
            address = "Client5 street, Client city, USA",
            email = "client5@email.com",
            phone = "0333654324",
        )
        self.c_client6 = CompanyClient.objects.create(
            tax_number = "32546921",
            name = "Client6 SRL",
            address = "Client6 street, Client city, Peru",
            email = "client6@email.com",
            phone = "4487654325",
        )
        self.c_client7 = CompanyClient.objects.create(
            tax_number = "33546921",
            name = "Client7 SA",
            address = "Client7 street, Client city, China",
            email = "client7@gmail.com",
            phone = "1212654326",
        )
    
    def create_suppliers(self):
        self.supplier3 = Supplier.objects.create(
            tax_number = "78493261547",
            name = "Supplier3 SA",
            address = "Supplier3 street, Supplier, Argentina",
            email = "supplier3@gmail.com",
            phone = "4938201567",
        )
        self.supplier4 = Supplier.objects.create(
            tax_number = "23984715680",
            name = "Supplier4 SA",
            address = "Supplier4 street, Supplier city, Brazil",
            email = "supplier4@gmail.com",
            phone = "7029183456",
        )
        self.supplier5 = Supplier.objects.create(
            tax_number = "59102348762",
            name = "Supplier5 SRL",
            address = "Supplier5 street, Supplier city, USA",
            email = "supplier5@email.com",
            phone = "1837460928",
        )
        self.supplier6 = Supplier.objects.create(
            tax_number = "74639018254",
            name = "Supplier6 SRL",
            address = "Supplier6 street, Supplier city, Peru",
            email = "supplier6@email.com",
            phone = "9571304826",
        )
        self.supplier7 = Supplier.objects.create(
            tax_number = "83092147563",
            name = "Supplier3 SA",
            address = "Supplier7 street, Supplier city, China",
            email = "supplier7@gmail.com",
            phone = "3648190275",
        )


class BackBaseTest(TestCase):
    """Common Properties and functions for Backend tests"""
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

    def check_page_get_response(self, url, url_name, template, page_content=None, 
            wrong_content=None):
        """
        Check that page responds correctly.
        Parameters: 
        - url: Url of page I want to check.
        - url_name: Name of url to connect through reverse. If it has kwargs,
        pass the dict as the second element of the list.
        - template: Name of template used.
        - Page content: Optional. Rext that should appear in the web page.
        - Wrong content: Optional. Text that shouldn't appear in the web page.
        """
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)
        
        # If url_name is a list, it uses kwargs.
        if isinstance(url_name, list):
            response = self.client.get(reverse(url_name[0], kwargs=url_name[1]))
        else:
            response = self.client.get(reverse(url_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)

        if page_content:
            # Sometimes I do more than 1 assert contains
            if isinstance(page_content, str):
                page_content = [page_content]
            for text in page_content:
                self.assertContains(response, text)
        
        if wrong_content:
            self.assertNotContains(response, wrong_content)       
        
    def check_page_post_response(self, url_name, post_object, expected_status,
            model_result=None):
        """
        Check if server responds as expected after posting, and db update
        Parameters:
        - url_name: Name of the URL where I do the post. It should be a list if
        it has kwargs, being the second element a dict.
        - post_object: Dict. Object submitted in POST.
        - expected_status: Status I expect to receive in response.
        - model_result: Touple. First arg is name of model, second arg is the 
        number of instances I expect.

        Returns:
        - Form: Form from post with error messages.
        """
        # Get response with or w/o reverse kwargs.
        if isinstance(url_name, list):
            response = self.client.post(
                reverse(url_name[0], kwargs=url_name[1]), post_object
            )
        else:
            response = self.client.post(reverse(url_name), post_object)

        # check response status and model instances
        self.assertEqual(response.status_code, expected_status)
        if model_result:
            self.assertEqual(model_result[0].objects.all().count(), 
                model_result[1])

        # In case of error (status diff from 302), return information.
        if response.status_code == 200:
            return response

        elif response.status_code == 400:
            return response.content.decode("utf-8")


class APIBaseTest(APITestCase):
    """Common functions for API tests"""
    def check_api_get_response(self, url, url_name=None, page_content=None, 
            wrong_content=None, count=None):
        """
        Check that API responds correctly when using GET method.
        Parameters: 
        - url: Url of API page I want to check.
        - url_name: Optional. Name of url to connect through reverse. If it has 
        kwargs, pass the dict as the second element of the list.
        - Page content: Optional. Text that should appear in the API.
        - Wrong content: Optional. Text that shouldn't appear in the web page.
        - Count: optional. Expected instances' count in the api web page.
        """
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # If url_name is a list, it uses kwargs.
        if url_name:
            if isinstance(url_name, list):
                response = self.client.get(reverse(
                    url_name[0], kwargs=url_name[1]
                    ), format="json"
                )
            else:
                response = self.client.get(reverse(url_name))
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test content
        if page_content:
            # Sometimes I do more than 1 assert contains
            for text in page_content:
                self.assertContains(response, text)
        if wrong_content:
            self.assertNotContains(response, wrong_content)

        # Test instances' count in api webpage.
        if count:
            self.assertEqual(len(response.json()), count)

    def check_api_post_response(self, url_name, post_object, count):
        """
        Check that API responds correctly when using lists on POST method.
        Parameters: 
        - url_name: Name of url to connect through reverse.
        - post_object: List of model's objects I want to create.
        - count: Tuple with model and expected count.
        """
        response = self.client.post(reverse(url_name), post_object, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(count[0].objects.count(), count[1])

    def check_api_delete_response(self, url_name, status_code, count, 
        delete_object=None):
        """
        Check that API responds correctly when using DELETE method.
        Parameters: 
        - url_name: Name of url to connect through reverse. For kwargs,
        pass the dict as the second element of the list.
        - status_code: DRF status method. Expected status response.
        - count: Tuple with model and expected count.
        - delete_object: Default None. A dict with a list of id objects to delete.
        """
        if delete_object:
            response = self.client.delete(
                reverse(url_name[0]), data=delete_object, format="json"
            )
        else:
            response = self.client.delete(
                reverse(url_name[0], kwargs=url_name[1]), format="json"
            )
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(count[0].objects.count(), count[1])
  

        