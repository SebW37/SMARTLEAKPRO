"""
Router pour la gestion des rapports
"""

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import os
import aiofiles

from ..database import get_db
from ..models import Rapport, FichierRapport, Intervention, StatutRapport, TypeRapport
from ..schemas import (
    RapportCreate, RapportUpdate, RapportResponse, 
    RapportListResponse, FichierRapportCreate, FichierRapportResponse,
    GenerationRapport, RapportStats, ExportRapport
)
from ..auth import get_current_user
from ..services.report_generator import ReportGenerator, ReportExporter

router = APIRouter()


@router.post("/", response_model=RapportResponse, status_code=201)
async def create_rapport(
    rapport_data: RapportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Créer un nouveau rapport"""
    try:
        # Vérifier que l'intervention existe
        intervention_result = await db.execute(
            select(Intervention).where(Intervention.id == rapport_data.intervention_id)
        )
        intervention = intervention_result.scalar_one_or_none()
        if not intervention:
            raise HTTPException(status_code=404, detail="Intervention non trouvée")
        
        # Créer le rapport
        db_rapport = Rapport(**rapport_data.dict())
        db_rapport.auteur_rapport = current_user.get("username", "Système")
        db.add(db_rapport)
        await db.commit()
        await db.refresh(db_rapport)
        
        # Charger les relations
        await db.refresh(db_rapport, ['intervention'])
        
        return RapportResponse.from_orm(db_rapport)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.get("/", response_model=RapportListResponse)
async def list_rapports(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Taille de page"),
    intervention_id: Optional[UUID] = Query(None, description="Filtrer par intervention"),
    type_rapport: Optional[str] = Query(None, description="Filtrer par type"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    auteur: Optional[str] = Query(None, description="Filtrer par auteur"),
    date_debut: Optional[datetime] = Query(None, description="Date de début"),
    date_fin: Optional[datetime] = Query(None, description="Date de fin"),
    search: Optional[str] = Query(None, description="Recherche dans titre/description"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lister les rapports avec pagination et filtres"""
    try:
        # Construction de la requête avec relations
        query = select(Rapport).options(selectinload(Rapport.intervention))
        count_query = select(func.count(Rapport.id))
        
        # Filtres
        filters = []
        
        if intervention_id:
            filters.append(Rapport.intervention_id == intervention_id)
        
        if type_rapport:
            try:
                type_enum = TypeRapport(type_rapport)
                filters.append(Rapport.type_rapport == type_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Type de rapport invalide")
        
        if statut:
            try:
                statut_enum = StatutRapport(statut)
                filters.append(Rapport.statut == statut_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Statut invalide")
        
        if auteur:
            filters.append(Rapport.auteur_rapport.ilike(f"%{auteur}%"))
        
        if date_debut:
            filters.append(Rapport.date_creation >= date_debut)
        
        if date_fin:
            filters.append(Rapport.date_creation <= date_fin)
        
        if search:
            search_filter = or_(
                Rapport.titre.ilike(f"%{search}%"),
                Rapport.description.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        # Appliquer les filtres
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Pagination
        offset = (page - 1) * size
        query = query.order_by(desc(Rapport.date_creation)).offset(offset).limit(size)
        
        # Exécution des requêtes
        result = await db.execute(query)
        rapports = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Calcul du nombre de pages
        pages = (total + size - 1) // size
        
        return RapportListResponse(
            rapports=[RapportResponse.from_orm(rapport) for rapport in rapports],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{rapport_id}", response_model=RapportResponse)
async def get_rapport(
    rapport_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer un rapport par ID"""
    try:
        result = await db.execute(
            select(Rapport)
            .options(selectinload(Rapport.intervention), selectinload(Rapport.fichiers))
            .where(Rapport.id == rapport_id)
        )
        rapport = result.scalar_one_or_none()
        
        if not rapport:
            raise HTTPException(status_code=404, detail="Rapport non trouvé")
        
        return RapportResponse.from_orm(rapport)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.put("/{rapport_id}", response_model=RapportResponse)
async def update_rapport(
    rapport_id: UUID,
    rapport_data: RapportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour un rapport"""
    try:
        # Récupérer le rapport
        result = await db.execute(select(Rapport).where(Rapport.id == rapport_id))
        rapport = result.scalar_one_or_none()
        
        if not rapport:
            raise HTTPException(status_code=404, detail="Rapport non trouvé")
        
        # Mise à jour des champs
        update_data = rapport_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rapport, field, value)
        
        # Gérer les changements de statut
        if 'statut' in update_data:
            if update_data['statut'] == StatutRapport.VALIDE:
                rapport.date_validation = datetime.utcnow()
            elif update_data['statut'] == StatutRapport.ARCHIVE:
                rapport.date_archivage = datetime.utcnow()
        
        await db.commit()
        await db.refresh(rapport)
        await db.refresh(rapport, ['intervention'])
        
        return RapportResponse.from_orm(rapport)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{rapport_id}", status_code=204)
async def delete_rapport(
    rapport_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Supprimer un rapport"""
    try:
        # Récupérer le rapport
        result = await db.execute(select(Rapport).where(Rapport.id == rapport_id))
        rapport = result.scalar_one_or_none()
        
        if not rapport:
            raise HTTPException(status_code=404, detail="Rapport non trouvé")
        
        # Vérifier si le rapport peut être supprimé
        if rapport.statut in [StatutRapport.VALIDE, StatutRapport.ARCHIVE]:
            raise HTTPException(
                status_code=400, 
                detail="Impossible de supprimer un rapport validé ou archivé"
            )
        
        # Supprimer les fichiers associés
        if rapport.chemin_fichier and os.path.exists(rapport.chemin_fichier):
            os.remove(rapport.chemin_fichier)
        
        await db.delete(rapport)
        await db.commit()
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


@router.post("/generate", response_model=dict)
async def generate_rapport(
    generation_data: GenerationRapport,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Générer un rapport automatiquement"""
    try:
        # Récupérer l'intervention
        intervention_result = await db.execute(
            select(Intervention)
            .options(selectinload(Intervention.client), selectinload(Intervention.inspections))
            .where(Intervention.id == generation_data.intervention_id)
        )
        intervention = intervention_result.scalar_one_or_none()
        
        if not intervention:
            raise HTTPException(status_code=404, detail="Intervention non trouvée")
        
        # Générer le rapport
        generator = ReportGenerator()
        result = await generator.generate_report(
            intervention, 
            generation_data, 
            current_user.get("username", "Système")
        )
        
        # Créer l'enregistrement en base
        rapport = Rapport(
            intervention_id=generation_data.intervention_id,
            type_rapport=generation_data.type_rapport,
            titre=f"Rapport {generation_data.type_rapport.value} - {intervention.client.nom}",
            description=f"Rapport généré automatiquement pour l'intervention {intervention.id}",
            auteur_rapport=current_user.get("username", "Système"),
            statut=StatutRapport.VALIDE,
            chemin_fichier=result["file_path"],
            type_fichier=result["file_type"],
            taille_fichier=result["file_size"],
            contenu={"generation_data": generation_data.dict()}
        )
        
        db.add(rapport)
        await db.commit()
        await db.refresh(rapport)
        
        return {
            "rapport_id": str(rapport.id),
            "file_path": result["file_path"],
            "file_size": result["file_size"],
            "file_type": result["file_type"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")


@router.get("/{rapport_id}/download")
async def download_rapport(
    rapport_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Télécharger un rapport"""
    try:
        result = await db.execute(select(Rapport).where(Rapport.id == rapport_id))
        rapport = result.scalar_one_or_none()
        
        if not rapport:
            raise HTTPException(status_code=404, detail="Rapport non trouvé")
        
        if not rapport.chemin_fichier or not os.path.exists(rapport.chemin_fichier):
            raise HTTPException(status_code=404, detail="Fichier du rapport non trouvé")
        
        return FileResponse(
            path=rapport.chemin_fichier,
            filename=f"{rapport.titre}.{rapport.type_fichier}",
            media_type='application/octet-stream'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du téléchargement: {str(e)}")


@router.get("/stats/summary", response_model=RapportStats)
async def get_rapports_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les statistiques des rapports"""
    try:
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Total des rapports
        total_result = await db.execute(select(func.count(Rapport.id)))
        total_rapports = total_result.scalar()
        
        # Rapports ce mois
        month_result = await db.execute(
            select(func.count(Rapport.id))
            .where(Rapport.date_creation >= month_start)
        )
        rapports_ce_mois = month_result.scalar()
        
        # Rapports en attente (brouillons)
        pending_result = await db.execute(
            select(func.count(Rapport.id))
            .where(Rapport.statut == StatutRapport.BROUILLON)
        )
        rapports_en_attente = pending_result.scalar()
        
        # Rapports validés
        validated_result = await db.execute(
            select(func.count(Rapport.id))
            .where(Rapport.statut == StatutRapport.VALIDE)
        )
        rapports_valides = validated_result.scalar()
        
        # Statistiques par type
        type_stats = await db.execute(
            select(Rapport.type_rapport, func.count(Rapport.id))
            .group_by(Rapport.type_rapport)
        )
        par_type = dict(type_stats.fetchall())
        
        # Statistiques par auteur
        auteur_stats = await db.execute(
            select(Rapport.auteur_rapport, func.count(Rapport.id))
            .where(Rapport.auteur_rapport.isnot(None))
            .group_by(Rapport.auteur_rapport)
        )
        par_auteur = dict(auteur_stats.fetchall())
        
        # Taille totale
        taille_result = await db.execute(
            select(func.sum(Rapport.taille_fichier))
            .where(Rapport.taille_fichier.isnot(None))
        )
        taille_totale = taille_result.scalar() or 0
        
        return RapportStats(
            total_rapports=total_rapports,
            rapports_ce_mois=rapports_ce_mois,
            rapports_en_attente=rapports_en_attente,
            rapports_valides=rapports_valides,
            par_type=par_type,
            par_auteur=par_auteur,
            taille_totale=taille_totale
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des stats: {str(e)}")


@router.post("/export")
async def export_rapports(
    export_data: ExportRapport,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Exporter les rapports en différents formats"""
    try:
        # Construire la requête avec filtres
        query = select(Rapport).options(selectinload(Rapport.intervention))
        
        if export_data.filtres:
            filters = []
            if 'type_rapport' in export_data.filtres:
                filters.append(Rapport.type_rapport == export_data.filtres['type_rapport'])
            if 'statut' in export_data.filtres:
                filters.append(Rapport.statut == export_data.filtres['statut'])
            if 'date_debut' in export_data.filtres:
                filters.append(Rapport.date_creation >= export_data.filtres['date_debut'])
            if 'date_fin' in export_data.filtres:
                filters.append(Rapport.date_creation <= export_data.filtres['date_fin'])
            
            if filters:
                query = query.where(and_(*filters))
        
        # Exécuter la requête
        result = await db.execute(query)
        rapports = result.scalars().all()
        
        # Convertir en dictionnaires
        rapports_data = [rapport.to_dict() for rapport in rapports]
        
        # Générer le fichier d'export
        filename = f"export_rapports_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        file_path = f"backend/static/exports/{filename}"
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if export_data.format.lower() == "csv":
            await ReportExporter.export_to_csv(rapports_data, f"{file_path}.csv")
            return FileResponse(f"{file_path}.csv", filename=f"{filename}.csv")
        elif export_data.format.lower() == "xlsx":
            await ReportExporter.export_to_excel(rapports_data, f"{file_path}.xlsx")
            return FileResponse(f"{file_path}.xlsx", filename=f"{filename}.xlsx")
        elif export_data.format.lower() == "pdf":
            await ReportExporter.export_to_pdf_summary(rapports_data, f"{file_path}.pdf")
            return FileResponse(f"{file_path}.pdf", filename=f"{filename}.pdf")
        else:
            raise HTTPException(status_code=400, detail="Format d'export non supporté")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export: {str(e)}")
