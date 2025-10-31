"""
Funciones auxiliares y utilidades para el sistema LP2 RENIEC Service
Incluye validaciones, formateo, conversiones, helpers y más
"""

import re
import json
import hashlib
import secrets
import string
import asyncio
from typing import (
    Any, Dict, List, Optional, Union, Callable, TypeVar, Generic,
    Type, Optional, Callable, Awaitable
)
from datetime import datetime, date, timedelta
from functools import wraps, lru_cache
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urlparse, parse_qs
import uuid
import base64
import csv
import io
from pathlib import Path
import tempfile
import aiofiles
from loguru import logger

# === VALIDACIONES ===
class Validators:
    """Validadores reutilizables"""
    
    @staticmethod
    def is_valid_dni(dni: str) -> bool:
        """Validar DNI peruano"""
        if not dni or len(dni) != 8 or not dni.isdigit():
            return False
        
        # Algoritmo de validación del DNI peruano
        coeficientes = [3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(dni[i]) * coeficientes[i] for i in range(8))
        resto = suma % 11
        digito_verificador = 11 - resto if resto < 2 else 11 - resto - 1
        
        return int(dni[7]) == digito_verificador
    
    @staticmethod
    def is_valid_ruc(ruc: str) -> bool:
        """Validar RUC peruano"""
        if not ruc or len(ruc) != 11 or not ruc.isdigit():
            return False
        
        # Validación básica del RUC peruano
        suma = (
            int(ruc[0]) * 5 +
            int(ruc[1]) * 4 +
            int(ruc[2]) * 3 +
            int(ruc[3]) * 2 +
            int(ruc[4]) * 7 +
            int(ruc[5]) * 6 +
            int(ruc[6]) * 5 +
            int(ruc[7]) * 4 +
            int(ruc[8]) * 3 +
            int(ruc[9]) * 2
        )
        
        resto = suma % 11
        if resto == 0:
            return int(ruc[10]) == 6
        elif resto == 1:
            return int(ruc[10]) == 1
        else:
            return int(ruc[10]) == 11 - resto
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validar número de teléfono peruano"""
        # Acepta formatos: +51 999 888 777, 999888777, 999-888-777
        phone = re.sub(r'[^\d]', '', phone)
        return len(phone) == 9 and phone.startswith(('9', '8', '7', '6'))
    
    @staticmethod
    def is_valid_postal_code(postal_code: str) -> bool:
        """Validar código postal peruano"""
        return bool(re.match(r'^\d{5}$', postal_code))
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitizar entrada de texto"""
        if not text:
            return ""
        
        # Eliminar caracteres peligrosos
        text = re.sub(r'[<>"\']', '', text)
        text = text.strip()
        return text
    
    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
        """Enmascarar datos sensibles"""
        if not data or len(data) <= visible_chars:
            return "*" * len(data)
        
        return data[:visible_chars] + "*" * (len(data) - visible_chars)


# === FORMATEADORES ===
class Formatters:
    """Formateadores para diferentes tipos de datos"""
    
    @staticmethod
    def format_dni(dni: str) -> str:
        """Formatear DNI con separadores"""
        if not dni or len(dni) != 8:
            return dni
        return f"{dni[:1]}.{dni[1:4]}.{dni[4:7]}-{dni[7]}"
    
    @staticmethod
    def format_ruc(ruc: str) -> str:
        """Formatear RUC con separadores"""
        if not ruc or len(ruc) != 11:
            return ruc
        return f"{ruc[:2]}.{ruc[2:9]}.{ruc[9:10]}-{ruc[10]}"
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Formatear número de teléfono"""
        if not phone:
            return phone
        
        # Limpiar y formatear
        phone = re.sub(r'[^\d]', '', phone)
        if len(phone) == 9:
            return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
        return phone
    
    @staticmethod
    def format_currency(amount: Union[int, float, Decimal], currency: str = "PEN") -> str:
        """Formatear cantidad monetaria"""
        if isinstance(amount, str):
            try:
                amount = float(amount)
            except ValueError:
                return amount
        
        formatted = f"{amount:,.2f}"
        if currency == "PEN":
            return f"S/ {formatted}"
        return f"{currency} {formatted}"
    
    @staticmethod
    def format_date(date_obj: Union[datetime, date], format_str: str = "%d/%m/%Y") -> str:
        """Formatear fecha"""
        if isinstance(date_obj, datetime):
            return date_obj.strftime(format_str)
        elif isinstance(date_obj, date):
            return date_obj.strftime(format_str)
        return str(date_obj)
    
    @staticmethod
    def format_datetime(datetime_obj: datetime, format_str: str = "%d/%m/%Y %H:%M:%S") -> str:
        """Formatear fecha y hora"""
        return datetime_obj.strftime(format_str)
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncar texto con sufijo"""
        if not text or len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix


