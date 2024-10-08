"""Base classes for tests"""
import datetime
from django.test import TestCase
from django.urls import reverse

from company.models import Company, FinancialYear


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
            wrong_content = None):
        """
        Check that page responds correctly.
        Parameters: 
        - url: Url of page I want to check.
        - url_name: Name of url to connect through reverse. If it has kwargs,
        pass the dict as the second element of the list.
        - template: Name of template used.
        - Page content: Some text that should appear in the web page.
        - Wrong content: Optional. Text that should appear in the web page.
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

