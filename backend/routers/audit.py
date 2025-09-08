"""
Router pour l'audit trail - Phase 6 Sécurité
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..database import get_db
from ..models import LogAudit, TypeAction, NiveauLog, Utilisateur
from ..schemas import (
    LogAuditResponse, LogAuditListResponse, LogAuditSearch, SecurityStats
)
from ..auth import get_current_user, get_current_active_user, get_client_ip, get_user_agent
from ..services.security_service import security_service

router = APIRouter()


@router.get("/logs", response_model=LogAuditListResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Taille de page"),
    utilisateur_id: Optional[UUID] = Query(None, description="Filtrer par utilisateur"),
    type_action: Optional[str] = Query(None, description="Filtrer par type d'action"),
    ressource: Optional[str] = Query(None, description="Filtrer par ressource"),
    niveau_log: Optional[str] = Query(None, description="Filtrer par niveau de log"),
    date_debut: Optional[datetime] = Query(None, description="Date de début"),
    date_fin: Optional[datetime] = Query(None, description="Date de fin"),
    succes: Optional[bool] = Query(None, description="Filtrer par succès"),
    ip_address: Optional[str] = Query(None, description="Filtrer par adresse IP"),
    search: Optional[str] = Query(None, description="Recherche textuelle"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Récupérer les logs d'audit avec pagination et filtres"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "audit", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Construction de la requête
        query = select(LogAudit)
        count_query = select(func.count(LogAudit.id))
        
        # Filtres
        filters = []
        
        if utilisateur_id:
            filters.append(LogAudit.utilisateur_id == utilisateur_id)
        
        if type_action:
            try:
                type_enum = TypeAction(type_action)
                filters.append(LogAudit.type_action == type_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Type d'action invalide")
        
        if ressource:
            filters.append(LogAudit.ressource.ilike(f"%{ressource}%"))
        
        if niveau_log:
            try:
                niveau_enum = NiveauLog(niveau_log)
                filters.append(LogAudit.niveau_log == niveau_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Niveau de log invalide")
        
        if date_debut:
            filters.append(LogAudit.timestamp >= date_debut)
        
        if date_fin:
            filters.append(LogAudit.timestamp <= date_fin)
        
        if succes is not None:
            filters.append(LogAudit.succes == succes)
        
        if ip_address:
            filters.append(LogAudit.ip_address.ilike(f"%{ip_address}%"))
        
        if search:
            search_filter = or_(
                LogAudit.nom_utilisateur.ilike(f"%{search}%"),
                LogAudit.description.ilike(f"%{search}%"),
                LogAudit.ressource.ilike(f"%{search}%"),
                LogAudit.action.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        # Appliquer les filtres
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Pagination
        offset = (page - 1) * size
        query = query.order_by(desc(LogAudit.timestamp)).offset(offset).limit(size)
        
        # Exécution des requêtes
        result = await db.execute(query)
        logs = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Calcul du nombre de pages
        pages = (total + size - 1) // size
        
        return LogAuditListResponse(
            logs=[LogAuditResponse.from_orm(log) for log in logs],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/logs/{log_id}", response_model=LogAuditResponse)
async def get_audit_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Récupérer un log d'audit spécifique"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "audit", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        result = await db.execute(select(LogAudit).where(LogAudit.id == log_id))
        log = result.scalar_one_or_none()
        
        if not log:
            raise HTTPException(status_code=404, detail="Log non trouvé")
        
        return LogAuditResponse.from_orm(log)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


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
            "audit", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        stats = await security_service.get_security_stats(db)
        return SecurityStats(**stats)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/stats/activity", response_model=dict)
async def get_activity_stats(
    days: int = Query(7, ge=1, le=365, description="Nombre de jours"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Récupérer les statistiques d'activité"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "audit", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Statistiques par type d'action
        action_stats = await db.execute(
            select(LogAudit.type_action, func.count(LogAudit.id))
            .where(LogAudit.timestamp >= start_date)
            .group_by(LogAudit.type_action)
        )
        par_action = dict(action_stats.fetchall())
        
        # Statistiques par ressource
        resource_stats = await db.execute(
            select(LogAudit.ressource, func.count(LogAudit.id))
            .where(LogAudit.timestamp >= start_date)
            .group_by(LogAudit.ressource)
        )
        par_ressource = dict(resource_stats.fetchall())
        
        # Statistiques par niveau de log
        level_stats = await db.execute(
            select(LogAudit.niveau_log, func.count(LogAudit.id))
            .where(LogAudit.timestamp >= start_date)
            .group_by(LogAudit.niveau_log)
        )
        par_niveau = dict(level_stats.fetchall())
        
        # Statistiques par utilisateur
        user_stats = await db.execute(
            select(LogAudit.nom_utilisateur, func.count(LogAudit.id))
            .where(LogAudit.timestamp >= start_date)
            .group_by(LogAudit.nom_utilisateur)
            .order_by(desc(func.count(LogAudit.id)))
            .limit(10)
        )
        top_utilisateurs = dict(user_stats.fetchall())
        
        # Activité par jour
        daily_stats = await db.execute(
            select(
                func.date(LogAudit.timestamp).label('date'),
                func.count(LogAudit.id).label('count')
            )
            .where(LogAudit.timestamp >= start_date)
            .group_by(func.date(LogAudit.timestamp))
            .order_by(func.date(LogAudit.timestamp))
        )
        activite_quotidienne = [
            {"date": str(row.date), "count": row.count} 
            for row in daily_stats.fetchall()
        ]
        
        # Erreurs récentes
        recent_errors = await db.execute(
            select(LogAudit)
            .where(
                and_(
                    LogAudit.timestamp >= start_date,
                    LogAudit.succes == False
                )
            )
            .order_by(desc(LogAudit.timestamp))
            .limit(10)
        )
        erreurs_recentes = [
            {
                "timestamp": log.timestamp.isoformat(),
                "utilisateur": log.nom_utilisateur,
                "action": log.action,
                "ressource": log.ressource,
                "message": log.message_erreur
            }
            for log in recent_errors.scalars().all()
        ]
        
        return {
            "periode": f"{days} derniers jours",
            "par_action": par_action,
            "par_ressource": par_ressource,
            "par_niveau": par_niveau,
            "top_utilisateurs": top_utilisateurs,
            "activite_quotidienne": activite_quotidienne,
            "erreurs_recentes": erreurs_recentes
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/alerts", response_model=List[dict])
async def get_security_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Récupérer les alertes de sécurité"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "audit", "read"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        alerts = []
        
        # Alertes sur les échecs de connexion
        failed_logins = await db.execute(
            select(func.count(LogAudit.id))
            .where(
                and_(
                    LogAudit.type_action == TypeAction.CONNEXION,
                    LogAudit.succes == False,
                    LogAudit.timestamp >= datetime.utcnow() - timedelta(hours=1)
                )
            )
        )
        failed_count = failed_logins.scalar()
        
        if failed_count > 10:
            alerts.append({
                "type": "warning",
                "title": "Tentatives de connexion échouées",
                "message": f"{failed_count} échecs de connexion dans la dernière heure",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Alertes sur les actions critiques
        critical_actions = await db.execute(
            select(LogAudit)
            .where(
                and_(
                    LogAudit.niveau_log == NiveauLog.CRITICAL,
                    LogAudit.timestamp >= datetime.utcnow() - timedelta(hours=24)
                )
            )
            .order_by(desc(LogAudit.timestamp))
            .limit(5)
        )
        
        for log in critical_actions.scalars().all():
            alerts.append({
                "type": "critical",
                "title": "Action critique détectée",
                "message": f"{log.action} sur {log.ressource} par {log.nom_utilisateur}",
                "timestamp": log.timestamp.isoformat()
            })
        
        # Alertes sur les utilisateurs inactifs
        inactive_users = await db.execute(
            select(Utilisateur)
            .where(
                and_(
                    Utilisateur.statut == "actif",
                    Utilisateur.derniere_connexion < datetime.utcnow() - timedelta(days=30)
                )
            )
        )
        
        for user in inactive_users.scalars().all():
            alerts.append({
                "type": "info",
                "title": "Utilisateur inactif",
                "message": f"{user.nom_utilisateur} ne s'est pas connecté depuis 30 jours",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.post("/export", response_model=dict)
async def export_audit_logs(
    search_criteria: LogAuditSearch,
    format: str = Query("json", description="Format d'export"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Exporter les logs d'audit"""
    try:
        # Vérifier les permissions
        if not security_service.check_permission(
            await _get_user_from_db(db, current_user.get("user_id")), 
            "audit", "export"
        ):
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
        
        # Construire la requête avec les critères de recherche
        query = select(LogAudit)
        filters = []
        
        if search_criteria.utilisateur_id:
            filters.append(LogAudit.utilisateur_id == search_criteria.utilisateur_id)
        
        if search_criteria.type_action:
            filters.append(LogAudit.type_action == search_criteria.type_action)
        
        if search_criteria.ressource:
            filters.append(LogAudit.ressource.ilike(f"%{search_criteria.ressource}%"))
        
        if search_criteria.niveau_log:
            filters.append(LogAudit.niveau_log == search_criteria.niveau_log)
        
        if search_criteria.date_debut:
            filters.append(LogAudit.timestamp >= search_criteria.date_debut)
        
        if search_criteria.date_fin:
            filters.append(LogAudit.timestamp <= search_criteria.date_fin)
        
        if search_criteria.succes is not None:
            filters.append(LogAudit.succes == search_criteria.succes)
        
        if search_criteria.ip_address:
            filters.append(LogAudit.ip_address.ilike(f"%{search_criteria.ip_address}%"))
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(desc(LogAudit.timestamp))
        
        # Exécuter la requête
        result = await db.execute(query)
        logs = result.scalars().all()
        
        # Convertir en format d'export
        export_data = [log.to_dict() for log in logs]
        
        # Logger l'export
        await security_service.log_audit(
            db, current_user.get("user_id"), TypeAction.EXPORT, "audit", "export",
            f"Export de {len(export_data)} logs d'audit",
            NiveauLog.INFO,
            succes=True
        )
        
        return {
            "message": f"Export de {len(export_data)} logs d'audit",
            "format": format,
            "count": len(export_data),
            "data": export_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export: {str(e)}")


async def _get_user_from_db(db: AsyncSession, user_id: str) -> Optional[Utilisateur]:
    """Récupérer un utilisateur depuis la base de données"""
    if not user_id:
        return None
    
    result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
    return result.scalar_one_or_none()
