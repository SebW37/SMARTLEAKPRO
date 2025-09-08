"""
Tests de performance et de charge - Phase 8
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from httpx import AsyncClient
import statistics
from typing import List, Dict, Any

from ..main import app
from ..database import get_db
from ..models import Client, Intervention, Utilisateur
from ..services.api_service import api_service


class TestPerformance:
    """Tests de performance de l'application"""
    
    @pytest.mark.asyncio
    async def test_api_response_time(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test temps de réponse des API"""
        endpoints = [
            "/api/clients/",
            "/api/interventions/",
            "/api/planning/",
            "/api/rapports/",
            "/api/medias/",
            "/api/utilisateurs/",
            "/api/api-keys/",
            "/api/webhooks/",
            "/api/integrations/"
        ]
        
        response_times = []
        
        for endpoint in endpoints:
            start_time = time.time()
            response = await async_client.get(endpoint, headers=auth_headers)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # en millisecondes
            response_times.append(response_time)
            
            # Vérifier que la réponse est valide
            assert response.status_code in [200, 401, 403]  # 401/403 si pas de données
        
        # Calculer les statistiques
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"Temps de réponse moyen: {avg_response_time:.2f}ms")
        print(f"Temps de réponse max: {max_response_time:.2f}ms")
        print(f"Temps de réponse min: {min_response_time:.2f}ms")
        
        # Vérifier que le temps de réponse moyen est acceptable (< 500ms)
        assert avg_response_time < 500, f"Temps de réponse moyen trop élevé: {avg_response_time:.2f}ms"
        
        # Vérifier qu'aucune requête ne dépasse 2 secondes
        assert max_response_time < 2000, f"Temps de réponse max trop élevé: {max_response_time:.2f}ms"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test requêtes concurrentes"""
        num_requests = 50
        endpoint = "/api/clients/"
        
        async def make_request():
            response = await async_client.get(endpoint, headers=auth_headers)
            return response.status_code, time.time()
        
        # Lancer les requêtes concurrentes
        start_time = time.time()
        tasks = [make_request() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Analyser les résultats
        status_codes = [result[0] for result in results]
        response_times = [(result[1] - start_time) * 1000 for result in results]
        
        # Vérifier que toutes les requêtes ont réussi
        success_count = sum(1 for code in status_codes if code == 200)
        success_rate = (success_count / num_requests) * 100
        
        print(f"Requêtes réussies: {success_count}/{num_requests} ({success_rate:.1f}%)")
        print(f"Temps total: {(end_time - start_time):.2f}s")
        print(f"Requêtes par seconde: {num_requests / (end_time - start_time):.2f}")
        
        # Vérifier que le taux de succès est acceptable (> 95%)
        assert success_rate >= 95, f"Taux de succès trop faible: {success_rate:.1f}%"
        
        # Vérifier que le temps total est acceptable (< 10 secondes)
        total_time = end_time - start_time
        assert total_time < 10, f"Temps total trop élevé: {total_time:.2f}s"
    
    @pytest.mark.asyncio
    async def test_database_performance(self, db_session, test_user):
        """Test performance de la base de données"""
        # Test création en masse
        start_time = time.time()
        
        clients = []
        for i in range(100):
            client = Client(
                nom=f"Client Test {i}",
                email=f"client{i}@example.com",
                telephone=f"012345678{i%10}",
                adresse=f"{i} Rue Test, 75001 Paris",
                statut="actif"
            )
            clients.append(client)
        
        db_session.add_all(clients)
        await db_session.commit()
        
        creation_time = time.time() - start_time
        print(f"Création de 100 clients: {creation_time:.2f}s")
        
        # Test requêtes de lecture
        start_time = time.time()
        
        from sqlalchemy import select
        result = await db_session.execute(select(Client).limit(50))
        clients = result.scalars().all()
        
        read_time = time.time() - start_time
        print(f"Lecture de 50 clients: {read_time:.2f}s")
        
        # Vérifier que les performances sont acceptables
        assert creation_time < 5, f"Création trop lente: {creation_time:.2f}s"
        assert read_time < 1, f"Lecture trop lente: {read_time:.2f}s"
    
    @pytest.mark.asyncio
    async def test_memory_usage(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test utilisation mémoire"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Effectuer plusieurs requêtes pour tester la mémoire
        for i in range(100):
            response = await async_client.get("/api/clients/", headers=auth_headers)
            assert response.status_code in [200, 401, 403]
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Mémoire initiale: {initial_memory:.2f}MB")
        print(f"Mémoire finale: {final_memory:.2f}MB")
        print(f"Augmentation: {memory_increase:.2f}MB")
        
        # Vérifier que l'augmentation mémoire est raisonnable (< 100MB)
        assert memory_increase < 100, f"Augmentation mémoire trop importante: {memory_increase:.2f}MB"


class TestLoadTesting:
    """Tests de charge"""
    
    @pytest.mark.asyncio
    async def test_high_load(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test charge élevée"""
        num_requests = 200
        endpoint = "/api/clients/"
        
        async def make_request():
            start_time = time.time()
            response = await async_client.get(endpoint, headers=auth_headers)
            end_time = time.time()
            return response.status_code, (end_time - start_time) * 1000
        
        # Lancer les requêtes
        start_time = time.time()
        tasks = [make_request() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyser les résultats
        successful_requests = []
        failed_requests = []
        
        for result in results:
            if isinstance(result, Exception):
                failed_requests.append(result)
            else:
                status_code, response_time = result
                if status_code == 200:
                    successful_requests.append(response_time)
                else:
                    failed_requests.append(f"Status {status_code}")
        
        success_count = len(successful_requests)
        success_rate = (success_count / num_requests) * 100
        avg_response_time = statistics.mean(successful_requests) if successful_requests else 0
        total_time = end_time - start_time
        rps = num_requests / total_time
        
        print(f"Requêtes réussies: {success_count}/{num_requests} ({success_rate:.1f}%)")
        print(f"Temps de réponse moyen: {avg_response_time:.2f}ms")
        print(f"Temps total: {total_time:.2f}s")
        print(f"Requêtes par seconde: {rps:.2f}")
        print(f"Échecs: {len(failed_requests)}")
        
        # Vérifier que le taux de succès est acceptable (> 90%)
        assert success_rate >= 90, f"Taux de succès trop faible: {success_rate:.1f}%"
        
        # Vérifier que le temps de réponse moyen est acceptable (< 1s)
        assert avg_response_time < 1000, f"Temps de réponse moyen trop élevé: {avg_response_time:.2f}ms"
    
    @pytest.mark.asyncio
    async def test_sustained_load(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test charge soutenue"""
        duration = 30  # secondes
        requests_per_second = 10
        total_requests = duration * requests_per_second
        
        async def make_request():
            response = await async_client.get("/api/clients/", headers=auth_headers)
            return response.status_code, time.time()
        
        start_time = time.time()
        results = []
        
        # Lancer les requêtes à intervalles réguliers
        for i in range(total_requests):
            if i > 0:
                await asyncio.sleep(1 / requests_per_second)
            
            result = await make_request()
            results.append(result)
        
        end_time = time.time()
        
        # Analyser les résultats
        status_codes = [result[0] for result in results]
        success_count = sum(1 for code in status_codes if code == 200)
        success_rate = (success_count / len(results)) * 100
        
        actual_duration = end_time - start_time
        actual_rps = len(results) / actual_duration
        
        print(f"Durée prévue: {duration}s, Durée réelle: {actual_duration:.2f}s")
        print(f"RPS prévu: {requests_per_second}, RPS réel: {actual_rps:.2f}")
        print(f"Taux de succès: {success_rate:.1f}%")
        
        # Vérifier que le taux de succès reste élevé
        assert success_rate >= 95, f"Taux de succès trop faible: {success_rate:.1f}%"
        
        # Vérifier que le débit est proche de l'attendu
        assert abs(actual_rps - requests_per_second) < 2, f"Débit trop différent: {actual_rps:.2f} vs {requests_per_second}"


class TestStressTesting:
    """Tests de stress"""
    
    @pytest.mark.asyncio
    async def test_memory_stress(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test stress mémoire"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Effectuer beaucoup de requêtes pour tester la mémoire
        tasks = []
        for i in range(500):
            task = async_client.get("/api/clients/", headers=auth_headers)
            tasks.append(task)
        
        # Exécuter toutes les requêtes
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Mémoire initiale: {initial_memory:.2f}MB")
        print(f"Mémoire finale: {final_memory:.2f}MB")
        print(f"Augmentation: {memory_increase:.2f}MB")
        
        # Vérifier qu'il n'y a pas de fuite mémoire excessive
        assert memory_increase < 200, f"Augmentation mémoire excessive: {memory_increase:.2f}MB"
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test récupération après erreurs"""
        # Tester avec des requêtes invalides
        invalid_requests = [
            ("/api/clients/", {"invalid": "data"}),
            ("/api/clients/invalid-id", {}),
            ("/api/nonexistent/", {}),
        ]
        
        for endpoint, data in invalid_requests:
            if data:
                response = await async_client.post(endpoint, json=data, headers=auth_headers)
            else:
                response = await async_client.get(endpoint, headers=auth_headers)
            
            # Vérifier que l'application gère les erreurs correctement
            assert response.status_code in [400, 404, 422, 500]
        
        # Vérifier que l'application fonctionne toujours après les erreurs
        response = await async_client.get("/api/clients/", headers=auth_headers)
        assert response.status_code in [200, 401, 403]


class TestScalability:
    """Tests de scalabilité"""
    
    @pytest.mark.asyncio
    async def test_database_scalability(self, db_session, test_user):
        """Test scalabilité de la base de données"""
        # Créer un grand nombre d'enregistrements
        batch_size = 1000
        start_time = time.time()
        
        clients = []
        for i in range(batch_size):
            client = Client(
                nom=f"Client {i}",
                email=f"client{i}@example.com",
                telephone=f"012345678{i%10}",
                adresse=f"{i} Rue Test, 75001 Paris",
                statut="actif"
            )
            clients.append(client)
        
        db_session.add_all(clients)
        await db_session.commit()
        
        creation_time = time.time() - start_time
        print(f"Création de {batch_size} clients: {creation_time:.2f}s")
        
        # Test requêtes avec pagination
        start_time = time.time()
        
        from sqlalchemy import select
        result = await db_session.execute(select(Client).limit(100))
        clients = result.scalars().all()
        
        read_time = time.time() - start_time
        print(f"Lecture de 100 clients: {read_time:.2f}s")
        
        # Vérifier que les performances restent acceptables
        assert creation_time < 30, f"Création trop lente: {creation_time:.2f}s"
        assert read_time < 2, f"Lecture trop lente: {read_time:.2f}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_writes(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test écritures concurrentes"""
        num_writes = 50
        
        async def create_client(i):
            client_data = {
                "nom": f"Client Concurrent {i}",
                "email": f"concurrent{i}@example.com",
                "telephone": f"012345678{i%10}",
                "adresse": f"{i} Rue Concurrent, 75001 Paris",
                "statut": "actif"
            }
            response = await async_client.post("/api/clients/", json=client_data, headers=auth_headers)
            return response.status_code
        
        # Lancer les créations concurrentes
        start_time = time.time()
        tasks = [create_client(i) for i in range(num_writes)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyser les résultats
        success_count = sum(1 for result in results if result == 201)
        success_rate = (success_count / num_writes) * 100
        total_time = end_time - start_time
        
        print(f"Créations réussies: {success_count}/{num_writes} ({success_rate:.1f}%)")
        print(f"Temps total: {total_time:.2f}s")
        
        # Vérifier que la plupart des créations ont réussi
        assert success_rate >= 90, f"Taux de succès trop faible: {success_rate:.1f}%"
