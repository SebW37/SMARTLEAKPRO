"""
Router pour la gestion des utilisateurs - Phase 6 Sécurité
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Utilisateur, RoleUtilisateur, StatutUtilisateur, TypeAction, NiveauLog
from ..schemas import (
    UtilisateurCreate, UtilisateurUpdate, UtilisateurResponse, 
    UtilisateurPublicResponse, UtilisateurListResponse, LoginRequest,
    LoginResponse, ChangePasswordRequest, TwoFactorSetupResponse,
    TwoFactorVerifyRequest, SecurityStats, PermissionCheck, PermissionResponse
)
from ..auth import get_current_user, get_current_active_user, require_role, get_client_ip, get_user_agent
from ..services.security_service import security_service

router = APIRouter()


@router.post("/register", response_model=UtilisateurResponse)
async def register_user(
    user_data: UtilisateurCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Créer un nouvel utilisateur (Admin uniquement)"""
    try:
        # Vérifier les permissions
        if current_user.get("role") != RoleUtilisateur.ADMIN.value:
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Vérifier la force du mot de passe
        is_strong, errors = security_service.validate_password_strength(user_data.mot_de_passe)
        if not is_strong:
            raise HTTPException(status_code=400, detail=f"Mot de passe faible: {', '.join(errors)}")
        
        # Vérifier l'unicité du nom d'utilisateur et email
        existing_user = await db.execute(
            select(Utilisateur).where(
                or_(
                    Utilisateur.nom_utilisateur == user_data.nom_utilisateur,
                    Utilisateur.email == user_data.email
                )
            )
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Nom d'utilisateur ou email déjà utilisé")
        
        # Créer l'utilisateur
        hashed_password = security_service.get_password_hash(user_data.mot_de_passe)
        
        db_user = Utilisateur(
            nom_utilisateur=user_data.nom_utilisateur,
            email=user_data.email,
            nom=user_data.nom,
            prenom=user_data.prenom,
            mot_de_passe_hash=hashed_password,
            role=user_data.role,
            telephone=user_data.telephone,
            adresse=user_data.adresse,
            date_naissance=user_data.date_naissance,
            consentement_rgpd=user_data.consentement_rgpd,
            date_consentement=datetime.utcnow() if user_data.consentement_rgpd else None,
            langue=user_data.langue,
            fuseau_horaire=user_data.fuseau_horaire,
            notifications_email=user_data.notifications_email,
            notifications_push=user_data.notifications_push,
            cree_par=current_user.get("user_id")
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        # Logger la création
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.CREATION, "utilisateurs", "create",
            f"Utilisateur créé: {db_user.nom_utilisateur}",
            NiveauLog.INFO,
            str(db_user.id)
        )
        
        return UtilisateurResponse.from_orm(db_user)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.get("/", response_model=UtilisateurListResponse)
async def list_utilisateurs(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Taille de page"),
    role: Optional[str] = Query(None, description="Filtrer par rôle"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    search: Optional[str] = Query(None, description="Recherche textuelle"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Lister les utilisateurs avec pagination et filtres"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "utilisateurs", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Construction de la requête
        query = select(Utilisateur)
        count_query = select(func.count(Utilisateur.id))
        
        # Filtres
        filters = []
        
        if role:
            try:
                role_enum = RoleUtilisateur(role)
                filters.append(Utilisateur.role == role_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Rôle invalide")
        
        if statut:
            try:
                statut_enum = StatutUtilisateur(statut)
                filters.append(Utilisateur.statut == statut_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Statut invalide")
        
        if search:
            search_filter = or_(
                Utilisateur.nom_utilisateur.ilike(f"%{search}%"),
                Utilisateur.nom.ilike(f"%{search}%"),
                Utilisateur.prenom.ilike(f"%{search}%"),
                Utilisateur.email.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        # Appliquer les filtres
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Pagination
        offset = (page - 1) * size
        query = query.order_by(desc(Utilisateur.date_creation)).offset(offset).limit(size)
        
        # Exécution des requêtes
        result = await db.execute(query)
        utilisateurs = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Calcul du nombre de pages
        pages = (total + size - 1) // size
        
        return UtilisateurListResponse(
            utilisateurs=[UtilisateurPublicResponse.from_orm(user) for user in utilisateurs],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{user_id}", response_model=UtilisateurResponse)
async def get_utilisateur(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Récupérer un utilisateur par ID"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "utilisateurs", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        return UtilisateurResponse.from_orm(user)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.put("/{user_id}", response_model=UtilisateurResponse)
async def update_utilisateur(
    user_id: UUID,
    user_data: UtilisateurUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Mettre à jour un utilisateur"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "utilisateurs", "write"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer l'utilisateur
        result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Sauvegarder les anciennes valeurs pour l'audit
        anciennes_valeurs = user.to_dict()
        
        # Mise à jour des champs
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.modifie_par = current_user.get("user_id")
        
        await db.commit()
        await db.refresh(user)
        
        # Logger la modification
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.MODIFICATION, "utilisateurs", "update",
            f"Utilisateur modifié: {user.nom_utilisateur}",
            NiveauLog.INFO,
            str(user_id),
            anciennes_valeurs,
            user.to_dict()
        )
        
        return UtilisateurResponse.from_orm(user)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{user_id}", status_code=204)
async def delete_utilisateur(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Supprimer un utilisateur (Admin uniquement)"""
    try:
        # Vérifier les permissions
        if current_user.get("role") != RoleUtilisateur.ADMIN.value:
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Empêcher l'auto-suppression
        if str(user_id) == current_user.get("user_id"):
            raise HTTPException(status_code=400, detail="Impossible de supprimer son propre compte")
        
        # Récupérer l'utilisateur
        result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Logger la suppression
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.SUPPRESSION, "utilisateurs", "delete",
            f"Utilisateur supprimé: {user.nom_utilisateur}",
            NiveauLog.WARNING,
            str(user_id)
        )
        
        # Supprimer l'utilisateur
        await db.delete(user)
        await db.commit()
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


@router.post("/{user_id}/change-password", response_model=dict)
async def change_password(
    user_id: UUID,
    password_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Changer le mot de passe d'un utilisateur"""
    try:
        # Vérifier les permissions (utilisateur peut changer son propre mot de passe)
        if str(user_id) != current_user.get("user_id") and current_user.get("role") != RoleUtilisateur.ADMIN.value:
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Récupérer l'utilisateur
        result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Vérifier le mot de passe actuel (sauf pour admin)
        if str(user_id) == current_user.get("user_id"):
            if not security_service.verify_password(password_data.mot_de_passe_actuel, user.mot_de_passe_hash):
                raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
        
        # Vérifier la force du nouveau mot de passe
        is_strong, errors = security_service.validate_password_strength(password_data.nouveau_mot_de_passe)
        if not is_strong:
            raise HTTPException(status_code=400, detail=f"Mot de passe faible: {', '.join(errors)}")
        
        # Mettre à jour le mot de passe
        user.mot_de_passe_hash = security_service.get_password_hash(password_data.nouveau_mot_de_passe)
        user.modifie_par = current_user.get("user_id")
        
        await db.commit()
        
        # Logger le changement
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.MODIFICATION, "utilisateurs", "change_password",
            f"Mot de passe modifié pour: {user.nom_utilisateur}",
            NiveauLog.INFO,
            str(user_id)
        )
        
        return {"message": "Mot de passe modifié avec succès"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors du changement: {str(e)}")


@router.post("/{user_id}/toggle-status", response_model=dict)
async def toggle_user_status(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Activer/Désactiver un utilisateur (Admin uniquement)"""
    try:
        # Vérifier les permissions
        if current_user.get("role") != RoleUtilisateur.ADMIN.value:
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Empêcher l'auto-désactivation
        if str(user_id) == current_user.get("user_id"):
            raise HTTPException(status_code=400, detail="Impossible de modifier son propre statut")
        
        # Récupérer l'utilisateur
        result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Changer le statut
        ancien_statut = user.statut
        if user.statut == StatutUtilisateur.ACTIF:
            user.statut = StatutUtilisateur.SUSPENDU
            nouveau_statut = "suspendu"
        else:
            user.statut = StatutUtilisateur.ACTIF
            nouveau_statut = "actif"
        
        user.modifie_par = current_user.get("user_id")
        await db.commit()
        
        # Logger le changement
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.MODIFICATION, "utilisateurs", "toggle_status",
            f"Statut changé de {ancien_statut.value} à {nouveau_statut} pour: {user.nom_utilisateur}",
            NiveauLog.INFO,
            str(user_id)
        )
        
        return {"message": f"Statut changé en {nouveau_statut}"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors du changement: {str(e)}")


@router.get("/stats/security", response_model=SecurityStats)
async def get_security_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Récupérer les statistiques de sécurité"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "utilisateurs", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        stats = await security_service.get_security_stats(db)
        return SecurityStats(**stats)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.post("/check-permission", response_model=PermissionResponse)
async def check_permission(
    permission_data: PermissionCheck,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Vérifier les permissions d'un utilisateur"""
    try:
        user_id = permission_data.utilisateur_id or current_user.get("user_id")
        user = await _get_user_from_db(db, user_id)
        
        if not user:
            return PermissionResponse(autorise=False, raison="Utilisateur non trouvé")
        
        autorise = security_service.check_permission(user, permission_data.resource, permission_data.action)
        
        return PermissionResponse(autorise=autorise)
    
    except Exception as e:
        return PermissionResponse(autorise=False, raison=str(e))


async def _get_user_from_db(db: AsyncSession, user_id: str) -> Optional[Utilisateur]:
    """Récupérer un utilisateur depuis la base de données"""
    if not user_id:
        return None
    
    result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
    return result.scalar_one_or_none()