# === GENERADORES ===
class Generators:
    """Generadores de datos aleatorios"""
    
    @staticmethod
    def generate_id(length: int = 8) -> str:
        """Generar ID único"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    
    @staticmethod
    def generate_uuid() -> str:
        """Generar UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generar token seguro"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_api_key(prefix: str = "rk") -> str:
        """Generar API key con prefijo"""
        token = secrets.token_urlsafe(32)
        return f"{prefix}_{token}"
    
    @staticmethod
    def generate_password(length: int = 12) -> str:
        """Generar contraseña segura"""
        # Asegurar al menos un carácter de cada tipo
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits),
            secrets.choice("!@#$%^&*")
        ]
        # Completar el resto
        password.extend(secrets.choice(chars) for _ in range(length - 4))
        # Mezclar
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    @staticmethod
    def generate_hash(data: str, algorithm: str = "sha256") -> str:
        """Generar hash de datos"""
        if algorithm == "sha256":
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(data.encode()).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(data.encode()).hexdigest()
        else:
            raise ValueError(f"Algoritmo no soportado: {algorithm}")


# === CONVERSORES ===
class Converters:
    """Conversores de tipos de datos"""
    
    @staticmethod
    def to_int(value: Any, default: int = 0) -> int:
        """Convertir a entero de forma segura"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def to_float(value: Any, default: float = 0.0) -> float:
        """Convertir a flotante de forma segura"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def to_decimal(value: Any, default: Decimal = Decimal('0')) -> Decimal:
        """Convertir a Decimal de forma segura"""
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def to_bool(value: Any, default: bool = False) -> bool:
        """Convertir a booleano de forma segura"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'si', 'sí')
        if isinstance(value, (int, float)):
            return value != 0
        return default
    
    @staticmethod
    def to_datetime(value: Any, format_str: str = None) -> Optional[datetime]:
        """Convertir a datetime de forma segura"""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                if format_str:
                    return datetime.strptime(value, format_str)
                else:
                    # Intentar formatos comunes
                    formats = [
                        "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%d",
                        "%d/%m/%Y %H:%M:%S",
                        "%d/%m/%Y",
                        "%Y-%m-%dT%H:%M:%S",
                        "%Y-%m-%dT%H:%M:%S.%f"
                    ]
                    for fmt in formats:
                        try:
                            return datetime.strptime(value, fmt)
                        except ValueError:
                            continue
            except ValueError:
                pass
        return None
    
    @staticmethod
    def to_dict(obj: Any) -> Dict[str, Any]:
        """Convertir objeto a diccionario de forma segura"""
        if isinstance(obj, dict):
            return obj
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        try:
            return json.loads(str(obj))
        except (ValueError, TypeError):
            return {}


# === CACHE Y RENDIMIENTO ===
class Cache:
    """Sistema de caché simple en memoria"""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._max_size = 1000
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Guardar en caché con TTL"""
        if len(self._cache) >= self._max_size:
            # Limpiar entradas más antiguas
            oldest_key = min(self._timestamps, key=lambda k: self._timestamps[k])
            del self._cache[oldest_key]
            del self._timestamps[oldest_key]
        
        self._cache[key] = value
        self._timestamps[key] = datetime.utcnow() + timedelta(seconds=ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """Obtener del caché"""
        if key in self._cache:
            if datetime.utcnow() < self._timestamps[key]:
                return self._cache[key]
            else:
                # Expirado
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def delete(self, key: str):
        """Eliminar del caché"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self):
        """Limpiar todo el caché"""
        self._cache.clear()
        self._timestamps.clear()
    
    def cleanup(self):
        """Limpiar entradas expiradas"""
        now = datetime.utcnow()
        expired_keys = [key for key, timestamp in self._timestamps.items() if now >= timestamp]
        for key in expired_keys:
            del self._cache[key]
            del self._timestamps[key]


# === UTILIDADES DE ARCHIVO ===
class FileUtils:
    """Utilidades para manejo de archivos"""
    
    @staticmethod
    async def read_file(file_path: Union[str, Path]) -> str:
        """Leer archivo de forma asíncrona"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            return await file.read()
    
    @staticmethod
    async def write_file(file_path: Union[str, Path], content: str):
        """Escribir archivo de forma asíncrona"""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
            await file.write(content)
    
    @staticmethod
    def get_file_extension(file_path: Union[str, Path]) -> str:
        """Obtener extensión de archivo"""
        return Path(file_path).suffix.lower()
    
    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """Obtener tamaño de archivo en bytes"""
        return Path(file_path).stat().st_size
    
    @staticmethod
    def ensure_directory(dir_path: Union[str, Path]):
        """Asegurar que el directorio existe"""
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def parse_csv(content: str) -> List[Dict[str, str]]:
        """Parsear contenido CSV"""
        csv_reader = csv.DictReader(io.StringIO(content))
        return list(csv_reader)
    
    @staticmethod
    def to_csv(data: List[Dict[str, Any]], filename: str = None) -> str:
        """Convertir datos a formato CSV"""
        if not data:
            return ""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        csv_content = output.getvalue()
        output.close()
        
        if filename:
            FileUtils.ensure_directory("temp")
            temp_path = Path("temp") / filename
            Path(temp_path).write_text(csv_content, encoding='utf-8')
        
        return csv_content


# === UTILIDADES DE TIEMPO ===
class TimeUtils:
    """Utilidades para manejo de tiempo"""
    
    @staticmethod
    def now() -> datetime:
        """Obtener tiempo actual"""
        return datetime.utcnow()
    
    @staticmethod
    def today() -> date:
        """Obtener fecha actual"""
        return datetime.utcnow().date()
    
    @staticmethod
    def parse_timezone(dt_str: str, timezone: str = "UTC") -> datetime:
        """Parsear string de fecha con timezone"""
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            # Fallback
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """Verificar si es fin de semana"""
        return dt.weekday() >= 5
    
    @staticmethod
    def add_business_days(start_date: date, business_days: int) -> date:
        """Agregar días hábiles"""
        current_date = start_date
        added_days = 0
        
        while added_days < business_days:
            current_date += timedelta(days=1)
            if not TimeUtils.is_weekend(current_date):
                added_days += 1
        
        return current_date


# === DECORADORES ÚTILES ===
def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """Decorador para reintentar operaciones"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (2 ** attempt))  # Backoff exponencial
                    else:
                        raise last_exception
        return wrapper
    return decorator


def cache_result(ttl: int = 300):
    """Decorador para cachear resultados"""
    def decorator(func):
        cache_instance = Cache()
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Crear clave de caché basada en función y argumentos
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Verificar caché
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función
            result = await func(*args, **kwargs)
            
            # Guardar en caché
            cache_instance.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def measure_time(func):
    """Decorador para medir tiempo de ejecución"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        try:
            result = await func(*args, **kwargs)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"⏱️  {func.__name__} ejecutado en {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"❌ {func.__name__} falló después de {execution_time:.4f}s: {e}")
            raise
    return wrapper


# === INSTANCIAS GLOBALES ===
validators = Validators()
formatters = Formatters()
generators = Generators()
converters = Converters()
cache_instance = Cache()


# === EXPORTACIONES ===
__all__ = [
    # Validadores
    "Validators",
    "validators",
    
    # Formateadores
    "Formatters",
    "formatters",
    
    # Generadores
    "Generators", 
    "generators",
    
    # Conversores
    "Converters",
    "converters",
    
    # Cache
    "Cache",
    "cache_instance",
    
    # Utilidades de archivo
    "FileUtils",
    
    # Utilidades de tiempo
    "TimeUtils",
    
    # Decoradores
    "retry",
    "cache_result",
    "measure_time"
]