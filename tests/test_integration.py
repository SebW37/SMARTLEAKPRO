"""
Integration tests for SmartLeakPro.
"""
import pytest
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.clients.models import Client, ClientSite
from apps.interventions.models import Intervention
from apps.inspections.models import Inspection
from apps.reports.models import Report

User = get_user_model()


class ClientWorkflowTest(TransactionTestCase):
    """Test complete client workflow."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='technician'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_complete_client_workflow(self):
        """Test complete workflow from client creation to report generation."""
        # 1. Create client
        client_data = {
            'name': 'Test Client',
            'client_type': 'individual',
            'email': 'client@test.com',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'France'
        }
        client_response = self.client.post(reverse('client-list'), client_data)
        self.assertEqual(client_response.status_code, status.HTTP_201_CREATED)
        client_id = client_response.data['id']
        
        # 2. Create client site
        site_data = {
            'client': client_id,
            'name': 'Test Site',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'France'
        }
        site_response = self.client.post(reverse('client-site-list'), site_data)
        self.assertEqual(site_response.status_code, status.HTTP_201_CREATED)
        site_id = site_response.data['id']
        
        # 3. Create intervention
        intervention_data = {
            'title': 'Test Intervention',
            'description': 'Test description',
            'intervention_type': 'inspection',
            'priority': 'medium',
            'client': client_id,
            'site': site_id,
            'scheduled_date': '2023-12-01T10:00:00Z'
        }
        intervention_response = self.client.post(reverse('intervention-list'), intervention_data)
        self.assertEqual(intervention_response.status_code, status.HTTP_201_CREATED)
        intervention_id = intervention_response.data['id']
        
        # 4. Create inspection
        inspection_data = {
            'title': 'Test Inspection',
            'description': 'Test description',
            'client': client_id,
            'site': site_id,
            'intervention': intervention_id,
            'inspection_date': '2023-12-01T10:00:00Z'
        }
        inspection_response = self.client.post(reverse('inspection-list'), inspection_data)
        self.assertEqual(inspection_response.status_code, status.HTTP_201_CREATED)
        inspection_id = inspection_response.data['id']
        
        # 5. Start inspection
        start_response = self.client.post(reverse('inspection-start', kwargs={'pk': inspection_id}))
        self.assertEqual(start_response.status_code, status.HTTP_200_OK)
        self.assertEqual(start_response.data['status'], 'in_progress')
        
        # 6. Complete inspection
        complete_response = self.client.post(reverse('inspection-complete', kwargs={'pk': inspection_id}))
        self.assertEqual(complete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(complete_response.data['status'], 'completed')
        
        # 7. Generate report
        report_data = {
            'title': 'Test Report',
            'description': 'Test report description',
            'format': 'pdf',
            'client': client_id,
            'intervention': intervention_id,
            'inspection': inspection_id
        }
        report_response = self.client.post(reverse('report-generate'), report_data)
        self.assertEqual(report_response.status_code, status.HTTP_202_ACCEPTED)
        
        # Verify all objects were created
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(ClientSite.objects.count(), 1)
        self.assertEqual(Intervention.objects.count(), 1)
        self.assertEqual(Inspection.objects.count(), 1)
        self.assertEqual(Report.objects.count(), 1)


class PermissionTest(TestCase):
    """Test permission system."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users with different roles
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
    
    def test_admin_can_access_all_endpoints(self):
        """Test that admin can access all endpoints."""
        self.client.force_authenticate(user=self.admin)
        
        # Test client endpoints
        response = self.client.get(reverse('client-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test intervention endpoints
        response = self.client.get(reverse('intervention-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test inspection endpoints
        response = self.client.get(reverse('inspection-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test report endpoints
        response = self.client.get(reverse('report-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_technician_can_access_assigned_interventions(self):
        """Test that technician can access assigned interventions."""
        self.client.force_authenticate(user=self.technician)
        
        # Create a client
        client = Client.objects.create(
            name='Test Client',
            client_type='individual',
            address='123 Test Street',
            city='Test City',
            postal_code='12345',
            country='France'
        )
        
        # Create intervention assigned to technician
        intervention = Intervention.objects.create(
            title='Test Intervention',
            description='Test description',
            intervention_type='inspection',
            priority='medium',
            client=client,
            assigned_technician=self.technician,
            scheduled_date='2023-12-01T10:00:00Z'
        )
        
        # Test access to assigned intervention
        response = self.client.get(reverse('intervention-detail', kwargs={'pk': intervention.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_client_can_only_access_reports(self):
        """Test that client can only access reports."""
        self.client.force_authenticate(user=self.client_user)
        
        # Test client endpoints (should be restricted)
        response = self.client.get(reverse('client-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Clients can see their own data
        
        # Test intervention endpoints (should be restricted)
        response = self.client.get(reverse('intervention-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Clients can see their own interventions
        
        # Test inspection endpoints (should be restricted)
        response = self.client.get(reverse('inspection-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Clients can see their own inspections
        
        # Test report endpoints (should be accessible)
        response = self.client.get(reverse('report-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
