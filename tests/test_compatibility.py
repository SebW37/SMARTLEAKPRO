"""
Compatibility tests for SmartLeakPro.
"""
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.clients.models import Client
from apps.interventions.models import Intervention
from apps.inspections.models import Inspection
import json

User = get_user_model()


class CompatibilityTest(TestCase):
    """Test compatibility with different systems and configurations."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test users
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role='admin'
        )
        
        self.technician = User.objects.create_user(
            username='technician',
            email='technician@example.com',
            password='testpass123',
            role='technician'
        )
        
        # Create test data
        self.test_client = Client.objects.create(
            name='Test Client',
            client_type='individual',
            address='123 Test Street',
            city='Test City',
            postal_code='12345',
            country='France'
        )
        
        self.test_intervention = Intervention.objects.create(
            title='Test Intervention',
            description='Test description',
            intervention_type='inspection',
            priority='medium',
            client=self.test_client,
            scheduled_date='2023-12-01T10:00:00Z'
        )
        
        self.test_inspection = Inspection.objects.create(
            title='Test Inspection',
            description='Test description',
            client=self.test_client,
            inspection_date='2023-12-01T10:00:00Z'
        )
    
    def test_json_compatibility(self):
        """Test JSON serialization/deserialization compatibility."""
        self.client.force_authenticate(user=self.technician)
        
        # Test client data serialization
        response = self.client.get(reverse('client-detail', kwargs={'pk': self.test_client.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify JSON structure
        data = response.json()
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('client_type', data)
        self.assertIn('address', data)
        self.assertIn('city', data)
        self.assertIn('postal_code', data)
        self.assertIn('country', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        
        # Test that data can be re-serialized
        json_string = json.dumps(data)
        parsed_data = json.loads(json_string)
        self.assertEqual(data, parsed_data)
    
    def test_datetime_compatibility(self):
        """Test datetime format compatibility."""
        self.client.force_authenticate(user=self.technician)
        
        # Test ISO 8601 datetime format
        data = {
            'title': 'Datetime Test Intervention',
            'description': 'Test description',
            'intervention_type': 'inspection',
            'priority': 'medium',
            'client': self.test_client.pk,
            'scheduled_date': '2023-12-01T10:00:00Z'
        }
        response = self.client.post(reverse('intervention-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify datetime format in response
        self.assertRegex(response.data['scheduled_date'], r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')
        
        # Test different datetime formats
        formats = [
            '2023-12-01T10:00:00Z',
            '2023-12-01T10:00:00+00:00',
            '2023-12-01T10:00:00.000Z',
            '2023-12-01 10:00:00'
        ]
        
        for dt_format in formats:
            data['scheduled_date'] = dt_format
            response = self.client.post(reverse('intervention-list'), data)
            # Should either succeed or return a validation error
            self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_unicode_compatibility(self):
        """Test Unicode character compatibility."""
        self.client.force_authenticate(user=self.technician)
        
        # Test Unicode characters in client data
        unicode_data = {
            'name': 'Client avec caractères spéciaux: éàçùñ',
            'client_type': 'individual',
            'address': '123 Rue de la Paix, 75001 Paris',
            'city': 'Paris',
            'postal_code': '75001',
            'country': 'France'
        }
        response = self.client.post(reverse('client-list'), unicode_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify Unicode characters are preserved
        self.assertEqual(response.data['name'], 'Client avec caractères spéciaux: éàçùñ')
        self.assertEqual(response.data['address'], '123 Rue de la Paix, 75001 Paris')
        
        # Test emoji characters
        emoji_data = {
            'name': 'Client with emoji 🏠🔧',
            'client_type': 'individual',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'France'
        }
        response = self.client.post(reverse('client-list'), emoji_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Client with emoji 🏠🔧')
    
    def test_browser_compatibility(self):
        """Test browser compatibility headers."""
        self.client.force_authenticate(user=self.technician)
        
        # Test CORS headers
        response = self.client.options(reverse('client-list'))
        self.assertIn('Access-Control-Allow-Origin', response)
        self.assertIn('Access-Control-Allow-Methods', response)
        self.assertIn('Access-Control-Allow-Headers', response)
        
        # Test content type headers
        response = self.client.get(reverse('client-list'))
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Test cache headers
        self.assertIn('Cache-Control', response)
        self.assertIn('ETag', response)
    
    def test_mobile_compatibility(self):
        """Test mobile device compatibility."""
        self.client.force_authenticate(user=self.technician)
        
        # Test mobile user agent
        mobile_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        }
        
        response = self.client.get(reverse('client-list'), **mobile_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test tablet user agent
        tablet_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        }
        
        response = self.client.get(reverse('client-list'), **tablet_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_api_version_compatibility(self):
        """Test API version compatibility."""
        self.client.force_authenticate(user=self.technician)
        
        # Test different API versions
        versions = ['v1', 'v2', 'latest']
        
        for version in versions:
            # Test with version in URL
            response = self.client.get(f'/api/{version}/clients/')
            # Should either succeed or return 404 for non-existent versions
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
            
            # Test with version in header
            response = self.client.get(reverse('client-list'), HTTP_API_VERSION=version)
            # Should either succeed or ignore the header
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
    
    def test_database_compatibility(self):
        """Test database compatibility."""
        self.client.force_authenticate(user=self.technician)
        
        # Test different data types
        data_types = [
            {'name': 'String Test', 'client_type': 'individual'},
            {'name': 'Unicode Test', 'client_type': 'individual'},
            {'name': '123', 'client_type': 'individual'},  # Numeric string
            {'name': 'A' * 1000, 'client_type': 'individual'},  # Long string
        ]
        
        for data_type in data_types:
            client_data = {
                'name': data_type['name'],
                'client_type': data_type['client_type'],
                'address': '123 Test Street',
                'city': 'Test City',
                'postal_code': '12345',
                'country': 'France'
            }
            response = self.client.post(reverse('client-list'), client_data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_http_method_compatibility(self):
        """Test HTTP method compatibility."""
        self.client.force_authenticate(user=self.technician)
        
        # Test GET
        response = self.client.get(reverse('client-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test POST
        data = {
            'name': 'HTTP Test Client',
            'client_type': 'individual',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'France'
        }
        response = self.client.post(reverse('client-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test PUT
        data['name'] = 'Updated HTTP Test Client'
        response = self.client.put(
            reverse('client-detail', kwargs={'pk': self.test_client.pk}),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test PATCH
        patch_data = {'name': 'Patched HTTP Test Client'}
        response = self.client.patch(
            reverse('client-detail', kwargs={'pk': self.test_client.pk}),
            patch_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test DELETE
        client = Client.objects.create(
            name='To Delete Client',
            client_type='individual',
            address='123 Delete Street',
            city='Delete City',
            postal_code='12345',
            country='France'
        )
        response = self.client.delete(
            reverse('client-detail', kwargs={'pk': client.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_encoding_compatibility(self):
        """Test different encoding compatibility."""
        self.client.force_authenticate(user=self.technician)
        
        # Test UTF-8 encoding
        utf8_data = {
            'name': 'UTF-8 Test: éàçùñ',
            'client_type': 'individual',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'France'
        }
        response = self.client.post(reverse('client-list'), utf8_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test Latin-1 encoding
        latin1_data = {
            'name': 'Latin-1 Test: éàçùñ',
            'client_type': 'individual',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'France'
        }
        response = self.client.post(reverse('client-list'), latin1_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_content_type_compatibility(self):
        """Test different content type compatibility."""
        self.client.force_authenticate(user=self.technician)
        
        # Test application/json
        data = {
            'name': 'JSON Test Client',
            'client_type': 'individual',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'France'
        }
        response = self.client.post(
            reverse('client-list'),
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test application/x-www-form-urlencoded
        response = self.client.post(
            reverse('client-list'),
            data,
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test multipart/form-data
        response = self.client.post(
            reverse('client-list'),
            data,
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)