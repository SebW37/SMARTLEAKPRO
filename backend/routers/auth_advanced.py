"""
Router d'authentification avancé - Phase 6 Sécurité
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Utilisateur, TypeAction, NiveauLog
from ..schemas import (
    LoginRequest, LoginResponse, RefreshTokenRequest, TwoFactorSetupResponse,
    TwoFactorVerifyRequest, ResetPasswordRequest, ResetPasswordConfirm
)
from ..auth import get_current_user, get_client_ip, get_user_agent
from ..services.security_service import security_service

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Connexion utilisateur avec authentification forte"""
    try:
        # Authentifier l'utilisateur
        user = await security_service.authenticate_user(
            db, login_data.nom_utilisateur, login_data.mot_de_passe
        )
        
        if not user:
            # Logger la tentative d'échec
            await security_service.log_audit(
                db, None, TypeAction.CONNEXION, "auth", "login_failed",
                f"Tentative de connexion échouée pour: {login_data.nom_utilisateur}",
                NiveauLog.WARNING,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                succes=False,
                message_erreur="Identifiants invalides"
            )
            raise HTTPException(status_code=401, detail="Identifiants invalides")
        
        # Vérifier 2FA si activé
        if user.deux_facteurs_actif:
            if not login_data.code_2fa:
                raise HTTPException(
                    status_code=400, 
                    detail="Code 2FA requis",
                    headers={"X-2FA-Required": "true"}
                )
            
            if not security_service.verify_2fa_code(user.secret_2fa, login_data.code_2fa):
                # Logger l'échec 2FA
                await security_service.log_audit(
                    db, str(user.id), TypeAction.CONNEXION, "auth", "login_2fa_failed",
                    f"Code 2FA invalide pour: {user.nom_utilisateur}",
                    NiveauLog.WARNING,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    succes=False,
                    message_erreur="Code 2FA invalide"
                )
                raise HTTPException(status_code=401, detail="Code 2FA invalide")
        
        # Créer les tokens
        access_token = security_service.create_access_token(
            data={"sub": str(user.id), "username": user.nom_utilisateur}
        )
        refresh_token = security_service.create_refresh_token(
            data={"sub": str(user.id), "username": user.nom_utilisateur}
        )
        
        # Mettre à jour les informations de connexion
        user.derniere_connexion = datetime.utcnow()
        user.derniere_activite = datetime.utcnow()
        user.refresh_token = refresh_token
        user.refresh_token_expire = datetime.utcnow() + timedelta(days=7)
        
        await db.commit()
        
        # Logger la connexion réussie
        await security_service.log_audit(
            db, str(user.id), TypeAction.CONNEXION, "auth", "login_success",
            f"Connexion réussie pour: {user.nom_utilisateur}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutes
            utilisateur=user.to_dict()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la connexion: {str(e)}")


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Rafraîchir un token d'accès"""
    try:
        # Vérifier le refresh token
        payload = security_service.verify_token(refresh_data.refresh_token, "refresh")
        if not payload:
            raise HTTPException(status_code=401, detail="Refresh token invalide")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Refresh token invalide")
        
        # Récupérer l'utilisateur
        result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active():
            raise HTTPException(status_code=401, detail="Utilisateur inactif")
        
        # Vérifier que le refresh token correspond
        if user.refresh_token != refresh_data.refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token invalide")
        
        # Vérifier l'expiration
        if user.refresh_token_expire and datetime.utcnow() > user.refresh_token_expire:
            raise HTTPException(status_code=401, detail="Refresh token expiré")
        
        # Créer un nouveau token d'accès
        access_token = security_service.create_access_token(
            data={"sub": str(user.id), "username": user.nom_utilisateur}
        )
        
        # Mettre à jour l'activité
        user.derniere_activite = datetime.utcnow()
        await db.commit()
        
        # Logger le rafraîchissement
        await security_service.log_audit(
            db, str(user.id), TypeAction.CONNEXION, "auth", "token_refresh",
            f"Token rafraîchi pour: {user.nom_utilisateur}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token,  # Garder le même refresh token
            token_type="bearer",
            expires_in=30 * 60,
            utilisateur=user.to_dict()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors du rafraîchissement: {str(e)}")


@router.post("/logout", response_model=dict)
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Déconnexion utilisateur"""
    try:
        user_id = current_user.get("user_id")
        
        # Récupérer l'utilisateur
        result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            # Invalider le refresh token
            user.refresh_token = None
            user.refresh_token_expire = None
            await db.commit()
        
        # Logger la déconnexion
        await security_service.log_audit(
            db, user_id, TypeAction.DECONNEXION, "auth", "logout",
            f"Déconnexion de: {current_user.get('username')}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True
        )
        
        return {"message": "Déconnexion réussie"}
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la déconnexion: {str(e)}")


@router.post("/setup-2fa", response_model=TwoFactorSetupResponse)
async def setup_2fa(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Configurer l'authentification à deux facteurs"""
    try:
        user_id = current_user.get("user_id")
        
        # Récupérer l'utilisateur
        result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Générer le secret 2FA
        secret = security_service.generate_2fa_secret()
        qr_code_url = security_service.generate_2fa_qr_code(user.nom_utilisateur, secret)
        backup_codes = security_service.generate_backup_codes()
        
        # Sauvegarder temporairement le secret (pas encore activé)
        user.secret_2fa = secret
        await db.commit()
        
        # Logger la configuration 2FA
        await security_service.log_audit(
            db, user_id, TypeAction.ACTIVATION_2FA, "auth", "setup_2fa",
            f"Configuration 2FA pour: {user.nom_utilisateur}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True
        )
        
        return TwoFactorSetupResponse(
            secret=secret,
            qr_code_url=qr_code_url,
            backup_codes=backup_codes
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la configuration: {str(e)}")


@router.post("/verify-2fa", response_model=dict)
async def verify_2fa(
    verify_data: TwoFactorVerifyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Vérifier et activer l'authentification à deux facteurs"""
    try:
        user_id = current_user.get("user_id")
        
        # Récupérer l'utilisateur
        result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.secret_2fa:
            raise HTTPException(status_code=400, detail="2FA non configuré")
        
        # Vérifier le code
        if not security_service.verify_2fa_code(user.secret_2fa, verify_data.code):
            # Logger l'échec de vérification
            await security_service.log_audit(
                db, user_id, TypeAction.ACTIVATION_2FA, "auth", "verify_2fa_failed",
                f"Code 2FA invalide pour: {user.nom_utilisateur}",
                NiveauLog.WARNING,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                succes=False,
                message_erreur="Code 2FA invalide"
            )
            raise HTTPException(status_code=400, detail="Code 2FA invalide")
        
        # Activer 2FA
        user.deux_facteurs_actif = True
        await db.commit()
        
        # Logger l'activation 2FA
        await security_service.log_audit(
            db, user_id, TypeAction.ACTIVATION_2FA, "auth", "activate_2fa",
            f"2FA activé pour: {user.nom_utilisateur}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True
        )
        
        return {"message": "2FA activé avec succès"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification: {str(e)}")


@router.post("/disable-2fa", response_model=dict)
async def disable_2fa(
    verify_data: TwoFactorVerifyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Désactiver l'authentification à deux facteurs"""
    try:
        user_id = current_user.get("user_id")
        
        # Récupérer l'utilisateur
        result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.deux_facteurs_actif:
            raise HTTPException(status_code=400, detail="2FA non activé")
        
        # Vérifier le code
        if not security_service.verify_2fa_code(user.secret_2fa, verify_data.code):
            raise HTTPException(status_code=400, detail="Code 2FA invalide")
        
        # Désactiver 2FA
        user.deux_facteurs_actif = False
        user.secret_2fa = None
        await db.commit()
        
        # Logger la désactivation 2FA
        await security_service.log_audit(
            db, user_id, TypeAction.DESACTIVATION_2FA, "auth", "disable_2fa",
            f"2FA désactivé pour: {user.nom_utilisateur}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True
        )
        
        return {"message": "2FA désactivé avec succès"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la désactivation: {str(e)}")


@router.post("/request-reset-password", response_model=dict)
async def request_reset_password(
    reset_data: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Demander une réinitialisation de mot de passe"""
    try:
        # Récupérer l'utilisateur par email
        result = await db.execute(select(Utilisateur).where(Utilisateur.email == reset_data.email))
        user = result.scalar_one_or_none()
        
        if not user:
            # Ne pas révéler si l'email existe ou non
            return {"message": "Si l'email existe, un lien de réinitialisation a été envoyé"}
        
        # Générer un token de réinitialisation
        reset_token = security_service.generate_secure_token()
        
        # Ici, vous devriez envoyer un email avec le token
        # Pour la démo, on log juste le token
        print(f"Token de réinitialisation pour {user.email}: {reset_token}")
        
        # Logger la demande de réinitialisation
        await security_service.log_audit(
            db, str(user.id), TypeAction.RESET_PASSWORD, "auth", "request_reset",
            f"Demande de réinitialisation pour: {user.email}",
            NiveauLog.INFO,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            succes=True
        )
        
        return {"message": "Si l'email existe, un lien de réinitialisation a été envoyé"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la demande: {str(e)}")


@router.post("/confirm-reset-password", response_model=dict)
async def confirm_reset_password(
    confirm_data: ResetPasswordConfirm,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Confirmer la réinitialisation de mot de passe"""
    try:
        # Dans une vraie implémentation, vous vérifieriez le token
        # Pour la démo, on accepte n'importe quel token
        
        # Vérifier la force du mot de passe
        is_strong, errors = security_service.validate_password_strength(confirm_data.nouveau_mot_de_passe)
        if not is_strong:
            raise HTTPException(status_code=400, detail=f"Mot de passe faible: {', '.join(errors)}")
        
        # Ici, vous devriez récupérer l'utilisateur via le token
        # Pour la démo, on retourne un message générique
        return {"message": "Mot de passe réinitialisé avec succès"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la réinitialisation: {str(e)}")
