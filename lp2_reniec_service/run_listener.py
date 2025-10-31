"""
Script de ejemplo para ejecutar los listeners RabbitMQ individualmente.
"""

import argparse
import sys
import os
import logging

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.listeners import BancoValidationListener, ReniecConfigListener, HeartbeatListener

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_banco_validation_listener(rabbitmq_host: str = 'localhost'):
    """Ejecuta el listener de validaciones del banco."""
    logger.info("Iniciando BancoValidationListener...")
    listener = BancoValidationListener(rabbitmq_host=rabbitmq_host)
    listener.start_consuming()

def run_reniec_config_listener(rabbitmq_host: str = 'localhost'):
    """Ejecuta el listener de configuraciones."""
    logger.info("Iniciando ReniecConfigListener...")
    listener = ReniecConfigListener(rabbitmq_host=rabbitmq_host)
    listener.start_consuming()

def run_heartbeat_listener(rabbitmq_host: str = 'localhost'):
    """Ejecuta el listener de heartbeats."""
    logger.info("Iniciando HeartbeatListener...")
    listener = HeartbeatListener(rabbitmq_host=rabbitmq_host)
    listener.start_consuming()

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description='Ejecutar listeners RabbitMQ')
    parser.add_argument(
        '--listener', 
        choices=['validation', 'config', 'heartbeat'],
        required=True,
        help='Tipo de listener a ejecutar'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host de RabbitMQ (default: localhost)'
    )
    
    args = parser.parse_args()
    
    logger.info(f"Ejecutando listener: {args.listener}")
    logger.info(f"Host RabbitMQ: {args.host}")
    
    try:
        if args.listener == 'validation':
            run_banco_validation_listener(args.host)
        elif args.listener == 'config':
            run_reniec_config_listener(args.host)
        elif args.listener == 'heartbeat':
            run_heartbeat_listener(args.host)
    except KeyboardInterrupt:
        logger.info("Deteniendo listener...")
    except Exception as e:
        logger.error(f"Error ejecutando listener: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()