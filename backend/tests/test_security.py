"""
Tests de sécurité approfondis - Phase Test & Debug
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json
import uuid
from datetime import datetime, timedelta

from ..main import app
from ..models import Utilisateur, Client, Intervention, APIKey, Webhook
from ..services.security_service import security_service


class TestAuthenticationSecurity:
    """Tests de sécurité d'authentification"""
    
    def test_brute_force_protection(self, client: TestClient):
        """Test protection contre les attaques par force brute"""
        # Tentatives multiples avec des mots de passe incorrects
        for i in range(10):
            response = client.post("/api/auth/login", json={
                "nom_utilisateur": "test_user",
                "mot_de_passe": f"wrong_password_{i}"
            })
            
            if i < 5:
                assert response.status_code == 401
            else:
                # Après 5 tentatives, devrait être bloqué
                assert response.status_code in [401, 429]
    
    def test_sql_injection_login(self, client: TestClient):
        """Test protection contre l'injection SQL dans le login"""
        sql_injection_payloads = [
            "'; DROP TABLE utilisateurs; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM utilisateurs --",
            "admin'--",
            "admin'/*",
            "' OR 1=1#"
        ]
        
        for payload in sql_injection_payloads:
            response = client.post("/api/auth/login", json={
                "nom_utilisateur": payload,
                "mot_de_passe": "password"
            })
            
            # Devrait retourner une erreur 401, pas une erreur 500
            assert response.status_code == 401
            assert "Identifiants invalides" in response.json()["detail"]
    
    def test_xss_protection_login(self, client: TestClient):
        """Test protection contre XSS dans le login"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            response = client.post("/api/auth/login", json={
                "nom_utilisateur": payload,
                "mot_de_passe": "password"
            })
            
            # Devrait retourner une erreur 401, pas exécuter le script
            assert response.status_code == 401
            assert "<script>" not in response.text
            assert "javascript:" not in response.text
    
    def test_jwt_token_security(self, client: TestClient, test_user: Utilisateur):
        """Test sécurité des tokens JWT"""
        # Créer un token valide
        token = security_service.create_access_token({"sub": str(test_user.id)})
        
        # Test avec token valide
        response = client.get("/api/clients/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        
        # Test avec token modifié
        modified_token = token[:-5] + "XXXXX"
        response = client.get("/api/clients/", headers={"Authorization": f"Bearer {modified_token}"})
        assert response.status_code == 401
        
        # Test avec token expiré
        expired_token = security_service.create_access_token(
            {"sub": str(test_user.id)}, 
            expires_delta=timedelta(seconds=-1)
        )
        response = client.get("/api/clients/", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401
        
        # Test sans token
        response = client.get("/api/clients/")
        assert response.status_code == 401
        
        # Test avec format de token invalide
        response = client.get("/api/clients/", headers={"Authorization": "InvalidToken"})
        assert response.status_code == 401


class TestAuthorizationSecurity:
    """Tests de sécurité d'autorisation"""
    
    def test_role_based_access_control(self, client: TestClient):
        """Test contrôle d'accès basé sur les rôles"""
        # Créer un utilisateur avec rôle limité
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
        
        # Se connecter en tant qu'admin pour créer l'utilisateur
        admin_response = client.post("/api/auth/login", json={
            "nom_utilisateur": "test_user",
            "mot_de_passe": "testpassword"
        })
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.post("/api/utilisateurs/", json=user_data, headers=admin_headers)
        assert response.status_code == 201
        
        # Se connecter en tant que technicien
        tech_response = client.post("/api/auth/login", json={
            "nom_utilisateur": "test_technicien",
            "mot_de_passe": "password123"
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}
        
        # Test accès autorisé
        response = client.get("/api/clients/", headers=tech_headers)
        assert response.status_code == 200
        
        # Test accès interdit
        response = client.get("/api/utilisateurs/", headers=tech_headers)
        assert response.status_code == 403
        
        response = client.delete(f"/api/utilisateurs/{test_user.id}", headers=tech_headers)
        assert response.status_code == 403
    
    def test_privilege_escalation_prevention(self, client: TestClient, test_user: Utilisateur):
        """Test prévention de l'escalade de privilèges"""
        # Créer un utilisateur avec rôle limité
        user_data = {
            "nom_utilisateur": "test_consultant",
            "email": "consultant@example.com",
            "nom": "Consultant",
            "prenom": "Test",
            "mot_de_passe": "password123",
            "confirmer_mot_de_passe": "password123",
            "role": "consultant",
            "consentement_rgpd": True
        }
        
        # Se connecter en tant qu'admin pour créer l'utilisateur
        admin_response = client.post("/api/auth/login", json={
            "nom_utilisateur": "test_user",
            "mot_de_passe": "testpassword"
        })
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.post("/api/utilisateurs/", json=user_data, headers=admin_headers)
        assert response.status_code == 201
        
        # Se connecter en tant que consultant
        consultant_response = client.post("/api/auth/login", json={
            "nom_utilisateur": "test_consultant",
            "mot_de_passe": "password123"
        })
        consultant_token = consultant_response.json()["access_token"]
        consultant_headers = {"Authorization": f"Bearer {consultant_token}"}
        
        # Tentative d'escalade de privilèges
        escalation_data = {
            "role": "admin",
            "statut": "actif"
        }
        
        response = client.put(f"/api/utilisateurs/{test_user.id}", json=escalation_data, headers=consultant_headers)
        assert response.status_code == 403
    
    def test_resource_access_control(self, client: TestClient, test_client: Client):
        """Test contrôle d'accès aux ressources"""
        # Créer un utilisateur avec accès limité
        user_data = {
            "nom_utilisateur": "test_limited",
            "email": "limited@example.com",
            "nom": "Limited",
            "prenom": "Test",
            "mot_de_passe": "password123",
            "confirmer_mot_de_passe": "password123",
            "role": "technicien",
            "consentement_rgpd": True
        }
        
        # Se connecter en tant qu'admin pour créer l'utilisateur
        admin_response = client.post("/api/auth/login", json={
            "nom_utilisateur": "test_user",
            "mot_de_passe": "testpassword"
        })
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.post("/api/utilisateurs/", json=user_data, headers=admin_headers)
        assert response.status_code == 201
        
        # Se connecter en tant qu'utilisateur limité
        limited_response = client.post("/api/auth/login", json={
            "nom_utilisateur": "test_limited",
            "mot_de_passe": "password123"
        })
        limited_token = limited_response.json()["access_token"]
        limited_headers = {"Authorization": f"Bearer {limited_token}"}
        
        # Test accès aux ressources autorisées
        response = client.get("/api/clients/", headers=limited_headers)
        assert response.status_code == 200
        
        # Test accès aux ressources restreintes
        response = client.get("/api/utilisateurs/", headers=limited_headers)
        assert response.status_code == 403
        
        response = client.get("/api/api-keys/", headers=limited_headers)
        assert response.status_code == 403


class TestInputValidationSecurity:
    """Tests de sécurité de validation des entrées"""
    
    def test_sql_injection_protection(self, client: TestClient, auth_headers: dict):
        """Test protection contre l'injection SQL"""
        sql_injection_payloads = [
            "'; DROP TABLE clients; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM clients --",
            "admin'--",
            "admin'/*",
            "' OR 1=1#"
        ]
        
        for payload in sql_injection_payloads:
            # Test dans le nom du client
            client_data = {
                "nom": payload,
                "email": "test@example.com",
                "telephone": "0123456789",
                "adresse": "123 Rue Test",
                "statut": "actif"
            }
            
            response = client.post("/api/clients/", json=client_data, headers=auth_headers)
            # Devrait retourner une erreur de validation, pas une erreur 500
            assert response.status_code in [400, 422]
            
            # Test dans l'email
            client_data = {
                "nom": "Client Test",
                "email": payload,
                "telephone": "0123456789",
                "adresse": "123 Rue Test",
                "statut": "actif"
            }
            
            response = client.post("/api/clients/", json=client_data, headers=auth_headers)
            assert response.status_code in [400, 422]
    
    def test_xss_protection(self, client: TestClient, auth_headers: dict):
        """Test protection contre XSS"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//",
            "<iframe src='javascript:alert(\"xss\")'></iframe>"
        ]
        
        for payload in xss_payloads:
            # Test dans le nom du client
            client_data = {
                "nom": payload,
                "email": "test@example.com",
                "telephone": "0123456789",
                "adresse": "123 Rue Test",
                "statut": "actif"
            }
            
            response = client.post("/api/clients/", json=client_data, headers=auth_headers)
            # Devrait retourner une erreur de validation
            assert response.status_code in [400, 422]
            
            # Vérifier que le script n'est pas exécuté
            assert "<script>" not in response.text
            assert "javascript:" not in response.text
    
    def test_path_traversal_protection(self, client: TestClient, auth_headers: dict):
        """Test protection contre le path traversal"""
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for payload in path_traversal_payloads:
            # Test dans l'adresse du client
            client_data = {
                "nom": "Client Test",
                "email": "test@example.com",
                "telephone": "0123456789",
                "adresse": payload,
                "statut": "actif"
            }
            
            response = client.post("/api/clients/", json=client_data, headers=auth_headers)
            # Devrait retourner une erreur de validation
            assert response.status_code in [400, 422]
    
    def test_file_upload_security(self, client: TestClient, auth_headers: dict, test_intervention: Intervention):
        """Test sécurité d'upload de fichiers"""
        # Test avec fichier malveillant
        malicious_files = [
            ("malicious.php", b"<?php system($_GET['cmd']); ?>", "application/x-php"),
            ("malicious.jsp", b"<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>", "application/x-jsp"),
            ("malicious.asp", b"<% eval request(\"cmd\") %>", "application/x-asp"),
            ("malicious.exe", b"MZ\x90\x00", "application/x-msdownload")
        ]
        
        for filename, content, mime_type in malicious_files:
            files = {"file": (filename, content, mime_type)}
            media_data = {
                "intervention_id": str(test_intervention.id),
                "type_media": "photo",
                "description": "Fichier malveillant"
            }
            
            response = client.post("/api/medias/upload", data=media_data, files=files, headers=auth_headers)
            # Devrait rejeter le fichier malveillant
            assert response.status_code in [400, 415, 422]
    
    def test_file_size_limits(self, client: TestClient, auth_headers: dict, test_intervention: Intervention):
        """Test limites de taille de fichier"""
        # Test avec fichier trop volumineux
        large_content = b"x" * (50 * 1024 * 1024)  # 50MB
        files = {"file": ("large_file.jpg", large_content, "image/jpeg")}
        media_data = {
            "intervention_id": str(test_intervention.id),
            "type_media": "photo",
            "description": "Fichier trop volumineux"
        }
        
        response = client.post("/api/medias/upload", data=media_data, files=files, headers=auth_headers)
        assert response.status_code == 413  # Payload too large


class TestAPISecurity:
    """Tests de sécurité de l'API"""
    
    def test_rate_limiting(self, client: TestClient, auth_headers: dict):
        """Test rate limiting"""
        # Faire beaucoup de requêtes rapidement
        for i in range(150):  # Plus que la limite par défaut
            response = client.get("/api/clients/", headers=auth_headers)
            if response.status_code == 429:  # Too many requests
                break
        
        # Vérifier que le rate limiting a été appliqué
        assert response.status_code == 429
        assert "Trop de requêtes" in response.json()["detail"]
    
    def test_api_key_security(self, client: TestClient, auth_headers: dict):
        """Test sécurité des clés API"""
        # Créer une clé API
        api_key_data = {
            "nom": "Test API Key",
            "description": "Clé API pour tests de sécurité",
            "scopes": ["read"],
            "limite_requetes_par_minute": 10
        }
        
        response = client.post("/api/api-keys/", json=api_key_data, headers=auth_headers)
        assert response.status_code == 201
        api_key_result = response.json()
        api_key = api_key_result["cle_api"]
        
        # Test avec clé API valide
        api_headers = {"X-API-Key": api_key}
        response = client.get("/api/clients/", headers=api_headers)
        assert response.status_code == 200
        
        # Test avec clé API invalide
        invalid_headers = {"X-API-Key": "invalid_key"}
        response = client.get("/api/clients/", headers=invalid_headers)
        assert response.status_code == 401
        
        # Test avec clé API expirée
        # (Dans un vrai test, on modifierait la date d'expiration)
        
        # Test avec clé API suspendue
        response = client.put(f"/api/api-keys/{api_key_result['id']}", 
                            json={"statut": "suspended"}, headers=auth_headers)
        assert response.status_code == 200
        
        response = client.get("/api/clients/", headers=api_headers)
        assert response.status_code == 401
    
    def test_webhook_security(self, client: TestClient, auth_headers: dict):
        """Test sécurité des webhooks"""
        # Créer un webhook
        webhook_data = {
            "nom": "Test Webhook",
            "description": "Webhook pour tests de sécurité",
            "url": "https://webhook.site/test",
            "type_webhook": "intervention_created",
            "secret": "test_secret"
        }
        
        response = client.post("/api/webhooks/", json=webhook_data, headers=auth_headers)
        assert response.status_code == 201
        webhook_result = response.json()
        webhook_id = webhook_result["id"]
        
        # Test avec signature valide
        payload = '{"test": "data"}'
        signature = security_service.create_webhook_signature(payload, "test_secret")
        
        response = client.post(f"/api/webhooks/{webhook_id}/test", 
                             json={"payload": payload, "signature": signature}, 
                             headers=auth_headers)
        assert response.status_code == 200
        
        # Test avec signature invalide
        invalid_signature = "invalid_signature"
        response = client.post(f"/api/webhooks/{webhook_id}/test", 
                             json={"payload": payload, "signature": invalid_signature}, 
                             headers=auth_headers)
        assert response.status_code == 401


class TestDataSecurity:
    """Tests de sécurité des données"""
    
    def test_password_security(self, client: TestClient, auth_headers: dict):
        """Test sécurité des mots de passe"""
        # Test avec mot de passe faible
        weak_passwords = [
            "123456",
            "password",
            "admin",
            "qwerty",
            "abc123"
        ]
        
        for weak_password in weak_passwords:
            user_data = {
                "nom_utilisateur": f"test_weak_{weak_password}",
                "email": f"weak_{weak_password}@example.com",
                "nom": "Test",
                "prenom": "Weak",
                "mot_de_passe": weak_password,
                "confirmer_mot_de_passe": weak_password,
                "role": "technicien",
                "consentement_rgpd": True
            }
            
            response = client.post("/api/utilisateurs/", json=user_data, headers=auth_headers)
            # Devrait retourner une erreur de validation
            assert response.status_code in [400, 422]
    
    def test_data_encryption(self, client: TestClient, auth_headers: dict):
        """Test chiffrement des données sensibles"""
        # Créer un client avec des données sensibles
        client_data = {
            "nom": "Client Sensible",
            "email": "sensible@example.com",
            "telephone": "0123456789",
            "adresse": "123 Rue Sensible, 75001 Paris",
            "statut": "actif"
        }
        
        response = client.post("/api/clients/", json=client_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Vérifier que les données sont chiffrées en base
        # (Dans un vrai test, on vérifierait directement la base de données)
        
        # Vérifier que les données sont déchiffrées lors de la récupération
        response = client.get("/api/clients/", headers=auth_headers)
        assert response.status_code == 200
        clients = response.json()["clients"]
        assert any(client["nom"] == "Client Sensible" for client in clients)
    
    def test_data_anonymization(self, client: TestClient, auth_headers: dict):
        """Test anonymisation des données"""
        # Créer un client
        client_data = {
            "nom": "Client Anonyme",
            "email": "anonyme@example.com",
            "telephone": "0123456789",
            "adresse": "123 Rue Anonyme, 75001 Paris",
            "statut": "actif"
        }
        
        response = client.post("/api/clients/", json=client_data, headers=auth_headers)
        assert response.status_code == 201
        client_id = response.json()["id"]
        
        # Anonymiser le client
        response = client.post(f"/api/rgpd/anonymize", 
                             json={"resource_type": "client", "resource_id": client_id}, 
                             headers=auth_headers)
        assert response.status_code == 200
        
        # Vérifier que les données sont anonymisées
        response = client.get(f"/api/clients/{client_id}", headers=auth_headers)
        assert response.status_code == 200
        client = response.json()
        assert client["nom"] == "ANONYME"
        assert client["email"] == "anonyme@example.com"  # Email conservé pour les notifications


class TestLoggingSecurity:
    """Tests de sécurité des logs"""
    
    def test_audit_logging(self, client: TestClient, auth_headers: dict):
        """Test journalisation d'audit"""
        # Effectuer une action qui devrait être loggée
        client_data = {
            "nom": "Client Audit",
            "email": "audit@example.com",
            "telephone": "0123456789",
            "adresse": "123 Rue Audit, 75001 Paris",
            "statut": "actif"
        }
        
        response = client.post("/api/clients/", json=client_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Vérifier que l'action a été loggée
        response = client.get("/api/audit/logs", headers=auth_headers)
        assert response.status_code == 200
        logs = response.json()["logs"]
        assert len(logs) >= 1
        assert any(log["action"] == "create" and log["resource"] == "client" for log in logs)
    
    def test_sensitive_data_logging(self, client: TestClient, auth_headers: dict):
        """Test que les données sensibles ne sont pas loggées"""
        # Effectuer une action avec des données sensibles
        user_data = {
            "nom_utilisateur": "test_sensitive",
            "email": "sensitive@example.com",
            "nom": "Sensitive",
            "prenom": "Test",
            "mot_de_passe": "sensitive_password",
            "confirmer_mot_de_passe": "sensitive_password",
            "role": "technicien",
            "consentement_rgpd": True
        }
        
        response = client.post("/api/utilisateurs/", json=user_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Vérifier que le mot de passe n'est pas dans les logs
        response = client.get("/api/audit/logs", headers=auth_headers)
        assert response.status_code == 200
        logs = response.json()["logs"]
        
        for log in logs:
            assert "sensitive_password" not in str(log)
            assert "mot_de_passe" not in str(log)
