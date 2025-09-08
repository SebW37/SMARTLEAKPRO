"""
Tests unitaires pour les API - Phase 8
"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json


class TestAuthAPI:
    """Tests pour les API d'authentification"""
    
    def test_login_success(self, client: TestClient, test_user):
        """Test connexion réussie"""
        response = client.post("/api/auth/login", json={
            "nom_utilisateur": "test_user",
            "mot_de_passe": "testpassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "utilisateur" in data
    
    def test_login_invalid_credentials(self, client: TestClient):
        """Test connexion avec identifiants invalides"""
        response = client.post("/api/auth/login", json={
            "nom_utilisateur": "invalid_user",
            "mot_de_passe": "wrong_password"
        })
        
        assert response.status_code == 401
        assert "Identifiants invalides" in response.json()["detail"]
    
    def test_refresh_token(self, client: TestClient, test_user, auth_headers):
        """Test rafraîchissement de token"""
        # D'abord se connecter pour obtenir un refresh token
        login_response = client.post("/api/auth/login", json={
            "nom_utilisateur": "test_user",
            "mot_de_passe": "testpassword"
        })
        
        refresh_token = login_response.json()["refresh_token"]
        
        # Utiliser le refresh token
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_logout(self, client: TestClient, auth_headers):
        """Test déconnexion"""
        response = client.post("/api/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        assert "Déconnexion réussie" in response.json()["message"]


class TestClientsAPI:
    """Tests pour les API des clients"""
    
    def test_create_client(self, client: TestClient, auth_headers):
        """Test création d'un client"""
        client_data = {
            "nom": "Nouveau Client",
            "email": "nouveau@example.com",
            "telephone": "0123456789",
            "adresse": "123 Rue Nouvelle, 75001 Paris",
            "statut": "actif"
        }
        
        response = client.post("/api/clients/", json=client_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["nom"] == "Nouveau Client"
        assert data["email"] == "nouveau@example.com"
        assert "id" in data
    
    def test_get_clients(self, client: TestClient, auth_headers, test_client):
        """Test récupération de la liste des clients"""
        response = client.get("/api/clients/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "clients" in data
        assert "total" in data
        assert "page" in data
        assert len(data["clients"]) >= 1
    
    def test_get_client_by_id(self, client: TestClient, auth_headers, test_client):
        """Test récupération d'un client par ID"""
        response = client.get(f"/api/clients/{test_client.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_client.id)
        assert data["nom"] == "Client Test"
    
    def test_update_client(self, client: TestClient, auth_headers, test_client):
        """Test mise à jour d'un client"""
        update_data = {
            "nom": "Client Modifié",
            "email": "modifie@example.com"
        }
        
        response = client.put(f"/api/clients/{test_client.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nom"] == "Client Modifié"
        assert data["email"] == "modifie@example.com"
    
    def test_delete_client(self, client: TestClient, auth_headers, test_client):
        """Test suppression d'un client"""
        response = client.delete(f"/api/clients/{test_client.id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Vérifier que le client a été supprimé
        response = client.get(f"/api/clients/{test_client.id}", headers=auth_headers)
        assert response.status_code == 404


class TestInterventionsAPI:
    """Tests pour les API des interventions"""
    
    def test_create_intervention(self, client: TestClient, auth_headers, test_client):
        """Test création d'une intervention"""
        intervention_data = {
            "client_id": str(test_client.id),
            "date_intervention": "2024-12-31T10:00:00Z",
            "type_intervention": "inspection",
            "statut": "planifie",
            "lieu": "123 Rue Test, 75001 Paris",
            "description": "Intervention de test"
        }
        
        response = client.post("/api/interventions/", json=intervention_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["client_id"] == str(test_client.id)
        assert data["type_intervention"] == "inspection"
        assert data["statut"] == "planifie"
    
    def test_get_interventions(self, client: TestClient, auth_headers, test_intervention):
        """Test récupération de la liste des interventions"""
        response = client.get("/api/interventions/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "interventions" in data
        assert "total" in data
        assert len(data["interventions"]) >= 1
    
    def test_change_intervention_status(self, client: TestClient, auth_headers, test_intervention):
        """Test changement de statut d'intervention"""
        response = client.post(
            f"/api/interventions/{test_intervention.id}/change-status",
            json={"nouveau_statut": "en_cours"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Statut changé avec succès"
        
        # Vérifier que le statut a été changé
        response = client.get(f"/api/interventions/{test_intervention.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["statut"] == "en_cours"


class TestAPIKeysAPI:
    """Tests pour les API des clés API"""
    
    def test_create_api_key(self, client: TestClient, auth_headers):
        """Test création d'une clé API"""
        api_key_data = {
            "nom": "Test API Key",
            "description": "Clé API pour les tests",
            "scopes": ["read", "write"],
            "limite_requetes_par_minute": 100,
            "limite_requetes_par_jour": 1000,
            "limite_requetes_par_mois": 30000
        }
        
        response = client.post("/api/api-keys/", json=api_key_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["nom"] == "Test API Key"
        assert data["scopes"] == ["read", "write"]
        assert "cle_api" in data
        assert data["statut"] == "active"
    
    def test_get_api_keys(self, client: TestClient, auth_headers, test_api_key):
        """Test récupération de la liste des clés API"""
        response = client.get("/api/api-keys/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "api_keys" in data
        assert "total" in data
        assert len(data["api_keys"]) >= 1
    
    def test_api_key_authentication(self, client: TestClient, test_api_key):
        """Test authentification avec clé API"""
        headers = {"X-API-Key": test_api_key.cle_api}
        
        response = client.get("/api/clients/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "clients" in data
    
    def test_api_key_invalid(self, client: TestClient):
        """Test avec clé API invalide"""
        headers = {"X-API-Key": "invalid_key"}
        
        response = client.get("/api/clients/", headers=headers)
        
        assert response.status_code == 401


class TestWebhooksAPI:
    """Tests pour les API des webhooks"""
    
    def test_create_webhook(self, client: TestClient, auth_headers):
        """Test création d'un webhook"""
        webhook_data = {
            "nom": "Test Webhook",
            "description": "Webhook pour les tests",
            "url": "https://webhook.site/test",
            "type_webhook": "intervention_created",
            "secret": "test_secret",
            "nombre_tentatives_max": 3,
            "delai_entre_tentatives": 60,
            "timeout": 30
        }
        
        response = client.post("/api/webhooks/", json=webhook_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["nom"] == "Test Webhook"
        assert data["url"] == "https://webhook.site/test"
        assert data["type_webhook"] == "intervention_created"
        assert data["statut"] == "active"
    
    def test_get_webhooks(self, client: TestClient, auth_headers, test_webhook):
        """Test récupération de la liste des webhooks"""
        response = client.get("/api/webhooks/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "webhooks" in data
        assert "total" in data
        assert len(data["webhooks"]) >= 1
    
    def test_test_webhook(self, client: TestClient, auth_headers, test_webhook):
        """Test d'un webhook"""
        test_data = {
            "type": "intervention_created",
            "timestamp": "2024-01-01T10:00:00Z",
            "data": {"test": True},
            "resource_id": "test-123"
        }
        
        response = client.post(
            f"/api/webhooks/{test_webhook.id}/test",
            json=test_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "Test webhook envoyé avec succès" in response.json()["message"]


class TestIntegrationsAPI:
    """Tests pour les API des intégrations"""
    
    def test_create_integration(self, client: TestClient, auth_headers):
        """Test création d'une intégration"""
        integration_data = {
            "nom": "Test Integration",
            "description": "Intégration pour les tests",
            "type_integration": "zapier",
            "configuration": {
                "webhook_url": "https://hooks.zapier.com/test",
                "api_key": "test_api_key"
            }
        }
        
        response = client.post("/api/integrations/", json=integration_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["nom"] == "Test Integration"
        assert data["type_integration"] == "zapier"
        assert data["statut"] == "active"
    
    def test_get_integrations(self, client: TestClient, auth_headers):
        """Test récupération de la liste des intégrations"""
        response = client.get("/api/integrations/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "integrations" in data
        assert "total" in data
    
    def test_get_available_types(self, client: TestClient, auth_headers):
        """Test récupération des types d'intégrations disponibles"""
        response = client.get("/api/integrations/types/available", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Vérifier que les types attendus sont présents
        types = [item["type"] for item in data]
        assert "zapier" in types
        assert "salesforce" in types
        assert "hubspot" in types


class TestErrorHandling:
    """Tests pour la gestion d'erreurs"""
    
    def test_404_error(self, client: TestClient, auth_headers):
        """Test erreur 404"""
        response = client.get("/api/clients/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        
        assert response.status_code == 404
        assert "Client non trouvé" in response.json()["detail"]
    
    def test_422_validation_error(self, client: TestClient, auth_headers):
        """Test erreur de validation"""
        client_data = {
            "nom": "",  # Nom vide
            "email": "invalid_email"  # Email invalide
        }
        
        response = client.post("/api/clients/", json=client_data, headers=auth_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_401_unauthorized(self, client: TestClient):
        """Test erreur d'autorisation"""
        response = client.get("/api/clients/")
        
        assert response.status_code == 401
    
    def test_403_forbidden(self, client: TestClient, auth_headers):
        """Test erreur d'accès interdit"""
        # Créer un utilisateur avec des permissions limitées
        # et tester l'accès à des ressources restreintes
        pass


class TestPagination:
    """Tests pour la pagination"""
    
    def test_pagination_default(self, client: TestClient, auth_headers):
        """Test pagination par défaut"""
        response = client.get("/api/clients/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "size" in data
        assert "total" in data
        assert "pages" in data
        assert data["page"] == 1
        assert data["size"] == 10
    
    def test_pagination_custom(self, client: TestClient, auth_headers):
        """Test pagination personnalisée"""
        response = client.get("/api/clients/?page=2&size=5", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["size"] == 5
    
    def test_pagination_invalid(self, client: TestClient, auth_headers):
        """Test pagination avec paramètres invalides"""
        response = client.get("/api/clients/?page=0&size=0", headers=auth_headers)
        
        assert response.status_code == 422  # Validation error


class TestSearchAndFilters:
    """Tests pour la recherche et les filtres"""
    
    def test_search_clients(self, client: TestClient, auth_headers, test_client):
        """Test recherche de clients"""
        response = client.get("/api/clients/?search=Test", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["clients"]) >= 1
        assert any("Test" in client["nom"] for client in data["clients"])
    
    def test_filter_by_status(self, client: TestClient, auth_headers, test_client):
        """Test filtrage par statut"""
        response = client.get("/api/clients/?statut=actif", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert all(client["statut"] == "actif" for client in data["clients"])
    
    def test_combined_filters(self, client: TestClient, auth_headers, test_client):
        """Test combinaison de filtres"""
        response = client.get("/api/clients/?search=Test&statut=actif", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert all(
            "Test" in client["nom"] and client["statut"] == "actif" 
            for client in data["clients"]
        )
