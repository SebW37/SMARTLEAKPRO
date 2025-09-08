"""
Router pour la gestion des clés API - Phase 7 API & Intégrations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..database import get_db
from ..models import APIKey, StatutAPIKey, TypeAction, NiveauLog
from ..schemas import (
    APIKeyCreate, APIKeyUpdate, APIKeyResponse, APIKeyListResponse, APIStats
)
from ..auth import get_current_user, get_current_active_user, get_client_ip, get_user_agent
from ..services.api_service import api_service
from ..services.security_service import security_service

router = APIRouter()


@router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    api_key_data: APIKeyCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Créer une nouvelle clé API"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "api_keys", "create"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Créer la clé API
        api_key = await api_service.create_api_key(
            db=db,
            utilisateur_id=current_user.get("user_id"),
            nom=api_key_data.nom,
            description=api_key_data.description,
            scopes=api_key_data.scopes,
            limite_requetes_par_minute=api_key_data.limite_requetes_par_minute,
            limite_requetes_par_jour=api_key_data.limite_requetes_par_jour,
            limite_requetes_par_mois=api_key_data.limite_requetes_par_mois,
            date_expiration=api_key_data.date_expiration,
            ips_autorisees=api_key_data.ips_autorisees,
            user_agents_autorises=api_key_data.user_agents_autorises
        )
        
        # Logger la création
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.CREATION, "api_keys", "create",
            f"Clé API créée: {api_key.nom}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True,
            str(api_key.id)
        )
        
        return APIKeyResponse.from_orm(api_key)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.get("/", response_model=APIKeyListResponse)
async def list_api_keys(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Taille de page"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    search: Optional[str] = Query(None, description="Recherche textuelle"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Lister les clés API avec pagination et filtres"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "api_keys", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Construction de la requête
        query = select(APIKey)
        count_query = select(func.count(APIKey.id))
        
        # Filtres
        filters = []
        
        # Filtrer par utilisateur (sauf admin)
        if current_user.get("role") != "admin":
            filters.append(APIKey.utilisateur_id == current_user.get("user_id"))
        
        if statut:
            try:
                statut_enum = StatutAPIKey(statut)
                filters.append(APIKey.statut == statut_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Statut invalide")
        
        if search:
            search_filter = or_(
                APIKey.nom.ilike(f"%{search}%"),
                APIKey.description.ilike(f"%{search}%"),
                APIKey.cle_api.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        # Appliquer les filtres
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Pagination
        offset = (page - 1) * size
        query = query.order_by(desc(APIKey.date_creation)).offset(offset).limit(size)
        
        # Exécution des requêtes
        result = await db.execute(query)
        api_keys = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Calcul du nombre de pages
        pages = (total + size - 1) // size
        
        return APIKeyListResponse(
            api_keys=[APIKeyResponse.from_orm(key) for key in api_keys],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Récupérer une clé API par ID"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "api_keys", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer la clé API
        result = await db.execute(select(APIKey).where(APIKey.id == key_id))
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(status_code=404, detail="Clé API non trouvée")
        
        # Vérifier que l'utilisateur peut accéder à cette clé
        if (current_user.get("role") != "admin" and 
            str(api_key.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        return APIKeyResponse.from_orm(api_key)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.put("/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: UUID,
    api_key_data: APIKeyUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Mettre à jour une clé API"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "api_keys", "write"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer la clé API
        result = await db.execute(select(APIKey).where(APIKey.id == key_id))
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(status_code=404, detail="Clé API non trouvée")
        
        # Vérifier que l'utilisateur peut modifier cette clé
        if (current_user.get("role") != "admin" and 
            str(api_key.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Sauvegarder les anciennes valeurs pour l'audit
        anciennes_valeurs = api_key.to_dict()
        
        # Mise à jour des champs
        update_data = api_key_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(api_key, field, value)
        
        await db.commit()
        await db.refresh(api_key)
        
        # Logger la modification
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.MODIFICATION, "api_keys", "update",
            f"Clé API modifiée: {api_key.nom}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True,
            str(key_id),
            anciennes_valeurs,
            api_key.to_dict()
        )
        
        return APIKeyResponse.from_orm(api_key)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{key_id}", status_code=204)
async def delete_api_key(
    key_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Supprimer une clé API"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "api_keys", "delete"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer la clé API
        result = await db.execute(select(APIKey).where(APIKey.id == key_id))
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(status_code=404, detail="Clé API non trouvée")
        
        # Vérifier que l'utilisateur peut supprimer cette clé
        if (current_user.get("role") != "admin" and 
            str(api_key.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Logger la suppression
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.SUPPRESSION, "api_keys", "delete",
            f"Clé API supprimée: {api_key.nom}",
            NiveauLog.WARNING,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True,
            str(key_id)
        )
        
        # Supprimer la clé API
        await db.delete(api_key)
        await db.commit()
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


@router.post("/{key_id}/regenerate", response_model=APIKeyResponse)
async def regenerate_api_key(
    key_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Régénérer une clé API (nouvelle clé et secret)"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "api_keys", "write"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer la clé API
        result = await db.execute(select(APIKey).where(APIKey.id == key_id))
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(status_code=404, detail="Clé API non trouvée")
        
        # Vérifier que l'utilisateur peut modifier cette clé
        if (current_user.get("role") != "admin" and 
            str(api_key.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Sauvegarder les anciennes valeurs pour l'audit
        anciennes_valeurs = api_key.to_dict()
        
        # Régénérer la clé et le secret
        api_key.cle_api = api_service._generate_api_key()
        api_key.secret_key = api_service._generate_secret_key()
        
        await db.commit()
        await db.refresh(api_key)
        
        # Logger la régénération
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.MODIFICATION, "api_keys", "regenerate",
            f"Clé API régénérée: {api_key.nom}",
            NiveauLog.WARNING,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True,
            str(key_id),
            anciennes_valeurs,
            api_key.to_dict()
        )
        
        return APIKeyResponse.from_orm(api_key)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la régénération: {str(e)}")


@router.post("/{key_id}/toggle-status", response_model=dict)
async def toggle_api_key_status(
    key_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Activer/Désactiver une clé API"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "api_keys", "write"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer la clé API
        result = await db.execute(select(APIKey).where(APIKey.id == key_id))
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(status_code=404, detail="Clé API non trouvée")
        
        # Vérifier que l'utilisateur peut modifier cette clé
        if (current_user.get("role") != "admin" and 
            str(api_key.utilisateur_id) != current_user.get("user_id")):
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        # Changer le statut
        ancien_statut = api_key.statut
        if api_key.statut == StatutAPIKey.ACTIVE:
            api_key.statut = StatutAPIKey.INACTIVE
            nouveau_statut = "inactif"
        else:
            api_key.statut = StatutAPIKey.ACTIVE
            nouveau_statut = "actif"
        
        await db.commit()
        
        # Logger le changement
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.MODIFICATION, "api_keys", "toggle_status",
            f"Statut changé de {ancien_statut.value} à {nouveau_statut} pour: {api_key.nom}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True,
            str(key_id)
        )
        
        return {"message": f"Statut changé en {nouveau_statut}"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors du changement: {str(e)}")


@router.get("/stats/usage", response_model=APIStats)
async def get_api_usage_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Récupérer les statistiques d'utilisation de l'API"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "api_keys", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer les statistiques
        stats = await api_service.get_api_stats(db, current_user.get("user_id"))
        return APIStats(**stats)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/scopes/available", response_model=List[dict])
async def get_available_scopes():
    """Récupérer les scopes disponibles pour les clés API"""
    return [
        {
            "scope": "read",
            "description": "Lecture seule des données",
            "resources": ["clients", "interventions", "planning", "rapports", "medias"]
        },
        {
            "scope": "write",
            "description": "Lecture et écriture des données",
            "resources": ["clients", "interventions", "planning", "rapports", "medias"]
        },
        {
            "scope": "admin",
            "description": "Accès administrateur complet",
            "resources": ["*"]
        },
        {
            "scope": "webhooks",
            "description": "Gestion des webhooks",
            "resources": ["webhooks"]
        },
        {
            "scope": "integrations",
            "description": "Gestion des intégrations",
            "resources": ["integrations"]
        }
    ]


async def _get_user_from_db(db: AsyncSession, user_id: str):
    """Récupérer un utilisateur depuis la base de données"""
    if not user_id:
        return None
    
    from ..models import Utilisateur
    result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
    return result.scalar_one_or_none()
