"""
API tests for SmartLeakPro.
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


class APITestCase(TestCase):
    """Base test case for API tests."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='technician'
        )
        self.client.force_authenticate(user=self.user)


class AuthenticationAPITest(APITestCase):
    """Test authentication API endpoints."""
    
    def test_login_success(self):
        """Test successful login."""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_profile_access(self):
        """Test profile access for authenticated user."""
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')


class ClientAPITest(APITestCase):
    """Test client API endpoints."""
    
    def test_create_client(self):
        """Test creating a new client."""
        url = reverse('client-list')
        data = {
            'name': 'Test Client',
            'client_type': 'individual',
            'email': 'client@test.com',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'France'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(Client.objects.get().name, 'Test Client')
    
    def test_list_clients(self):
        """Test listing clients."""
        Client.objects.create(
            name='Test Client',
            client_type='individual',
            address='123 Test Street',
            city='Test City',
            postal_code='12345',
            country='France'
        )
        url = reverse('client-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_client_detail(self):
        """Test getting client details."""
        client = Client.objects.create(
            name='Test Client',
            client_type='individual',
            address='123 Test Street',
            city='Test City',
            postal_code='12345',
            country='France'
        )
        url = reverse('client-detail', kwargs={'pk': client.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Client')


class InterventionAPITest(APITestCase):
    """Test intervention API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(
            name='Test Client',
            client_type='individual',
            address='123 Test Street',
            city='Test City',
            postal_code='12345',
            country='France'
        )
    
    def test_create_intervention(self):
        """Test creating a new intervention."""
        url = reverse('intervention-list')
        data = {
            'title': 'Test Intervention',
            'description': 'Test description',
            'intervention_type': 'inspection',
            'priority': 'medium',
            'client': self.client_obj.pk,
            'scheduled_date': '2023-12-01T10:00:00Z'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Intervention.objects.count(), 1)
        self.assertEqual(Intervention.objects.get().title, 'Test Intervention')
    
    def test_list_interventions(self):
        """Test listing interventions."""
        Intervention.objects.create(
            title='Test Intervention',
            description='Test description',
            intervention_type='inspection',
            priority='medium',
            client=self.client_obj,
            scheduled_date='2023-12-01T10:00:00Z'
        )
        url = reverse('intervention-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class InspectionAPITest(APITestCase):
    """Test inspection API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(
            name='Test Client',
            client_type='individual',
            address='123 Test Street',
            city='Test City',
            postal_code='12345',
            country='France'
        )
    
    def test_create_inspection(self):
        """Test creating a new inspection."""
        url = reverse('inspection-list')
        data = {
            'title': 'Test Inspection',
            'description': 'Test description',
            'client': self.client_obj.pk,
            'inspection_date': '2023-12-01T10:00:00Z'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Inspection.objects.count(), 1)
        self.assertEqual(Inspection.objects.get().title, 'Test Inspection')
    
    def test_list_inspections(self):
        """Test listing inspections."""
        Inspection.objects.create(
            title='Test Inspection',
            description='Test description',
            client=self.client_obj,
            inspection_date='2023-12-01T10:00:00Z'
        )
        url = reverse('inspection-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
