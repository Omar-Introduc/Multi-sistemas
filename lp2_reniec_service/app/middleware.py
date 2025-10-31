"""
Middleware avanzado para FastAPI
Incluye CORS, request logging, rate limiting, security headers y más
"""

import time
import json
import uuid
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
import redis.asyncio as redis
from loguru import logger
import re
from datetime import datetime, timedelta

from app.config import settings, security_config, logging_config
from app.middleware.logging import LoggingMiddleware


# === MIDDLEWARE DE RATE LIMITING ===
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware avanzado de rate limiting con Redis"""
    
    def __init__(self, app, calls: int = None, window: int = None):
        super().__init__(app)
        self.calls = calls or security_config.rate_limit_calls
        self.window = window or security_config.rate_limit_window
        self.redis_client = None
        self.enabled = settings.rate_limit_enabled
        
        if self.enabled:
            try:
                # Inicializar Redis para rate limiting
                redis_url = settings.rate_limit_storage_url
                self.redis_client = redis.from_url(
                    redis_url, 
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                logger.info("✅ Rate limiting con Redis habilitado")
            except Exception as e:
                logger.warning(f"⚠️  No se pudo inicializar Redis para rate limiting: {e}")
                self.enabled = False
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Procesar request con rate limiting"""
        if not self.enabled:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        endpoint = self._get_endpoint_key(request)
        key = f"rate_limit:{client_ip}:{endpoint}"
        
        try:
            if self.redis_client:
                # Rate limiting con Redis
                current_requests = await self.redis_client.get(key)
                if current_requests is None:
                    # Primera request en la ventana
                    await self.redis_client.setex(
                        key, 
                        self.window, 
                        1
                    )
                else:
                    current_requests = int(current_requests)
                    if current_requests >= self.calls:
                        # Rate limit excedido
                        logger.warning(f"🚨 Rate limit excedido para {client_ip} en {endpoint}")
                        return JSONResponse(
                            status_code=429,
                            content={
                                "error": "Rate limit exceeded",
                                "message": f"Demasiadas requests. Máximo {self.calls} requests por {self.window} segundos.",
                                "retry_after": self.window
                            },
                            headers={
                                "X-RateLimit-Limit": str(self.calls),
                                "X-RateLimit-Remaining": "0",
                                "X-RateLimit-Reset": str(int(time.time()) + self.window),
                                "Retry-After": str(self.window)
                            }
                        )
                    else:
                        # Incrementar contador
                        await self.redis_client.incr(key)
                        
                        # Actualizar TTL
                        await self.redis_client.expire(key, self.window)
                        
                        remaining = self.calls - (current_requests + 1)
            else:
                # Rate limiting en memoria (fallback)
                if not hasattr(self, '_memory_storage'):
                    self._memory_storage = {}
                
                current_time = time.time()
                window_start = int(current_time // self.window) * self.window
                
                if key not in self._memory_storage:
                    self._memory_storage[key] = {
                        'count': 0,
                        'window_start': window_start
                    }
                
                if self._memory_storage[key]['window_start'] != window_start:
                    # Nueva ventana
                    self._memory_storage[key] = {
                        'count': 1,
                        'window_start': window_start
                    }
                else:
                    self._memory_storage[key]['count'] += 1
                    if self._memory_storage[key]['count'] > self.calls:
                        return JSONResponse(
                            status_code=429,
                            content={
                                "error": "Rate limit exceeded",
                                "message": f"Demasiadas requests en memoria",
                                "retry_after": self.window
                            }
                        )
                
                remaining = self.calls - self._memory_storage[key]['count']
            
            # Procesar request
            response = await call_next(request)
            
            # Agregar headers de rate limiting
            response.headers["X-RateLimit-Limit"] = str(self.calls)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error en rate limiting: {e}")
            return await call_next(request)  # Fallback sin rate limiting
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtener IP real del cliente"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def _get_endpoint_key(self, request: Request) -> str:
        """Crear clave para el endpoint"""
        path = request.url.path
        method = request.method
        
        # Agrupar endpoints similares
        if "/api/v1/" in path:
            return f"{method}:{path.split('/api/v1/')[1]}"
        else:
            return f"{method}:{path}"


# === MIDDLEWARE DE SECURITY HEADERS ===
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar headers de seguridad"""
    
    def __init__(self, app):
        super().__init__(app)
        self.enabled = settings.enable_security_headers
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Agregar headers de seguridad"""
        response = await call_next(request)
        
        if not self.enabled:
            return response
        
        # Headers de seguridad estándar
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }
        
        # Content Security Policy básico
        security_headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' wss: https:; "
            "frame-ancestors 'none';"
        )
        
        # Strict Transport Security (solo HTTPS)
        if request.url.scheme == "https":
            security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Aplicar headers a la respuesta
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


# === MIDDLEWARE DE REQUEST ID ===
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar ID único a cada request"""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Agregar ID único al request"""
        # Obtener o generar ID de request
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Agregar al estado del request para uso posterior
        request.state.request_id = request_id
        
        # Procesar request
        response = await call_next(request)
        
        # Agregar ID a la respuesta
        response.headers["X-Request-ID"] = request_id
        
        return response


