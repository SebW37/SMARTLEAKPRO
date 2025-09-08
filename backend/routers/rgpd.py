"""
Router pour la gestion RGPD - Phase 6 Sécurité
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..database import get_db
from ..models import ConsentementRGPD, Utilisateur, TypeAction, NiveauLog
from ..schemas import (
    ConsentementRGPDCreate, ConsentementRGPDResponse, RGPDExportRequest, RGPDAnonymizeRequest
)
from ..auth import get_current_user, get_current_active_user, get_client_ip, get_user_agent
from ..services.security_service import security_service

router = APIRouter()


@router.post("/consentements", response_model=ConsentementRGPDResponse)
async def create_consentement(
    consentement_data: ConsentementRGPDCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Créer un consentement RGPD"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
        
        # Créer le consentement
        consentement = await security_service.create_consentement(
            db, user_id, consentement_data.type_consentement,
            consentement_data.consentement_donne,
            get_client_ip(request),
            get_user_agent(request),
            "web"
        )
        
        # Logger la création du consentement
        await security_service.log_audit(
            db, user_id, TypeAction.CREATION, "rgpd", "create_consentement",
            f"Consentement {consentement_data.type_consentement} créé",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True
        )
        
        return ConsentementRGPDResponse.from_orm(consentement)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.get("/consentements", response_model=List[ConsentementRGPDResponse])
async def get_consentements(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les consentements de l'utilisateur"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
        
        result = await db.execute(
            select(ConsentementRGPD)
            .where(ConsentementRGPD.utilisateur_id == user_id)
            .order_by(desc(ConsentementRGPD.date_creation))
        )
        consentements = result.scalars().all()
        
        return [ConsentementRGPDResponse.from_orm(consentement) for consentement in consentements]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.post("/consentements/{consentement_id}/revoke", response_model=dict)
async def revoke_consentement(
    consentement_id: UUID,
    raison: Optional[str] = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Révoquer un consentement RGPD"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
        
        # Récupérer le consentement
        result = await db.execute(
            select(ConsentementRGPD).where(
                and_(
                    ConsentementRGPD.id == consentement_id,
                    ConsentementRGPD.utilisateur_id == user_id
                )
            )
        )
        consentement = result.scalar_one_or_none()
        
        if not consentement:
            raise HTTPException(status_code=404, detail="Consentement non trouvé")
        
        # Révoquer le consentement
        success = await security_service.revoke_consentement(
            db, user_id, consentement.type_consentement, raison
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Impossible de révoquer le consentement")
        
        # Logger la révocation
        await security_service.log_audit(
            db, user_id, TypeAction.MODIFICATION, "rgpd", "revoke_consentement",
            f"Consentement {consentement.type_consentement} révoqué",
            NiveauLog.INFO,
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else None,
            succes=True
        )
        
        return {"message": "Consentement révoqué avec succès"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la révocation: {str(e)}")


@router.post("/export-data", response_model=dict)
async def export_user_data(
    export_data: RGPDExportRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Exporter les données personnelles de l'utilisateur (RGPD)"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
        
        # Vérifier que l'utilisateur demande ses propres données
        if str(export_data.utilisateur_id) != user_id:
            raise HTTPException(status_code=403, detail="Impossible d'exporter les données d'un autre utilisateur")
        
        # Exporter les données
        user_data = await security_service.get_user_data_export(db, user_id)
        
        # Logger l'export
        await security_service.log_audit(
            db, user_id, TypeAction.EXPORT, "rgpd", "export_data",
            f"Export des données personnelles demandé",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True
        )
        
        return {
            "message": "Données exportées avec succès",
            "format": export_data.format,
            "data": user_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export: {str(e)}")


@router.post("/anonymize-data", response_model=dict)
async def anonymize_user_data(
    anonymize_data: RGPDAnonymizeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Anonymiser les données personnelles de l'utilisateur (RGPD)"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
        
        # Vérifier que l'utilisateur demande l'anonymisation de ses propres données
        if str(anonymize_data.utilisateur_id) != user_id:
            raise HTTPException(status_code=403, detail="Impossible d'anonymiser les données d'un autre utilisateur")
        
        # Anonymiser les données
        success = await security_service.anonymize_user_data(db, user_id, anonymize_data.raison)
        
        if not success:
            raise HTTPException(status_code=400, detail="Impossible d'anonymiser les données")
        
        # Logger l'anonymisation
        await security_service.log_audit(
            db, user_id, TypeAction.MODIFICATION, "rgpd", "anonymize_data",
            f"Anonymisation des données demandée - Raison: {anonymize_data.raison}",
            NiveauLog.WARNING,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True
        )
        
        return {"message": "Données anonymisées avec succès"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'anonymisation: {str(e)}")


@router.get("/consent-types", response_model=List[dict])
async def get_consent_types():
    """Récupérer les types de consentement disponibles"""
    return [
        {
            "type": "cookies",
            "description": "Cookies et technologies similaires",
            "required": True
        },
        {
            "type": "marketing",
            "description": "Communications marketing et publicitaires",
            "required": False
        },
        {
            "type": "analytics",
            "description": "Analyse et statistiques d'utilisation",
            "required": False
        },
        {
            "type": "personalization",
            "description": "Personnalisation de l'expérience utilisateur",
            "required": False
        },
        {
            "type": "third_party",
            "description": "Partage avec des tiers",
            "required": False
        }
    ]


@router.get("/privacy-policy", response_model=dict)
async def get_privacy_policy():
    """Récupérer la politique de confidentialité"""
    return {
        "version": "1.0",
        "last_updated": "2024-01-01",
        "content": {
            "introduction": "Cette politique de confidentialité décrit comment SmartLeakPro collecte, utilise et protège vos données personnelles.",
            "data_collection": "Nous collectons les données nécessaires au fonctionnement de l'application de gestion de détection de fuite.",
            "data_usage": "Vos données sont utilisées pour fournir nos services, améliorer l'application et respecter nos obligations légales.",
            "data_sharing": "Nous ne partageons vos données qu'avec votre consentement explicite ou pour des raisons légales.",
            "data_retention": "Nous conservons vos données aussi longtemps que nécessaire pour fournir nos services.",
            "your_rights": "Vous avez le droit d'accéder, modifier, supprimer ou exporter vos données personnelles.",
            "contact": "Pour toute question sur cette politique, contactez-nous à privacy@smartleakpro.com"
        }
    }


@router.get("/data-usage", response_model=dict)
async def get_data_usage_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les statistiques d'utilisation des données de l'utilisateur"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
        
        # Statistiques des consentements
        consentements_result = await db.execute(
            select(ConsentementRGPD)
            .where(ConsentementRGPD.utilisateur_id == user_id)
        )
        consentements = consentements_result.scalars().all()
        
        # Statistiques des logs d'audit
        logs_result = await db.execute(
            select(func.count())
            .where(ConsentementRGPD.utilisateur_id == user_id)
        )
        total_logs = logs_result.scalar()
        
        # Récupérer l'utilisateur
        user_result = await db.execute(
            select(Utilisateur).where(Utilisateur.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        return {
            "utilisateur": {
                "nom": user.nom,
                "prenom": user.prenom,
                "email": user.email,
                "date_creation": user.date_creation.isoformat(),
                "derniere_connexion": user.derniere_connexion.isoformat() if user.derniere_connexion else None
            },
            "consentements": {
                "total": len(consentements),
                "actifs": len([c for c in consentements if c.is_valid()]),
                "types": list(set([c.type_consentement for c in consentements]))
            },
            "donnees": {
                "total_logs": total_logs,
                "taille_estimee": "~2.5 MB",  # Estimation
                "derniere_export": None,  # À implémenter
                "anonymise": user.date_anonymisation is not None
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")
