"""
Router pour la gestion des webhooks - Phase 7 API & Intégrations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Webhook, WebhookExecution, TypeWebhook, StatutWebhook, TypeAction, NiveauLog
from ..schemas import (
    WebhookCreate, WebhookUpdate, WebhookResponse, WebhookListResponse,
    WebhookExecutionResponse, WebhookEvent
)
from ..auth import get_current_user, get_current_active_user, get_client_ip, get_user_agent
from ..services.api_service import api_service
from ..services.security_service import security_service

router = APIRouter()


@router.post("/", response_model=WebhookResponse)
async def create_webhook(
    webhook_data: WebhookCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Créer un nouveau webhook"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "webhooks", "create"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Créer le webhook
        webhook = await api_service.create_webhook(
            db=db,
            utilisateur_id=current_user.get("user_id"),
            nom=webhook_data.nom,
            description=webhook_data.description,
            url=webhook_data.url,
            type_webhook=webhook_data.type_webhook,
            secret=webhook_data.secret,
            headers_customises=webhook_data.headers_customises,
            conditions=webhook_data.conditions,
            ressources_filtrees=webhook_data.ressources_filtrees,
            nombre_tentatives_max=webhook_data.nombre_tentatives_max,
            delai_entre_tentatives=webhook_data.delai_entre_tentatives,
            timeout=webhook_data.timeout
        )
        
        # Logger la création
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.CREATION, "webhooks", "create",
            f"Webhook créé: {webhook.nom}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True,
            str(webhook.id)
        )
        
        return WebhookResponse.from_orm(webhook)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.get("/", response_model=WebhookListResponse)
async def list_webhooks(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Taille de page"),
    type_webhook: Optional[str] = Query(None, description="Filtrer par type"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    search: Optional[str] = Query(None, description="Recherche textuelle"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Lister les webhooks avec pagination et filtres"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "webhooks", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Construction de la requête
        query = select(Webhook)
        count_query = select(func.count(Webhook.id))
        
        # Filtres
        filters = []
        
        # Filtrer par utilisateur (sauf admin)
        if current_user.get("role") != "admin":
            filters.append(Webhook.utilisateur_id == current_user.get("user_id"))
        
        if type_webhook:
            try:
                type_enum = TypeWebhook(type_webhook)
                filters.append(Webhook.type_webhook == type_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Type de webhook invalide")
        
        if statut:
            try:
                statut_enum = StatutWebhook(statut)
                filters.append(Webhook.statut == statut_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Statut invalide")
        
        if search:
            search_filter = or_(
                Webhook.nom.ilike(f"%{search}%"),
                Webhook.description.ilike(f"%{search}%"),
                Webhook.url.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        # Appliquer les filtres
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Pagination
        offset = (page - 1) * size
        query = query.order_by(desc(Webhook.date_creation)).offset(offset).limit(size)
        
        # Exécution des requêtes
        result = await db.execute(query)
        webhooks = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Calcul du nombre de pages
        pages = (total + size - 1) // size
        
        return WebhookListResponse(
            webhooks=[WebhookResponse.from_orm(webhook) for webhook in webhooks],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Récupérer un webhook par ID"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "webhooks", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer le webhook
        result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
        webhook = result.scalar_one_or_none()
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook non trouvé")
        
        # Vérifier que l'utilisateur peut accéder à ce webhook
        if (current_user.get("role") != "admin" and 
            str(webhook.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        return WebhookResponse.from_orm(webhook)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: UUID,
    webhook_data: WebhookUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Mettre à jour un webhook"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "webhooks", "write"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer le webhook
        result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
        webhook = result.scalar_one_or_none()
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook non trouvé")
        
        # Vérifier que l'utilisateur peut modifier ce webhook
        if (current_user.get("role") != "admin" and 
            str(webhook.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Sauvegarder les anciennes valeurs pour l'audit
        anciennes_valeurs = webhook.to_dict()
        
        # Mise à jour des champs
        update_data = webhook_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(webhook, field, value)
        
        await db.commit()
        await db.refresh(webhook)
        
        # Logger la modification
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.MODIFICATION, "webhooks", "update",
            f"Webhook modifié: {webhook.nom}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True,
            str(webhook_id),
            anciennes_valeurs,
            webhook.to_dict()
        )
        
        return WebhookResponse.from_orm(webhook)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{webhook_id}", status_code=204)
async def delete_webhook(
    webhook_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Supprimer un webhook"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "webhooks", "delete"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer le webhook
        result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
        webhook = result.scalar_one_or_none()
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook non trouvé")
        
        # Vérifier que l'utilisateur peut supprimer ce webhook
        if (current_user.get("role") != "admin" and 
            str(webhook.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Logger la suppression
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.SUPPRESSION, "webhooks", "delete",
            f"Webhook supprimé: {webhook.nom}",
            NiveauLog.WARNING,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True,
            str(webhook_id)
        )
        
        # Supprimer le webhook
        await db.delete(webhook)
        await db.commit()
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


@router.post("/{webhook_id}/test", response_model=dict)
async def test_webhook(
    webhook_id: UUID,
    test_data: Optional[dict] = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Tester un webhook avec des données de test"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "webhooks", "write"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer le webhook
        result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
        webhook = result.scalar_one_or_none()
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook non trouvé")
        
        # Vérifier que l'utilisateur peut tester ce webhook
        if (current_user.get("role") != "admin" and 
            str(webhook.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Données de test par défaut
        if not test_data:
            test_data = {
                "type": webhook.type_webhook.value,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {"test": True, "message": "Test webhook"},
                "resource_id": "test-123"
            }
        
        # Déclencher le webhook
        await api_service.trigger_webhook(
            db, webhook.type_webhook.value, test_data, "test-123", current_user.get("user_id")
        )
        
        # Logger le test
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.MODIFICATION, "webhooks", "test",
            f"Test webhook: {webhook.nom}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else None,
            succes=True,
            str(webhook_id)
        )
        
        return {"message": "Test webhook envoyé avec succès"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du test: {str(e)}")


@router.get("/{webhook_id}/executions", response_model=List[WebhookExecutionResponse])
async def get_webhook_executions(
    webhook_id: UUID,
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Taille de page"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Récupérer les exécutions d'un webhook"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "webhooks", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer le webhook
        result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
        webhook = result.scalar_one_or_none()
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook non trouvé")
        
        # Vérifier que l'utilisateur peut accéder à ce webhook
        if (current_user.get("role") != "admin" and 
            str(webhook.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Récupérer les exécutions
        offset = (page - 1) * size
        result = await db.execute(
            select(WebhookExecution)
            .where(WebhookExecution.webhook_id == webhook_id)
            .order_by(desc(WebhookExecution.date_debut))
            .offset(offset)
            .limit(size)
        )
        executions = result.scalars().all()
        
        return [WebhookExecutionResponse.from_orm(execution) for execution in executions]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/types/available", response_model=List[dict])
async def get_available_webhook_types():
    """Récupérer les types de webhooks disponibles"""
    return [
        {
            "type": "intervention_created",
            "description": "Nouvelle intervention créée",
            "data_fields": ["id", "client_id", "date_intervention", "type_intervention", "statut"]
        },
        {
            "type": "intervention_updated",
            "description": "Intervention mise à jour",
            "data_fields": ["id", "client_id", "changes", "updated_fields"]
        },
        {
            "type": "intervention_status_changed",
            "description": "Statut d'intervention changé",
            "data_fields": ["id", "ancien_statut", "nouveau_statut", "client_id"]
        },
        {
            "type": "rapport_generated",
            "description": "Rapport généré",
            "data_fields": ["id", "intervention_id", "type_rapport", "url", "taille"]
        },
        {
            "type": "media_uploaded",
            "description": "Média uploadé",
            "data_fields": ["id", "intervention_id", "type_media", "nom_fichier", "taille"]
        },
        {
            "type": "user_created",
            "description": "Utilisateur créé",
            "data_fields": ["id", "nom_utilisateur", "email", "role"]
        },
        {
            "type": "user_updated",
            "description": "Utilisateur mis à jour",
            "data_fields": ["id", "nom_utilisateur", "changes", "updated_fields"]
        },
        {
            "type": "client_created",
            "description": "Client créé",
            "data_fields": ["id", "nom", "email", "telephone"]
        },
        {
            "type": "client_updated",
            "description": "Client mis à jour",
            "data_fields": ["id", "nom", "changes", "updated_fields"]
        },
        {
            "type": "planning_created",
            "description": "Rendez-vous créé",
            "data_fields": ["id", "intervention_id", "client_id", "date_heure_debut"]
        },
        {
            "type": "planning_updated",
            "description": "Rendez-vous mis à jour",
            "data_fields": ["id", "intervention_id", "changes", "updated_fields"]
        }
    ]


@router.post("/trigger/{event_type}", response_model=dict)
async def trigger_webhook_event(
    event_type: str,
    event_data: WebhookEvent,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Déclencher manuellement un événement webhook (Admin uniquement)"""
    try:
        # Vérifier les permissions (Admin uniquement)
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Déclencher l'événement
        await api_service.trigger_webhook(
            db, event_type, event_data.data, event_data.resource_id, event_data.user_id
        )
        
        return {"message": f"Événement {event_type} déclenché avec succès"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du déclenchement: {str(e)}")


async def _get_user_from_db(db: AsyncSession, user_id: str):
    """Récupérer un utilisateur depuis la base de données"""
    if not user_id:
        return None
    
    from ..models import Utilisateur
    result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
    return result.scalar_one_or_none()
