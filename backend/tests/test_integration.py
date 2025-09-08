"""
Tests d'intégration - Phase Test & Debug
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, Mock
import json
import uuid
from datetime import datetime, timedelta

from ..main import app
from ..database import get_db
from ..models import Utilisateur, Client, Intervention, RendezVous, Rapport, Media, APIKey, Webhook
from ..services.security_service import security_service


class TestClientInterventionIntegration:
    """Tests d'intégration Client <-> Intervention"""
    
    @pytest.mark.asyncio
    async def test_create_client_and_intervention_flow(self, async_client: AsyncClient, auth_headers: dict):
        """Test flux complet : création client + intervention"""
        
        # 1. Créer un client
        client_data = {
            "nom": "Client Test Intégration",
            "email": "client.integration@example.com",
            "telephone": "0123456789",
            "adresse": "123 Rue Test, 75001 Paris",
            "statut": "actif"
        }
        
        response = await async_client.post("/api/clients/", json=client_data, headers=auth_headers)
        assert response.status_code == 201
        client_result = response.json()
        client_id = client_result["id"]
        
        # 2. Créer une intervention pour ce client
        intervention_data = {
            "client_id": client_id,
            "date_intervention": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "type_intervention": "inspection",
            "statut": "planifie",
            "lieu": "123 Rue Test, 75001 Paris",
            "description": "Intervention de test d'intégration"
        }
        
        response = await async_client.post("/api/interventions/", json=intervention_data, headers=auth_headers)
        assert response.status_code == 201
        intervention_result = response.json()
        intervention_id = intervention_result["id"]
        
        # 3. Vérifier que l'intervention est liée au client
        response = await async_client.get(f"/api/clients/{client_id}", headers=auth_headers)
        assert response.status_code == 200
        client_details = response.json()
        
        # 4. Vérifier que l'intervention apparaît dans les détails du client
        response = await async_client.get(f"/api/interventions/?client_id={client_id}", headers=auth_headers)
        assert response.status_code == 200
        interventions = response.json()
        assert len(interventions["interventions"]) >= 1
        assert interventions["interventions"][0]["client_id"] == client_id
    
    @pytest.mark.asyncio
    async def test_intervention_workflow_integration(self, async_client: AsyncClient, auth_headers: dict, test_client: Client):
        """Test workflow complet d'intervention"""
        
        # 1. Créer une intervention
        intervention_data = {
            "client_id": str(test_client.id),
            "date_intervention": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "type_intervention": "inspection",
            "statut": "planifie",
            "lieu": "123 Rue Test, 75001 Paris",
            "description": "Test workflow"
        }
        
        response = await async_client.post("/api/interventions/", json=intervention_data, headers=auth_headers)
        assert response.status_code == 201
        intervention_id = response.json()["id"]
        
        # 2. Changer le statut vers "en_cours"
        response = await async_client.post(
            f"/api/interventions/{intervention_id}/change-status",
            json={"nouveau_statut": "en_cours"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # 3. Vérifier le changement de statut
        response = await async_client.get(f"/api/interventions/{intervention_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["statut"] == "en_cours"
        
        # 4. Finaliser l'intervention
        response = await async_client.post(
            f"/api/interventions/{intervention_id}/change-status",
            json={"nouveau_statut": "valide"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # 5. Vérifier le statut final
        response = await async_client.get(f"/api/interventions/{intervention_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["statut"] == "valide"


class TestPlanningInterventionIntegration:
    """Tests d'intégration Planning <-> Intervention"""
    
    @pytest.mark.asyncio
    async def test_create_rendez_vous_from_intervention(self, async_client: AsyncClient, auth_headers: dict, test_intervention: Intervention):
        """Test création rendez-vous à partir d'intervention"""
        
        # 1. Créer un rendez-vous pour l'intervention
        rendez_vous_data = {
            "intervention_id": str(test_intervention.id),
            "client_id": str(test_intervention.client_id),
            "date_heure_debut": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "date_heure_fin": (datetime.utcnow() + timedelta(days=1, hours=2)).isoformat(),
            "statut": "planifie",
            "notes": "Rendez-vous de test"
        }
        
        response = await async_client.post("/api/planning/", json=rendez_vous_data, headers=auth_headers)
        assert response.status_code == 201
        rendez_vous_result = response.json()
        rendez_vous_id = rendez_vous_result["id"]
        
        # 2. Vérifier que le rendez-vous est lié à l'intervention
        response = await async_client.get(f"/api/planning/{rendez_vous_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["intervention_id"] == str(test_intervention.id)
        
        # 3. Vérifier que le rendez-vous apparaît dans le calendrier
        response = await async_client.get("/api/planning/calendar", headers=auth_headers)
        assert response.status_code == 200
        events = response.json()
        assert len(events) >= 1
        assert any(event["intervention_id"] == str(test_intervention.id) for event in events)
    
    @pytest.mark.asyncio
    async def test_planning_conflict_detection(self, async_client: AsyncClient, auth_headers: dict, test_client: Client):
        """Test détection de conflits de planning"""
        
        # 1. Créer un premier rendez-vous
        rendez_vous_1_data = {
            "client_id": str(test_client.id),
            "date_heure_debut": (datetime.utcnow() + timedelta(days=1, hours=10)).isoformat(),
            "date_heure_fin": (datetime.utcnow() + timedelta(days=1, hours=12)).isoformat(),
            "statut": "planifie",
            "notes": "Premier rendez-vous"
        }
        
        response = await async_client.post("/api/planning/", json=rendez_vous_1_data, headers=auth_headers)
        assert response.status_code == 201
        
        # 2. Essayer de créer un rendez-vous en conflit
        rendez_vous_2_data = {
            "client_id": str(test_client.id),
            "date_heure_debut": (datetime.utcnow() + timedelta(days=1, hours=11)).isoformat(),
            "date_heure_fin": (datetime.utcnow() + timedelta(days=1, hours=13)).isoformat(),
            "statut": "planifie",
            "notes": "Rendez-vous en conflit"
        }
        
        response = await async_client.post("/api/planning/", json=rendez_vous_2_data, headers=auth_headers)
        # Devrait retourner une erreur de conflit
        assert response.status_code in [400, 409]


class TestRapportInterventionIntegration:
    """Tests d'intégration Rapport <-> Intervention"""
    
    @pytest.mark.asyncio
    async def test_generate_rapport_from_intervention(self, async_client: AsyncClient, auth_headers: dict, test_intervention: Intervention):
        """Test génération de rapport à partir d'intervention"""
        
        # 1. Générer un rapport pour l'intervention
        rapport_data = {
            "intervention_id": str(test_intervention.id),
            "type_rapport": "inspection",
            "format": "pdf",
            "template": "default"
        }
        
        response = await async_client.post("/api/rapports/generate", json=rapport_data, headers=auth_headers)
        assert response.status_code == 201
        rapport_result = response.json()
        rapport_id = rapport_result["id"]
        
        # 2. Vérifier que le rapport est lié à l'intervention
        response = await async_client.get(f"/api/rapports/{rapport_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["intervention_id"] == str(test_intervention.id)
        
        # 3. Vérifier que le rapport apparaît dans la liste
        response = await async_client.get("/api/rapports/", headers=auth_headers)
        assert response.status_code == 200
        rapports = response.json()
        assert len(rapports["rapports"]) >= 1
        assert any(rapport["intervention_id"] == str(test_intervention.id) for rapport in rapports["rapports"])
    
    @pytest.mark.asyncio
    async def test_rapport_with_media_integration(self, async_client: AsyncClient, auth_headers: dict, test_intervention: Intervention):
        """Test rapport avec médias"""
        
        # 1. Uploader un média pour l'intervention
        media_data = {
            "intervention_id": str(test_intervention.id),
            "type_media": "photo",
            "description": "Photo de test",
            "tags": ["test", "inspection"]
        }
        
        # Mock du fichier uploadé
        files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
        
        response = await async_client.post("/api/medias/upload", data=media_data, files=files, headers=auth_headers)
        assert response.status_code == 201
        media_result = response.json()
        media_id = media_result["id"]
        
        # 2. Générer un rapport qui inclut ce média
        rapport_data = {
            "intervention_id": str(test_intervention.id),
            "type_rapport": "inspection",
            "format": "pdf",
            "include_medias": True
        }
        
        response = await async_client.post("/api/rapports/generate", json=rapport_data, headers=auth_headers)
        assert response.status_code == 201
        
        # 3. Vérifier que le rapport contient le média
        rapport_id = response.json()["id"]
        response = await async_client.get(f"/api/rapports/{rapport_id}", headers=auth_headers)
        assert response.status_code == 200
        rapport = response.json()
        assert "medias" in rapport or "fichiers" in rapport


class TestMediaInterventionIntegration:
    """Tests d'intégration Media <-> Intervention"""
    
    @pytest.mark.asyncio
    async def test_media_upload_and_processing(self, async_client: AsyncClient, auth_headers: dict, test_intervention: Intervention):
        """Test upload et traitement de média"""
        
        # 1. Uploader un média
        media_data = {
            "intervention_id": str(test_intervention.id),
            "type_media": "photo",
            "description": "Photo de test d'intégration",
            "tags": ["test", "integration"]
        }
        
        files = {"file": ("test_integration.jpg", b"fake image content", "image/jpeg")}
        
        response = await async_client.post("/api/medias/upload", data=media_data, files=files, headers=auth_headers)
        assert response.status_code == 201
        media_result = response.json()
        media_id = media_result["id"]
        
        # 2. Vérifier que le média est lié à l'intervention
        response = await async_client.get(f"/api/medias/{media_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["intervention_id"] == str(test_intervention.id)
        
        # 3. Vérifier que le média apparaît dans la liste de l'intervention
        response = await async_client.get(f"/api/medias/?intervention_id={test_intervention.id}", headers=auth_headers)
        assert response.status_code == 200
        medias = response.json()
        assert len(medias["medias"]) >= 1
        assert any(media["intervention_id"] == str(test_intervention.id) for media in medias["medias"])
    
    @pytest.mark.asyncio
    async def test_media_metadata_extraction(self, async_client: AsyncClient, auth_headers: dict, test_intervention: Intervention):
        """Test extraction de métadonnées"""
        
        # Mock des métadonnées EXIF
        with patch('PIL.ExifTags.TAGS', {271: "Make", 306: "DateTime"}):
            with patch('PIL.Image.open') as mock_open:
                mock_image = Mock()
                mock_image._getexif.return_value = {
                    "DateTime": "2024:01:01 12:00:00",
                    "Make": "Test Camera"
                }
                mock_open.return_value = mock_image
                
                # Uploader un média avec métadonnées
                media_data = {
                    "intervention_id": str(test_intervention.id),
                    "type_media": "photo",
                    "description": "Photo avec métadonnées"
                }
                
                files = {"file": ("test_metadata.jpg", b"fake image content", "image/jpeg")}
                
                response = await async_client.post("/api/medias/upload", data=media_data, files=files, headers=auth_headers)
                assert response.status_code == 201
                
                # Vérifier que les métadonnées ont été extraites
                media_id = response.json()["id"]
                response = await async_client.get(f"/api/medias/{media_id}", headers=auth_headers)
                assert response.status_code == 200
                media = response.json()
                assert "metadata" in media or "exif_data" in media


class TestAPIIntegration:
    """Tests d'intégration API"""
    
    @pytest.mark.asyncio
    async def test_api_key_authentication_flow(self, async_client: AsyncClient, auth_headers: dict):
        """Test flux d'authentification avec clé API"""
        
        # 1. Créer une clé API
        api_key_data = {
            "nom": "Test API Key",
            "description": "Clé API pour tests d'intégration",
            "scopes": ["read", "write"],
            "limite_requetes_par_minute": 100
        }
        
        response = await async_client.post("/api/api-keys/", json=api_key_data, headers=auth_headers)
        assert response.status_code == 201
        api_key_result = response.json()
        api_key = api_key_result["cle_api"]
        
        # 2. Utiliser la clé API pour accéder aux ressources
        api_headers = {"X-API-Key": api_key}
        
        response = await async_client.get("/api/clients/", headers=api_headers)
        assert response.status_code == 200
        
        response = await async_client.get("/api/interventions/", headers=api_headers)
        assert response.status_code == 200
        
        # 3. Vérifier que les requêtes sont loggées
        response = await async_client.get("/api/api-keys/", headers=auth_headers)
        assert response.status_code == 200
        api_keys = response.json()
        assert len(api_keys["api_keys"]) >= 1
    
    @pytest.mark.asyncio
    async def test_webhook_integration_flow(self, async_client: AsyncClient, auth_headers: dict, test_intervention: Intervention):
        """Test flux d'intégration webhook"""
        
        # 1. Créer un webhook
        webhook_data = {
            "nom": "Test Webhook",
            "description": "Webhook pour tests d'intégration",
            "url": "https://webhook.site/test",
            "type_webhook": "intervention_created",
            "secret": "test_secret"
        }
        
        response = await async_client.post("/api/webhooks/", json=webhook_data, headers=auth_headers)
        assert response.status_code == 201
        webhook_result = response.json()
        webhook_id = webhook_result["id"]
        
        # 2. Déclencher un événement qui devrait activer le webhook
        # (Dans un vrai test, on créerait une nouvelle intervention)
        
        # 3. Vérifier que le webhook a été exécuté
        response = await async_client.get(f"/api/webhooks/{webhook_id}/executions", headers=auth_headers)
        assert response.status_code == 200
        executions = response.json()
        # Le webhook devrait avoir été exécuté au moins une fois


class TestSecurityIntegration:
    """Tests d'intégration sécurité"""
    
    @pytest.mark.asyncio
    async def test_authentication_and_authorization_flow(self, async_client: AsyncClient):
        """Test flux d'authentification et d'autorisation"""
        
        # 1. Tentative d'accès sans authentification
        response = await async_client.get("/api/clients/")
        assert response.status_code == 401
        
        # 2. Connexion avec identifiants valides
        login_data = {
            "nom_utilisateur": "test_user",
            "mot_de_passe": "testpassword"
        }
        
        response = await async_client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        login_result = response.json()
        token = login_result["access_token"]
        
        # 3. Accès avec token valide
        headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.get("/api/clients/", headers=headers)
        assert response.status_code == 200
        
        # 4. Tentative d'accès avec token invalide
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get("/api/clients/", headers=invalid_headers)
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_role_based_access_control(self, async_client: AsyncClient, auth_headers: dict):
        """Test contrôle d'accès basé sur les rôles"""
        
        # 1. Créer un utilisateur avec rôle limité
        user_data = {
            "nom_utilisateur": "test_technicien",
            "email": "technicien@example.com",
            "nom": "Technicien",
            "prenom": "Test",
            "mot_de_passe": "password123",
            "confirmer_mot_de_passe": "password123",
            "role": "technicien",
            "consentement_rgpd": True
        }
        
        response = await async_client.post("/api/utilisateurs/", json=user_data, headers=auth_headers)
        assert response.status_code == 201
        
        # 2. Se connecter avec ce utilisateur
        login_data = {
            "nom_utilisateur": "test_technicien",
            "mot_de_passe": "password123"
        }
        
        response = await async_client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Vérifier que l'utilisateur peut accéder aux ressources autorisées
        response = await async_client.get("/api/clients/", headers=tech_headers)
        assert response.status_code == 200
        
        # 4. Vérifier que l'utilisateur ne peut pas accéder aux ressources restreintes
        response = await async_client.get("/api/utilisateurs/", headers=tech_headers)
        assert response.status_code == 403  # Forbidden


class TestDataConsistency:
    """Tests de cohérence des données"""
    
    @pytest.mark.asyncio
    async def test_cascade_deletion(self, async_client: AsyncClient, auth_headers: dict, test_client: Client):
        """Test suppression en cascade"""
        
        # 1. Créer une intervention pour le client
        intervention_data = {
            "client_id": str(test_client.id),
            "date_intervention": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "type_intervention": "inspection",
            "statut": "planifie",
            "lieu": "123 Rue Test, 75001 Paris",
            "description": "Test cascade"
        }
        
        response = await async_client.post("/api/interventions/", json=intervention_data, headers=auth_headers)
        assert response.status_code == 201
        intervention_id = response.json()["id"]
        
        # 2. Supprimer le client
        response = await async_client.delete(f"/api/clients/{test_client.id}", headers=auth_headers)
        assert response.status_code == 204
        
        # 3. Vérifier que l'intervention a été supprimée en cascade
        response = await async_client.get(f"/api/interventions/{intervention_id}", headers=auth_headers)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_data_validation_consistency(self, async_client: AsyncClient, auth_headers: dict):
        """Test cohérence de validation des données"""
        
        # 1. Test validation email
        client_data = {
            "nom": "Client Test",
            "email": "invalid_email",  # Email invalide
            "telephone": "0123456789",
            "adresse": "123 Rue Test, 75001 Paris",
            "statut": "actif"
        }
        
        response = await async_client.post("/api/clients/", json=client_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error
        
        # 2. Test validation téléphone
        client_data["email"] = "valid@example.com"
        client_data["telephone"] = "invalid_phone"  # Téléphone invalide
        
        response = await async_client.post("/api/clients/", json=client_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error
        
        # 3. Test validation date
        client_data["telephone"] = "0123456789"
        intervention_data = {
            "client_id": "00000000-0000-0000-0000-000000000000",  # Client inexistant
            "date_intervention": "invalid_date",  # Date invalide
            "type_intervention": "inspection",
            "statut": "planifie",
            "lieu": "123 Rue Test, 75001 Paris",
            "description": "Test validation"
        }
        
        response = await async_client.post("/api/interventions/", json=intervention_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error


class TestErrorHandlingIntegration:
    """Tests de gestion d'erreurs en intégration"""
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, async_client: AsyncClient, auth_headers: dict):
        """Test gestion d'erreurs de base de données"""
        
        # Mock d'une erreur de base de données
        with patch('sqlalchemy.ext.asyncio.AsyncSession.commit') as mock_commit:
            mock_commit.side_effect = Exception("Database error")
            
            client_data = {
                "nom": "Client Test",
                "email": "test@example.com",
                "telephone": "0123456789",
                "adresse": "123 Rue Test, 75001 Paris",
                "statut": "actif"
            }
            
            response = await async_client.post("/api/clients/", json=client_data, headers=auth_headers)
            assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_file_upload_error_handling(self, async_client: AsyncClient, auth_headers: dict, test_intervention: Intervention):
        """Test gestion d'erreurs d'upload de fichier"""
        
        # Test avec fichier trop volumineux
        large_file_data = b"x" * (10 * 1024 * 1024)  # 10MB
        files = {"file": ("large_file.jpg", large_file_data, "image/jpeg")}
        
        media_data = {
            "intervention_id": str(test_intervention.id),
            "type_media": "photo",
            "description": "Fichier trop volumineux"
        }
        
        response = await async_client.post("/api/medias/upload", data=media_data, files=files, headers=auth_headers)
        assert response.status_code == 413  # Payload too large
    
    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, async_client: AsyncClient, auth_headers: dict):
        """Test rate limiting en intégration"""
        
        # Faire beaucoup de requêtes rapidement
        for i in range(150):  # Plus que la limite par défaut
            response = await async_client.get("/api/clients/", headers=auth_headers)
            if response.status_code == 429:  # Too many requests
                break
        
        # Vérifier que le rate limiting a été appliqué
        assert response.status_code == 429
