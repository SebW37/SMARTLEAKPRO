"""
Service de gestion des API - Phase 7 API & Intégrations
"""

import secrets
import hashlib
import hmac
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
import httpx
import structlog

from ..models import APIKey, Webhook, WebhookExecution, LogAPI, Integration, TypeWebhook, StatutWebhook
from ..schemas import WebhookEvent

logger = structlog.get_logger(__name__)


class APIService:
    """Service centralisé pour la gestion des API et intégrations"""
    
    def __init__(self):
        self.rate_limits = {}  # Cache pour les limites de taux
        self.webhook_queue = asyncio.Queue()  # Queue pour les webhooks
    
    async def create_api_key(
        self, 
        db: AsyncSession, 
        utilisateur_id: str, 
        nom: str, 
        description: str = None,
        scopes: List[str] = None,
        limite_requetes_par_minute: int = 100,
        limite_requetes_par_jour: int = 10000,
        limite_requetes_par_mois: int = 300000,
        date_expiration: datetime = None,
        ips_autorisees: List[str] = None,
        user_agents_autorises: List[str] = None
    ) -> APIKey:
        """Créer une nouvelle clé API"""
        try:
            # Générer la clé API et le secret
            cle_api = self._generate_api_key()
            secret_key = self._generate_secret_key()
            
            # Créer la clé API
            api_key = APIKey(
                nom=nom,
                description=description,
                cle_api=cle_api,
                secret_key=secret_key,
                utilisateur_id=utilisateur_id,
                scopes=scopes or ["read"],
                limite_requetes_par_minute=limite_requetes_par_minute,
                limite_requetes_par_jour=limite_requetes_par_jour,
                limite_requetes_par_mois=limite_requetes_par_mois,
                date_expiration=date_expiration,
                ips_autorisees=ips_autorisees,
                user_agents_autorises=user_agents_autorises
            )
            
            db.add(api_key)
            await db.commit()
            await db.refresh(api_key)
            
            logger.info("API key created", 
                       api_key_id=str(api_key.id), 
                       utilisateur_id=utilisateur_id,
                       nom=nom)
            
            return api_key
            
        except Exception as e:
            await db.rollback()
            logger.error("Error creating API key", error=str(e))
            raise
    
    def _generate_api_key(self) -> str:
        """Générer une clé API unique"""
        return f"sk_{secrets.token_urlsafe(32)}"
    
    def _generate_secret_key(self) -> str:
        """Générer un secret pour la clé API"""
        return secrets.token_urlsafe(64)
    
    async def validate_api_key(
        self, 
        db: AsyncSession, 
        cle_api: str, 
        required_scope: str = None
    ) -> Optional[APIKey]:
        """Valider une clé API et vérifier les permissions"""
        try:
            result = await db.execute(
                select(APIKey).where(APIKey.cle_api == cle_api)
            )
            api_key = result.scalar_one_or_none()
            
            if not api_key:
                return None
            
            # Vérifier si la clé est active
            if not api_key.is_active():
                return None
            
            # Vérifier les quotas
            if not api_key.can_make_request():
                return None
            
            # Vérifier le scope si requis
            if required_scope and not api_key.has_scope(required_scope):
                return None
            
            return api_key
            
        except Exception as e:
            logger.error("Error validating API key", error=str(e))
            return None
    
    async def log_api_request(
        self,
        db: AsyncSession,
        api_key_id: str = None,
        method: str = None,
        endpoint: str = None,
        query_params: dict = None,
        request_headers: dict = None,
        request_body: str = None,
        status_code: int = None,
        response_headers: dict = None,
        response_body: str = None,
        temps_reponse_ms: int = None,
        ip_address: str = None,
        user_agent: str = None,
        utilisateur_id: str = None
    ):
        """Logger une requête API"""
        try:
            log = LogAPI(
                api_key_id=api_key_id,
                method=method,
                endpoint=endpoint,
                query_params=query_params,
                request_headers=request_headers,
                request_body=request_body,
                status_code=status_code,
                response_headers=response_headers,
                response_body=response_body,
                temps_reponse_ms=temps_reponse_ms,
                ip_address=ip_address,
                user_agent=user_agent,
                utilisateur_id=utilisateur_id
            )
            
            db.add(log)
            
            # Mettre à jour les compteurs de la clé API
            if api_key_id:
                result = await db.execute(
                    select(APIKey).where(APIKey.id == api_key_id)
                )
                api_key = result.scalar_one_or_none()
                if api_key:
                    api_key.nombre_requetes_total += 1
                    api_key.nombre_requetes_ce_mois += 1
                    api_key.derniere_utilisation = datetime.utcnow()
            
            await db.commit()
            
        except Exception as e:
            await db.rollback()
            logger.error("Error logging API request", error=str(e))
    
    async def create_webhook(
        self,
        db: AsyncSession,
        utilisateur_id: str,
        nom: str,
        description: str = None,
        url: str = None,
        type_webhook: TypeWebhook = None,
        secret: str = None,
        headers_customises: dict = None,
        conditions: List[dict] = None,
        ressources_filtrees: List[str] = None,
        nombre_tentatives_max: int = 3,
        delai_entre_tentatives: int = 60,
        timeout: int = 30
    ) -> Webhook:
        """Créer un nouveau webhook"""
        try:
            webhook = Webhook(
                nom=nom,
                description=description,
                url=url,
                type_webhook=type_webhook,
                utilisateur_id=utilisateur_id,
                secret=secret,
                headers_customises=headers_customises,
                conditions=conditions,
                ressources_filtrees=ressources_filtrees,
                nombre_tentatives_max=nombre_tentatives_max,
                delai_entre_tentatives=delai_entre_tentatives,
                timeout=timeout
            )
            
            db.add(webhook)
            await db.commit()
            await db.refresh(webhook)
            
            logger.info("Webhook created", 
                       webhook_id=str(webhook.id), 
                       utilisateur_id=utilisateur_id,
                       nom=nom)
            
            return webhook
            
        except Exception as e:
            await db.rollback()
            logger.error("Error creating webhook", error=str(e))
            raise
    
    async def trigger_webhook(
        self,
        db: AsyncSession,
        type_evenement: str,
        donnees_evenement: dict,
        ressource_id: str = None,
        utilisateur_id: str = None
    ):
        """Déclencher un webhook pour un événement"""
        try:
            # Récupérer les webhooks actifs pour ce type d'événement
            result = await db.execute(
                select(Webhook).where(
                    and_(
                        Webhook.type_webhook == type_evenement,
                        Webhook.statut == StatutWebhook.ACTIVE
                    )
                )
            )
            webhooks = result.scalars().all()
            
            # Traiter chaque webhook
            for webhook in webhooks:
                if webhook.should_trigger(donnees_evenement):
                    await self._execute_webhook(db, webhook, type_evenement, donnees_evenement, ressource_id)
            
        except Exception as e:
            logger.error("Error triggering webhook", error=str(e))
    
    async def _execute_webhook(
        self,
        db: AsyncSession,
        webhook: Webhook,
        type_evenement: str,
        donnees_evenement: dict,
        ressource_id: str = None
    ):
        """Exécuter un webhook"""
        try:
            # Créer l'exécution du webhook
            execution = WebhookExecution(
                webhook_id=webhook.id,
                type_evenement=type_evenement,
                ressource_id=ressource_id,
                donnees_evenement=donnees_evenement,
                statut=StatutWebhook.PENDING
            )
            
            db.add(execution)
            await db.commit()
            await db.refresh(execution)
            
            # Exécuter le webhook de manière asynchrone
            asyncio.create_task(self._send_webhook_request(webhook, execution, donnees_evenement))
            
        except Exception as e:
            logger.error("Error executing webhook", error=str(e))
    
    async def _send_webhook_request(
        self,
        webhook: Webhook,
        execution: WebhookExecution,
        donnees_evenement: dict
    ):
        """Envoyer la requête webhook"""
        try:
            # Préparer les données
            event_data = {
                "type": webhook.type_webhook.value,
                "timestamp": datetime.utcnow().isoformat(),
                "data": donnees_evenement,
                "resource_id": execution.ressource_id
            }
            
            # Ajouter la signature HMAC si secret fourni
            headers = {"Content-Type": "application/json"}
            if webhook.secret:
                signature = self._generate_webhook_signature(webhook.secret, json.dumps(event_data))
                headers["X-Webhook-Signature"] = f"sha256={signature}"
            
            # Ajouter les headers personnalisés
            if webhook.headers_customises:
                headers.update(webhook.headers_customises)
            
            # Envoyer la requête
            async with httpx.AsyncClient(timeout=webhook.timeout) as client:
                start_time = datetime.utcnow()
                response = await client.post(
                    webhook.url,
                    json=event_data,
                    headers=headers
                )
                end_time = datetime.utcnow()
                
                # Calculer le temps de réponse
                temps_reponse_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Mettre à jour l'exécution
                execution.statut = StatutWebhook.DELIVERED if response.status_code < 400 else StatutWebhook.FAILED
                execution.code_reponse_http = response.status_code
                execution.temps_reponse_ms = temps_reponse_ms
                execution.date_fin = end_time
                
                if response.status_code >= 400:
                    execution.message_erreur = f"HTTP {response.status_code}: {response.text}"
                
                # Mettre à jour les compteurs du webhook
                webhook.nombre_executions_total += 1
                if execution.statut == StatutWebhook.DELIVERED:
                    webhook.nombre_executions_reussies += 1
                else:
                    webhook.nombre_executions_echec += 1
                
                webhook.derniere_execution = end_time
                
                # Sauvegarder en base
                from ..database import get_db
                async for db in get_db():
                    await db.commit()
                    break
                
        except Exception as e:
            logger.error("Error sending webhook request", error=str(e))
            
            # Marquer comme échec
            execution.statut = StatutWebhook.FAILED
            execution.message_erreur = str(e)
            execution.date_fin = datetime.utcnow()
            
            # Mettre à jour les compteurs
            webhook.nombre_executions_total += 1
            webhook.nombre_executions_echec += 1
            
            # Sauvegarder en base
            from ..database import get_db
            async for db in get_db():
                await db.commit()
                break
    
    def _generate_webhook_signature(self, secret: str, payload: str) -> str:
        """Générer une signature HMAC pour le webhook"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def get_api_stats(self, db: AsyncSession, utilisateur_id: str = None) -> dict:
        """Récupérer les statistiques de l'API"""
        try:
            # Statistiques générales
            total_requetes = await db.execute(select(func.count(LogAPI.id)))
            total_requetes = total_requetes.scalar()
            
            # Requêtes ce mois
            debut_mois = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            requetes_ce_mois = await db.execute(
                select(func.count(LogAPI.id)).where(LogAPI.timestamp >= debut_mois)
            )
            requetes_ce_mois = requetes_ce_mois.scalar()
            
            # Requêtes aujourd'hui
            debut_jour = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            requetes_aujourd_hui = await db.execute(
                select(func.count(LogAPI.id)).where(LogAPI.timestamp >= debut_jour)
            )
            requetes_aujourd_hui = requetes_aujourd_hui.scalar()
            
            # Taux d'erreur
            requetes_erreur = await db.execute(
                select(func.count(LogAPI.id)).where(LogAPI.status_code >= 400)
            )
            requetes_erreur = requetes_erreur.scalar()
            taux_erreur = (requetes_erreur / total_requetes * 100) if total_requetes > 0 else 0
            
            # Temps de réponse moyen
            temps_moyen = await db.execute(
                select(func.avg(LogAPI.temps_reponse_ms))
            )
            temps_moyen = temps_moyen.scalar() or 0
            
            # Statistiques par endpoint
            par_endpoint = await db.execute(
                select(LogAPI.endpoint, func.count(LogAPI.id))
                .group_by(LogAPI.endpoint)
                .order_by(desc(func.count(LogAPI.id)))
                .limit(10)
            )
            par_endpoint = dict(par_endpoint.fetchall())
            
            # Statistiques par status code
            par_status = await db.execute(
                select(LogAPI.status_code, func.count(LogAPI.id))
                .group_by(LogAPI.status_code)
                .order_by(desc(func.count(LogAPI.id)))
            )
            par_status = dict(par_status.fetchall())
            
            # Top IPs
            top_ips = await db.execute(
                select(LogAPI.ip_address, func.count(LogAPI.id))
                .where(LogAPI.ip_address.isnot(None))
                .group_by(LogAPI.ip_address)
                .order_by(desc(func.count(LogAPI.id)))
                .limit(10)
            )
            top_ips = [{"ip": ip, "count": count} for ip, count in top_ips.fetchall()]
            
            return {
                "total_requetes": total_requetes,
                "requetes_ce_mois": requetes_ce_mois,
                "requetes_aujourd_hui": requetes_aujourd_hui,
                "taux_erreur": round(taux_erreur, 2),
                "temps_reponse_moyen": round(temps_moyen, 2),
                "par_endpoint": par_endpoint,
                "par_status_code": par_status,
                "top_ips": top_ips
            }
            
        except Exception as e:
            logger.error("Error getting API stats", error=str(e))
            return {}
    
    async def create_integration(
        self,
        db: AsyncSession,
        utilisateur_id: str,
        nom: str,
        description: str = None,
        type_integration: str = None,
        configuration: dict = None
    ) -> Integration:
        """Créer une nouvelle intégration"""
        try:
            integration = Integration(
                nom=nom,
                description=description,
                type_integration=type_integration,
                configuration=configuration,
                utilisateur_id=utilisateur_id
            )
            
            db.add(integration)
            await db.commit()
            await db.refresh(integration)
            
            logger.info("Integration created", 
                       integration_id=str(integration.id), 
                       utilisateur_id=utilisateur_id,
                       nom=nom)
            
            return integration
            
        except Exception as e:
            await db.rollback()
            logger.error("Error creating integration", error=str(e))
            raise


# Instance globale du service
api_service = APIService()
