"""
Middleware de rate limiting pour les API - Phase 7
"""

import time
from typing import Dict, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import structlog

logger = structlog.get_logger(__name__)


class RateLimiter:
    """Gestionnaire de rate limiting pour les API"""
    
    def __init__(self):
        self.requests: Dict[str, Dict[str, float]] = {}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window: int = 60,
        burst_limit: int = None
    ) -> bool:
        """
        Vérifier si une requête est autorisée
        
        Args:
            key: Clé unique pour l'identification (IP, API key, etc.)
            limit: Nombre maximum de requêtes par fenêtre
            window: Fenêtre de temps en secondes
            burst_limit: Limite de burst (requêtes simultanées)
        
        Returns:
            bool: True si autorisé, False sinon
        """
        current_time = time.time()
        
        # Nettoyage périodique
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(current_time)
            self.last_cleanup = current_time
        
        # Initialiser la clé si nécessaire
        if key not in self.requests:
            self.requests[key] = {
                "requests": [],
                "burst_count": 0,
                "last_burst_reset": current_time
            }
        
        key_data = self.requests[key]
        
        # Vérifier la limite de burst
        if burst_limit:
            if current_time - key_data["last_burst_reset"] > 1:  # Reset chaque seconde
                key_data["burst_count"] = 0
                key_data["last_burst_reset"] = current_time
            
            if key_data["burst_count"] >= burst_limit:
                return False
            
            key_data["burst_count"] += 1
        
        # Nettoyer les requêtes anciennes
        cutoff_time = current_time - window
        key_data["requests"] = [
            req_time for req_time in key_data["requests"] 
            if req_time > cutoff_time
        ]
        
        # Vérifier la limite
        if len(key_data["requests"]) >= limit:
            return False
        
        # Ajouter la requête actuelle
        key_data["requests"].append(current_time)
        
        return True
    
    def get_remaining_requests(self, key: str, limit: int, window: int = 60) -> int:
        """Obtenir le nombre de requêtes restantes"""
        if key not in self.requests:
            return limit
        
        current_time = time.time()
        cutoff_time = current_time - window
        
        key_data = self.requests[key]
        recent_requests = [
            req_time for req_time in key_data["requests"] 
            if req_time > cutoff_time
        ]
        
        return max(0, limit - len(recent_requests))
    
    def get_reset_time(self, key: str, window: int = 60) -> float:
        """Obtenir le temps de reset de la fenêtre"""
        if key not in self.requests or not self.requests[key]["requests"]:
            return time.time()
        
        oldest_request = min(self.requests[key]["requests"])
        return oldest_request + window
    
    def _cleanup_old_entries(self, current_time: float):
        """Nettoyer les entrées anciennes"""
        keys_to_remove = []
        
        for key, key_data in self.requests.items():
            # Supprimer les clés sans requêtes récentes
            if not key_data["requests"]:
                keys_to_remove.append(key)
                continue
            
            # Supprimer les clés avec des requêtes très anciennes
            oldest_request = min(key_data["requests"])
            if current_time - oldest_request > 3600:  # 1 heure
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.requests[key]
    
    def reset_key(self, key: str):
        """Réinitialiser les compteurs pour une clé"""
        if key in self.requests:
            del self.requests[key]


# Instance globale
rate_limiter = RateLimiter()


