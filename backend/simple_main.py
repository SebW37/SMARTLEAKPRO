"""
SmartLeakPro - Version simplifiée pour démonstration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import uuid

# Configuration CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Modèles Pydantic simplifiés
class ClientBase(BaseModel):
    nom: str
    email: str
    telephone: str
    adresse: str
    statut: str = "actif"

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: str
    date_creation: datetime
    
    class Config:
        from_attributes = True

class InterventionBase(BaseModel):
    client_id: str
    date_intervention: datetime
    type_intervention: str
    statut: str
    lieu: str
    description: str

class InterventionCreate(InterventionBase):
    pass

class InterventionResponse(InterventionBase):
    id: str
    date_creation: datetime
    
    class Config:
        from_attributes = True

# Base de données en mémoire (pour la démo)
clients_db = []
interventions_db = []

# Application FastAPI
app = FastAPI(
    title="SmartLeakPro API",
    description="API de gestion de détection de fuite",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes de base
@app.get("/")
async def root():
    return {"message": "SmartLeakPro API - Version Démo", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Routes Clients
@app.get("/api/clients/", response_model=List[ClientResponse])
async def get_clients():
    return clients_db

@app.post("/api/clients/", response_model=ClientResponse)
async def create_client(client: ClientCreate):
    client_id = str(uuid.uuid4())
    client_data = ClientResponse(
        id=client_id,
        nom=client.nom,
        email=client.email,
        telephone=client.telephone,
        adresse=client.adresse,
        statut=client.statut,
        date_creation=datetime.utcnow()
    )
    clients_db.append(client_data)
    return client_data

@app.get("/api/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str):
    for client in clients_db:
        if client.id == client_id:
            return client
    raise HTTPException(status_code=404, detail="Client non trouvé")

# Routes Interventions
@app.get("/api/interventions/", response_model=List[InterventionResponse])
async def get_interventions():
    return interventions_db

@app.post("/api/interventions/", response_model=InterventionResponse)
async def create_intervention(intervention: InterventionCreate):
    intervention_id = str(uuid.uuid4())
    intervention_data = InterventionResponse(
        id=intervention_id,
        client_id=intervention.client_id,
        date_intervention=intervention.date_intervention,
        type_intervention=intervention.type_intervention,
        statut=intervention.statut,
        lieu=intervention.lieu,
        description=intervention.description,
        date_creation=datetime.utcnow()
    )
    interventions_db.append(intervention_data)
    return intervention_data

@app.get("/api/interventions/{intervention_id}", response_model=InterventionResponse)
async def get_intervention(intervention_id: str):
    for intervention in interventions_db:
        if intervention.id == intervention_id:
            return intervention
    raise HTTPException(status_code=404, detail="Intervention non trouvée")

# Routes de démonstration
@app.get("/api/demo/init")
async def init_demo_data():
    """Initialise des données de démonstration"""
    global clients_db, interventions_db
    
    # Clients de démo
    demo_clients = [
        ClientResponse(
            id=str(uuid.uuid4()),
            nom="Client Démo 1",
            email="client1@demo.com",
            telephone="0123456789",
            adresse="123 Rue Démo, 75001 Paris",
            statut="actif",
            date_creation=datetime.utcnow()
        ),
        ClientResponse(
            id=str(uuid.uuid4()),
            nom="Client Démo 2",
            email="client2@demo.com",
            telephone="0987654321",
            adresse="456 Avenue Test, 69000 Lyon",
            statut="actif",
            date_creation=datetime.utcnow()
        )
    ]
    
    clients_db = demo_clients
    
    # Interventions de démo
    demo_interventions = [
        InterventionResponse(
            id=str(uuid.uuid4()),
            client_id=clients_db[0].id,
            date_intervention=datetime.utcnow(),
            type_intervention="inspection",
            statut="planifie",
            lieu="123 Rue Démo, 75001 Paris",
            description="Inspection de routine",
            date_creation=datetime.utcnow()
        ),
        InterventionResponse(
            id=str(uuid.uuid4()),
            client_id=clients_db[1].id,
            date_intervention=datetime.utcnow(),
            type_intervention="detection",
            statut="en_cours",
            lieu="456 Avenue Test, 69000 Lyon",
            description="Détection de fuite urgente",
            date_creation=datetime.utcnow()
        )
    ]
    
    interventions_db = demo_interventions
    
    return {
        "message": "Données de démonstration initialisées",
        "clients": len(clients_db),
        "interventions": len(interventions_db)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
