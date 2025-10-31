"""
Middleware personalizado para Rate Limiting
Incluye funcionalidades avanzadas de rate limiting
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import hashlib
from typing import Dict, List, Optional
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class AdvancedRateLimitMiddleware:
    """
    Middleware avanzado de rate limiting con múltiples estrategias
    """
    
    def __init__(
        self,
        public_limit: int = 100,
        admin_limit: int = 50,
        window_size: int = 60,
        burst_limit: int = 10
    ):
        """
        Inicializar middleware de rate limiting
        
        Args:
            public_limit: Límite para endpoints públicos
            admin_limit: Límite para endpoints de administración
            window_size: Ventana de tiempo en segundos
            burst_limit: Límite de burst adicional
        """
        self.public_limit = public_limit
        self.admin_limit = admin_limit
        self.window_size = window_size
        self.burst_limit = burst_limit
        
        # Almacén de requests por IP
        self.requests: Dict[str, deque] = defaultdict(deque)
        
        # Contador de requests burst por IP
        self.burst_counter: Dict[str, int] = defaultdict(int)
        
        # IPs bloqueadas temporalmente
        self.blocked_ips: Dict[str, float] = {}
        
        # Limpiar bloqueos antiguos periódicamente
        self._cleanup_interval = 300  # 5 minutos
        self._last_cleanup = time.time()
    
    def _cleanup_old_data(self):
        """Limpiar datos antiguos del almacenamiento"""
        current_time = time.time()
        
        # Limpiar bloqueos expirados
        expired_ips = [
            ip for ip, block_time in self.blocked_ips.items()
            if current_time - block_time > 600  # 10 minutos de bloqueo
        ]
        for ip in expired_ips:
            del self.blocked_ips[ip]
            if ip in self.burst_counter:
                del self.burst_counter[ip]
        
        # Limpiar requests antiguos
        cutoff_time = current_time - self.window_size
        for ip in list(self.requests.keys()):
            # Remover requests antiguos
            while self.requests[ip] and self.requests[ip][0] < cutoff_time:
                self.requests[ip].popleft()
            
            # Remover IP si no tiene requests recientes
            if not self.requests[ip]:
                del self.requests[ip]
        
        self._last_cleanup = current_time
    
    def _get_client_key(self, request: Request) -> str:
        """
        Generar clave única para el cliente
        Combina IP y User-Agent para identificar clientes únicos
        """
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        # Crear hash único del cliente
        client_string = f"{client_ip}:{user_agent}"
        return hashlib.md5(client_string.encode()).hexdigest()[:16]
    
    def _is_admin_endpoint(self, path: str) -> bool:
        """Determinar si el endpoint es de administración"""
        admin_prefixes = ["/api/admin", "/api/v1/admin"]
        return any(path.startswith(prefix) for prefix in admin_prefixes)
    
    def _should_bypass_rate_limit(self, request: Request) -> bool:
        """
        Determinar si el request debe ser exento de rate limiting
        """
        bypass_paths = [
            "/health",
            "/health/live",
            "/health/ready",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        # Health checks siempre pasan
        if request.url.path in bypass_paths:
            return True
        
        # Requests internos o de monitoreo
        user_agent = request.headers.get("user-agent", "").lower()
        if "load balancer" in user_agent or "health check" in user_agent:
            return True
        
        return False
    
    def _check_rate_limit(
        self, 
        client_key: str, 
        is_admin: bool, 
        current_time: float
    ) -> tuple[bool, Optional[str]]:
        """
        Verificar rate limiting para un cliente
        
        Returns:
            Tuple (allowed: bool, reason: Optional[str])
        """
        # Verificar si está bloqueado
        if client_key in self.blocked_ips:
            return False, "IP bloqueada temporalmente"
        
        # Obtener límite apropiado
        limit = self.admin_limit if is_admin else self.public_limit
        
        # Verificar límite de ventana deslizante
        request_times = self.requests[client_key]
        
        # Remover requests antiguos
        cutoff_time = current_time - self.window_size
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
        
        # Verificar límite principal
        if len(request_times) >= limit:
            return False, f"Límite de {limit} requests por {self.window_size} segundos excedido"
        
        # Verificar burst limit (límite adicional temporal)
        burst_key = f"{client_key}:burst"
        if self.burst_counter[burst_key] >= self.burst_limit:
            return False, f"Límite de burst de {self.burst_limit} requests excedido"
        
        return True, None
    
    def _record_request(self, client_key: str, current_time: float):
        """Registrar un request exitoso"""
        self.requests[client_key].append(current_time)
        
        # Incrementar contador de burst
        burst_key = f"{client_key}:burst"
        self.burst_counter[burst_key] += 1
        
        # Resetear contador de burst cada minuto
        # (implementación simplificada)
        if self.burst_counter[burst_key] > 100:  # Reset automático
            self.burst_counter[burst_key] = 0
    
    def _get_remaining_requests(self, client_key: str, is_admin: bool) -> int:
        """Calcular requests restantes para el cliente"""
        limit = self.admin_limit if is_admin else self.public_limit
        return max(0, limit - len(self.requests[client_key]))
    
    def _create_rate_limit_response(
        self, 
        client_key: str, 
        reason: str, 
        retry_after: Optional[int] = None
    ):
        """Crear respuesta de rate limit excedido"""
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "codigo": 429,
                    "tipo": "RATE_LIMIT_EXCEEDED",
                    "mensaje": reason,
                    "detalle": "Ha excedido el límite de solicitudes. Intente más tarde.",
                    "timestamp": time.time(),
                    "retry_after": retry_after or self.window_size,
                    "client_id": client_key[:8]  # Solo primeros 8 caracteres
                }
            },
            headers={
                "Retry-After": str(retry_after or self.window_size),
                "X-RateLimit-Limit": str(self.admin_limit if client_key.startswith("admin") else self.public_limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + (retry_after or self.window_size)))
            }
        )
    
    async def __call__(self, request: Request, call_next):
        """
        Middleware principal de rate limiting
        """
        current_time = time.time()
        
        # Limpiar datos antiguos periódicamente
        if current_time - self._last_cleanup > self._cleanup_interval:
            self._cleanup_old_data()
        
        # Verificar si debe saltarse rate limiting
        if self._should_bypass_rate_limit(request):
            return await call_next(request)
        
        # Obtener clave del cliente
        client_key = self._get_client_key(request)
        
        # Determinar si es endpoint de administración
        is_admin = self._is_admin_endpoint(request.url.path)
        
        # Verificar rate limiting
        allowed, reason = self._check_rate_limit(client_key, is_admin, current_time)
        
        if not allowed:
            logger.warning(
                f"Rate limit excedido - IP: {client_key}, Path: {request.url.path}, "
                f"Reason: {reason}"
            )
            
            # Agregar a lista de bloqueo si excede múltiples veces
            # (implementación básica - en producción usar Redis)
            retry_after = reason.split()[-2] if reason else self.window_size
            return self._create_rate_limit_response(client_key, reason, int(retry_after))
        
        # Procesar request
        try:
            response = await call_next(request)
            
            # Registrar request exitoso
            self._record_request(client_key, current_time)
            
            # Agregar headers de rate limiting
            remaining = self._get_remaining_requests(client_key, is_admin)
            limit = self.admin_limit if is_admin else self.public_limit
            
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_size))
            
            return response
            
        except Exception as e:
            # No registrar requests que fallen en el middleware
            logger.error(f"Error en middleware de rate limiting: {str(e)}")
            raise


class DistributedRateLimitMiddleware(AdvancedRateLimitMiddleware):
    """
    Middleware de rate limiting distribuido para múltiples instancias
    Utiliza Redis para compartir estado entre instancias
    """
    
    def __init__(self, redis_client=None, **kwargs):
        super().__init__(**kwargs)
        self.redis_client = redis_client
    
    async def _get_shared_requests(self, client_key: str) -> List[float]:
        """Obtener requests desde almacenamiento compartido"""
        if not self.redis_client:
            return list(self.requests[client_key])
        
        try:
            key = f"rate_limit:{client_key}"
            requests_data = await self.redis_client.get(key)
            if requests_data:
                return eval(requests_data)  # Eval para simplificar - usar JSON en producción
            return []
        except Exception as e:
            logger.error(f"Error obteniendo requests compartidos: {e}")
            return list(self.requests[client_key])
    
    async def _save_shared_requests(self, client_key: str, requests_data: List[float]):
        """Guardar requests en almacenamiento compartido"""
        if not self.redis_client:
            self.requests[client_key] = deque(requests_data)
            return
        
        try:
            key = f"rate_limit:{client_key}"
            await self.redis_client.setex(
                key, 
                self.window_size * 2, 
                str(requests_data)  # Usar JSON en producción
            )
        except Exception as e:
            logger.error(f"Error guardando requests compartidos: {e}")


# Función helper para crear middleware instance
def create_rate_limit_middleware(
    public_limit: int = 100,
    admin_limit: int = 50,
    window_size: int = 60,
    burst_limit: int = 10,
    distributed: bool = False
):
    """
    Factory function para crear middleware de rate limiting
    
    Args:
        public_limit: Límite para endpoints públicos
        admin_limit: Límite para endpoints de administración
        window_size: Ventana de tiempo en segundos
        burst_limit: Límite de burst
        distributed: Usar versión distribuida
    
    Returns:
        Middleware instance
    """
    if distributed:
        return DistributedRateLimitMiddleware(
            public_limit=public_limit,
            admin_limit=admin_limit,
            window_size=window_size,
            burst_limit=burst_limit
        )
    else:
        return AdvancedRateLimitMiddleware(
            public_limit=public_limit,
            admin_limit=admin_limit,
            window_size=window_size,
            burst_limit=burst_limit
        )