# === MIDDLEWARE DE TRACKING DE PERFORMANCE ===
class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware para tracking de performance"""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Trackear performance del request"""
        start_time = time.time()
        
        # Agregar timestamp inicial
        request.state.start_time = start_time
        
        try:
            response = await call_next(request)
            
            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time
            
            # Agregar headers de timing
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            response.headers["X-Process-Time-Ms"] = f"{process_time * 1000:.2f}"
            
            # Loggear requests lentos
            if process_time > 1.0:  # Más de 1 segundo
                logger.warning(
                    f"🐌 Request lento detectado: {request.method} {request.url.path} "
                    f"tomó {process_time:.4f}s - IP: {self._get_client_ip(request)}"
                )
            
            return response
            
        except Exception as e:
            # Loggear errores con timing
            process_time = time.time() - start_time
            logger.error(
                f"❌ Error en request: {request.method} {request.url.path} "
                f"después de {process_time:.4f}s - Error: {str(e)}"
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtener IP del cliente"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"


# === MIDDLEWARE CORS AVANZADO ===
class AdvancedCORSMiddleware:
    """Middleware CORS avanzado con configuración flexible"""
    
    def __init__(self, app):
        self.app = app
        
    def add_cors_middleware(self):
        """Agregar middleware CORS a la aplicación"""
        from fastapi import FastAPI
        if isinstance(self.app, FastAPI):
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=security_config.cors_origins,
                allow_credentials=True,
                allow_methods=security_config.cors_methods,
                allow_headers=security_config.cors_headers,
                expose_headers=[
                    "X-Request-ID",
                    "X-Process-Time",
                    "X-RateLimit-Limit",
                    "X-RateLimit-Remaining",
                    "X-RateLimit-Reset"
                ],
                max_age=86400,  # 24 horas
            )


# === MIDDLEWARE DE IP BLOCKING ===
class IPBlockingMiddleware(BaseHTTPMiddleware):
    """Middleware para bloquear IPs maliciosas"""
    
    def __init__(self, app):
        super().__init__(app)
        self.blocked_ips = set()
        self.suspicious_patterns = [
            r'\.\./',  # Path traversal
            r'union.*select',  # SQL injection
            r'<script',  # XSS
            r'javascript:',  # JavaScript injection
            r'eval\(',  # Code injection
        ]
        self.block_duration = 3600  # 1 hora
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Verificar y bloquear IPs sospechosas"""
        client_ip = self._get_client_ip(request)
        
        # Verificar si la IP está bloqueada
        if client_ip in self.blocked_ips:
            logger.warning(f"🚨 Request bloqueado de IP sospechosa: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={"error": "Access denied"}
            )
        
        # Verificar patrones sospechosos en URL y headers
        if self._is_suspicious_request(request):
            logger.warning(f"🚨 IP sospechosa detectada: {client_ip}")
            self.blocked_ips.add(client_ip)
            return JSONResponse(
                status_code=403,
                content={"error": "Suspicious activity detected"}
            )
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtener IP del cliente"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def _is_suspicious_request(self, request: Request) -> bool:
        """Detectar requests sospechosos"""
        # Verificar URL
        url = str(request.url)
        for pattern in self.suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # Verificar headers
        headers_str = str(request.headers).lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, headers_str, re.IGNORECASE):
                return True
        
        return False


# === CONFIGURADOR DE MIDDLEWARE ===
class MiddlewareConfig:
    """Configurador centralizado de todos los middleware"""
    
    def __init__(self, app):
        self.app = app
        self._middleware_added = False
    
    def add_all_middleware(self):
        """Agregar todos los middleware configurados"""
        if self._middleware_added:
            return
        
        from fastapi import FastAPI
        if not isinstance(self.app, FastAPI):
            return
        
        # CORS
        if settings.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=security_config.cors_origins,
                allow_credentials=True,
                allow_methods=security_config.cors_methods,
                allow_headers=security_config.cors_headers,
                expose_headers=[
                    "X-Request-ID",
                    "X-Process-Time",
                    "X-RateLimit-Limit",
                    "X-RateLimit-Remaining",
                    "X-RateLimit-Reset"
                ],
                max_age=86400,
            )
        
        # Trusted Host (si está configurado)
        if security_config.allowed_hosts:
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=security_config.allowed_hosts
            )
        
        # Request ID
        self.app.add_middleware(RequestIDMiddleware)
        
        # Rate Limiting
        if settings.enable_rate_limiting:
            self.app.add_middleware(
                RateLimitMiddleware,
                calls=security_config.rate_limit_calls,
                window=security_config.rate_limit_window
            )
        
        # Security Headers
        if settings.enable_security_headers:
            self.app.add_middleware(SecurityHeadersMiddleware)
        
        # Performance Tracking
        self.app.add_middleware(PerformanceMiddleware)
        
        # IP Blocking
        self.app.add_middleware(IPBlockingMiddleware)
        
        # Logging (si está habilitado)
        if settings.enable_request_logging:
            # El middleware de logging se agrega directamente en main.py
            pass
        
        self._middleware_added = True
        logger.info("✅ Todos los middleware configurados correctamente")


# === FUNCIONES DE UTILIDAD ===
def create_middleware_stack(app):
    """Crear stack completo de middleware"""
    middleware_config = MiddlewareConfig(app)
    middleware_config.add_all_middleware()
    return middleware_config


# === EXPORTACIONES ===
__all__ = [
    "RateLimitMiddleware",
    "SecurityHeadersMiddleware", 
    "RequestIDMiddleware",
    "PerformanceMiddleware",
    "AdvancedCORSMiddleware",
    "IPBlockingMiddleware",
    "MiddlewareConfig",
    "create_middleware_stack",
    "LoggingMiddleware"
]