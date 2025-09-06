"""
Regression tests for SmartLeakPro.
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
from apps.reports.models import Report
from apps.notifications.models import Notification

User = get_user_model()


class RegressionTest(TestCase):
    """Test for regression issues."""
    
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
    
    def test_client_creation_regression(self):
        """Test that client creation still works after changes."""
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'name': 'Regression Test Client',
            'client_type': 'individual',
            'address': '123 Regression Street',
            'city': 'Regression City',
            'postal_code': '12345',
            'country': 'France'
        }
        response = self.client.post(reverse('client-list'), data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Regression Test Client')
        self.assertEqual(response.data['client_type'], 'individual')
        self.assertEqual(response.data['address'], '123 Regression Street')
        self.assertEqual(response.data['city'], 'Regression City')
        self.assertEqual(response.data['postal_code'], '12345')
        self.assertEqual(response.data['country'], 'France')
    
    def test_client_update_regression(self):
        """Test that client update still works after changes."""
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'name': 'Updated Client',
            'client_type': 'company',
            'address': '456 Updated Street',
            'city': 'Updated City',
            'postal_code': '54321',
            'country': 'France'
        }
        response = self.client.put(
            reverse('client-detail', kwargs={'pk': self.test_client.pk}),
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Client')
        self.assertEqual(response.data['client_type'], 'company')
        self.assertEqual(response.data['address'], '456 Updated Street')
        self.assertEqual(response.data['city'], 'Updated City')
        self.assertEqual(response.data['postal_code'], '54321')
        self.assertEqual(response.data['country'], 'France')
    
    def test_client_deletion_regression(self):
        """Test that client deletion still works after changes."""
        self.client.force_authenticate(user=self.technician)
        
        # Create a client to delete
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
        self.assertFalse(Client.objects.filter(pk=client.pk).exists())
    
    def test_intervention_creation_regression(self):
        """Test that intervention creation still works after changes."""
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'title': 'Regression Test Intervention',
            'description': 'Regression test description',
            'intervention_type': 'inspection',
            'priority': 'high',
            'client': self.test_client.pk,
            'scheduled_date': '2023-12-01T10:00:00Z'
        }
        response = self.client.post(reverse('intervention-list'), data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Regression Test Intervention')
        self.assertEqual(response.data['description'], 'Regression test description')
        self.assertEqual(response.data['intervention_type'], 'inspection')
        self.assertEqual(response.data['priority'], 'high')
        self.assertEqual(response.data['client'], self.test_client.pk)
        self.assertEqual(response.data['scheduled_date'], '2023-12-01T10:00:00Z')
    
    def test_intervention_update_regression(self):
        """Test that intervention update still works after changes."""
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'title': 'Updated Intervention',
            'description': 'Updated description',
            'intervention_type': 'maintenance',
            'priority': 'low',
            'client': self.test_client.pk,
            'scheduled_date': '2023-12-02T10:00:00Z'
        }
        response = self.client.put(
            reverse('intervention-detail', kwargs={'pk': self.test_intervention.pk}),
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Intervention')
        self.assertEqual(response.data['description'], 'Updated description')
        self.assertEqual(response.data['intervention_type'], 'maintenance')
        self.assertEqual(response.data['priority'], 'low')
        self.assertEqual(response.data['client'], self.test_client.pk)
        self.assertEqual(response.data['scheduled_date'], '2023-12-02T10:00:00Z')
    
    def test_inspection_creation_regression(self):
        """Test that inspection creation still works after changes."""
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'title': 'Regression Test Inspection',
            'description': 'Regression test description',
            'client': self.test_client.pk,
            'inspection_date': '2023-12-01T10:00:00Z'
        }
        response = self.client.post(reverse('inspection-list'), data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Regression Test Inspection')
        self.assertEqual(response.data['description'], 'Regression test description')
        self.assertEqual(response.data['client'], self.test_client.pk)
        self.assertEqual(response.data['inspection_date'], '2023-12-01T10:00:00Z')
    
    def test_inspection_update_regression(self):
        """Test that inspection update still works after changes."""
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'title': 'Updated Inspection',
            'description': 'Updated description',
            'client': self.test_client.pk,
            'inspection_date': '2023-12-02T10:00:00Z'
        }
        response = self.client.put(
            reverse('inspection-detail', kwargs={'pk': self.test_inspection.pk}),
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Inspection')
        self.assertEqual(response.data['description'], 'Updated description')
        self.assertEqual(response.data['client'], self.test_client.pk)
        self.assertEqual(response.data['inspection_date'], '2023-12-02T10:00:00Z')
    
    def test_authentication_regression(self):
        """Test that authentication still works after changes."""
        # Test login
        data = {
            'username': 'technician',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('login'), data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Test logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
    
    def test_authorization_regression(self):
        """Test that authorization still works after changes."""
        # Test that technician can access their own data
        self.client.force_authenticate(user=self.technician)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test that unauthenticated user cannot access protected data
        self.client.logout()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_data_consistency_regression(self):
        """Test that data consistency is maintained after changes."""
        self.client.force_authenticate(user=self.technician)
        
        # Create a client
        client_data = {
            'name': 'Consistency Test Client',
            'client_type': 'individual',
            'address': '123 Consistency Street',
            'city': 'Consistency City',
            'postal_code': '12345',
            'country': 'France'
        }
        response = self.client.post(reverse('client-list'), client_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        client_id = response.data['id']
        
        # Create an intervention for this client
        intervention_data = {
            'title': 'Consistency Test Intervention',
            'description': 'Consistency test description',
            'intervention_type': 'inspection',
            'priority': 'medium',
            'client': client_id,
            'scheduled_date': '2023-12-01T10:00:00Z'
        }
        response = self.client.post(reverse('intervention-list'), intervention_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        intervention_id = response.data['id']
        
        # Create an inspection for this client
        inspection_data = {
            'title': 'Consistency Test Inspection',
            'description': 'Consistency test description',
            'client': client_id,
            'inspection_date': '2023-12-01T10:00:00Z'
        }
        response = self.client.post(reverse('inspection-list'), inspection_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        inspection_id = response.data['id']
        
        # Verify data consistency
        client = Client.objects.get(pk=client_id)
        intervention = Intervention.objects.get(pk=intervention_id)
        inspection = Inspection.objects.get(pk=inspection_id)
        
        self.assertEqual(intervention.client, client)
        self.assertEqual(inspection.client, client)
        self.assertEqual(client.interventions.count(), 1)
        self.assertEqual(client.inspections.count(), 1)
    
    def test_error_handling_regression(self):
        """Test that error handling still works after changes."""
        self.client.force_authenticate(user=self.technician)
        
        # Test invalid client creation
        invalid_data = {
            'name': '',  # Invalid: empty name
            'client_type': 'invalid_type',  # Invalid type
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'France'
        }
        response = self.client.post(reverse('client-list'), invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('client_type', response.data)
        
        # Test invalid intervention creation
        invalid_data = {
            'title': '',  # Invalid: empty title
            'description': 'Test description',
            'intervention_type': 'invalid_type',  # Invalid type
            'priority': 'invalid_priority',  # Invalid priority
            'client': 99999,  # Invalid: non-existent client
            'scheduled_date': 'invalid_date'  # Invalid date format
        }
        response = self.client.post(reverse('intervention-list'), invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('intervention_type', response.data)
        self.assertIn('priority', response.data)
        self.assertIn('client', response.data)
        self.assertIn('scheduled_date', response.data)
    
    def test_performance_regression(self):
        """Test that performance hasn't degraded after changes."""
        self.client.force_authenticate(user=self.technician)
        
        # Test response time for client list
        start_time = time.time()
        response = self.client.get(reverse('client-list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 1.0)  # Should respond within 1 second
        
        # Test response time for intervention list
        start_time = time.time()
        response = self.client.get(reverse('intervention-list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 1.0)  # Should respond within 1 second
        
        # Test response time for inspection list
        start_time = time.time()
        response = self.client.get(reverse('inspection-list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 1.0)  # Should respond within 1 second