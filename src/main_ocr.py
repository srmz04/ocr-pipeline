"""
Script principal del pipeline OCR
Procesa imágenes de Google Drive, extrae CURPs y actualiza Google Sheets
"""
import os
import sys
import logging
import tempfile
from datetime import datetime
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    LOG_FILE,
    LOG_FORMAT,
    LOG_LEVEL,
    MAX_FILES_PER_RUN,
    IMAGE_TIMEOUT,
    CONFIDENCE_THRESHOLD,
    FOLDER_ENTRADA_NAME,
    FOLDER_PROCESADAS_NAME,
    FOLDER_ERRORES_NAME,
    FOLDER_REVISION_NAME
)

from src.auth import get_drive_service, get_sheets_client
from src.drive_manager import DriveManager
from src.sheets_manager import SheetsManager
from src.image_processor import preprocess_image, validate_image
from src.ocr_engine import extract_text_hybrid
from src.curp_validator import (
    extract_curp_from_text,
    validate_curp_complete,
    extract_info_from_curp
)

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


class OCRPipeline:
    """Pipeline principal de procesamiento OCR"""
    
    def __init__(self):
        """Inicializa el pipeline"""
        self.drive_manager = None
        self.sheets_manager = None
        self.stats = {
            'total_procesados': 0,
            'exitosos': 0,
            'errores': 0,
            'revision': 0,
            'duplicados': 0
        }
    
    def initialize(self):
        """
        Inicializa servicios de Drive y Sheets.
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        logger.info("=" * 80)
        logger.info("🚀 INICIANDO PIPELINE OCR")
        logger.info("=" * 80)
        
        try:
            # Inicializar Drive
            logger.info("📁 Inicializando Google Drive...")
            drive_service = get_drive_service()
            self.drive_manager = DriveManager(drive_service)
            
            if not self.drive_manager.initialize_folders():
                logger.error("❌ Error al inicializar carpetas de Drive")
                return False
            
            # Inicializar Sheets
            logger.info("📊 Inicializando Google Sheets...")
            sheets_client = get_sheets_client()
            self.sheets_manager = SheetsManager(sheets_client)
            
            # Buscar spreadsheet (debe estar configurado en variable de entorno o hardcoded)
            spreadsheet_name = os.environ.get('SPREADSHEET_NAME', 'REGISTRO_MASTER')
            
            if not self.sheets_manager.initialize_spreadsheet(spreadsheet_name):
                logger.error("❌ Error al inicializar spreadsheet")
                return False
            
            logger.info("✅ Inicialización completada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en inicialización: {e}")
            return False
    
    def process_image(self, file_info, temp_dir):
        """
        Procesa una imagen individual.
        
        Args:
            file_info (dict): Información del archivo de Drive
            temp_dir (str): Directorio temporal para descargas
        
        Returns:
            dict: Resultado del procesamiento
        """
        file_id = file_info['id']
        file_name = file_info['name']
        
        logger.info(f"\n{'=' * 60}")
        logger.info(f"📸 Procesando: {file_name}")
        logger.info(f"{'=' * 60}")
        
        result = {
            'success': False,
            'file_name': file_name,
            'file_id': file_id,
            'curp': 'X',
            'confidence': 0.0,
            'status': 'ERROR',
            'destination_folder': FOLDER_ERRORES_NAME,
            'raw_text': '',
            'nombre': '',
            'sexo': ''
        }
        
        try:
            # Descargar imagen
            temp_path = os.path.join(temp_dir, file_name)
            
            if not self.drive_manager.download_file(file_id, temp_path):
                result['status'] = 'ERROR_DESCARGA'
                return result
            
            # Validar imagen
            is_valid, validation_msg = validate_image(temp_path)
            if not is_valid:
                logger.warning(f"⚠️ Imagen inválida: {validation_msg}")
                result['status'] = f'ERROR_VALIDACION: {validation_msg}'
                return result
            
            # Preprocesar imagen
            logger.info("🔧 Preprocesando imagen...")
            processed_image = preprocess_image(temp_path)
            
            # Extraer texto con OCR híbrido
            logger.info("🔍 Extrayendo texto con OCR...")
            raw_text, ocr_confidence, ocr_method = extract_text_hybrid(processed_image)
            
            result['raw_text'] = raw_text[:500]  # Limitar a 500 caracteres
            result['confidence'] = ocr_confidence
            
            logger.info(f"📝 Texto extraído ({ocr_method}): {len(raw_text)} caracteres")
            logger.info(f"📊 Confianza OCR: {ocr_confidence:.2f}")
            
            # Extraer CURP del texto
            logger.info("🔎 Buscando CURP...")
            curps_found = extract_curp_from_text(raw_text)
            
            if not curps_found:
                logger.warning("⚠️ No se encontró CURP en el texto")
                result['status'] = 'SIN_CURP'
                result['destination_folder'] = FOLDER_REVISION_NAME
                result['curp'] = 'X'
                return result
            
            # Validar CURP(s) encontrada(s)
            best_curp = None
            best_confidence = 0.0
            
            for curp in curps_found:
                is_valid, curp_conf, msg = validate_curp_complete(curp)
                logger.info(f"   CURP: {curp} - Válida: {is_valid} - Confianza: {curp_conf:.2f} - {msg}")
                
                if is_valid and curp_conf > best_confidence:
                    best_curp = curp
                    best_confidence = curp_conf
            
            if not best_curp:
                logger.warning("⚠️ CURPs encontradas pero ninguna es válida")
                result['status'] = 'CURP_INVALIDA'
                result['destination_folder'] = FOLDER_REVISION_NAME
                result['curp'] = curps_found[0] if curps_found else 'X'
                return result
            
            # CURP válida encontrada
            result['curp'] = best_curp
            result['success'] = True
            
            # Verificar si es duplicado
            if self.sheets_manager.check_curp_exists(best_curp):
                logger.warning(f"⚠️ CURP duplicada: {best_curp}")
                result['status'] = 'DUPLICADO'
                result['destination_folder'] = FOLDER_REVISION_NAME
                self.stats['duplicados'] += 1
                return result
            
            # Extraer información adicional de la CURP
            curp_info = extract_info_from_curp(best_curp)
            if curp_info:
                result['sexo'] = curp_info['sexo']
            
            # Determinar carpeta destino según confianza
            if best_confidence >= CONFIDENCE_THRESHOLD:
                result['status'] = 'PROCESADO'
                result['destination_folder'] = FOLDER_PROCESADAS_NAME
                logger.info(f"✅ CURP válida: {best_curp} (confianza: {best_confidence:.2f})")
            else:
                result['status'] = 'BAJA_CONFIANZA'
                result['destination_folder'] = FOLDER_REVISION_NAME
                logger.warning(f"⚠️ CURP con baja confianza: {best_curp} ({best_confidence:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error al procesar imagen: {e}", exc_info=True)
            result['status'] = f'ERROR: {str(e)[:100]}'
            return result
    
    def run(self):
        """
        Ejecuta el pipeline completo.
        
        Returns:
            bool: True si la ejecución fue exitosa
        """
        if not self.initialize():
            logger.error("❌ Fallo en inicialización")
            return False
        
        try:
            # Listar archivos en carpeta ENTRADA
            logger.info(f"\n📂 Buscando archivos en carpeta '{FOLDER_ENTRADA_NAME}'...")
            files = self.drive_manager.list_files_in_folder(
                FOLDER_ENTRADA_NAME,
                max_files=MAX_FILES_PER_RUN
            )
            
            if not files:
                logger.info("ℹ️ No hay archivos para procesar")
                return True
            
            logger.info(f"📋 {len(files)} archivos encontrados")
            
            # Crear directorio temporal
            with tempfile.TemporaryDirectory() as temp_dir:
                logger.info(f"📁 Directorio temporal: {temp_dir}")
                
                # Procesar cada archivo
                for i, file_info in enumerate(files, 1):
                    logger.info(f"\n{'#' * 80}")
                    logger.info(f"Archivo {i}/{len(files)}")
                    logger.info(f"{'#' * 80}")
                    
                    # Procesar imagen
                    result = self.process_image(file_info, temp_dir)
                    
                    # Actualizar estadísticas
                    self.stats['total_procesados'] += 1
                    
                    if result['success']:
                        if result['status'] == 'PROCESADO':
                            self.stats['exitosos'] += 1
                        elif result['status'] in ['BAJA_CONFIANZA', 'SIN_CURP', 'CURP_INVALIDA']:
                            self.stats['revision'] += 1
                    else:
                        self.stats['errores'] += 1
                    
                    # Agregar registro a Sheets
                    file_link = self.drive_manager.get_file_link(result['file_id'])
                    
                    registro_data = {
                        'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'nombre_archivo': result['file_name'],
                        'curp_detectada': result['curp'],
                        'confianza_ocr': f"{result['confidence']:.2f}",
                        'nombre_extraido': result['nombre'],
                        'sexo_extraido': result['sexo'],
                        'texto_crudo': result['raw_text'],
                        'status': result['status'],
                        'link_foto': file_link
                    }
                    
                    self.sheets_manager.add_registro(registro_data)
                    
                    # Mover archivo a carpeta correspondiente
                    self.drive_manager.move_file(
                        result['file_id'],
                        result['destination_folder']
                    )
                    
                    logger.info(f"📦 Movido a: {result['destination_folder']}")
            
            # Actualizar dashboard
            logger.info("\n📊 Actualizando dashboard...")
            
            total_registros = self.sheets_manager.get_total_registros()
            tasa_exito = (self.stats['exitosos'] / self.stats['total_procesados'] * 100) if self.stats['total_procesados'] > 0 else 0
            
            dashboard_metrics = {
                'Total de Registros': total_registros,
                'Procesados en esta ejecución': self.stats['total_procesados'],
                'Exitosos': self.stats['exitosos'],
                'Para Revisión': self.stats['revision'],
                'Errores': self.stats['errores'],
                'Duplicados': self.stats['duplicados'],
                'Tasa de Éxito (%)': f"{tasa_exito:.1f}%"
            }
            
            self.sheets_manager.update_dashboard(dashboard_metrics)
            
            # Resumen final
            logger.info("\n" + "=" * 80)
            logger.info("📊 RESUMEN DE EJECUCIÓN")
            logger.info("=" * 80)
            for metric, value in dashboard_metrics.items():
                logger.info(f"   {metric}: {value}")
            logger.info("=" * 80)
            logger.info("✅ Pipeline completado exitosamente")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en ejecución del pipeline: {e}", exc_info=True)
            return False


def main():
    """Función principal"""
    pipeline = OCRPipeline()
    success = pipeline.run()
    
    if not success:
        logger.error("❌ Pipeline terminó con errores")
        sys.exit(1)
    
    logger.info("✅ Pipeline terminó exitosamente")
    sys.exit(0)


if __name__ == "__main__":
    main()
