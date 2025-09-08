"""
Router pour la gestion des médias
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import os
import aiofiles
import mimetypes

from ..database import get_db
from ..models import Media, Intervention, Inspection, TypeMedia, StatutMedia
from ..schemas import (
    MediaCreate, MediaUpdate, MediaResponse, MediaThumbnailResponse,
    MediaListResponse, MediaUpload, MediaUploadResponse, MediaStats,
    MediaSearch, MediaBatchOperation
)
from ..auth import get_current_user
from ..services.media_processor import MediaProcessor

router = APIRouter()


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media(
    intervention_id: str = Form(...),
    inspection_id: Optional[str] = Form(None),
    type_media: str = Form(...),
    annotations: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    latitude: Optional[str] = Form(None),
    longitude: Optional[str] = Form(None),
    precision_gps: Optional[str] = Form(None),
    altitude: Optional[str] = Form(None),
    date_prise: Optional[str] = Form(None),
    appareil_info: Optional[str] = Form(None),
    mode_capture: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Uploader un média"""
    try:
        # Vérifier que l'intervention existe
        intervention_result = await db.execute(
            select(Intervention).where(Intervention.id == intervention_id)
        )
        intervention = intervention_result.scalar_one_or_none()
        if not intervention:
            raise HTTPException(status_code=404, detail="Intervention non trouvée")
        
        # Vérifier l'inspection si fournie
        if inspection_id:
            inspection_result = await db.execute(
                select(Inspection).where(Inspection.id == inspection_id)
            )
            inspection = inspection_result.scalar_one_or_none()
            if not inspection:
                raise HTTPException(status_code=404, detail="Inspection non trouvée")
        
        # Créer un fichier temporaire
        temp_filename = f"temp_{UUID().hex}_{file.filename}"
        temp_path = f"backend/static/temp/{temp_filename}"
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        # Sauvegarder le fichier temporaire
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Traiter le fichier
        processor = MediaProcessor()
        user_data = {
            "username": current_user.get("username", "Système"),
            "mode_capture": mode_capture
        }
        
        result = await processor.process_uploaded_file(
            temp_path,
            file.filename,
            intervention_id,
            inspection_id,
            user_data
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail="Erreur lors du traitement du fichier")
        
        # Créer l'enregistrement en base
        media_data = result["media_data"]
        media_data.update({
            "annotations": annotations,
            "description": description,
            "latitude": latitude,
            "longitude": longitude,
            "precision_gps": precision_gps,
            "altitude": altitude,
            "appareil_info": appareil_info,
            "mode_capture": mode_capture
        })
        
        if date_prise:
            try:
                media_data["date_prise"] = datetime.fromisoformat(date_prise)
            except ValueError:
                pass
        
        db_media = Media(**media_data)
        db.add(db_media)
        await db.commit()
        await db.refresh(db_media)
        
        return MediaUploadResponse(
            media_id=db_media.id,
            status="success",
            message="Média uploadé avec succès"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")


@router.get("/", response_model=MediaListResponse)
async def list_medias(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Taille de page"),
    intervention_id: Optional[UUID] = Query(None, description="Filtrer par intervention"),
    inspection_id: Optional[UUID] = Query(None, description="Filtrer par inspection"),
    type_media: Optional[str] = Query(None, description="Filtrer par type"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    avec_gps: Optional[bool] = Query(None, description="Avec coordonnées GPS"),
    avec_annotations: Optional[bool] = Query(None, description="Avec annotations"),
    date_debut: Optional[datetime] = Query(None, description="Date de début"),
    date_fin: Optional[datetime] = Query(None, description="Date de fin"),
    search: Optional[str] = Query(None, description="Recherche textuelle"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lister les médias avec pagination et filtres"""
    try:
        # Construction de la requête
        query = select(Media)
        count_query = select(func.count(Media.id))
        
        # Filtres
        filters = []
        
        if intervention_id:
            filters.append(Media.intervention_id == intervention_id)
        
        if inspection_id:
            filters.append(Media.inspection_id == inspection_id)
        
        if type_media:
            try:
                type_enum = TypeMedia(type_media)
                filters.append(Media.type_media == type_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Type de média invalide")
        
        if statut:
            try:
                statut_enum = StatutMedia(statut)
                filters.append(Media.statut == statut_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Statut invalide")
        
        if avec_gps:
            filters.append(and_(Media.latitude.isnot(None), Media.longitude.isnot(None)))
        
        if avec_annotations:
            filters.append(Media.annotations.isnot(None))
        
        if date_debut:
            filters.append(Media.date_upload >= date_debut)
        
        if date_fin:
            filters.append(Media.date_upload <= date_fin)
        
        if search:
            search_filter = or_(
                Media.nom_fichier.ilike(f"%{search}%"),
                Media.annotations.ilike(f"%{search}%"),
                Media.description.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        # Appliquer les filtres
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Pagination
        offset = (page - 1) * size
        query = query.order_by(desc(Media.date_upload)).offset(offset).limit(size)
        
        # Exécution des requêtes
        result = await db.execute(query)
        medias = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Calcul du nombre de pages
        pages = (total + size - 1) // size
        
        return MediaListResponse(
            medias=[MediaThumbnailResponse.from_orm(media) for media in medias],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{media_id}", response_model=MediaResponse)
async def get_media(
    media_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer un média par ID"""
    try:
        result = await db.execute(select(Media).where(Media.id == media_id))
        media = result.scalar_one_or_none()
        
        if not media:
            raise HTTPException(status_code=404, detail="Média non trouvé")
        
        return MediaResponse.from_orm(media)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.put("/{media_id}", response_model=MediaResponse)
async def update_media(
    media_id: UUID,
    media_data: MediaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour un média"""
    try:
        # Récupérer le média
        result = await db.execute(select(Media).where(Media.id == media_id))
        media = result.scalar_one_or_none()
        
        if not media:
            raise HTTPException(status_code=404, detail="Média non trouvé")
        
        # Mise à jour des champs
        update_data = media_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(media, field, value)
        
        await db.commit()
        await db.refresh(media)
        
        return MediaResponse.from_orm(media)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{media_id}", status_code=204)
async def delete_media(
    media_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Supprimer un média"""
    try:
        # Récupérer le média
        result = await db.execute(select(Media).where(Media.id == media_id))
        media = result.scalar_one_or_none()
        
        if not media:
            raise HTTPException(status_code=404, detail="Média non trouvé")
        
        # Supprimer les fichiers associés
        processor = MediaProcessor()
        await processor.delete_media_files(media)
        
        # Supprimer l'enregistrement
        await db.delete(media)
        await db.commit()
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


@router.get("/{media_id}/download")
async def download_media(
    media_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Télécharger un média"""
    try:
        result = await db.execute(select(Media).where(Media.id == media_id))
        media = result.scalar_one_or_none()
        
        if not media:
            raise HTTPException(status_code=404, detail="Média non trouvé")
        
        processor = MediaProcessor()
        file_path = processor.get_media_file_path(media)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        return FileResponse(
            path=str(file_path),
            filename=media.nom_original,
            media_type=media.mime_type or 'application/octet-stream'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du téléchargement: {str(e)}")


@router.get("/{media_id}/thumbnail")
async def get_media_thumbnail(
    media_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer la miniature d'un média"""
    try:
        result = await db.execute(select(Media).where(Media.id == media_id))
        media = result.scalar_one_or_none()
        
        if not media:
            raise HTTPException(status_code=404, detail="Média non trouvé")
        
        processor = MediaProcessor()
        thumbnail_path = processor.get_thumbnail_path(media)
        
        if not thumbnail_path or not thumbnail_path.exists():
            # Retourner l'image originale si pas de miniature
            file_path = processor.get_media_file_path(media)
            if file_path.exists():
                return FileResponse(str(file_path))
            else:
                raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        return FileResponse(str(thumbnail_path))
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/stats/summary", response_model=MediaStats)
async def get_medias_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les statistiques des médias"""
    try:
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Total des médias
        total_result = await db.execute(select(func.count(Media.id)))
        total_medias = total_result.scalar()
        
        # Médias ce mois
        month_result = await db.execute(
            select(func.count(Media.id))
            .where(Media.date_upload >= month_start)
        )
        medias_ce_mois = month_result.scalar()
        
        # Médias en attente
        pending_result = await db.execute(
            select(func.count(Media.id))
            .where(Media.statut.in_([StatutMedia.UPLOADING, StatutMedia.PROCESSING]))
        )
        medias_en_attente = pending_result.scalar()
        
        # Médias prêts
        ready_result = await db.execute(
            select(func.count(Media.id))
            .where(Media.statut == StatutMedia.READY)
        )
        medias_ready = ready_result.scalar()
        
        # Statistiques par type
        type_stats = await db.execute(
            select(Media.type_media, func.count(Media.id))
            .group_by(Media.type_media)
        )
        par_type = dict(type_stats.fetchall())
        
        # Statistiques par intervention
        intervention_stats = await db.execute(
            select(Media.intervention_id, func.count(Media.id))
            .group_by(Media.intervention_id)
        )
        par_intervention = dict(intervention_stats.fetchall())
        
        # Taille totale
        taille_result = await db.execute(
            select(func.sum(Media.taille_fichier))
            .where(Media.taille_fichier.isnot(None))
        )
        taille_totale = taille_result.scalar() or 0
        
        # Médias avec GPS
        gps_result = await db.execute(
            select(func.count(Media.id))
            .where(and_(Media.latitude.isnot(None), Media.longitude.isnot(None)))
        )
        medias_avec_gps = gps_result.scalar()
        
        # Médias avec annotations
        annotations_result = await db.execute(
            select(func.count(Media.id))
            .where(Media.annotations.isnot(None))
        )
        medias_avec_annotations = annotations_result.scalar()
        
        return MediaStats(
            total_medias=total_medias,
            medias_ce_mois=medias_ce_mois,
            medias_en_attente=medias_en_attente,
            medias_ready=medias_ready,
            par_type=par_type,
            par_intervention=par_intervention,
            taille_totale=taille_totale,
            medias_avec_gps=medias_avec_gps,
            medias_avec_annotations=medias_avec_annotations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des stats: {str(e)}")


@router.post("/batch-operation", response_model=dict)
async def batch_operation(
    operation_data: MediaBatchOperation,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Effectuer une opération en lot sur les médias"""
    try:
        # Récupérer les médias
        result = await db.execute(
            select(Media).where(Media.id.in_(operation_data.media_ids))
        )
        medias = result.scalars().all()
        
        if not medias:
            raise HTTPException(status_code=404, detail="Aucun média trouvé")
        
        # Effectuer l'opération selon le type
        if operation_data.operation == "delete":
            processor = MediaProcessor()
            for media in medias:
                await processor.delete_media_files(media)
                await db.delete(media)
            await db.commit()
            
            return {"message": f"{len(medias)} médias supprimés", "count": len(medias)}
        
        elif operation_data.operation == "update_status":
            new_status = operation_data.parameters.get("status")
            if not new_status:
                raise HTTPException(status_code=400, detail="Statut requis")
            
            for media in medias:
                media.statut = StatutMedia(new_status)
            await db.commit()
            
            return {"message": f"Statut mis à jour pour {len(medias)} médias", "count": len(medias)}
        
        else:
            raise HTTPException(status_code=400, detail="Opération non supportée")
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'opération: {str(e)}")
