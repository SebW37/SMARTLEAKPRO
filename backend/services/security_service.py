"""
Service de sécurité avancé pour la Phase 6
"""

import os
import secrets
import hashlib
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
import structlog

from ..models import Utilisateur, LogAudit, ConsentementRGPD, RoleUtilisateur, StatutUtilisateur, TypeAction, NiveauLog
from ..schemas import UtilisateurCreate, LoginRequest

logger = structlog.get_logger()

# Configuration de sécurité
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30

# Contexte de hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityService:
    """Service de sécurité pour authentification, autorisation et audit"""
    
    def __init__(self):
        self.pwd_context = pwd_context
    
    # === AUTHENTIFICATION ===
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifier un mot de passe"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hacher un mot de passe"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Créer un token d'accès JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Créer un token de rafraîchissement"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        """Vérifier et décoder un token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError:
            return None
    
    async def authenticate_user(self, db: AsyncSession, username: str, password: str) -> Optional[Utilisateur]:
        """Authentifier un utilisateur"""
        try:
            # Rechercher par nom d'utilisateur ou email
            result = await db.execute(
                select(Utilisateur).where(
                    or_(
                        Utilisateur.nom_utilisateur == username,
                        Utilisateur.email == username
                    )
                )
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # Vérifier le statut
            if not user.is_active():
                return None
            
            # Vérifier le verrouillage
            if user.is_locked():
                return None
            
            # Vérifier le mot de passe
            if not self.verify_password(password, user.mot_de_passe_hash):
                # Incrémenter les tentatives d'échec
                await self._increment_failed_attempts(db, user)
                return None
            
            # Réinitialiser les tentatives d'échec
            await self._reset_failed_attempts(db, user)
            
            return user
            
        except Exception as e:
            logger.error("Erreur lors de l'authentification", error=str(e), username=username)
            return None
    
    async def _increment_failed_attempts(self, db: AsyncSession, user: Utilisateur):
        """Incrémenter les tentatives d'échec"""
        user.nombre_tentatives_echec += 1
        
        # Verrouiller le compte si trop de tentatives
        if user.nombre_tentatives_echec >= MAX_LOGIN_ATTEMPTS:
            user.compte_verrouille_jusqu_a = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            await self._log_audit(
                db, user.id, TypeAction.CONNEXION, "auth", "login_failed_locked",
                f"Compte verrouillé après {MAX_LOGIN_ATTEMPTS} tentatives d'échec",
                NiveauLog.WARNING
            )
        
        await db.commit()
    
    async def _reset_failed_attempts(self, db: AsyncSession, user: Utilisateur):
        """Réinitialiser les tentatives d'échec"""
        if user.nombre_tentatives_echec > 0:
            user.nombre_tentatives_echec = 0
            user.compte_verrouille_jusqu_a = None
            await db.commit()
    
    # === 2FA (Two-Factor Authentication) ===
    
    def generate_2fa_secret(self) -> str:
        """Générer un secret 2FA"""
        return pyotp.random_base32()
    
    def generate_2fa_qr_code(self, username: str, secret: str) -> str:
        """Générer un QR code pour 2FA"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name="SmartLeakPro"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir en base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_2fa_code(self, secret: str, code: str) -> bool:
        """Vérifier un code 2FA"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
    
    def generate_backup_codes(self, count: int = 10) -> list:
        """Générer des codes de sauvegarde"""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    # === AUTORISATION ===
    
    def check_permission(self, user: Utilisateur, resource: str, action: str) -> bool:
        """Vérifier les permissions d'un utilisateur"""
        return user.can_access(resource, action)
    
    def get_user_permissions(self, user: Utilisateur) -> list:
        """Obtenir toutes les permissions d'un utilisateur"""
        permissions = {
            RoleUtilisateur.ADMIN: ["*"],
            RoleUtilisateur.MANAGER: [
                "clients:read", "clients:write", "clients:delete",
                "interventions:read", "interventions:write", "interventions:delete",
                "planning:read", "planning:write", "planning:delete",
                "rapports:read", "rapports:write", "rapports:delete",
                "medias:read", "medias:write", "medias:delete",
                "utilisateurs:read", "utilisateurs:write"
            ],
            RoleUtilisateur.TECHNICIEN: [
                "clients:read",
                "interventions:read", "interventions:write",
                "planning:read", "planning:write",
                "rapports:read", "rapports:write",
                "medias:read", "medias:write", "medias:upload"
            ],
            RoleUtilisateur.CONSULTANT: [
                "clients:read",
                "interventions:read",
                "planning:read",
                "rapports:read", "rapports:export",
                "medias:read", "medias:download"
            ],
            RoleUtilisateur.LECTEUR: [
                "clients:read",
                "interventions:read",
                "planning:read",
                "rapports:read",
                "medias:read"
            ]
        }
        
        return permissions.get(user.role, [])
    
    # === AUDIT TRAIL ===
    
    async def log_audit(
        self,
        db: AsyncSession,
        utilisateur_id: Optional[str],
        type_action: TypeAction,
        ressource: str,
        action: str,
        description: Optional[str] = None,
        niveau_log: NiveauLog = NiveauLog.INFO,
        ressource_id: Optional[str] = None,
        anciennes_valeurs: Optional[dict] = None,
        nouvelles_valeurs: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        module: Optional[str] = None,
        fonction: Optional[str] = None,
        ligne_code: Optional[int] = None,
        duree_ms: Optional[int] = None,
        succes: bool = True,
        message_erreur: Optional[str] = None
    ):
        """Enregistrer un log d'audit"""
        try:
            # Récupérer le nom d'utilisateur si possible
            nom_utilisateur = None
            if utilisateur_id:
                result = await db.execute(
                    select(Utilisateur.nom_utilisateur).where(Utilisateur.id == utilisateur_id)
                )
                nom_utilisateur = result.scalar_one_or_none()
            
            log = LogAudit(
                utilisateur_id=utilisateur_id,
                nom_utilisateur=nom_utilisateur,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                type_action=type_action,
                ressource=ressource,
                ressource_id=ressource_id,
                action=action,
                description=description,
                anciennes_valeurs=anciennes_valeurs,
                nouvelles_valeurs=nouvelles_valeurs,
                niveau_log=niveau_log,
                module=module,
                fonction=fonction,
                ligne_code=ligne_code,
                duree_ms=duree_ms,
                succes=succes,
                message_erreur=message_erreur
            )
            
            db.add(log)
            await db.commit()
            
            # Logger également dans les logs structurés
            logger.info(
                "Audit log",
                utilisateur_id=utilisateur_id,
                nom_utilisateur=nom_utilisateur,
                type_action=type_action.value,
                ressource=ressource,
                action=action,
                description=description,
                niveau_log=niveau_log.value,
                ip_address=ip_address,
                succes=succes
            )
            
        except Exception as e:
            logger.error("Erreur lors de l'enregistrement du log d'audit", error=str(e))
    
    # === RGPD ===
    
    async def create_consentement(
        self,
        db: AsyncSession,
        utilisateur_id: str,
        type_consentement: str,
        consentement_donne: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        source: str = "web"
    ) -> ConsentementRGPD:
        """Créer un consentement RGPD"""
        consentement = ConsentementRGPD(
            utilisateur_id=utilisateur_id,
            type_consentement=type_consentement,
            consentement_donne=consentement_donne,
            ip_address=ip_address,
            user_agent=user_agent,
            source=source
        )
        
        db.add(consentement)
        await db.commit()
        await db.refresh(consentement)
        
        return consentement
    
    async def revoke_consentement(
        self,
        db: AsyncSession,
        utilisateur_id: str,
        type_consentement: str,
        raison: Optional[str] = None
    ) -> bool:
        """Révoquer un consentement RGPD"""
        try:
            result = await db.execute(
                select(ConsentementRGPD).where(
                    and_(
                        ConsentementRGPD.utilisateur_id == utilisateur_id,
                        ConsentementRGPD.type_consentement == type_consentement,
                        ConsentementRGPD.date_revocation.is_(None)
                    )
                )
            )
            consentement = result.scalar_one_or_none()
            
            if consentement:
                consentement.date_revocation = datetime.utcnow()
                consentement.raison_revocation = raison
                await db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error("Erreur lors de la révocation du consentement", error=str(e))
            return False
    
    async def get_user_data_export(self, db: AsyncSession, utilisateur_id: str) -> dict:
        """Exporter toutes les données d'un utilisateur (RGPD)"""
        try:
            # Récupérer l'utilisateur
            result = await db.execute(
                select(Utilisateur).where(Utilisateur.id == utilisateur_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return {}
            
            # Récupérer les logs d'audit
            logs_result = await db.execute(
                select(LogAudit).where(LogAudit.utilisateur_id == utilisateur_id)
            )
            logs = logs_result.scalars().all()
            
            # Récupérer les consentements
            consentements_result = await db.execute(
                select(ConsentementRGPD).where(ConsentementRGPD.utilisateur_id == utilisateur_id)
            )
            consentements = consentements_result.scalars().all()
            
            return {
                "utilisateur": user.to_dict(),
                "logs_audit": [log.to_dict() for log in logs],
                "consentements": [consentement.to_dict() for consentement in consentements],
                "date_export": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Erreur lors de l'export des données utilisateur", error=str(e))
            return {}
    
    async def anonymize_user_data(self, db: AsyncSession, utilisateur_id: str, raison: str) -> bool:
        """Anonymiser les données d'un utilisateur (RGPD)"""
        try:
            # Récupérer l'utilisateur
            result = await db.execute(
                select(Utilisateur).where(Utilisateur.id == utilisateur_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Anonymiser les données personnelles
            user.nom = f"Utilisateur_{user.id[:8]}"
            user.prenom = "Anonyme"
            user.email = f"anonyme_{user.id[:8]}@anonyme.local"
            user.telephone = None
            user.adresse = None
            user.date_naissance = None
            user.date_anonymisation = datetime.utcnow()
            user.statut = StatutUtilisateur.INACTIF
            
            await db.commit()
            
            # Logger l'anonymisation
            await self.log_audit(
                db, utilisateur_id, TypeAction.MODIFICATION, "utilisateurs", "anonymize",
                f"Données anonymisées - Raison: {raison}",
                NiveauLog.INFO
            )
            
            return True
            
        except Exception as e:
            logger.error("Erreur lors de l'anonymisation des données", error=str(e))
            return False
    
    # === SÉCURITÉ ===
    
    def validate_password_strength(self, password: str) -> Tuple[bool, list]:
        """Valider la force d'un mot de passe"""
        errors = []
        
        if len(password) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères")
        
        if not any(c.isupper() for c in password):
            errors.append("Le mot de passe doit contenir au moins une majuscule")
        
        if not any(c.islower() for c in password):
            errors.append("Le mot de passe doit contenir au moins une minuscule")
        
        if not any(c.isdigit() for c in password):
            errors.append("Le mot de passe doit contenir au moins un chiffre")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Le mot de passe doit contenir au moins un caractère spécial")
        
        return len(errors) == 0, errors
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Générer un token sécurisé"""
        return secrets.token_urlsafe(length)
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hasher des données sensibles"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    # === MONITORING ===
    
    async def get_security_stats(self, db: AsyncSession) -> dict:
        """Obtenir les statistiques de sécurité"""
        try:
            now = datetime.utcnow()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Statistiques utilisateurs
            total_users = await db.scalar(select(func.count(Utilisateur.id)))
            active_users = await db.scalar(
                select(func.count(Utilisateur.id)).where(Utilisateur.statut == StatutUtilisateur.ACTIF)
            )
            users_with_2fa = await db.scalar(
                select(func.count(Utilisateur.id)).where(Utilisateur.deux_facteurs_actif == True)
            )
            
            # Statistiques de connexion
            connexions_ce_mois = await db.scalar(
                select(func.count(LogAudit.id)).where(
                    and_(
                        LogAudit.type_action == TypeAction.CONNEXION,
                        LogAudit.timestamp >= month_start,
                        LogAudit.succes == True
                    )
                )
            )
            
            echecs_ce_mois = await db.scalar(
                select(func.count(LogAudit.id)).where(
                    and_(
                        LogAudit.type_action == TypeAction.CONNEXION,
                        LogAudit.timestamp >= month_start,
                        LogAudit.succes == False
                    )
                )
            )
            
            # Statistiques par rôle
            role_stats = await db.execute(
                select(Utilisateur.role, func.count(Utilisateur.id))
                .group_by(Utilisateur.role)
            )
            par_role = dict(role_stats.fetchall())
            
            # Statistiques par statut
            statut_stats = await db.execute(
                select(Utilisateur.statut, func.count(Utilisateur.id))
                .group_by(Utilisateur.statut)
            )
            par_statut = dict(statut_stats.fetchall())
            
            return {
                "total_utilisateurs": total_users or 0,
                "utilisateurs_actifs": active_users or 0,
                "utilisateurs_avec_2fa": users_with_2fa or 0,
                "connexions_ce_mois": connexions_ce_mois or 0,
                "echecs_connexion_ce_mois": echecs_ce_mois or 0,
                "par_role": par_role,
                "par_statut": par_statut
            }
            
        except Exception as e:
            logger.error("Erreur lors de la récupération des statistiques de sécurité", error=str(e))
            return {}


# Instance globale du service
security_service = SecurityService()
