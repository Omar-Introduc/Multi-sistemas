"""
Middleware de autenticación
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
from loguru import logger
from app.config.settings import settings
from app.services.redis_service import redis_service


class AuthMiddleware:
    """
    Middleware para autenticación de usuarios
    """
    
    def __init__(self):
        self.security = HTTPBearer()
        self.exempt_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/health",
            "/api/v1/health/",
            "/api/v1/health/detailed",
            "/api/v1/health/ready",
            "/api/v1/health/live",
            "/api/v1/reniec/consulta-dni",  # Permitir consultas públicas
        ]
    
    async def __call__(self, request: Request, call_next):
        """
        Procesar request y verificar autenticación
        """
        # Verificar si la ruta está exenta
        if request.url.path in self.exempt_paths or request.url.path.startswith("/static/"):
            return await call_next(request)
        
        # Verificar si es una consulta pública de DNI
        if "/reniec/consulta-dni/" in request.url.path:
            return await call_next(request)
        
        try:
            # Verificar autorización
            credentials = await self._get_credentials(request)
            
            if not credentials:
                # Permitir acceso si no hay credenciales para endpoints públicos
                if self._is_public_endpoint(request.url.path):
                    return await call_next(request)
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de acceso requerido",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verificar token
            user_data = await self._verify_token(credentials)
            
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido o expirado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Agregar información del usuario al request
            request.state.user = user_data
            
            return await call_next(request)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error en middleware de autenticación: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno de autenticación"
            )
    
    async def _get_credentials(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        """
        Obtener credenciales del request
        """
        try:
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return None
            
            token = authorization.split(" ")[1]
            
            class Credentials:
                def __init__(self, token):
                    self.credentials = token
            
            return Credentials(token)
            
        except Exception:
            return None
    
    async def _verify_token(self, credentials) -> Optional[dict]:
        """
        Verificar token JWT
        """
        try:
            token = credentials.credentials
            
            # Decodificar token
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            # Verificar en Redis si el token sigue siendo válido
            if redis_service.connected:
                session_data = await redis_service.get_user_session(user_id)
                if not session_data:
                    return None
                
                stored_token = session_data.get("token")
                if stored_token != token:
                    return None
            
            return {
                "user_id": user_id,
                "username": payload.get("username"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", [])
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token JWT expirado")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Error verificando JWT: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verificando token: {e}")
            return None
    
    def _is_public_endpoint(self, path: str) -> bool:
        """
        Verificar si es un endpoint público
        """
        public_patterns = [
            "/api/v1/reniec/verificar-dni",
            "/api/v1/reniec/documento/",  # Para verificación pública
        ]
        
        return any(path.startswith(pattern) for pattern in public_patterns)


class RequirePermission:
    """
    Decorador para requerir permisos específicos
    """
    
    def __init__(self, permission: str):
        self.permission = permission
    
    def __call__(self, func):
        async def wrapper(request: Request, *args, **kwargs):
            user = getattr(request.state, 'user', None)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            permissions = user.get('permissions', [])
            roles = user.get('roles', [])
            
            # Verificar permisos directos
            if self.permission in permissions:
                return await func(request, *args, **kwargs)
            
            # Verificar permisos por rol
            role_permissions = self._get_role_permissions(roles)
            if self.permission in role_permissions:
                return await func(request, *args, **kwargs)
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso requerido: {self.permission}"
            )
        
        return wrapper
    
    def _get_role_permissions(self, roles: list) -> list:
        """
        Obtener permisos basados en roles
        """
        role_permission_map = {
            "admin": ["*"],  # Admin tiene todos los permisos
            "operator": [
                "read:citizens",
                "create:citizens",
                "update:citizens",
                "read:documents",
                "create:documents",
                "update:documents",
                "read:solicitudes",
                "create:solicitudes",
                "update:solicitudes",
            ],
            "viewer": [
                "read:citizens",
                "read:documents",
                "read:solicitudes",
            ]
        }
        
        all_permissions = []
        for role in roles:
            all_permissions.extend(role_permission_map.get(role, []))
        
        return list(set(all_permissions))  # Eliminar duplicados


# Instancia global del middleware
auth_middleware = AuthMiddleware()