"""
Module d'authentification pour SmartLeakPro - Phase 6 Sécurité
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from .database import get_db
from .models import Utilisateur, RoleUtilisateur, StatutUtilisateur
from .services.security_service import security_service

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexte de hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schéma de sécurité
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hacher un mot de passe"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Créer un token d'accès JWT"""
    return security_service.create_access_token(data, expires_delta)


def create_refresh_token(data: dict) -> str:
    """Créer un token de rafraîchissement"""
    return security_service.create_refresh_token(data)


def verify_token(token: str) -> Optional[dict]:
    """Vérifier et décoder un token JWT"""
    return security_service.verify_token(token)


async def authenticate_user(username: str, password: str, db: AsyncSession):
    """Authentifier un utilisateur (Phase 1 - Compatibilité)"""
    # Pour la Phase 1, on utilise des utilisateurs hardcodés
    # En production, ceci viendrait de la base de données
    
    # Utilisateurs de test
    test_users = {
        "admin": "admin123",
        "technicien": "tech123",
        "manager": "manager123"
    }
    
    if username in test_users and test_users[username] == password:
        return {"username": username, "role": "admin" if username == "admin" else "user"}
    
    return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Obtenir l'utilisateur actuel à partir du token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Récupérer l'utilisateur depuis la base de données
    result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur inactif",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": str(user.id),
        "username": user.nom_utilisateur,
        "email": user.email,
        "role": user.role.value,
        "statut": user.statut.value,
        "deux_facteurs_actif": user.deux_facteurs_actif
    }


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Obtenir l'utilisateur actuel actif"""
    if current_user.get("statut") != StatutUtilisateur.ACTIF.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte utilisateur inactif"
        )
    return current_user


def require_role(required_role: RoleUtilisateur):
    """Décorateur pour vérifier le rôle requis"""
    def role_checker(current_user: dict = Depends(get_current_active_user)):
        user_role = current_user.get("role")
        if user_role != required_role.value and user_role != RoleUtilisateur.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rôle {required_role.value} requis"
            )
        return current_user
    return role_checker


def require_permission(resource: str, action: str):
    """Décorateur pour vérifier les permissions"""
    def permission_checker(
        current_user: dict = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
    ):
        # Récupérer l'utilisateur complet pour vérifier les permissions
        # Cette fonction sera implémentée dans le router
        return current_user
    return permission_checker


def get_client_ip(request: Request) -> str:
    """Obtenir l'adresse IP du client"""
    # Vérifier les headers de proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # IP directe
    if hasattr(request, "client") and request.client:
        return request.client.host
    
    return "unknown"


def get_user_agent(request: Request) -> str:
    """Obtenir le User-Agent du client"""
    return request.headers.get("User-Agent", "unknown")
