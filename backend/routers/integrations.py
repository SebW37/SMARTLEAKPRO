"""
Router pour la gestion des intégrations - Phase 7 API & Intégrations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Integration, TypeIntegration, TypeAction, NiveauLog
from ..schemas import (
    IntegrationCreate, IntegrationUpdate, IntegrationResponse, IntegrationListResponse
)
from ..auth import get_current_user, get_current_active_user, get_client_ip, get_user_agent
from ..services.api_service import api_service
from ..services.security_service import security_service

router = APIRouter()


@router.post("/", response_model=IntegrationResponse)
async def create_integration(
    integration_data: IntegrationCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Créer une nouvelle intégration"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "integrations", "create"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Créer l'intégration
        integration = await api_service.create_integration(
            db=db,
            utilisateur_id=current_user.get("user_id"),
            nom=integration_data.nom,
            description=integration_data.description,
            type_integration=integration_data.type_integration,
            configuration=integration_data.configuration
        )
        
        # Logger la création
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.CREATION, "integrations", "create",
            f"Intégration créée: {integration.nom}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True,
            str(integration.id)
        )
        
        return IntegrationResponse.from_orm(integration)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.get("/", response_model=IntegrationListResponse)
async def list_integrations(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Taille de page"),
    type_integration: Optional[str] = Query(None, description="Filtrer par type"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    search: Optional[str] = Query(None, description="Recherche textuelle"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Lister les intégrations avec pagination et filtres"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "integrations", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Construction de la requête
        query = select(Integration)
        count_query = select(func.count(Integration.id))
        
        # Filtres
        filters = []
        
        # Filtrer par utilisateur (sauf admin)
        if current_user.get("role") != "admin":
            filters.append(Integration.utilisateur_id == current_user.get("user_id"))
        
        if type_integration:
            try:
                type_enum = TypeIntegration(type_integration)
                filters.append(Integration.type_integration == type_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Type d'intégration invalide")
        
        if statut:
            filters.append(Integration.statut == statut)
        
        if search:
            search_filter = or_(
                Integration.nom.ilike(f"%{search}%"),
                Integration.description.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        # Appliquer les filtres
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Pagination
        offset = (page - 1) * size
        query = query.order_by(desc(Integration.date_creation)).offset(offset).limit(size)
        
        # Exécution des requêtes
        result = await db.execute(query)
        integrations = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Calcul du nombre de pages
        pages = (total + size - 1) // size
        
        return IntegrationListResponse(
            integrations=[IntegrationResponse.from_orm(integration) for integration in integrations],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Récupérer une intégration par ID"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "integrations", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer l'intégration
        result = await db.execute(select(Integration).where(Integration.id == integration_id))
        integration = result.scalar_one_or_none()
        
        if not integration:
            raise HTTPException(status_code=404, detail="Intégration non trouvée")
        
        # Vérifier que l'utilisateur peut accéder à cette intégration
        if (current_user.get("role") != "admin" and 
            str(integration.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        return IntegrationResponse.from_orm(integration)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: UUID,
    integration_data: IntegrationUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Mettre à jour une intégration"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "integrations", "write"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer l'intégration
        result = await db.execute(select(Integration).where(Integration.id == integration_id))
        integration = result.scalar_one_or_none()
        
        if not integration:
            raise HTTPException(status_code=404, detail="Intégration non trouvée")
        
        # Vérifier que l'utilisateur peut modifier cette intégration
        if (current_user.get("role") != "admin" and 
            str(integration.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Sauvegarder les anciennes valeurs pour l'audit
        anciennes_valeurs = integration.to_dict()
        
        # Mise à jour des champs
        update_data = integration_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(integration, field, value)
        
        await db.commit()
        await db.refresh(integration)
        
        # Logger la modification
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.MODIFICATION, "integrations", "update",
            f"Intégration modifiée: {integration.nom}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True,
            str(integration_id),
            anciennes_valeurs,
            integration.to_dict()
        )
        
        return IntegrationResponse.from_orm(integration)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{integration_id}", status_code=204)
async def delete_integration(
    integration_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Supprimer une intégration"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "integrations", "delete"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer l'intégration
        result = await db.execute(select(Integration).where(Integration.id == integration_id))
        integration = result.scalar_one_or_none()
        
        if not integration:
            raise HTTPException(status_code=404, detail="Intégration non trouvée")
        
        # Vérifier que l'utilisateur peut supprimer cette intégration
        if (current_user.get("role") != "admin" and 
            str(integration.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Logger la suppression
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.SUPPRESSION, "integrations", "delete",
            f"Intégration supprimée: {integration.nom}",
            NiveauLog.WARNING,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True,
            str(integration_id)
        )
        
        # Supprimer l'intégration
        await db.delete(integration)
        await db.commit()
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


@router.post("/{integration_id}/sync", response_model=dict)
async def sync_integration(
    integration_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Synchroniser une intégration"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "integrations", "write"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer l'intégration
        result = await db.execute(select(Integration).where(Integration.id == integration_id))
        integration = result.scalar_one_or_none()
        
        if not integration:
            raise HTTPException(status_code=404, detail="Intégration non trouvée")
        
        # Vérifier que l'utilisateur peut synchroniser cette intégration
        if (current_user.get("role") != "admin" and 
            str(integration.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Effectuer la synchronisation selon le type
        success = await _perform_sync(integration)
        
        if success:
            # Mettre à jour les métadonnées
            integration.derniere_synchronisation = datetime.utcnow()
            integration.nombre_synchronisations += 1
            await db.commit()
            
            # Logger la synchronisation
            await security_service.log_audit(
                db, current_user.get("user_id"), TypeAction.MODIFICATION, "integrations", "sync",
                f"Intégration synchronisée: {integration.nom}",
                NiveauLog.INFO,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                succes=True,
                str(integration_id)
            )
            
            return {"message": "Synchronisation réussie"}
        else:
            raise HTTPException(status_code=500, detail="Échec de la synchronisation")
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la synchronisation: {str(e)}")


@router.get("/types/available", response_model=List[dict])
async def get_available_integration_types():
    """Récupérer les types d'intégrations disponibles"""
    return [
        {
            "type": "zapier",
            "name": "Zapier",
            "description": "Automatisation de workflows avec Zapier",
            "configuration_fields": [
                {"name": "webhook_url", "type": "string", "required": True, "description": "URL du webhook Zapier"},
                {"name": "api_key", "type": "string", "required": False, "description": "Clé API Zapier"}
            ],
            "supported_events": ["intervention_created", "intervention_updated", "rapport_generated"]
        },
        {
            "type": "n8n",
            "name": "n8n",
            "description": "Workflow automation avec n8n",
            "configuration_fields": [
                {"name": "webhook_url", "type": "string", "required": True, "description": "URL du webhook n8n"},
                {"name": "api_key", "type": "string", "required": False, "description": "Clé API n8n"}
            ],
            "supported_events": ["*"]
        },
        {
            "type": "salesforce",
            "name": "Salesforce",
            "description": "Intégration CRM Salesforce",
            "configuration_fields": [
                {"name": "instance_url", "type": "string", "required": True, "description": "URL de l'instance Salesforce"},
                {"name": "client_id", "type": "string", "required": True, "description": "Client ID OAuth"},
                {"name": "client_secret", "type": "string", "required": True, "description": "Client Secret OAuth"},
                {"name": "username", "type": "string", "required": True, "description": "Nom d'utilisateur"},
                {"name": "password", "type": "string", "required": True, "description": "Mot de passe"},
                {"name": "security_token", "type": "string", "required": True, "description": "Token de sécurité"}
            ],
            "supported_events": ["client_created", "client_updated", "intervention_created"]
        },
        {
            "type": "hubspot",
            "name": "HubSpot",
            "description": "Intégration CRM HubSpot",
            "configuration_fields": [
                {"name": "api_key", "type": "string", "required": True, "description": "Clé API HubSpot"},
                {"name": "portal_id", "type": "string", "required": True, "description": "ID du portail HubSpot"}
            ],
            "supported_events": ["client_created", "client_updated", "intervention_created"]
        },
        {
            "type": "mailchimp",
            "name": "Mailchimp",
            "description": "Intégration emailing Mailchimp",
            "configuration_fields": [
                {"name": "api_key", "type": "string", "required": True, "description": "Clé API Mailchimp"},
                {"name": "list_id", "type": "string", "required": True, "description": "ID de la liste Mailchimp"},
                {"name": "server_prefix", "type": "string", "required": True, "description": "Préfixe du serveur (ex: us1)"}
            ],
            "supported_events": ["client_created", "intervention_created", "rapport_generated"]
        },
        {
            "type": "mqtt",
            "name": "MQTT",
            "description": "Intégration IoT via MQTT",
            "configuration_fields": [
                {"name": "broker_url", "type": "string", "required": True, "description": "URL du broker MQTT"},
                {"name": "port", "type": "integer", "required": True, "description": "Port du broker"},
                {"name": "username", "type": "string", "required": False, "description": "Nom d'utilisateur MQTT"},
                {"name": "password", "type": "string", "required": False, "description": "Mot de passe MQTT"},
                {"name": "topic_prefix", "type": "string", "required": True, "description": "Préfixe des topics"}
            ],
            "supported_events": ["intervention_created", "intervention_status_changed", "media_uploaded"]
        },
        {
            "type": "custom",
            "name": "Personnalisé",
            "description": "Intégration personnalisée",
            "configuration_fields": [
                {"name": "webhook_url", "type": "string", "required": True, "description": "URL de destination"},
                {"name": "auth_type", "type": "string", "required": False, "description": "Type d'authentification"},
                {"name": "auth_token", "type": "string", "required": False, "description": "Token d'authentification"}
            ],
            "supported_events": ["*"]
        }
    ]


