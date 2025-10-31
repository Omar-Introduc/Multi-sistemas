"""
Servicio para integración con Redis
"""

import redis.asyncio as redis
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
from app.config.settings import settings, REDIS_CONFIG


class RedisService:
    """
    Servicio para manejo de Redis
    """
    
    def __init__(self):
        self.redis_client = None
        self.connected = False
    
    async def initialize_redis(self):
        """
        Inicializar conexión con Redis
        """
        try:
            logger.info("Inicializando conexión con Redis...")
            
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=True,
                **REDIS_CONFIG
            )
            
            # Probar conexión
            await self.redis_client.ping()
            self.connected = True
            
            logger.info("✅ Conexión con Redis establecida correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Redis: {e}")
            self.connected = False
            raise
    
    async def close_redis(self):
        """
        Cerrar conexión con Redis
        """
        try:
            if self.redis_client:
                await self.redis_client.close()
                logger.info("✅ Conexión Redis cerrada correctamente")
        except Exception as e:
            logger.error(f"❌ Error cerrando Redis: {e}")
        finally:
            self.connected = False
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Obtener valor por clave
        """
        if not self.connected:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error obteniendo clave {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Establecer clave-valor
        """
        if not self.connected:
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            if expire:
                return await self.redis_client.setex(key, expire, serialized_value)
            else:
                return await self.redis_client.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Error estableciendo clave {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Eliminar clave
        """
        if not self.connected:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error eliminando clave {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Verificar si existe clave
        """
        if not self.connected:
            return False
        
        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error verificando existencia de clave {key}: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Establecer expiración para clave
        """
        if not self.connected:
            return False
        
        try:
            result = await self.redis_client.expire(key, seconds)
            return result
        except Exception as e:
            logger.error(f"Error estableciendo expiración para clave {key}: {e}")
            return False
    
    # === MÉTODOS ESPECÍFICOS PARA RENIEC ===
    
    async def cache_reniec_query(self, dni: str, data: Dict[str, Any], ttl: int = 3600):
        """
        Cachear resultado de consulta RENIEC
        """
        key = f"reniec:dni:{dni}"
        return await self.set(key, data, expire=ttl)
    
    async def get_reniec_cache(self, dni: str) -> Optional[Dict[str, Any]]:
        """
        Obtener datos cacheados de RENIEC
        """
        key = f"reniec:dni:{dni}"
        return await self.get(key)
    
    async def cache_user_session(self, user_id: str, session_data: Dict[str, Any], ttl: int = 1800):
        """
        Cachear sesión de usuario
        """
        key = f"session:user:{user_id}"
        return await self.set(key, session_data, expire=ttl)
    
    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener sesión de usuario cacheada
        """
        key = f"session:user:{user_id}"
        return await self.get(key)
    
    async def delete_user_session(self, user_id: str) -> bool:
        """
        Eliminar sesión de usuario
        """
        key = f"session:user:{user_id}"
        return await self.delete(key)
    
    async def increment_api_counter(self, endpoint: str, window: int = 3600) -> int:
        """
        Incrementar contador de API calls
        """
        key = f"counter:api:{endpoint}:{int(datetime.now().timestamp() / window)}"
        
        try:
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window * 2)  # Expirar en 2 ventanas
            results = await pipe.execute()
            return results[0]
        except Exception as e:
            logger.error(f"Error incrementando contador API {endpoint}: {e}")
            return 0
    
    async def get_api_counter(self, endpoint: str, window: int = 3600) -> int:
        """
        Obtener contador de API calls
        """
        key = f"counter:api:{endpoint}:{int(datetime.now().timestamp() / window)}"
        return await self.redis_client.get(key) or 0
    
    async def set_rate_limit(self, identifier: str, limit: int, window: int = 60) -> bool:
        """
        Establecer límite de tasa
        """
        key = f"ratelimit:{identifier}"
        count = await self.redis_client.incr(key)
        
        if count == 1:
            await self.redis_client.expire(key, window)
        
        return count <= limit
    
    async def cache_search_results(self, query_hash: str, results: List[Dict], ttl: int = 1800):
        """
        Cachear resultados de búsqueda
        """
        key = f"search:{query_hash}"
        return await self.set(key, results, expire=ttl)
    
    async def get_search_results(self, query_hash: str) -> Optional[List[Dict]]:
        """
        Obtener resultados de búsqueda cacheados
        """
        key = f"search:{query_hash}"
        return await self.get(key)
    
    async def cache_document_data(self, document_number: str, data: Dict[str, Any], ttl: int = 7200):
        """
        Cachear datos de documento
        """
        key = f"document:{document_number}"
        return await self.set(key, data, expire=ttl)
    
    async def get_document_cache(self, document_number: str) -> Optional[Dict[str, Any]]:
        """
        Obtener datos de documento cacheados
        """
        key = f"document:{document_number}"
        return await self.get(key)
    
    async def invalidate_user_cache(self, user_id: str):
        """
        Invalidar cache relacionado a un usuario
        """
        try:
            patterns = [
                f"session:user:{user_id}",
                f"search:*user:{user_id}*",
                f"document:*user:{user_id}*"
            ]
            
            for pattern in patterns:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    
        except Exception as e:
            logger.error(f"Error invalidando cache del usuario {user_id}: {e}")
    
    async def get_redis_info(self) -> Dict[str, Any]:
        """
        Obtener información de Redis
        """
        if not self.connected:
            return {"error": "Redis no conectado"}
        
        try:
            info = await self.redis_client.info()
            return {
                "connected": self.connected,
                "server": {
                    "redis_version": info.get("redis_version"),
                    "uptime_in_seconds": info.get("uptime_in_seconds"),
                    "used_memory_human": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients")
                },
                "keyspace": info.get("keyspace"),
                "stats": {
                    "total_commands_processed": info.get("total_commands_processed"),
                    "total_connections_received": info.get("total_connections_received"),
                    "keyspace_hits": info.get("keyspace_hits"),
                    "keyspace_misses": info.get("keyspace_misses")
                }
            }
        except Exception as e:
            logger.error(f"Error obteniendo info de Redis: {e}")
            return {"error": str(e)}


# Instancia global del servicio
redis_service = RedisService()


async def initialize_redis():
    """Función para inicializar Redis"""
    await redis_service.initialize_redis()


async def close_redis():
    """Función para cerrar Redis"""
    await redis_service.close_redis()


async def test_redis_connection() -> bool:
    """Probar conexión a Redis"""
    try:
        if redis_service.connected:
            return True
        
        test_redis = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password if settings.redis_password else None,
            decode_responses=True
        )
        
        await test_redis.ping()
        await test_redis.close()
        return True
        
    except Exception as e:
        logger.error(f"Error probando conexión Redis: {e}")
        return False