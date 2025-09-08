"""
Configuration des tests - Phase 8
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
from fastapi.testclient import TestClient

from ..main import app
from ..database import get_db, Base
from ..models import Utilisateur, Client, Intervention, RendezVous, Rapport, Media, APIKey, Webhook
from ..services.security_service import security_service
import uuid
from datetime import datetime, timedelta


# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Créer un event loop pour les tests asynchrones"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Créer une session de base de données pour les tests"""
    # Créer les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Créer une session
    async with TestingSessionLocal() as session:
        yield session
    
    # Nettoyer après le test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def override_get_db(db_session: AsyncSession):
    """Override de la dépendance get_db"""
    async def _override_get_db():
        yield db_session
    
    return _override_get_db


@pytest.fixture(scope="function")
def client(override_get_db) -> TestClient:
    """Client de test FastAPI"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Client asynchrone de test"""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> Utilisateur:
    """Créer un utilisateur de test"""
    user = Utilisateur(
        id=uuid.uuid4(),
        nom_utilisateur="test_user",
        email="test@example.com",
        nom="Test",
        prenom="User",
        mot_de_passe_hash=security_service.get_password_hash("testpassword"),
        role="admin",
        statut="actif",
        consentement_rgpd=True,
        date_consentement=datetime.utcnow()
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest.fixture(scope="function")
async def test_client(db_session: AsyncSession) -> Client:
    """Créer un client de test"""
    client = Client(
        id=uuid.uuid4(),
        nom="Client Test",
        email="client@example.com",
        telephone="0123456789",
        adresse="123 Rue Test, 75001 Paris",
        statut="actif"
    )
    
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    
    return client


@pytest.fixture(scope="function")
async def test_intervention(db_session: AsyncSession, test_client: Client) -> Intervention:
    """Créer une intervention de test"""
    intervention = Intervention(
        id=uuid.uuid4(),
        client_id=test_client.id,
        date_intervention=datetime.utcnow() + timedelta(days=1),
        type_intervention="inspection",
        statut="planifie",
        lieu="123 Rue Test, 75001 Paris",
        description="Intervention de test"
    )
    
    db_session.add(intervention)
    await db_session.commit()
    await db_session.refresh(intervention)
    
    return intervention


@pytest.fixture(scope="function")
async def test_api_key(db_session: AsyncSession, test_user: Utilisateur) -> APIKey:
    """Créer une clé API de test"""
    api_key = APIKey(
        id=uuid.uuid4(),
        nom="Test API Key",
        description="Clé API pour les tests",
        cle_api="sk_test_123456789",
        secret_key="secret_test_123456789",
        utilisateur_id=test_user.id,
        scopes=["read", "write"],
        statut="active"
    )
    
    db_session.add(api_key)
    await db_session.commit()
    await db_session.refresh(api_key)
    
    return api_key


@pytest.fixture(scope="function")
async def test_webhook(db_session: AsyncSession, test_user: Utilisateur) -> Webhook:
    """Créer un webhook de test"""
    webhook = Webhook(
        id=uuid.uuid4(),
        nom="Test Webhook",
        description="Webhook pour les tests",
        url="https://webhook.site/test",
        type_webhook="intervention_created",
        utilisateur_id=test_user.id,
        statut="active"
    )
    
    db_session.add(webhook)
    await db_session.commit()
    await db_session.refresh(webhook)
    
    return webhook


@pytest.fixture(scope="function")
def auth_headers(test_user: Utilisateur) -> dict:
    """Headers d'authentification pour les tests"""
    # Créer un token JWT pour l'utilisateur de test
    token = security_service.create_access_token(
        data={"sub": str(test_user.id), "username": test_user.nom_utilisateur}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def api_key_headers(test_api_key: APIKey) -> dict:
    """Headers avec clé API pour les tests"""
    return {"X-API-Key": test_api_key.cle_api}
