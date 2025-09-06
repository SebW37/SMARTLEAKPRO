"""
Performance tests for SmartLeakPro.
"""
import pytest
import time
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.clients.models import Client
from apps.interventions.models import Intervention
from apps.inspections.models import Inspection

User = get_user_model()


class PerformanceTest(TestCase):
    """Test API performance."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='technician'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.create_test_data()
    
    def create_test_data(self):
        """Create test data for performance tests."""
        # Create clients
        for i in range(100):
            Client.objects.create(
                name=f'Client {i}',
                client_type='individual',
                address=f'{i} Test Street',
                city='Test City',
                postal_code='12345',
                country='France'
            )
        
        # Create interventions
        clients = Client.objects.all()
        for i in range(50):
            Intervention.objects.create(
                title=f'Intervention {i}',
                description=f'Description {i}',
                intervention_type='inspection',
                priority='medium',
                client=clients[i % len(clients)],
                scheduled_date='2023-12-01T10:00:00Z'
            )
        
        # Create inspections
        interventions = Intervention.objects.all()
        for i in range(30):
            Inspection.objects.create(
                title=f'Inspection {i}',
                description=f'Description {i}',
                client=clients[i % len(clients)],
                intervention=interventions[i % len(interventions)],
                inspection_date='2023-12-01T10:00:00Z'
            )
    
    def test_client_list_performance(self):
        """Test client list API performance."""
        start_time = time.time()
        response = self.client.get(reverse('client-list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 1.0)  # Should complete in less than 1 second
        self.assertEqual(len(response.data['results']), 20)  # Default page size
    
    def test_intervention_list_performance(self):
        """Test intervention list API performance."""
        start_time = time.time()
        response = self.client.get(reverse('intervention-list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 1.0)  # Should complete in less than 1 second
        self.assertEqual(len(response.data['results']), 20)  # Default page size
    
    def test_inspection_list_performance(self):
        """Test inspection list API performance."""
        start_time = time.time()
        response = self.client.get(reverse('inspection-list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 1.0)  # Should complete in less than 1 second
        self.assertEqual(len(response.data['results']), 20)  # Default page size
    
    def test_client_search_performance(self):
        """Test client search performance."""
        start_time = time.time()
        response = self.client.get(reverse('client-list'), {'search': 'Client 1'})
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 1.0)  # Should complete in less than 1 second
    
    def test_client_filter_performance(self):
        """Test client filtering performance."""
        start_time = time.time()
        response = self.client.get(reverse('client-list'), {'client_type': 'individual'})
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 1.0)  # Should complete in less than 1 second
    
    def test_pagination_performance(self):
        """Test pagination performance."""
        start_time = time.time()
        response = self.client.get(reverse('client-list'), {'page': 2})
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 1.0)  # Should complete in less than 1 second
    
    def test_bulk_operations_performance(self):
        """Test bulk operations performance."""
        # Test creating multiple clients
        start_time = time.time()
        for i in range(10):
            data = {
                'name': f'Bulk Client {i}',
                'client_type': 'individual',
                'address': f'{i} Bulk Street',
                'city': 'Bulk City',
                'postal_code': '12345',
                'country': 'France'
            }
            response = self.client.post(reverse('client-list'), data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        end_time = time.time()
        
        self.assertLess(end_time - start_time, 5.0)  # Should complete in less than 5 seconds
    
    def test_concurrent_requests_performance(self):
        """Test concurrent requests performance."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            start_time = time.time()
            response = self.client.get(reverse('client-list'))
            end_time = time.time()
            results.put((response.status_code, end_time - start_time))
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        while not results.empty():
            status_code, duration = results.get()
            self.assertEqual(status_code, status.HTTP_200_OK)
            self.assertLess(duration, 2.0)  # Each request should complete in less than 2 seconds