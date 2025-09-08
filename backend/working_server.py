"""
SmartLeakPro - Serveur fonctionnel complet
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import uuid
import json
import os

# Configuration CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "*"  # Pour la démo
]

# Modèles Pydantic
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

# Base de données en mémoire
clients_db = []
interventions_db = []

# Application FastAPI
app = FastAPI(
    title="SmartLeakPro API",
    description="API de gestion de détection de fuite - Version Démo",
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
    return {
        "message": "SmartLeakPro API - Version Démo", 
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "clients": "/api/clients/",
            "interventions": "/api/interventions/",
            "demo": "/api/demo/init",
            "frontend": "/demo"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "clients_count": len(clients_db),
        "interventions_count": len(interventions_db)
    }

# Route pour servir la démo frontend
@app.get("/demo")
async def demo_frontend():
    demo_file = os.path.join("..", "frontend", "simple_demo.html")
    if os.path.exists(demo_file):
        return FileResponse(demo_file)
    else:
        return {"error": "Fichier de démo non trouvé"}

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

@app.put("/api/clients/{client_id}", response_model=ClientResponse)
async def update_client(client_id: str, client_update: ClientCreate):
    for i, client in enumerate(clients_db):
        if client.id == client_id:
            updated_client = ClientResponse(
                id=client_id,
                nom=client_update.nom,
                email=client_update.email,
                telephone=client_update.telephone,
                adresse=client_update.adresse,
                statut=client_update.statut,
                date_creation=client.date_creation
            )
            clients_db[i] = updated_client
            return updated_client
    raise HTTPException(status_code=404, detail="Client non trouvé")

@app.delete("/api/clients/{client_id}")
async def delete_client(client_id: str):
    global clients_db
    clients_db = [client for client in clients_db if client.id != client_id]
    return {"message": "Client supprimé avec succès"}

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

@app.put("/api/interventions/{intervention_id}", response_model=InterventionResponse)
async def update_intervention(intervention_id: str, intervention_update: InterventionCreate):
    for i, intervention in enumerate(interventions_db):
        if intervention.id == intervention_id:
            updated_intervention = InterventionResponse(
                id=intervention_id,
                client_id=intervention_update.client_id,
                date_intervention=intervention_update.date_intervention,
                type_intervention=intervention_update.type_intervention,
                statut=intervention_update.statut,
                lieu=intervention_update.lieu,
                description=intervention_update.description,
                date_creation=intervention.date_creation
            )
            interventions_db[i] = updated_intervention
            return updated_intervention
    raise HTTPException(status_code=404, detail="Intervention non trouvée")

@app.delete("/api/interventions/{intervention_id}")
async def delete_intervention(intervention_id: str):
    global interventions_db
    interventions_db = [intervention for intervention in interventions_db if intervention.id != intervention_id]
    return {"message": "Intervention supprimée avec succès"}

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
        ),
        ClientResponse(
            id=str(uuid.uuid4()),
            nom="Client Démo 3",
            email="client3@demo.com",
            telephone="0555666777",
            adresse="789 Boulevard Exemple, 13000 Marseille",
            statut="inactif",
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
            description="Inspection de routine - Vérification des canalisations",
            date_creation=datetime.utcnow()
        ),
        InterventionResponse(
            id=str(uuid.uuid4()),
            client_id=clients_db[1].id,
            date_intervention=datetime.utcnow(),
            type_intervention="detection",
            statut="en_cours",
            lieu="456 Avenue Test, 69000 Lyon",
            description="Détection de fuite urgente - Réparation en cours",
            date_creation=datetime.utcnow()
        ),
        InterventionResponse(
            id=str(uuid.uuid4()),
            client_id=clients_db[0].id,
            date_intervention=datetime.utcnow(),
            type_intervention="reparation",
            statut="valide",
            lieu="123 Rue Démo, 75001 Paris",
            description="Réparation terminée - Fuite colmatée",
            date_creation=datetime.utcnow()
        )
    ]
    
    interventions_db = demo_interventions
    
    return {
        "message": "Données de démonstration initialisées avec succès",
        "clients": len(clients_db),
        "interventions": len(interventions_db),
        "details": {
            "clients_actifs": len([c for c in clients_db if c.statut == "actif"]),
            "interventions_en_cours": len([i for i in interventions_db if i.statut == "en_cours"]),
            "interventions_terminees": len([i for i in interventions_db if i.statut == "valide"])
        }
    }

@app.get("/api/demo/reset")
async def reset_demo_data():
    """Remet à zéro les données de démonstration"""
    global clients_db, interventions_db
    clients_db = []
    interventions_db = []
    return {"message": "Données réinitialisées"}

@app.get("/api/stats")
async def get_stats():
    """Retourne les statistiques de l'application"""
    return {
        "clients": {
            "total": len(clients_db),
            "actifs": len([c for c in clients_db if c.statut == "actif"]),
            "inactifs": len([c for c in clients_db if c.statut == "inactif"])
        },
        "interventions": {
            "total": len(interventions_db),
            "planifiees": len([i for i in interventions_db if i.statut == "planifie"]),
            "en_cours": len([i for i in interventions_db if i.statut == "en_cours"]),
            "validees": len([i for i in interventions_db if i.statut == "valide"]),
            "archivees": len([i for i in interventions_db if i.statut == "archive"])
        },
        "types_intervention": {
            "inspection": len([i for i in interventions_db if i.type_intervention == "inspection"]),
            "detection": len([i for i in interventions_db if i.type_intervention == "detection"]),
            "reparation": len([i for i in interventions_db if i.type_intervention == "reparation"])
        }
    }

if __name__ == "__main__":
    print("🚀 Démarrage de SmartLeakPro...")
    print("📡 Backend: http://localhost:8000")
    print("🌐 Frontend: http://localhost:8000/demo")
    print("📚 API Docs: http://localhost:8000/docs")
    print("❤️  Health: http://localhost:8000/health")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
