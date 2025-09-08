"""
Load tests for SmartLeakPro.
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
import time
import threading
from concurrent.futures import ThreadPoolExecutor

User = get_user_model()


class LoadTest(TestCase):
    """Test system performance under load."""
    
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
    
    def test_concurrent_client_creation(self):
        """Test creating multiple clients concurrently."""
        self.client.force_authenticate(user=self.technician)
        
        def create_client(client_id):
            data = {
                'name': f'Test Client {client_id}',
                'client_type': 'individual',
                'address': f'{client_id} Test Street',
                'city': 'Test City',
                'postal_code': '12345',
                'country': 'France'
            }
            response = self.client.post(reverse('client-list'), data)
            return response.status_code == status.HTTP_201_CREATED
        
        # Test with 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_client, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        self.assertTrue(all(results))
        
        # Verify all clients were created
        self.assertEqual(Client.objects.count(), 11)  # 1 original + 10 new
    
    def test_concurrent_intervention_creation(self):
        """Test creating multiple interventions concurrently."""
        self.client.force_authenticate(user=self.technician)
        
        def create_intervention(intervention_id):
            data = {
                'title': f'Test Intervention {intervention_id}',
                'description': 'Test description',
                'intervention_type': 'inspection',
                'priority': 'medium',
                'client': self.test_client.pk,
                'scheduled_date': '2023-12-01T10:00:00Z'
            }
            response = self.client.post(reverse('intervention-list'), data)
            return response.status_code == status.HTTP_201_CREATED
        
        # Test with 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_intervention, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        self.assertTrue(all(results))
        
        # Verify all interventions were created
        self.assertEqual(Intervention.objects.count(), 11)  # 1 original + 10 new
    
    def test_concurrent_inspection_creation(self):
        """Test creating multiple inspections concurrently."""
        self.client.force_authenticate(user=self.technician)
        
        def create_inspection(inspection_id):
            data = {
                'title': f'Test Inspection {inspection_id}',
                'description': 'Test description',
                'client': self.test_client.pk,
                'inspection_date': '2023-12-01T10:00:00Z'
            }
            response = self.client.post(reverse('inspection-list'), data)
            return response.status_code == status.HTTP_201_CREATED
        
        # Test with 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_inspection, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        self.assertTrue(all(results))
        
        # Verify all inspections were created
        self.assertEqual(Inspection.objects.count(), 11)  # 1 original + 10 new
    
    def test_concurrent_read_operations(self):
        """Test reading data concurrently."""
        self.client.force_authenticate(user=self.technician)
        
        def read_clients():
            response = self.client.get(reverse('client-list'))
            return response.status_code == status.HTTP_200_OK
        
        def read_interventions():
            response = self.client.get(reverse('intervention-list'))
            return response.status_code == status.HTTP_200_OK
        
        def read_inspections():
            response = self.client.get(reverse('inspection-list'))
            return response.status_code == status.HTTP_200_OK
        
        # Test with 30 concurrent read requests
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = []
            for _ in range(10):
                futures.append(executor.submit(read_clients))
                futures.append(executor.submit(read_interventions))
                futures.append(executor.submit(read_inspections))
            
            results = [future.result() for future in futures]
        
        # All requests should succeed
        self.assertTrue(all(results))
    
    def test_mixed_operations_load(self):
        """Test mixed read/write operations under load."""
        self.client.force_authenticate(user=self.technician)
        
        def mixed_operation(operation_id):
            if operation_id % 3 == 0:
                # Create client
                data = {
                    'name': f'Test Client {operation_id}',
                    'client_type': 'individual',
                    'address': f'{operation_id} Test Street',
                    'city': 'Test City',
                    'postal_code': '12345',
                    'country': 'France'
                }
                response = self.client.post(reverse('client-list'), data)
                return response.status_code == status.HTTP_201_CREATED
            elif operation_id % 3 == 1:
                # Read clients
                response = self.client.get(reverse('client-list'))
                return response.status_code == status.HTTP_200_OK
            else:
                # Update client
                data = {
                    'name': f'Updated Client {operation_id}',
                    'client_type': 'individual',
                    'address': f'{operation_id} Updated Street',
                    'city': 'Updated City',
                    'postal_code': '54321',
                    'country': 'France'
                }
                response = self.client.put(
                    reverse('client-detail', kwargs={'pk': self.test_client.pk}),
                    data
                )
                return response.status_code == status.HTTP_200_OK
        
        # Test with 30 mixed operations
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(mixed_operation, i) for i in range(30)]
            results = [future.result() for future in futures]
        
        # All operations should succeed
        self.assertTrue(all(results))
    
    def test_database_connection_pooling(self):
        """Test database connection pooling under load."""
        self.client.force_authenticate(user=self.technician)
        
        def database_operation(operation_id):
            # Perform a database-intensive operation
            response = self.client.get(reverse('client-list'))
            if response.status_code == status.HTTP_200_OK:
                # Simulate some processing time
                time.sleep(0.1)
                return True
            return False
        
        # Test with 50 concurrent database operations
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(database_operation, i) for i in range(50)]
            results = [future.result() for future in futures]
        
        # All operations should succeed
        self.assertTrue(all(results))
    
    def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        self.client.force_authenticate(user=self.technician)
        
        def memory_intensive_operation(operation_id):
            # Create a large number of objects
            for i in range(100):
                data = {
                    'name': f'Test Client {operation_id}_{i}',
                    'client_type': 'individual',
                    'address': f'{operation_id}_{i} Test Street',
                    'city': 'Test City',
                    'postal_code': '12345',
                    'country': 'France'
                }
                response = self.client.post(reverse('client-list'), data)
                if response.status_code != status.HTTP_201_CREATED:
                    return False
            return True
        
        # Test with 5 concurrent memory-intensive operations
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(memory_intensive_operation, i) for i in range(5)]
            results = [future.result() for future in futures]
        
        # All operations should succeed
        self.assertTrue(all(results))
    
    def test_error_handling_under_load(self):
        """Test error handling under load."""
        self.client.force_authenticate(user=self.technician)
        
        def error_prone_operation(operation_id):
            if operation_id % 2 == 0:
                # Valid operation
                data = {
                    'name': f'Test Client {operation_id}',
                    'client_type': 'individual',
                    'address': f'{operation_id} Test Street',
                    'city': 'Test City',
                    'postal_code': '12345',
                    'country': 'France'
                }
                response = self.client.post(reverse('client-list'), data)
                return response.status_code == status.HTTP_201_CREATED
            else:
                # Invalid operation
                data = {
                    'name': '',  # Invalid: empty name
                    'client_type': 'invalid_type',  # Invalid type
                    'address': f'{operation_id} Test Street',
                    'city': 'Test City',
                    'postal_code': '12345',
                    'country': 'France'
                }
                response = self.client.post(reverse('client-list'), data)
                return response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test with 20 operations (10 valid, 10 invalid)
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(error_prone_operation, i) for i in range(20)]
            results = [future.result() for future in futures]
        
        # All operations should succeed (either create or return error)
        self.assertTrue(all(results))