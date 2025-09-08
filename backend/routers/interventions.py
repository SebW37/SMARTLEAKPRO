"""
Router pour la gestion des interventions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Intervention, Inspection, Client, StatutIntervention, TypeIntervention
from ..schemas import (
    InterventionCreate, InterventionUpdate, InterventionResponse, 
    InterventionListResponse, StatutChange, WorkflowAction
)
from ..auth import get_current_user

router = APIRouter()


@router.post("/", response_model=InterventionResponse, status_code=201)
async def create_intervention(
    intervention_data: InterventionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Créer une nouvelle intervention"""
    try:
        # Vérifier que le client existe
        client_result = await db.execute(
            select(Client).where(Client.id == intervention_data.client_id)
        )
        client = client_result.scalar_one_or_none()
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
        
        # Créer la nouvelle intervention
        db_intervention = Intervention(**intervention_data.dict())
        db.add(db_intervention)
        await db.commit()
        await db.refresh(db_intervention)
        
        # Charger les relations
        await db.refresh(db_intervention, ['client'])
        
        return InterventionResponse.from_orm(db_intervention)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.get("/", response_model=InterventionListResponse)
async def list_interventions(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Taille de page"),
    client_id: Optional[UUID] = Query(None, description="Filtrer par client"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    type_intervention: Optional[str] = Query(None, description="Filtrer par type"),
    priorite: Optional[str] = Query(None, description="Filtrer par priorité"),
    date_debut: Optional[datetime] = Query(None, description="Date de début"),
    date_fin: Optional[datetime] = Query(None, description="Date de fin"),
    technicien: Optional[str] = Query(None, description="Filtrer par technicien"),
    search: Optional[str] = Query(None, description="Recherche dans description/lieu"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lister les interventions avec pagination et filtres"""
    try:
        # Construction de la requête avec relations
        query = select(Intervention).options(selectinload(Intervention.client))
        count_query = select(func.count(Intervention.id))
        
        # Filtres
        filters = []
        
        if client_id:
            filters.append(Intervention.client_id == client_id)
        
        if statut:
            try:
                statut_enum = StatutIntervention(statut)
                filters.append(Intervention.statut == statut_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Statut invalide")
        
        if type_intervention:
            try:
                type_enum = TypeIntervention(type_intervention)
                filters.append(Intervention.type_intervention == type_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Type d'intervention invalide")
        
        if priorite:
            filters.append(Intervention.priorite == priorite)
        
        if technicien:
            filters.append(Intervention.technicien_assigné.ilike(f"%{technicien}%"))
        
        if date_debut:
            filters.append(Intervention.date_intervention >= date_debut)
        
        if date_fin:
            filters.append(Intervention.date_intervention <= date_fin)
        
        if search:
            search_filter = or_(
                Intervention.description.ilike(f"%{search}%"),
                Intervention.lieu.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        # Appliquer les filtres
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Pagination
        offset = (page - 1) * size
        query = query.order_by(desc(Intervention.date_intervention)).offset(offset).limit(size)
        
        # Exécution des requêtes
        result = await db.execute(query)
        interventions = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Calcul du nombre de pages
        pages = (total + size - 1) // size
        
        return InterventionListResponse(
            interventions=[InterventionResponse.from_orm(intervention) for intervention in interventions],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{intervention_id}", response_model=InterventionResponse)
async def get_intervention(
    intervention_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer une intervention par ID"""
    try:
        result = await db.execute(
            select(Intervention)
            .options(selectinload(Intervention.client), selectinload(Intervention.inspections))
            .where(Intervention.id == intervention_id)
        )
        intervention = result.scalar_one_or_none()
        
        if not intervention:
            raise HTTPException(status_code=404, detail="Intervention non trouvée")
        
        return InterventionResponse.from_orm(intervention)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.put("/{intervention_id}", response_model=InterventionResponse)
async def update_intervention(
    intervention_id: UUID,
    intervention_data: InterventionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour une intervention"""
    try:
        # Récupérer l'intervention
        result = await db.execute(select(Intervention).where(Intervention.id == intervention_id))
        intervention = result.scalar_one_or_none()
        
        if not intervention:
            raise HTTPException(status_code=404, detail="Intervention non trouvée")
        
        # Mise à jour des champs
        update_data = intervention_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(intervention, field, value)
        
        await db.commit()
        await db.refresh(intervention)
        await db.refresh(intervention, ['client'])
        
        return InterventionResponse.from_orm(intervention)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{intervention_id}", status_code=204)
async def delete_intervention(
    intervention_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Supprimer une intervention"""
    try:
        # Récupérer l'intervention
        result = await db.execute(select(Intervention).where(Intervention.id == intervention_id))
        intervention = result.scalar_one_or_none()
        
        if not intervention:
            raise HTTPException(status_code=404, detail="Intervention non trouvée")
        
        # Vérifier si l'intervention peut être supprimée
        if intervention.statut in [StatutIntervention.EN_COURS, StatutIntervention.VALIDE]:
            raise HTTPException(
                status_code=400, 
                detail="Impossible de supprimer une intervention en cours ou validée"
            )
        
        await db.delete(intervention)
        await db.commit()
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


@router.post("/{intervention_id}/change-status", response_model=InterventionResponse)
async def change_intervention_status(
    intervention_id: UUID,
    status_change: StatutChange,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Changer le statut d'une intervention (workflow)"""
    try:
        # Récupérer l'intervention
        result = await db.execute(select(Intervention).where(Intervention.id == intervention_id))
        intervention = result.scalar_one_or_none()
        
        if not intervention:
            raise HTTPException(status_code=404, detail="Intervention non trouvée")
        
        # Vérifier les transitions de statut valides
        current_status = intervention.statut
        new_status = status_change.nouveau_statut
        
        valid_transitions = {
            StatutIntervention.PLANIFIE: [StatutIntervention.EN_COURS, StatutIntervention.ARCHIVE],
            StatutIntervention.EN_COURS: [StatutIntervention.VALIDE, StatutIntervention.ARCHIVE],
            StatutIntervention.VALIDE: [StatutIntervention.ARCHIVE],
            StatutIntervention.ARCHIVE: []  # Pas de transition depuis archivé
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise HTTPException(
                status_code=400,
                detail=f"Transition invalide de {current_status} vers {new_status}"
            )
        
        # Mettre à jour le statut
        intervention.statut = new_status
        
        # Gérer les dates selon le statut
        now = datetime.utcnow()
        if new_status == StatutIntervention.EN_COURS and not intervention.date_debut:
            intervention.date_debut = status_change.date_debut or now
        elif new_status == StatutIntervention.VALIDE and not intervention.date_fin:
            intervention.date_fin = status_change.date_fin or now
        
        await db.commit()
        await db.refresh(intervention)
        await db.refresh(intervention, ['client'])
        
        return InterventionResponse.from_orm(intervention)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors du changement de statut: {str(e)}")


@router.get("/{intervention_id}/inspections", response_model=List[dict])
async def get_intervention_inspections(
    intervention_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les inspections d'une intervention"""
    try:
        result = await db.execute(
            select(Inspection).where(Inspection.intervention_id == intervention_id)
        )
        inspections = result.scalars().all()
        
        return [inspection.to_dict() for inspection in inspections]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/stats/summary", response_model=dict)
async def get_interventions_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les statistiques des interventions"""
    try:
        # Statistiques par statut
        statut_stats = await db.execute(
            select(Intervention.statut, func.count(Intervention.id))
            .group_by(Intervention.statut)
        )
        statut_counts = dict(statut_stats.fetchall())
        
        # Statistiques par type
        type_stats = await db.execute(
            select(Intervention.type_intervention, func.count(Intervention.id))
            .group_by(Intervention.type_intervention)
        )
        type_counts = dict(type_stats.fetchall())
        
        # Interventions de la semaine
        week_ago = datetime.utcnow() - timedelta(days=7)
        week_interventions = await db.execute(
            select(func.count(Intervention.id))
            .where(Intervention.date_creation >= week_ago)
        )
        week_count = week_interventions.scalar()
        
        return {
            "par_statut": statut_counts,
            "par_type": type_counts,
            "cette_semaine": week_count,
            "total": sum(statut_counts.values())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des stats: {str(e)}")
