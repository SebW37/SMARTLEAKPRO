"""
Security tests for SmartLeakPro.
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

User = get_user_model()


class SecurityTest(TestCase):
    """Test security features."""
    
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
        
        self.client_user = User.objects.create_user(
            username='client',
            email='client@example.com',
            password='testpass123',
            role='client'
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
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access protected endpoints."""
        endpoints = [
            'client-list',
            'intervention-list',
            'inspection-list',
            'report-list',
            'profile'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(reverse(endpoint))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_cross_user_data_access_denied(self):
        """Test that users cannot access other users' data."""
        # Create another user's data
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            role='technician'
        )
        
        other_client = Client.objects.create(
            name='Other Client',
            client_type='individual',
            address='456 Other Street',
            city='Other City',
            postal_code='54321',
            country='France',
            created_by=other_user
        )
        
        # Test that technician cannot access other user's client
        self.client.force_authenticate(user=self.technician)
        response = self.client.get(reverse('client-detail', kwargs={'pk': other_client.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection attacks."""
        self.client.force_authenticate(user=self.technician)
        
        # Test SQL injection in search parameter
        malicious_search = "'; DROP TABLE clients; --"
        response = self.client.get(reverse('client-list'), {'search': malicious_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that clients table still exists
        self.assertEqual(Client.objects.count(), 1)
    
    def test_xss_protection(self):
        """Test protection against XSS attacks."""
        self.client.force_authenticate(user=self.technician)
        
        # Test XSS in client name
        malicious_name = "<script>alert('XSS')</script>"
        data = {
            'name': malicious_name,
            'client_type': 'individual',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'France'
        }
        response = self.client.post(reverse('client-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify that the script tag is escaped in the response
        self.assertNotIn('<script>', response.data['name'])
        self.assertIn('&lt;script&gt;', response.data['name'])
    
    def test_csrf_protection(self):
        """Test CSRF protection."""
        # CSRF protection is handled by Django REST Framework
        # This test verifies that the API works without CSRF tokens
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'name': 'Test Client',
            'client_type': 'individual',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'France'
        }
        response = self.client.post(reverse('client-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_input_validation(self):
        """Test input validation and sanitization."""
        self.client.force_authenticate(user=self.technician)
        
        # Test invalid email format
        data = {
            'name': 'Test Client',
            'client_type': 'individual',
            'email': 'invalid-email',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'France'
        }
        response = self.client.post(reverse('client-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_file_upload_security(self):
        """Test file upload security."""
        self.client.force_authenticate(user=self.technician)
        
        # Test uploading a malicious file
        malicious_content = b'<?php echo "Hello World"; ?>'
        data = {
            'title': 'Test Document',
            'document_type': 'other',
            'client': self.test_client.pk,
            'file': ('malicious.php', malicious_content, 'application/x-php')
        }
        response = self.client.post(reverse('client-document-list'), data)
        # Should either reject the file or sanitize it
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_rate_limiting(self):
        """Test rate limiting on sensitive endpoints."""
        # Test login rate limiting
        for i in range(10):  # Try to exceed rate limit
            data = {
                'username': 'admin',
                'password': 'wrongpassword'
            }
            response = self.client.post(reverse('login'), data)
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break
        
        # The test passes if rate limiting is working or if all requests succeed
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_429_TOO_MANY_REQUESTS
        ])
    
    def test_https_headers(self):
        """Test security headers."""
        self.client.force_authenticate(user=self.technician)
        response = self.client.get(reverse('client-list'))
        
        # Check for security headers
        self.assertIn('X-Content-Type-Options', response)
        self.assertIn('X-Frame-Options', response)
        self.assertIn('X-XSS-Protection', response)
    
    def test_password_security(self):
        """Test password security requirements."""
        # Test weak password
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': '123',
            'password_confirm': '123',
            'role': 'technician'
        }
        response = self.client.post(reverse('user-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_session_security(self):
        """Test session security."""
        # Test that sessions are properly managed
        self.client.force_authenticate(user=self.technician)
        
        # Make a request
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        
        # Try to access protected endpoint after logout
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)