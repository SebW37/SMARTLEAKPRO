"""
Tests unitaires pour les modèles - Phase 8
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import (
    Utilisateur, Client, Intervention, RendezVous, Rapport, Media, 
    APIKey, Webhook, LogAPI, Integration,
    RoleUtilisateur, StatutUtilisateur, TypeIntervention, StatutIntervention,
    TypeMedia, StatutMedia, TypeWebhook, StatutWebhook, TypeIntegration
)


class TestUtilisateur:
    """Tests pour le modèle Utilisateur"""
    
    @pytest.mark.asyncio
    async def test_create_utilisateur(self, db_session: AsyncSession):
        """Test création d'un utilisateur"""
        user = Utilisateur(
            nom_utilisateur="test_user",
            email="test@example.com",
            nom="Test",
            prenom="User",
            mot_de_passe_hash="hashed_password",
            role=RoleUtilisateur.ADMIN,
            statut=StatutUtilisateur.ACTIF,
            consentement_rgpd=True,
            date_consentement=datetime.utcnow()
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.nom_utilisateur == "test_user"
        assert user.email == "test@example.com"
        assert user.role == RoleUtilisateur.ADMIN
        assert user.statut == StatutUtilisateur.ACTIF
    
    @pytest.mark.asyncio
    async def test_utilisateur_is_active(self, db_session: AsyncSession):
        """Test méthode is_active"""
        user = Utilisateur(
            nom_utilisateur="test_user",
            email="test@example.com",
            nom="Test",
            prenom="User",
            mot_de_passe_hash="hashed_password",
            role=RoleUtilisateur.ADMIN,
            statut=StatutUtilisateur.ACTIF,
            consentement_rgpd=True
        )
        
        assert user.is_active() is True
        
        user.statut = StatutUtilisateur.SUSPENDU
        assert user.is_active() is False
    
    @pytest.mark.asyncio
    async def test_utilisateur_can_access(self, db_session: AsyncSession):
        """Test méthode can_access"""
        user = Utilisateur(
            nom_utilisateur="test_user",
            email="test@example.com",
            nom="Test",
            prenom="User",
            mot_de_passe_hash="hashed_password",
            role=RoleUtilisateur.ADMIN,
            statut=StatutUtilisateur.ACTIF,
            consentement_rgpd=True
        )
        
        # Admin peut tout faire
        assert user.can_access("clients", "read") is True
        assert user.can_access("clients", "write") is True
        assert user.can_access("admin", "delete") is True
        
        # Test avec un rôle non-admin
        user.role = RoleUtilisateur.TECHNICIEN
        assert user.can_access("clients", "read") is True
        assert user.can_access("admin", "delete") is False


class TestClient:
    """Tests pour le modèle Client"""
    
    @pytest.mark.asyncio
    async def test_create_client(self, db_session: AsyncSession):
        """Test création d'un client"""
        client = Client(
            nom="Client Test",
            email="client@example.com",
            telephone="0123456789",
            adresse="123 Rue Test, 75001 Paris",
            statut="actif"
        )
        
        db_session.add(client)
        await db_session.commit()
        await db_session.refresh(client)
        
        assert client.id is not None
        assert client.nom == "Client Test"
        assert client.email == "client@example.com"
        assert client.statut == "actif"
    
    @pytest.mark.asyncio
    async def test_client_to_dict(self, db_session: AsyncSession):
        """Test méthode to_dict"""
        client = Client(
            nom="Client Test",
            email="client@example.com",
            telephone="0123456789",
            adresse="123 Rue Test, 75001 Paris",
            statut="actif"
        )
        
        client_dict = client.to_dict()
        
        assert isinstance(client_dict, dict)
        assert client_dict["nom"] == "Client Test"
        assert client_dict["email"] == "client@example.com"
        assert "id" in client_dict
        assert "date_creation" in client_dict


class TestIntervention:
    """Tests pour le modèle Intervention"""
    
    @pytest.mark.asyncio
    async def test_create_intervention(self, db_session: AsyncSession, test_client: Client):
        """Test création d'une intervention"""
        intervention = Intervention(
            client_id=test_client.id,
            date_intervention=datetime.utcnow() + timedelta(days=1),
            type_intervention=TypeIntervention.INSPECTION,
            statut=StatutIntervention.PLANIFIE,
            lieu="123 Rue Test, 75001 Paris",
            description="Intervention de test"
        )
        
        db_session.add(intervention)
        await db_session.commit()
        await db_session.refresh(intervention)
        
        assert intervention.id is not None
        assert intervention.client_id == test_client.id
        assert intervention.type_intervention == TypeIntervention.INSPECTION
        assert intervention.statut == StatutIntervention.PLANIFIE
    
    @pytest.mark.asyncio
    async def test_intervention_workflow(self, db_session: AsyncSession, test_client: Client):
        """Test workflow des statuts d'intervention"""
        intervention = Intervention(
            client_id=test_client.id,
            date_intervention=datetime.utcnow() + timedelta(days=1),
            type_intervention=TypeIntervention.INSPECTION,
            statut=StatutIntervention.PLANIFIE,
            lieu="123 Rue Test, 75001 Paris",
            description="Intervention de test"
        )
        
        # Test transition planifié -> en cours
        intervention.statut = StatutIntervention.EN_COURS
        assert intervention.statut == StatutIntervention.EN_COURS
        
        # Test transition en cours -> validé
        intervention.statut = StatutIntervention.VALIDE
        assert intervention.statut == StatutIntervention.VALIDE


class TestAPIKey:
    """Tests pour le modèle APIKey"""
    
    @pytest.mark.asyncio
    async def test_create_api_key(self, db_session: AsyncSession, test_user: Utilisateur):
        """Test création d'une clé API"""
        api_key = APIKey(
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
        
        assert api_key.id is not None
        assert api_key.nom == "Test API Key"
        assert api_key.cle_api == "sk_test_123456789"
        assert api_key.utilisateur_id == test_user.id
    
    @pytest.mark.asyncio
    async def test_api_key_is_active(self, db_session: AsyncSession, test_user: Utilisateur):
        """Test méthode is_active"""
        api_key = APIKey(
            nom="Test API Key",
            cle_api="sk_test_123456789",
            secret_key="secret_test_123456789",
            utilisateur_id=test_user.id,
            scopes=["read"],
            statut="active"
        )
        
        assert api_key.is_active() is True
        
        api_key.statut = "inactive"
        assert api_key.is_active() is False
    
    @pytest.mark.asyncio
    async def test_api_key_has_scope(self, db_session: AsyncSession, test_user: Utilisateur):
        """Test méthode has_scope"""
        api_key = APIKey(
            nom="Test API Key",
            cle_api="sk_test_123456789",
            secret_key="secret_test_123456789",
            utilisateur_id=test_user.id,
            scopes=["read", "write"],
            statut="active"
        )
        
        assert api_key.has_scope("read") is True
        assert api_key.has_scope("write") is True
        assert api_key.has_scope("admin") is False
        
        # Test avec scope admin
        api_key.scopes = ["admin"]
        assert api_key.has_scope("read") is True  # Admin a tous les droits
        assert api_key.has_scope("write") is True
        assert api_key.has_scope("admin") is True


class TestWebhook:
    """Tests pour le modèle Webhook"""
    
    @pytest.mark.asyncio
    async def test_create_webhook(self, db_session: AsyncSession, test_user: Utilisateur):
        """Test création d'un webhook"""
        webhook = Webhook(
            nom="Test Webhook",
            description="Webhook pour les tests",
            url="https://webhook.site/test",
            type_webhook=TypeWebhook.INTERVENTION_CREATED,
            utilisateur_id=test_user.id,
            statut=StatutWebhook.ACTIVE
        )
        
        db_session.add(webhook)
        await db_session.commit()
        await db_session.refresh(webhook)
        
        assert webhook.id is not None
        assert webhook.nom == "Test Webhook"
        assert webhook.url == "https://webhook.site/test"
        assert webhook.type_webhook == TypeWebhook.INTERVENTION_CREATED
    
    @pytest.mark.asyncio
    async def test_webhook_is_active(self, db_session: AsyncSession, test_user: Utilisateur):
        """Test méthode is_active"""
        webhook = Webhook(
            nom="Test Webhook",
            url="https://webhook.site/test",
            type_webhook=TypeWebhook.INTERVENTION_CREATED,
            utilisateur_id=test_user.id,
            statut=StatutWebhook.ACTIVE
        )
        
        assert webhook.is_active() is True
        
        webhook.statut = StatutWebhook.DISABLED
        assert webhook.is_active() is False
    
    @pytest.mark.asyncio
    async def test_webhook_should_trigger(self, db_session: AsyncSession, test_user: Utilisateur):
        """Test méthode should_trigger"""
        webhook = Webhook(
            nom="Test Webhook",
            url="https://webhook.site/test",
            type_webhook=TypeWebhook.INTERVENTION_CREATED,
            utilisateur_id=test_user.id,
            statut=StatutWebhook.ACTIVE
        )
        
        # Test sans conditions
        event_data = {"type": "intervention_created", "data": {"id": "123"}}
        assert webhook.should_trigger(event_data) is True
        
        # Test avec conditions
        webhook.conditions = [
            {"field": "data.id", "operator": "equals", "value": "123"}
        ]
        assert webhook.should_trigger(event_data) is True
        
        # Test avec condition non remplie
        event_data["data"]["id"] = "456"
        assert webhook.should_trigger(event_data) is False


class TestMedia:
    """Tests pour le modèle Media"""
    
    @pytest.mark.asyncio
    async def test_create_media(self, db_session: AsyncSession, test_intervention: Intervention):
        """Test création d'un média"""
        media = Media(
            intervention_id=test_intervention.id,
            nom_fichier="test_image.jpg",
            nom_original="test_image.jpg",
            type_media=TypeMedia.PHOTO,
            statut=StatutMedia.UPLOADED,
            url_fichier="/uploads/test_image.jpg",
            taille_fichier=1024000,
            mime_type="image/jpeg"
        )
        
        db_session.add(media)
        await db_session.commit()
        await db_session.refresh(media)
        
        assert media.id is not None
        assert media.intervention_id == test_intervention.id
        assert media.nom_fichier == "test_image.jpg"
        assert media.type_media == TypeMedia.PHOTO
        assert media.statut == StatutMedia.UPLOADED


class TestRapport:
    """Tests pour le modèle Rapport"""
    
    @pytest.mark.asyncio
    async def test_create_rapport(self, db_session: AsyncSession, test_intervention: Intervention):
        """Test création d'un rapport"""
        rapport = Rapport(
            intervention_id=test_intervention.id,
            type_rapport="inspection",
            contenu={"titre": "Rapport de test", "contenu": "Contenu du rapport"},
            auteur_rapport="test_user",
            statut="brouillon"
        )
        
        db_session.add(rapport)
        await db_session.commit()
        await db_session.refresh(rapport)
        
        assert rapport.id is not None
        assert rapport.intervention_id == test_intervention.id
        assert rapport.type_rapport == "inspection"
        assert rapport.statut == "brouillon"