class RateLimitMiddleware:
    """Middleware FastAPI pour le rate limiting"""
    
    def __init__(
        self, 
        calls_per_minute: int = 60,
        calls_per_hour: int = 1000,
        calls_per_day: int = 10000,
        burst_limit: int = 10
    ):
        self.calls_per_minute = calls_per_minute
        self.calls_per_hour = calls_per_hour
        self.calls_per_day = calls_per_day
        self.burst_limit = burst_limit
    
    async def __call__(self, request: Request, call_next):
        # Identifier la clé (IP ou API key)
        key = self._get_identifier(request)
        
        # Vérifier les limites
        if not self._check_limits(key, request):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Trop de requêtes. Veuillez réessayer plus tard.",
                    "retry_after": int(rate_limiter.get_reset_time(key, 60) - time.time())
                },
                headers={
                    "Retry-After": str(int(rate_limiter.get_reset_time(key, 60) - time.time())),
                    "X-RateLimit-Limit": str(self.calls_per_minute),
                    "X-RateLimit-Remaining": str(rate_limiter.get_remaining_requests(key, self.calls_per_minute)),
                    "X-RateLimit-Reset": str(int(rate_limiter.get_reset_time(key, 60)))
                }
            )
        
        # Ajouter les headers de rate limiting
        response = await call_next(request)
        
        response.headers["X-RateLimit-Limit"] = str(self.calls_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            rate_limiter.get_remaining_requests(key, self.calls_per_minute)
        )
        response.headers["X-RateLimit-Reset"] = str(int(rate_limiter.get_reset_time(key, 60)))
        
        return response
    
    def _get_identifier(self, request: Request) -> str:
        """Obtenir l'identifiant pour le rate limiting"""
        # Priorité: API key > IP
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        
        # Utiliser l'IP
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _check_limits(self, key: str, request: Request) -> bool:
        """Vérifier toutes les limites de rate limiting"""
        # Limite de burst (requêtes simultanées)
        if not rate_limiter.is_allowed(key, self.burst_limit, 1, self.burst_limit):
            logger.warning("Burst limit exceeded", key=key, limit=self.burst_limit)
            return False
        
        # Limite par minute
        if not rate_limiter.is_allowed(key, self.calls_per_minute, 60):
            logger.warning("Minute limit exceeded", key=key, limit=self.calls_per_minute)
            return False
        
        # Limite par heure
        if not rate_limiter.is_allowed(key, self.calls_per_hour, 3600):
            logger.warning("Hour limit exceeded", key=key, limit=self.calls_per_hour)
            return False
        
        # Limite par jour
        if not rate_limiter.is_allowed(key, self.calls_per_day, 86400):
            logger.warning("Day limit exceeded", key=key, limit=self.calls_per_day)
            return False
        
        return True


class APIKeyRateLimitMiddleware:
    """Middleware de rate limiting spécifique aux clés API"""
    
    def __init__(self):
        self.api_limits: Dict[str, Dict[str, int]] = {}
    
    async def __call__(self, request: Request, call_next):
        # Vérifier si c'est une requête avec clé API
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return await call_next(request)
        
        # Récupérer les limites de la clé API
        limits = self._get_api_key_limits(api_key)
        if not limits:
            return await call_next(request)
        
        # Vérifier les limites spécifiques à la clé
        if not self._check_api_key_limits(api_key, limits):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "API rate limit exceeded",
                    "message": "Limite de taux dépassée pour cette clé API",
                    "retry_after": 60
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(limits.get("per_minute", 60)),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        return await call_next(request)
    
    def _get_api_key_limits(self, api_key: str) -> Optional[Dict[str, int]]:
        """Récupérer les limites d'une clé API"""
        # En production, récupérer depuis la base de données
        # Pour la démo, utiliser des limites par défaut
        return {
            "per_minute": 100,
            "per_hour": 1000,
            "per_day": 10000
        }
    
    def _check_api_key_limits(self, api_key: str, limits: Dict[str, int]) -> bool:
        """Vérifier les limites d'une clé API"""
        key = f"api_key:{api_key}"
        
        # Vérifier la limite par minute
        if not rate_limiter.is_allowed(key, limits.get("per_minute", 100), 60):
            return False
        
        # Vérifier la limite par heure
        if not rate_limiter.is_allowed(key, limits.get("per_hour", 1000), 3600):
            return False
        
        # Vérifier la limite par jour
        if not rate_limiter.is_allowed(key, limits.get("per_day", 10000), 86400):
            return False
        
        return True
