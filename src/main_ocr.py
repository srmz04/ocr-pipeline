"""
Script principal del pipeline OCR (Refactorizado)
Punto de entrada para GitHub Actions.
"""
import os
import sys
import logging
import tempfile
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sheets_manager import INESheetsManager
from config import LOG_FILE, LOG_FORMAT, LOG_LEVEL

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    Entry point para GitHub Actions.
    """
    logger.info("🚀 Starting OCR Pipeline (Professional Architecture)")
    
    # Obtener credentials desde env variable o archivo
    # En local, usamos el archivo directo. En GitHub Actions, la variable de entorno.
    
    # Intentar cargar desde archivo local primero (para dev)
    local_creds = os.path.join(Path(__file__).parent.parent, 'credentials.json')
    creds_path = local_creds
    
    is_temp_creds = False
    
    if not os.path.exists(local_creds):
        # Si no existe local, buscar en variable de entorno (GitHub Actions)
        creds_json = os.environ.get('GCP_CREDENTIALS') # Usamos el nombre que ya tenías configurado
        if not creds_json:
            logger.error("❌ GCP_CREDENTIALS environment variable not set and no local file found")
            return

        # Escribir a archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(creds_json)
            creds_path = f.name
            is_temp_creds = True
            
    sheet_name = os.environ.get('SPREADSHEET_NAME', 'REGISTRO_INE') # Usar nombre por defecto o variable
    
    try:
        # Inicializar manager
        manager = INESheetsManager(creds_path, sheet_name)
        
        # Procesar pending rows
        manager.process_pending_rows()
        
        logger.info("✅ Pipeline execution completed")
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
        
    finally:
        # Limpiar archivo temporal si se creó
        if is_temp_creds and os.path.exists(creds_path):
            os.unlink(creds_path)

if __name__ == '__main__':
    main()
