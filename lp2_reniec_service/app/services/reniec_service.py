"""
Servicio para integración con RENIEC
"""

import httpx
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, date
from loguru import logger

from app.config.settings import settings


class ReniecService:
    """
    Servicio para integración con RENIEC
    """
    
    def __init__(self):
        self.base_url = settings.reniec_api_url
        self.api_key = settings.reniec_api_key
        self.timeout = settings.reniec_timeout
    
    async def consultar_dni(self, dni: str) -> Optional[Dict[str, Any]]:
        """
        Consultar información de una persona por DNI en RENIEC
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/consulta-dni/{dni}",
                    headers=headers
                )
            
            if response.status_code == 200:
                data = response.json()
                return self._procesar_respuesta_reniec(data)
            else:
                logger.warning(f"RENIEC API respondió con código {response.status_code} para DNI {dni}")
                return None
                
        except httpx.TimeoutException:
            logger.error(f"Timeout consultando DNI {dni} en RENIEC")
            return None
        except httpx.ConnectError:
            logger.error(f"Error de conexión con RENIEC para DNI {dni}")
            return None
        except Exception as e:
            logger.error(f"Error consultando DNI {dni}: {e}")
            return None
    
    async def verificar_dni(self, dni: str) -> Dict[str, Any]:
        """
        Verificar autenticidad de un DNI
        """
        try:
            datos = await self.consultar_dni(dni)
            
            if datos:
                return {
                    "valido": True,
                    "datos": datos
                }
            else:
                return {
                    "valido": False,
                    "datos": None
                }
                
        except Exception as e:
            logger.error(f"Error verificando DNI {dni}: {e}")
            return {
                "valido": False,
                "datos": None,
                "error": str(e)
            }
    
    async def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del servicio RENIEC
        """
        try:
            # Simular estadísticas (en un caso real, esto vendría de RENIEC)
            return {
                "api_operativa": True,
                "ultima_consulta": datetime.now().isoformat(),
                "total_consultas_ultimas_24h": 0,  # Se implementaría con Redis
                "tiempo_respuesta_promedio": "1.2s",
                "version_api": "v2.0"
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de RENIEC: {e}")
            return {
                "api_operativa": False,
                "error": str(e)
            }
    
    def _procesar_respuesta_reniec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesar y normalizar la respuesta de RENIEC
        """
        try:
            # Mapeo de campos típicos de RENIEC
            processed_data = {
                "dni": data.get("dni", ""),
                "nombres": data.get("nombres", ""),
                "apellido_paterno": data.get("apellido_paterno", ""),
                "apellido_materno": data.get("apellido_materno", ""),
                "fecha_nacimiento": self._parse_date(data.get("fecha_nacimiento")),
                "lugar_nacimiento": data.get("lugar_nacimiento", "No especificado"),
                "genero": data.get("genero", "M"),
                "estado_civil": data.get("estado_civil", "SOLTERO"),
                "direccion": data.get("direccion", ""),
                "ubigeo": data.get("ubigeo", ""),
                "fecha_consulta": datetime.now().isoformat()
            }
            
            # Crear campo de nombres y apellidos combinados
            processed_data["nombres_completos"] = f"{processed_data['nombres']} {processed_data['apellido_paterno']} {processed_data['apellido_materno']}".strip()
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error procesando respuesta de RENIEC: {e}")
            return {}
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """
        Parsear fecha desde string de RENIEC
        """
        if not date_str:
            return None
        
        try:
            # Formatos comunes de fecha de RENIEC
            for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            logger.warning(f"No se pudo parsear la fecha: {date_str}")
            return None
            
        except Exception as e:
            logger.error(f"Error parseando fecha {date_str}: {e}")
            return None
    
    async def validar_dni_formato(self, dni: str) -> bool:
        """
        Validar formato de DNI peruano
        """
        if len(dni) != 8:
            return False
        
        if not dni.isdigit():
            return False
        
        # Validar que no sea una secuencia
        if dni in ["00000000", "11111111", "22222222", "33333333", "44444444", 
                   "55555555", "66666666", "77777777", "88888888", "99999999"]:
            return False
        
        return True
    
    async def calcular_digito_verificador(self, dni: str) -> Optional[str]:
        """
        Calcular el dígito verificador del DNI peruano
        """
        try:
            if len(dni) != 8 or not dni.isdigit():
                return None
            
            # Factores para el cálculo del dígito verificador
            factores = [3, 7, 9, 8, 4, 6, 2, 0, 5]
            suma = sum(int(dni[i]) * factores[i] for i in range(8))
            
            modulo = suma % 11
            
            if modulo == 1:
                return "K"
            elif modulo == 0:
                return "0"
            else:
                return str(11 - modulo)
                
        except Exception as e:
            logger.error(f"Error calculando dígito verificador para DNI {dni}: {e}")
            return None