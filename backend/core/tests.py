"""
TODO: a test or two would be useful.
Up to you whether you want a unit test (meh, there's so little to unit test here)
or e2e test using rest_framework.test.APIClient (yeah).
"""
import json
import random
import logging
from django.test import TestCase
from core.models import OfficeSpace
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient

logger = logging.getLogger('django_test')

class OfficeSpaceTestCase(TestCase):
    def setUp(self):
        """Initialize the test Environment"""
        self.officeinfo = {'name': 'Central Tower',
                          'street': 'Street 1',
                          'city': 'Warsaw',
                          'zip_code': '12345',
                          'lat': '123',
                          'lng': '456',
                          'public': False}
        self.client = APIClient()
        
    def test_list_of_office(self):
        """Test the number of available record"""
        office_count = OfficeSpace.objects.count()
        response = self.client.get(reverse('office-spaces-list'))
        resp_json = json.loads(response.content.decode())
        print(resp_json)
        self.assertEqual(response.status_code, 200)
        #Validate against database.
        self.assertEqual(OfficeSpace.objects.count(), office_count)
        #validate against db.
        self.assertEqual(office_count, len(resp_json))

    def test_create_office(self):
        """Test the number of available record"""
        office_count = OfficeSpace.objects.count()
        response = self.client.post(reverse('office-spaces-list'),
                                    json.dumps(self.officeinfo), content_type='application/json')
        logger.info(response.json())
        self.assertEqual(response.status_code, 201)
        response = self.client.get(reverse('office-spaces-list'))
        resp_json = json.loads(response.content.decode())
        print(resp_json)
        self.assertEqual(response.status_code, 200)
        #Validate against database.
        self.assertEqual(OfficeSpace.objects.count(), office_count+1)
        #validate against db.
        self.assertEqual(office_count+1, len(resp_json))

    def test_details_office(self):
        """Test details of the record"""
        response = self.client.post(reverse('office-spaces-list'),
                                    json.dumps(self.officeinfo), content_type='application/json')
        office = OfficeSpace.objects.get(name='Central Tower')
        response = self.client.get(reverse('office-spaces-detail', args=[office.pk]))
        resp_json = response.json()
        print(resp_json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(8, len(resp_json))
        self.assertEqual(office.name, resp_json['name'])
