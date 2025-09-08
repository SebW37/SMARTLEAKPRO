"""
Router pour la gestion du planning et des rendez-vous
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_, not_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta, date

from ..database import get_db
from ..models import RendezVous, Client, Intervention, StatutRendezVous
from ..schemas import (
    RendezVousCreate, RendezVousUpdate, RendezVousResponse, 
    RendezVousListResponse, RendezVousCalendarResponse, CalendarEvent,
    PlanningStats, CreneauDisponible, ValidationCreneau
)
from ..auth import get_current_user

router = APIRouter()


@router.post("/", response_model=RendezVousResponse, status_code=201)
async def create_rendez_vous(
    rdv_data: RendezVousCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Créer un nouveau rendez-vous"""
    try:
        # Vérifier que le client existe
        client_result = await db.execute(
            select(Client).where(Client.id == rdv_data.client_id)
        )
        client = client_result.scalar_one_or_none()
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
        
        # Vérifier l'intervention si fournie
        if rdv_data.intervention_id:
            intervention_result = await db.execute(
                select(Intervention).where(Intervention.id == rdv_data.intervention_id)
            )
            intervention = intervention_result.scalar_one_or_none()
            if not intervention:
                raise HTTPException(status_code=404, detail="Intervention non trouvée")
        
        # Valider le créneau horaire
        await validate_creneau(
            db, 
            rdv_data.date_heure_debut, 
            rdv_data.date_heure_fin, 
            rdv_data.utilisateur_responsable
        )
        
        # Créer le rendez-vous
        db_rdv = RendezVous(**rdv_data.dict())
        db.add(db_rdv)
        await db.commit()
        await db.refresh(db_rdv)
        
        # Charger les relations
        await db.refresh(db_rdv, ['client', 'intervention'])
        
        return RendezVousResponse.from_orm(db_rdv)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.get("/", response_model=RendezVousListResponse)
