"""
Middleware de logging
"""

import time
from typing import Callable
from fastapi import Request
from fastapi.responses import Response
from loguru import logger
import json


class LoggingMiddleware:
    """
    Middleware para logging de requests y responses
    """
    
    def __init__(self):
        self.sensitive_paths = [
            "/login",
            "/auth",
            "/api/v1/health",  # No loggear health checks frecuentes
        ]
        
        self.sensitive_fields = [
            "password",
            "token",
            "authorization",
            "secret",
            "api_key",
            "credential"
        ]
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Procesar request y response con logging
        """
        # Saltar logging para health checks
        if "/health" in request.url.path and request.method == "GET":
            return await call_next(request)
        
        start_time = time.time()
        
        # Extraer información del request
        request_info = await self._extract_request_info(request)
        
        # Loggear request entrante
        logger.info(f"Incoming Request: {request_info}")
        
        try:
            # Procesar request
            response = await call_next(request)
            
            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Extraer información del response
            response_info = await self._extract_response_info(response, process_time)
            
            # Loggear response saliente
            logger.info(f"Response: {response_info}")
            
            return response
            
        except Exception as e:
            # Loggear errores
            process_time = time.time() - start_time
            error_info = {
                "error": str(e),
                "error_type": type(e).__name__,
                "process_time": f"{process_time:.4f}s",
                "request": request_info
            }
            
            logger.error(f"Request Error: {json.dumps(error_info, default=str)}")
            raise
    
    async def _extract_request_info(self, request: Request) -> dict:
        """
        Extraer información relevante del request
        """
        # Filtrar headers sensibles
        headers = dict(request.headers)
        for sensitive_field in self.sensitive_fields:
            if sensitive_field.lower() in headers:
                headers[sensitive_field.lower()] = "***REDACTED***"
        
        # Obtener parámetros de query
        query_params = dict(request.query_params)
        
        # Filtrar parámetros sensibles
        for param in list(query_params.keys()):
            if any(sensitive in param.lower() for sensitive in self.sensitive_fields):
                query_params[param] = "***REDACTED***"
        
        # Determinar si es un endpoint sensible
        is_sensitive = any(path in request.url.path for path in self.sensitive_paths)
        
        info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "Unknown"),
            "headers": headers,
            "query_params": query_params,
            "sensitive": is_sensitive
        }
        
        # Para requests POST/PUT, intentar obtener body (sin datos sensibles)
        if request.method in ["POST", "PUT", "PATCH"] and not is_sensitive:
            try:
                body = await request.body()
                if body:
                    # Intentar parsear como JSON
                    try:
                        body_data = json.loads(body)
                        # Filtrar campos sensibles del body
                        body_data = self._filter_sensitive_fields(body_data)
                        info["body"] = f"{str(body_data)[:200]}..." if len(str(body_data)) > 200 else str(body_data)
                    except json.JSONDecodeError:
                        info["body"] = f"<binary data: {len(body)} bytes>"
            except Exception:
                pass  # No es crítico si no podemos obtener el body
        
        return info
    
    async def _extract_response_info(self, response: Response, process_time: float) -> dict:
        """
        Extraer información del response
        """
        info = {
            "status_code": response.status_code,
            "process_time": f"{process_time:.4f}s",
            "headers": dict(response.headers)
        }
        
        # Determinar nivel de log basado en status code
        if response.status_code >= 500:
            info["level"] = "ERROR"
        elif response.status_code >= 400:
            info["level"] = "WARNING"
        else:
            info["level"] = "INFO"
        
        return info
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Obtener IP real del cliente considerando proxies
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
        
        return "Unknown"
    
    def _filter_sensitive_fields(self, data: dict) -> dict:
        """
        Filtrar campos sensibles del diccionario
        """
        if isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                    filtered[key] = "***REDACTED***"
                elif isinstance(value, dict):
                    filtered[key] = self._filter_sensitive_fields(value)
                elif isinstance(value, list):
                    filtered[key] = [
                        self._filter_sensitive_fields(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    filtered[key] = value
            return filtered
        elif isinstance(data, list):
            return [
                self._filter_sensitive_fields(item) if isinstance(item, dict) else item
                for item in data
            ]
        else:
            return data


# Instancia global del middleware
logging_middleware = LoggingMiddleware()