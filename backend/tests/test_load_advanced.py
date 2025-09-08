"""
Tests de montée en charge avancés - Phase Test & Debug
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from httpx import AsyncClient
import psutil
import os
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime, timedelta

from ..main import app
from ..database import get_db
from ..models import Client, Intervention, Utilisateur


class TestLoadScenarios:
    """Tests de scénarios de charge"""
    
    @pytest.mark.asyncio
    async def test_concurrent_user_sessions(self, async_client: AsyncClient, auth_headers: dict):
        """Test sessions utilisateur concurrentes"""
        num_users = 50
        requests_per_user = 10
        
        async def user_session(user_id: int):
            """Simuler une session utilisateur"""
            session_results = []
            
            for i in range(requests_per_user):
                start_time = time.time()
                
                # Simuler différentes actions utilisateur
                if i % 4 == 0:
                    response = await async_client.get("/api/clients/", headers=auth_headers)
                elif i % 4 == 1:
                    response = await async_client.get("/api/interventions/", headers=auth_headers)
                elif i % 4 == 2:
                    response = await async_client.get("/api/planning/", headers=auth_headers)
                else:
                    response = await async_client.get("/api/rapports/", headers=auth_headers)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                session_results.append({
                    "user_id": user_id,
                    "request_id": i,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "success": response.status_code == 200
                })
            
            return session_results
        
        # Lancer les sessions concurrentes
        start_time = time.time()
        tasks = [user_session(i) for i in range(num_users)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Analyser les résultats
        all_results = []
        for user_results in results:
            all_results.extend(user_results)
        
        total_requests = len(all_results)
        successful_requests = sum(1 for r in all_results if r["success"])
        success_rate = (successful_requests / total_requests) * 100
        
        response_times = [r["response_time"] for r in all_results if r["success"]]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max_response_time
        
        total_time = end_time - start_time
        requests_per_second = total_requests / total_time
        
        print(f"Sessions concurrentes: {num_users}")
        print(f"Requêtes par utilisateur: {requests_per_user}")
        print(f"Total requêtes: {total_requests}")
        print(f"Taux de succès: {success_rate:.2f}%")
        print(f"Temps de réponse moyen: {avg_response_time:.2f}ms")
        print(f"Temps de réponse max: {max_response_time:.2f}ms")
        print(f"Temps de réponse P95: {p95_response_time:.2f}ms")
        print(f"Requêtes par seconde: {requests_per_second:.2f}")
        print(f"Temps total: {total_time:.2f}s")
        
        # Vérifications de performance
        assert success_rate >= 95, f"Taux de succès trop faible: {success_rate:.2f}%"
        assert avg_response_time < 1000, f"Temps de réponse moyen trop élevé: {avg_response_time:.2f}ms"
        assert p95_response_time < 2000, f"Temps de réponse P95 trop élevé: {p95_response_time:.2f}ms"
        assert requests_per_second > 50, f"Débit trop faible: {requests_per_second:.2f} req/s"
    
    @pytest.mark.asyncio
    async def test_database_load_test(self, async_client: AsyncClient, auth_headers: dict):
        """Test de charge sur la base de données"""
        num_operations = 1000
        
        async def database_operation(operation_id: int):
            """Simuler une opération de base de données"""
            start_time = time.time()
            
            if operation_id % 3 == 0:
                # Création
                client_data = {
                    "nom": f"Client Load Test {operation_id}",
                    "email": f"loadtest{operation_id}@example.com",
                    "telephone": f"012345678{operation_id % 10}",
                    "adresse": f"{operation_id} Rue Load Test, 75001 Paris",
                    "statut": "actif"
                }
                response = await async_client.post("/api/clients/", json=client_data, headers=auth_headers)
            elif operation_id % 3 == 1:
                # Lecture
                response = await async_client.get("/api/clients/", headers=auth_headers)
            else:
                # Mise à jour (supposer qu'il y a des clients existants)
                response = await async_client.get("/api/clients/", headers=auth_headers)
                if response.status_code == 200 and response.json()["clients"]:
                    client_id = response.json()["clients"][0]["id"]
                    update_data = {"nom": f"Client Modifié {operation_id}"}
                    response = await async_client.put(f"/api/clients/{client_id}", json=update_data, headers=auth_headers)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                "operation_id": operation_id,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code in [200, 201, 204]
            }
        
        # Lancer les opérations
        start_time = time.time()
        tasks = [database_operation(i) for i in range(num_operations)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Analyser les résultats
        successful_operations = sum(1 for r in results if r["success"])
        success_rate = (successful_operations / num_operations) * 100
        
        response_times = [r["response_time"] for r in results if r["success"]]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        total_time = end_time - start_time
        operations_per_second = num_operations / total_time
        
        print(f"Opérations de base de données: {num_operations}")
        print(f"Taux de succès: {success_rate:.2f}%")
        print(f"Temps de réponse moyen: {avg_response_time:.2f}ms")
        print(f"Temps de réponse max: {max_response_time:.2f}ms")
        print(f"Opérations par seconde: {operations_per_second:.2f}")
        print(f"Temps total: {total_time:.2f}s")
        
        # Vérifications de performance
        assert success_rate >= 90, f"Taux de succès trop faible: {success_rate:.2f}%"
        assert avg_response_time < 500, f"Temps de réponse moyen trop élevé: {avg_response_time:.2f}ms"
        assert operations_per_second > 100, f"Débit trop faible: {operations_per_second:.2f} ops/s"
    
    @pytest.mark.asyncio
    async def test_file_upload_load(self, async_client: AsyncClient, auth_headers: dict, test_intervention: Intervention):
        """Test de charge pour l'upload de fichiers"""
        num_uploads = 50
        file_size = 1024 * 1024  # 1MB par fichier
        
        async def upload_file(upload_id: int):
            """Simuler un upload de fichier"""
            start_time = time.time()
            
            # Créer un fichier de test
            file_content = b"x" * file_size
            files = {"file": (f"test_file_{upload_id}.jpg", file_content, "image/jpeg")}
            
            media_data = {
                "intervention_id": str(test_intervention.id),
                "type_media": "photo",
                "description": f"Fichier de test {upload_id}"
            }
            
            response = await async_client.post("/api/medias/upload", data=media_data, files=files, headers=auth_headers)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                "upload_id": upload_id,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code == 201
            }
        
        # Lancer les uploads
        start_time = time.time()
        tasks = [upload_file(i) for i in range(num_uploads)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Analyser les résultats
        successful_uploads = sum(1 for r in results if r["success"])
        success_rate = (successful_uploads / num_uploads) * 100
        
        response_times = [r["response_time"] for r in results if r["success"]]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        total_time = end_time - start_time
        uploads_per_second = num_uploads / total_time
        total_data_transferred = num_uploads * file_size
        data_transfer_rate = total_data_transferred / total_time / (1024 * 1024)  # MB/s
        
        print(f"Uploads de fichiers: {num_uploads}")
        print(f"Taille par fichier: {file_size / (1024 * 1024):.2f}MB")
        print(f"Taux de succès: {success_rate:.2f}%")
        print(f"Temps de réponse moyen: {avg_response_time:.2f}ms")
        print(f"Temps de réponse max: {max_response_time:.2f}ms")
        print(f"Uploads par seconde: {uploads_per_second:.2f}")
        print(f"Débit de transfert: {data_transfer_rate:.2f}MB/s")
        print(f"Temps total: {total_time:.2f}s")
        
        # Vérifications de performance
        assert success_rate >= 90, f"Taux de succès trop faible: {success_rate:.2f}%"
        assert avg_response_time < 5000, f"Temps de réponse moyen trop élevé: {avg_response_time:.2f}ms"
        assert uploads_per_second > 5, f"Débit trop faible: {uploads_per_second:.2f} uploads/s"
    
    @pytest.mark.asyncio
    async def test_api_key_load_test(self, async_client: AsyncClient, auth_headers: dict):
        """Test de charge avec clés API"""
        # Créer plusieurs clés API
        num_api_keys = 10
        requests_per_key = 20
        
        api_keys = []
        for i in range(num_api_keys):
            api_key_data = {
                "nom": f"Load Test API Key {i}",
                "description": f"Clé API pour test de charge {i}",
                "scopes": ["read", "write"],
                "limite_requetes_par_minute": 100
            }
            
            response = await async_client.post("/api/api-keys/", json=api_key_data, headers=auth_headers)
            if response.status_code == 201:
                api_keys.append(response.json()["cle_api"])
        
        async def api_key_requests(api_key: str, key_id: int):
            """Simuler des requêtes avec une clé API"""
            key_headers = {"X-API-Key": api_key}
            key_results = []
            
            for i in range(requests_per_key):
                start_time = time.time()
                
                # Faire différentes requêtes
                if i % 3 == 0:
                    response = await async_client.get("/api/clients/", headers=key_headers)
                elif i % 3 == 1:
                    response = await async_client.get("/api/interventions/", headers=key_headers)
                else:
                    response = await async_client.get("/api/planning/", headers=key_headers)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                key_results.append({
                    "key_id": key_id,
                    "request_id": i,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "success": response.status_code == 200
                })
            
            return key_results
        
        # Lancer les requêtes avec les clés API
        start_time = time.time()
        tasks = [api_key_requests(api_key, i) for i, api_key in enumerate(api_keys)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Analyser les résultats
        all_results = []
        for key_results in results:
            all_results.extend(key_results)
        
        total_requests = len(all_results)
        successful_requests = sum(1 for r in all_results if r["success"])
        success_rate = (successful_requests / total_requests) * 100
        
        response_times = [r["response_time"] for r in all_results if r["success"]]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        total_time = end_time - start_time
        requests_per_second = total_requests / total_time
        
        print(f"Clés API: {num_api_keys}")
        print(f"Requêtes par clé: {requests_per_key}")
        print(f"Total requêtes: {total_requests}")
        print(f"Taux de succès: {success_rate:.2f}%")
        print(f"Temps de réponse moyen: {avg_response_time:.2f}ms")
        print(f"Temps de réponse max: {max_response_time:.2f}ms")
        print(f"Requêtes par seconde: {requests_per_second:.2f}")
        print(f"Temps total: {total_time:.2f}s")
        
        # Vérifications de performance
        assert success_rate >= 95, f"Taux de succès trop faible: {success_rate:.2f}%"
        assert avg_response_time < 1000, f"Temps de réponse moyen trop élevé: {avg_response_time:.2f}ms"
        assert requests_per_second > 100, f"Débit trop faible: {requests_per_second:.2f} req/s"


class TestStressScenarios:
    """Tests de scénarios de stress"""
    
    @pytest.mark.asyncio
    async def test_memory_stress(self, async_client: AsyncClient, auth_headers: dict):
        """Test de stress mémoire"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Effectuer beaucoup d'opérations pour tester la mémoire
        num_operations = 1000
        operations = []
        
        for i in range(num_operations):
            # Créer des objets en mémoire
            client_data = {
                "nom": f"Memory Stress Test {i}",
                "email": f"memory{i}@example.com",
                "telephone": f"012345678{i % 10}",
                "adresse": f"{i} Rue Memory Stress, 75001 Paris",
                "statut": "actif"
            }
            operations.append(client_data)
        
        # Effectuer les requêtes
        start_time = time.time()
        tasks = []
        for i, client_data in enumerate(operations):
            task = async_client.post("/api/clients/", json=client_data, headers=auth_headers)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Mesurer la mémoire finale
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Analyser les résultats
        successful_operations = sum(1 for r in results if not isinstance(r, Exception) and r.status_code == 201)
        success_rate = (successful_operations / num_operations) * 100
        
        total_time = end_time - start_time
        operations_per_second = num_operations / total_time
        
        print(f"Opérations de stress mémoire: {num_operations}")
        print(f"Mémoire initiale: {initial_memory:.2f}MB")
        print(f"Mémoire finale: {final_memory:.2f}MB")
        print(f"Augmentation mémoire: {memory_increase:.2f}MB")
        print(f"Taux de succès: {success_rate:.2f}%")
        print(f"Opérations par seconde: {operations_per_second:.2f}")
        print(f"Temps total: {total_time:.2f}s")
        
        # Vérifications de performance
        assert success_rate >= 80, f"Taux de succès trop faible: {success_rate:.2f}%"
        assert memory_increase < 500, f"Augmentation mémoire excessive: {memory_increase:.2f}MB"
        assert operations_per_second > 50, f"Débit trop faible: {operations_per_second:.2f} ops/s"
    
    @pytest.mark.asyncio
    async def test_connection_stress(self, async_client: AsyncClient, auth_headers: dict):
        """Test de stress des connexions"""
        num_connections = 200
        requests_per_connection = 5
        
        async def connection_stress(connection_id: int):
            """Simuler une connexion stressante"""
            connection_results = []
            
            for i in range(requests_per_connection):
                start_time = time.time()
                
                try:
                    response = await async_client.get("/api/clients/", headers=auth_headers)
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    connection_results.append({
                        "connection_id": connection_id,
                        "request_id": i,
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "success": response.status_code == 200
                    })
                except Exception as e:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    connection_results.append({
                        "connection_id": connection_id,
                        "request_id": i,
                        "status_code": 0,
                        "response_time": response_time,
                        "success": False,
                        "error": str(e)
                    })
            
            return connection_results
        
        # Lancer les connexions stressantes
        start_time = time.time()
        tasks = [connection_stress(i) for i in range(num_connections)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyser les résultats
        all_results = []
        for connection_results in results:
            if isinstance(connection_results, list):
                all_results.extend(connection_results)
        
        total_requests = len(all_results)
        successful_requests = sum(1 for r in all_results if r["success"])
        success_rate = (successful_requests / total_requests) * 100
        
        response_times = [r["response_time"] for r in all_results if r["success"]]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        total_time = end_time - start_time
        requests_per_second = total_requests / total_time
        
        print(f"Connexions stressantes: {num_connections}")
        print(f"Requêtes par connexion: {requests_per_connection}")
        print(f"Total requêtes: {total_requests}")
        print(f"Taux de succès: {success_rate:.2f}%")
        print(f"Temps de réponse moyen: {avg_response_time:.2f}ms")
        print(f"Temps de réponse max: {max_response_time:.2f}ms")
        print(f"Requêtes par seconde: {requests_per_second:.2f}")
        print(f"Temps total: {total_time:.2f}s")
        
        # Vérifications de performance
        assert success_rate >= 90, f"Taux de succès trop faible: {success_rate:.2f}%"
        assert avg_response_time < 2000, f"Temps de réponse moyen trop élevé: {avg_response_time:.2f}ms"
        assert requests_per_second > 100, f"Débit trop faible: {requests_per_second:.2f} req/s"
    
    @pytest.mark.asyncio
    async def test_error_recovery_stress(self, async_client: AsyncClient, auth_headers: dict):
        """Test de stress de récupération d'erreurs"""
        num_error_scenarios = 100
        
        async def error_scenario(scenario_id: int):
            """Simuler un scénario d'erreur"""
            scenario_results = []
            
            # Différents types d'erreurs
            error_types = [
                ("invalid_data", {"nom": "", "email": "invalid"}),
                ("missing_required", {"nom": "Test"}),
                ("invalid_format", {"email": "not_an_email"}),
                ("unauthorized", {}),
                ("not_found", {"id": "00000000-0000-0000-0000-000000000000"})
            ]
            
            for i, (error_type, data) in enumerate(error_types):
                start_time = time.time()
                
                try:
                    if error_type == "unauthorized":
                        response = await async_client.post("/api/clients/", json=data)
                    elif error_type == "not_found":
                        response = await async_client.get(f"/api/clients/{data['id']}", headers=auth_headers)
                    else:
                        response = await async_client.post("/api/clients/", json=data, headers=auth_headers)
                    
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    scenario_results.append({
                        "scenario_id": scenario_id,
                        "error_type": error_type,
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "success": response.status_code in [400, 401, 404, 422]
                    })
                except Exception as e:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    scenario_results.append({
                        "scenario_id": scenario_id,
                        "error_type": error_type,
                        "status_code": 0,
                        "response_time": response_time,
                        "success": False,
                        "error": str(e)
                    })
            
            return scenario_results
        
        # Lancer les scénarios d'erreur
        start_time = time.time()
        tasks = [error_scenario(i) for i in range(num_error_scenarios)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyser les résultats
        all_results = []
        for scenario_results in results:
            if isinstance(scenario_results, list):
                all_results.extend(scenario_results)
        
        total_scenarios = len(all_results)
        successful_scenarios = sum(1 for r in all_results if r["success"])
        success_rate = (successful_scenarios / total_scenarios) * 100
        
        response_times = [r["response_time"] for r in all_results if r["success"]]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        total_time = end_time - start_time
        scenarios_per_second = total_scenarios / total_time
        
        print(f"Scénarios d'erreur: {num_error_scenarios}")
        print(f"Total scénarios: {total_scenarios}")
        print(f"Taux de succès: {success_rate:.2f}%")
        print(f"Temps de réponse moyen: {avg_response_time:.2f}ms")
        print(f"Temps de réponse max: {max_response_time:.2f}ms")
        print(f"Scénarios par seconde: {scenarios_per_second:.2f}")
        print(f"Temps total: {total_time:.2f}s")
        
        # Vérifications de performance
        assert success_rate >= 80, f"Taux de succès trop faible: {success_rate:.2f}%"
        assert avg_response_time < 1000, f"Temps de réponse moyen trop élevé: {avg_response_time:.2f}ms"
        assert scenarios_per_second > 50, f"Débit trop faible: {scenarios_per_second:.2f} scenarios/s"


class TestResourceMonitoring:
    """Tests de surveillance des ressources"""
    
    @pytest.mark.asyncio
    async def test_cpu_usage_monitoring(self, async_client: AsyncClient, auth_headers: dict):
        """Test surveillance de l'utilisation CPU"""
        process = psutil.Process(os.getpid())
        
        # Mesurer l'utilisation CPU avant le test
        initial_cpu = process.cpu_percent()
        
        # Effectuer des opérations intensives
        num_operations = 500
        operations = []
        
        for i in range(num_operations):
            client_data = {
                "nom": f"CPU Test {i}",
                "email": f"cpu{i}@example.com",
                "telephone": f"012345678{i % 10}",
                "adresse": f"{i} Rue CPU Test, 75001 Paris",
                "statut": "actif"
            }
            operations.append(client_data)
        
        # Lancer les opérations
        start_time = time.time()
        tasks = []
        for client_data in operations:
            task = async_client.post("/api/clients/", json=client_data, headers=auth_headers)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Mesurer l'utilisation CPU après le test
        final_cpu = process.cpu_percent()
        avg_cpu = (initial_cpu + final_cpu) / 2
        
        # Analyser les résultats
        successful_operations = sum(1 for r in results if not isinstance(r, Exception) and r.status_code == 201)
        success_rate = (successful_operations / num_operations) * 100
        
        total_time = end_time - start_time
        operations_per_second = num_operations / total_time
        
        print(f"Opérations CPU: {num_operations}")
        print(f"Utilisation CPU initiale: {initial_cpu:.2f}%")
        print(f"Utilisation CPU finale: {final_cpu:.2f}%")
        print(f"Utilisation CPU moyenne: {avg_cpu:.2f}%")
        print(f"Taux de succès: {success_rate:.2f}%")
        print(f"Opérations par seconde: {operations_per_second:.2f}")
        print(f"Temps total: {total_time:.2f}s")
        
        # Vérifications de performance
        assert success_rate >= 90, f"Taux de succès trop faible: {success_rate:.2f}%"
        assert avg_cpu < 80, f"Utilisation CPU trop élevée: {avg_cpu:.2f}%"
        assert operations_per_second > 100, f"Débit trop faible: {operations_per_second:.2f} ops/s"
    
    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self, async_client: AsyncClient, auth_headers: dict):
        """Test surveillance de l'utilisation mémoire"""
        process = psutil.Process(os.getpid())
        
        # Mesurer la mémoire avant le test
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Effectuer des opérations intensives
        num_operations = 1000
        operations = []
        
        for i in range(num_operations):
            client_data = {
                "nom": f"Memory Test {i}",
                "email": f"memory{i}@example.com",
                "telephone": f"012345678{i % 10}",
                "adresse": f"{i} Rue Memory Test, 75001 Paris",
                "statut": "actif"
            }
            operations.append(client_data)
        
        # Lancer les opérations
        start_time = time.time()
        tasks = []
        for client_data in operations:
            task = async_client.post("/api/clients/", json=client_data, headers=auth_headers)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Mesurer la mémoire après le test
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Analyser les résultats
        successful_operations = sum(1 for r in results if not isinstance(r, Exception) and r.status_code == 201)
        success_rate = (successful_operations / num_operations) * 100
        
        total_time = end_time - start_time
        operations_per_second = num_operations / total_time
        
        print(f"Opérations mémoire: {num_operations}")
        print(f"Mémoire initiale: {initial_memory:.2f}MB")
        print(f"Mémoire finale: {final_memory:.2f}MB")
        print(f"Augmentation mémoire: {memory_increase:.2f}MB")
        print(f"Taux de succès: {success_rate:.2f}%")
        print(f"Opérations par seconde: {operations_per_second:.2f}")
        print(f"Temps total: {total_time:.2f}s")
        
        # Vérifications de performance
        assert success_rate >= 90, f"Taux de succès trop faible: {success_rate:.2f}%"
        assert memory_increase < 200, f"Augmentation mémoire excessive: {memory_increase:.2f}MB"
        assert operations_per_second > 100, f"Débit trop faible: {operations_per_second:.2f} ops/s"
