"""
Middleware de rate limiting
"""

import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from loguru import logger
from app.services.redis_service import redis_service


class RateLimitMiddleware:
    """
    Middleware para limitar la tasa de requests
    """
    
    def __init__(self):
        # Configuración de límites por tipo de endpoint
        self.limits = {
            "health": {"requests": 100, "window": 60},  # 100 requests por minuto
            "reniec_query": {"requests": 10, "window": 60},  # 10 consultas por minuto
            "api_general": {"requests": 1000, "window": 3600},  # 1000 requests por hora
            "auth": {"requests": 5, "window": 60},  # 5 intentos de auth por minuto
            "upload": {"requests": 10, "window": 300},  # 10 uploads por 5 minutos
            "default": {"requests": 500, "window": 3600}  # 500 requests por hora
        }
        
        # Rutas que no tienen límite
        self.exempt_paths = [
            "/docs",
            "/redoc", 
            "/openapi.json"
        ]
        
        # Cache en memoria para casos donde Redis no esté disponible
        self.memory_cache: Dict[str, Dict] = {}
    
    async def __call__(self, request: Request, call_next):
        """
        Verificar límites de tasa
        """
        # Verificar si la ruta está exenta
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Determinar tipo de endpoint
        endpoint_type = self._get_endpoint_type(request)
        
        # Obtener identificador del cliente
        client_id = await self._get_client_identifier(request)
        
        # Verificar límite
        if not await self._check_rate_limit(client_id, endpoint_type):
            logger.warning(f"Rate limit exceeded for {client_id} on {endpoint_type}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "type": endpoint_type,
                    "retry_after": self.limits[endpoint_type]["window"]
                }
            )
        
        return await call_next(request)
    
    async def _get_client_identifier(self, request: Request) -> str:
        """
        Obtener identificador único del cliente
        """
        # Usar IP real (considerando proxies)
        client_ip = self._get_client_ip(request)
        
        # Si hay usuario autenticado, usar su ID
        user = getattr(request.state, 'user', None)
        if user and user.get('user_id'):
            return f"user:{user['user_id']}"
        
        return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Obtener IP real del cliente
        """
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback a la dirección de conexión
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def _get_endpoint_type(self, request: Request) -> str:
        """
        Determinar el tipo de endpoint para aplicar el límite apropiado
        """
        path = request.url.path.lower()
        
        if "health" in path or "/live" in path or "/ready" in path:
            return "health"
        
        elif "/reniec/consulta-dni" in path or "/reniec/verificar-dni" in path:
            return "reniec_query"
        
        elif "login" in path or "auth" in path or "token" in path:
            return "auth"
        
        elif "upload" in path or "file" in path:
            return "upload"
        
        elif path.startswith("/api/"):
            return "api_general"
        
        else:
            return "default"
    
    async def _check_rate_limit(self, client_id: str, endpoint_type: str) -> bool:
        """
        Verificar si el cliente excede el límite de tasa
        """
        limit_config = self.limits[endpoint_type]
        limit = limit_config["requests"]
        window = limit_config["window"]
        
        if redis_service.connected:
            # Usar Redis para rate limiting
            try:
                return await redis_service.set_rate_limit(
                    f"{client_id}:{endpoint_type}",
                    limit,
                    window
                )
            except Exception as e:
                logger.error(f"Error usando Redis para rate limiting: {e}")
                # Fallback a cache en memoria
        
        # Fallback a cache en memoria
        return self._check_memory_rate_limit(client_id, endpoint_type, limit, window)
    
    def _check_memory_rate_limit(self, client_id: str, endpoint_type: str, limit: int, window: int) -> bool:
        """
        Rate limiting usando cache en memoria (fallback)
        """
        key = f"{client_id}:{endpoint_type}"
        current_time = time.time()
        
        if key not in self.memory_cache:
            self.memory_cache[key] = {
                "requests": [],
                "window_start": current_time
            }
        
        cache_entry = self.memory_cache[key]
        
        # Limpiar requests fuera de la ventana
        window_start = current_time - window
        cache_entry["requests"] = [
            req_time for req_time in cache_entry["requests"]
            if req_time > window_start
        ]
        
        # Verificar límite
        if len(cache_entry["requests"]) >= limit:
            return False
        
        # Agregar request actual
        cache_entry["requests"].append(current_time)
        
        # Limpiar cache antiguo periódicamente
        self._cleanup_old_cache(current_time)
        
        return True
    
    def _cleanup_old_cache(self, current_time: float):
        """
        Limpiar entradas antiguas del cache en memoria
        """
        keys_to_delete = []
        
        for key, cache_entry in self.memory_cache.items():
            # Si no hay requests en la última hora, eliminar
            if not cache_entry["requests"]:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.memory_cache[key]
        
        # Limitar tamaño del cache
        if len(self.memory_cache) > 1000:
            # Eliminar las 100 entradas más antiguas
            sorted_keys = sorted(
                self.memory_cache.keys(),
                key=lambda k: min(self.memory_cache[k]["requests"]) if self.memory_cache[k]["requests"] else current_time
            )
            
            for key in sorted_keys[:100]:
                del self.memory_cache[key]