async def list_rendez_vous(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Taille de page"),
    client_id: Optional[UUID] = Query(None, description="Filtrer par client"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    technicien: Optional[str] = Query(None, description="Filtrer par technicien"),
    date_debut: Optional[datetime] = Query(None, description="Date de début"),
    date_fin: Optional[datetime] = Query(None, description="Date de fin"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lister les rendez-vous avec pagination et filtres"""
    try:
        # Construction de la requête avec relations
        query = select(RendezVous).options(
            selectinload(RendezVous.client),
            selectinload(RendezVous.intervention)
        )
        count_query = select(func.count(RendezVous.id))
        
        # Filtres
        filters = []
        
        if client_id:
            filters.append(RendezVous.client_id == client_id)
        
        if statut:
            try:
                statut_enum = StatutRendezVous(statut)
                filters.append(RendezVous.statut == statut_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Statut invalide")
        
        if technicien:
            filters.append(RendezVous.utilisateur_responsable.ilike(f"%{technicien}%"))
        
        if date_debut:
            filters.append(RendezVous.date_heure_debut >= date_debut)
        
        if date_fin:
            filters.append(RendezVous.date_heure_fin <= date_fin)
        
        # Appliquer les filtres
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Pagination
        offset = (page - 1) * size
        query = query.order_by(RendezVous.date_heure_debut).offset(offset).limit(size)
        
        # Exécution des requêtes
        result = await db.execute(query)
        rdv_list = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Calcul du nombre de pages
        pages = (total + size - 1) // size
        
        return RendezVousListResponse(
            rendez_vous=[RendezVousResponse.from_orm(rdv) for rdv in rdv_list],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/calendar", response_model=RendezVousCalendarResponse)
async def get_calendar_events(
    start: Optional[datetime] = Query(None, description="Date de début"),
    end: Optional[datetime] = Query(None, description="Date de fin"),
    technicien: Optional[str] = Query(None, description="Filtrer par technicien"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les événements pour le calendrier"""
    try:
        # Construction de la requête
        query = select(RendezVous).options(
            selectinload(RendezVous.client),
            selectinload(RendezVous.intervention)
        )
        
        # Filtres de date
        if start:
            query = query.where(RendezVous.date_heure_debut >= start)
        if end:
            query = query.where(RendezVous.date_heure_fin <= end)
        
        # Filtre technicien
        if technicien:
            query = query.where(RendezVous.utilisateur_responsable.ilike(f"%{technicien}%"))
        
        # Exécution
        result = await db.execute(query)
        rdv_list = result.scalars().all()
        
        # Conversion en événements calendrier
        events = [rdv.to_calendar_event() for rdv in rdv_list]
        
        return RendezVousCalendarResponse(
            events=events,
            total=len(events)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{rdv_id}", response_model=RendezVousResponse)
async def get_rendez_vous(
    rdv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer un rendez-vous par ID"""
    try:
        result = await db.execute(
            select(RendezVous)
            .options(selectinload(RendezVous.client), selectinload(RendezVous.intervention))
            .where(RendezVous.id == rdv_id)
        )
        rdv = result.scalar_one_or_none()
        
        if not rdv:
            raise HTTPException(status_code=404, detail="Rendez-vous non trouvé")
        
        return RendezVousResponse.from_orm(rdv)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.put("/{rdv_id}", response_model=RendezVousResponse)
async def update_rendez_vous(
    rdv_id: UUID,
    rdv_data: RendezVousUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour un rendez-vous"""
    try:
        # Récupérer le rendez-vous
        result = await db.execute(select(RendezVous).where(RendezVous.id == rdv_id))
        rdv = result.scalar_one_or_none()
        
        if not rdv:
            raise HTTPException(status_code=404, detail="Rendez-vous non trouvé")
        
        # Valider le créneau si les dates changent
        if rdv_data.date_heure_debut or rdv_data.date_heure_fin:
            new_start = rdv_data.date_heure_debut or rdv.date_heure_debut
            new_end = rdv_data.date_heure_fin or rdv.date_heure_fin
            new_technicien = rdv_data.utilisateur_responsable or rdv.utilisateur_responsable
            
            await validate_creneau(
                db, 
                new_start, 
                new_end, 
                new_technicien,
                rdv_id_exclu=rdv_id
            )
        
        # Mise à jour des champs
        update_data = rdv_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rdv, field, value)
        
        await db.commit()
        await db.refresh(rdv)
        await db.refresh(rdv, ['client', 'intervention'])
        
        return RendezVousResponse.from_orm(rdv)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{rdv_id}", status_code=204)
async def delete_rendez_vous(
    rdv_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Supprimer un rendez-vous"""
    try:
        # Récupérer le rendez-vous
        result = await db.execute(select(RendezVous).where(RendezVous.id == rdv_id))
        rdv = result.scalar_one_or_none()
        
        if not rdv:
            raise HTTPException(status_code=404, detail="Rendez-vous non trouvé")
        
        # Vérifier si le RDV peut être supprimé
        if rdv.statut in [StatutRendezVous.CONFIRME, StatutRendezVous.TERMINE]:
            raise HTTPException(
                status_code=400, 
                detail="Impossible de supprimer un rendez-vous confirmé ou terminé"
            )
        
        await db.delete(rdv)
        await db.commit()
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


@router.post("/validate-creneau", response_model=dict)
async def validate_creneau_endpoint(
    validation_data: ValidationCreneau,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Valider un créneau horaire"""
    try:
        await validate_creneau(
            db,
            validation_data.date_debut,
            validation_data.date_fin,
            validation_data.technicien,
            validation_data.rdv_id_exclu
        )
        return {"valid": True, "message": "Créneau disponible"}
    
    except HTTPException as e:
        return {"valid": False, "message": e.detail}


@router.get("/stats/planning", response_model=PlanningStats)
async def get_planning_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les statistiques du planning"""
    try:
        now = datetime.utcnow()
        today = now.date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Total des RDV
        total_result = await db.execute(select(func.count(RendezVous.id)))
        total_rdv = total_result.scalar()
        
        # RDV aujourd'hui
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        today_result = await db.execute(
            select(func.count(RendezVous.id))
            .where(and_(
                RendezVous.date_heure_debut >= today_start,
                RendezVous.date_heure_debut <= today_end
            ))
        )
        rdv_aujourd_hui = today_result.scalar()
        
        # RDV cette semaine
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        week_end_dt = datetime.combine(week_end, datetime.max.time())
        week_result = await db.execute(
            select(func.count(RendezVous.id))
            .where(and_(
                RendezVous.date_heure_debut >= week_start_dt,
                RendezVous.date_heure_debut <= week_end_dt
            ))
        )
        rdv_cette_semaine = week_result.scalar()
        
        # RDV en retard (passés mais pas terminés)
        retard_result = await db.execute(
            select(func.count(RendezVous.id))
            .where(and_(
                RendezVous.date_heure_fin < now,
                RendezVous.statut.in_([StatutRendezVous.PLANIFIE, StatutRendezVous.CONFIRME])
            ))
        )
        rdv_en_retard = retard_result.scalar()
        
        # Statistiques par statut
        statut_stats = await db.execute(
            select(RendezVous.statut, func.count(RendezVous.id))
            .group_by(RendezVous.statut)
        )
        par_statut = dict(statut_stats.fetchall())
        
        # Statistiques par technicien
        technicien_stats = await db.execute(
            select(RendezVous.utilisateur_responsable, func.count(RendezVous.id))
            .where(RendezVous.utilisateur_responsable.isnot(None))
            .group_by(RendezVous.utilisateur_responsable)
        )
        par_technicien = dict(technicien_stats.fetchall())
        
        return PlanningStats(
            total_rdv=total_rdv,
            rdv_aujourd_hui=rdv_aujourd_hui,
            rdv_cette_semaine=rdv_cette_semaine,
            rdv_en_retard=rdv_en_retard,
            par_statut=par_statut,
            par_technicien=par_technicien
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des stats: {str(e)}")


async def validate_creneau(
    db: AsyncSession,
    date_debut: datetime,
    date_fin: datetime,
    technicien: Optional[str] = None,
    rdv_id_exclu: Optional[UUID] = None
):
    """Valider qu'un créneau horaire est disponible"""
    if date_debut >= date_fin:
        raise HTTPException(status_code=400, detail="La date de fin doit être après la date de début")
    
    # Construire la requête de vérification
    query = select(RendezVous).where(
        and_(
            RendezVous.date_heure_debut < date_fin,
            RendezVous.date_heure_fin > date_debut,
            RendezVous.statut.in_([
                StatutRendezVous.PLANIFIE, 
                StatutRendezVous.CONFIRME
            ])
        )
    )
    
    # Exclure le RDV en cours de modification
    if rdv_id_exclu:
        query = query.where(RendezVous.id != rdv_id_exclu)
    
    # Filtrer par technicien si spécifié
    if technicien:
        query = query.where(RendezVous.utilisateur_responsable == technicien)
    
    # Vérifier les conflits
    result = await db.execute(query)
    conflits = result.scalars().all()
    
    if conflits:
        raise HTTPException(
            status_code=400, 
            detail=f"Conflit détecté avec {len(conflits)} rendez-vous existant(s)"
        )
