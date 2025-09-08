"""
Router pour la gestion des clients
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from ..models import Client
from ..schemas import ClientCreate, ClientUpdate, ClientResponse, ClientListResponse
from ..auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ClientResponse, status_code=201)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Créer un nouveau client"""
    try:
        # Vérifier si l'email existe déjà
        if client_data.email:
            existing_client = await db.execute(
                select(Client).where(Client.email == client_data.email)
            )
            if existing_client.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail="Un client avec cet email existe déjà"
                )
        
        # Créer le nouveau client
        db_client = Client(**client_data.dict())
        db.add(db_client)
        await db.commit()
        await db.refresh(db_client)
        
        return ClientResponse.from_orm(db_client)
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.get("/", response_model=ClientListResponse)
async def list_clients(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(10, ge=1, le=100, description="Taille de page"),
    search: Optional[str] = Query(None, description="Recherche par nom ou email"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lister les clients avec pagination et filtres"""
    try:
        # Construction de la requête
        query = select(Client)
        count_query = select(func.count(Client.id))
        
        # Filtres
        if search:
            search_filter = Client.nom.ilike(f"%{search}%") | Client.email.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        if statut:
            query = query.where(Client.statut == statut)
            count_query = count_query.where(Client.statut == statut)
        
        # Pagination
        offset = (page - 1) * size
        query = query.order_by(desc(Client.date_creation)).offset(offset).limit(size)
        
        # Exécution des requêtes
        result = await db.execute(query)
        clients = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Calcul du nombre de pages
        pages = (total + size - 1) // size
        
        return ClientListResponse(
            clients=[ClientResponse.from_orm(client) for client in clients],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer un client par ID"""
    try:
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
        
        return ClientResponse.from_orm(client)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour un client"""
    try:
        # Récupérer le client
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
        
        # Vérifier l'email si fourni
        if client_data.email and client_data.email != client.email:
            existing_client = await db.execute(
                select(Client).where(Client.email == client_data.email)
            )
            if existing_client.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail="Un client avec cet email existe déjà"
                )
        
        # Mise à jour des champs
        update_data = client_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        await db.commit()
        await db.refresh(client)
        
        return ClientResponse.from_orm(client)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Supprimer un client"""
    try:
        # Récupérer le client
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
        
        await db.delete(client)
        await db.commit()
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")
