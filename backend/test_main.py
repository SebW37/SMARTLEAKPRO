"""
Tests unitaires pour SmartLeakPro - Phase 1
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models import Client, Intervention, Inspection

# Configuration de test
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Moteur de test
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    """Override de la dépendance de base de données pour les tests"""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """Créer un event loop pour les tests async"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """Configurer la base de données de test"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    """Client HTTP pour les tests"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestAuth:
    """Tests d'authentification"""
    
    async def test_login_success(self, client: AsyncClient):
        """Test de connexion réussie"""
        response = await client.post("/api/auth/test-login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_failure(self, client: AsyncClient):
        """Test de connexion échouée"""
        response = await client.post("/api/auth/test-login", json={
            "username": "wrong",
            "password": "wrong"
        })
        assert response.status_code == 401


class TestClients:
    """Tests des clients"""
    
    async def test_create_client(self, client: AsyncClient, setup_database):
        """Test de création de client"""
        # Se connecter d'abord
        login_response = await client.post("/api/auth/test-login", json={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # Créer un client
        client_data = {
            "nom": "Test Client",
            "email": "test@example.com",
            "telephone": "0123456789"
        }
        
        response = await client.post(
            "/api/clients/",
            json=client_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nom"] == "Test Client"
        assert data["email"] == "test@example.com"
    
    async def test_get_clients(self, client: AsyncClient, setup_database):
        """Test de récupération des clients"""
        # Se connecter d'abord
        login_response = await client.post("/api/auth/test-login", json={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # Récupérer les clients
        response = await client.get(
            "/api/clients/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "clients" in data
        assert "total" in data


class TestInterventions:
    """Tests des interventions"""
    
    async def test_create_intervention(self, client: AsyncClient, setup_database):
        """Test de création d'intervention"""
        # Se connecter d'abord
        login_response = await client.post("/api/auth/test-login", json={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # Créer un client d'abord
        client_data = {
            "nom": "Test Client",
            "email": "test@example.com"
        }
        client_response = await client.post(
            "/api/clients/",
            json=client_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        client_id = client_response.json()["id"]
        
        # Créer une intervention
        intervention_data = {
            "client_id": client_id,
            "date_intervention": "2024-01-15T10:00:00Z",
            "type_intervention": "inspection",
            "description": "Test intervention",
            "priorite": "normale"
        }
        
        response = await client.post(
            "/api/interventions/",
            json=intervention_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type_intervention"] == "inspection"
        assert data["statut"] == "planifié"
    
    async def test_get_interventions(self, client: AsyncClient, setup_database):
        """Test de récupération des interventions"""
        # Se connecter d'abord
        login_response = await client.post("/api/auth/test-login", json={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # Récupérer les interventions
        response = await client.get(
            "/api/interventions/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "interventions" in data
        assert "total" in data
    
    async def test_change_intervention_status(self, client: AsyncClient, setup_database):
        """Test de changement de statut d'intervention"""
        # Se connecter d'abord
        login_response = await client.post("/api/auth/test-login", json={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # Créer un client et une intervention
        client_data = {"nom": "Test Client", "email": "test@example.com"}
        client_response = await client.post(
            "/api/clients/",
            json=client_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        client_id = client_response.json()["id"]
        
        intervention_data = {
            "client_id": client_id,
            "date_intervention": "2024-01-15T10:00:00Z",
            "type_intervention": "inspection"
        }
        intervention_response = await client.post(
            "/api/interventions/",
            json=intervention_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        intervention_id = intervention_response.json()["id"]
        
        # Changer le statut
        status_change = {
            "nouveau_statut": "en_cours",
            "commentaire": "Début de l'intervention"
        }
        
        response = await client.post(
            f"/api/interventions/{intervention_id}/change-status",
            json=status_change,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["statut"] == "en_cours"


if __name__ == "__main__":
    pytest.main([__file__])