@router.get("/{integration_id}/status", response_model=dict)
async def get_integration_status(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Récupérer le statut d'une intégration"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "integrations", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer l'intégration
        result = await db.execute(select(Integration).where(Integration.id == integration_id))
        integration = result.scalar_one_or_none()
        
        if not integration:
            raise HTTPException(status_code=404, detail="Intégration non trouvée")
        
        # Vérifier que l'utilisateur peut accéder à cette intégration
        if (current_user.get("role") != "admin" and 
            str(integration.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Vérifier le statut de l'intégration
        status = await _check_integration_health(integration)
        
        return {
            "integration_id": str(integration.id),
            "nom": integration.nom,
            "type": integration.type_integration.value,
            "statut": integration.statut,
            "derniere_synchronisation": integration.derniere_synchronisation.isoformat() if integration.derniere_synchronisation else None,
            "nombre_synchronisations": integration.nombre_synchronisations,
            "health_status": status,
            "configuration_valid": True  # À implémenter selon le type
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification: {str(e)}")


async def _perform_sync(integration: Integration) -> bool:
    """Effectuer la synchronisation d'une intégration"""
    try:
        # Implémentation simplifiée - à étendre selon les besoins
        if integration.type_integration == TypeIntegration.ZAPIER:
            return await _sync_zapier(integration)
        elif integration.type_integration == TypeIntegration.N8N:
            return await _sync_n8n(integration)
        elif integration.type_integration == TypeIntegration.SALESFORCE:
            return await _sync_salesforce(integration)
        elif integration.type_integration == TypeIntegration.HUBSPOT:
            return await _sync_hubspot(integration)
        elif integration.type_integration == TypeIntegration.MAILCHIMP:
            return await _sync_mailchimp(integration)
        elif integration.type_integration == TypeIntegration.MQTT:
            return await _sync_mqtt(integration)
        else:
            return await _sync_custom(integration)
    except Exception as e:
        return False


async def _sync_zapier(integration: Integration) -> bool:
    """Synchroniser avec Zapier"""
    # Implémentation Zapier
    return True


async def _sync_n8n(integration: Integration) -> bool:
    """Synchroniser avec n8n"""
    # Implémentation n8n
    return True


async def _sync_salesforce(integration: Integration) -> bool:
    """Synchroniser avec Salesforce"""
    # Implémentation Salesforce
    return True


async def _sync_hubspot(integration: Integration) -> bool:
    """Synchroniser avec HubSpot"""
    # Implémentation HubSpot
    return True


async def _sync_mailchimp(integration: Integration) -> bool:
    """Synchroniser avec Mailchimp"""
    # Implémentation Mailchimp
    return True


async def _sync_mqtt(integration: Integration) -> bool:
    """Synchroniser avec MQTT"""
    # Implémentation MQTT
    return True


async def _sync_custom(integration: Integration) -> bool:
    """Synchroniser avec intégration personnalisée"""
    # Implémentation personnalisée
    return True


async def _check_integration_health(integration: Integration) -> str:
    """Vérifier la santé d'une intégration"""
    # Implémentation de vérification de santé
    return "healthy"


async def _get_user_from_db(db: AsyncSession, user_id: str):
    """Récupérer un utilisateur depuis la base de données"""
    if not user_id:
        return None
    
    from ..models import Utilisateur
    result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
    return result.scalar_one_or_none()
