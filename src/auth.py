"""
Módulo de autenticación para Google Cloud Platform
"""
import os
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread

from config import SCOPES

logger = logging.getLogger(__name__)


def get_credentials():
    """
    Obtiene las credenciales de GCP desde la variable de entorno.
    
    Returns:
        google.oauth2.service_account.Credentials: Credenciales autenticadas
    
    Raises:
        ValueError: Si no se encuentra la variable de entorno GCP_CREDENTIALS
    """
    creds_json = os.environ.get('GCP_CREDENTIALS')
    
    if not creds_json:
        raise ValueError(
            "No se encontró la variable de entorno 'GCP_CREDENTIALS'. "
            "Asegúrate de configurarla en GitHub Secrets."
        )
    
    try:
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=SCOPES
        )
        logger.info("✅ Credenciales de GCP cargadas exitosamente")
        return credentials
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error al parsear JSON de credenciales: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error al crear credenciales: {e}")
        raise


def get_drive_service():
    """
    Crea y retorna un servicio de Google Drive autenticado.
    
    Returns:
        googleapiclient.discovery.Resource: Servicio de Drive API
    """
    credentials = get_credentials()
    service = build('drive', 'v3', credentials=credentials)
    logger.info("✅ Servicio de Google Drive inicializado")
    return service


def get_sheets_client():
    """
    Crea y retorna un cliente de Google Sheets autenticado (gspread).
    
    Returns:
        gspread.Client: Cliente de gspread autenticado
    """
    credentials = get_credentials()
    client = gspread.authorize(credentials)
    logger.info("✅ Cliente de Google Sheets inicializado")
    return client
