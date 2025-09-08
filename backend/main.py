"""
SmartLeakPro - Phase 1
Backend FastAPI pour gestion des clients
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .database import init_db
from .routers import clients, auth, interventions, planning, rapports, medias, utilisateurs, auth_advanced, audit, rgpd, api_keys, webhooks, integrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


# Création de l'application FastAPI
app = FastAPI(
    title="SmartLeakPro API",
    description="API de gestion des détections de fuite - Phase 1",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(auth_advanced.router, prefix="/api/auth", tags=["Authentication Advanced"])
app.include_router(utilisateurs.router, prefix="/api/utilisateurs", tags=["Utilisateurs"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit Trail"])
app.include_router(rgpd.router, prefix="/api/rgpd", tags=["RGPD"])
app.include_router(api_keys.router, prefix="/api/api-keys", tags=["API Keys"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(interventions.router, prefix="/api/interventions", tags=["Interventions"])
app.include_router(planning.router, prefix="/api/planning", tags=["Planning"])
app.include_router(rapports.router, prefix="/api/rapports", tags=["Rapports"])
app.include_router(medias.router, prefix="/api/medias", tags=["Médias"])


@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "SmartLeakPro API - Phase 1",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
