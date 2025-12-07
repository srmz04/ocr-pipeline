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
    FOLDER_REVISION_NAME,
    ROOT_FOLDER_NAME,
    USE_EASYOCR_FALLBACK
)

from src.auth import get_drive_service, get_sheets_client
from src.drive_manager import DriveManager
from src.sheets_manager import SheetsManager
from src.image_processor import preprocess_image, validate_image
from src.ocr_engine import extract_text_hybrid
from src.robust_extractor import RobustExtractor
from src.curp_validator import (
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
            
            if not self.drive_manager.initialize_folders(ROOT_FOLDER_NAME):
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
            
            # Preprocesar imagen (legacy - para compatibilidad)
            logger.info("🔧 Preprocesando imagen...")
            processed_image = preprocess_image(temp_path)
            
            # Extraer texto con OCR multi-estrategia
            logger.info("🔍 Extrayendo texto con OCR multi-estrategia...")
            raw_text, ocr_confidence, ocr_method = extract_text_hybrid(
                processed_image,
                use_easyocr_fallback=USE_EASYOCR_FALLBACK,
                image_path=temp_path  # Pass original path for multi-pass
            )
            
            result['raw_text'] = raw_text[:500]  # Limitar a 500 caracteres
            result['confidence'] = ocr_confidence
            
            logger.info(f"📝 Texto extraído ({ocr_method}): {len(raw_text)} caracteres")
            logger.info(f"📊 Confianza OCR: {ocr_confidence:.2f}")
            
            # Extraer CURP del texto usando RobustExtractor
            logger.info("🔎 Buscando CURP con extractor robusto...")
            curp_result = RobustExtractor.find_curp_fuzzy(raw_text)
            
            if not curp_result:
                logger.warning("⚠️ No se encontró CURP en el texto")
                result['status'] = 'SIN_CURP'
                result['destination_folder'] = FOLDER_REVISION_NAME
                result['curp'] = 'X'
                return result
            
            curps_found = [curp_result]  # Convert to list for compatibility
            
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
            # 4. Extraer información (CURP)
            logger.info("🔍 Buscando CURP en el texto...")
            
            # Usar Extractor Robusto
            curp_encontrada = RobustExtractor.find_curp_fuzzy(raw_text)
            
            if curp_encontrada:
                logger.info(f"✅ CURP detectada: {curp_encontrada}")
                result['curp'] = curp_encontrada
                result['status'] = 'PROCESADO'
                result['destination_folder'] = FOLDER_PROCESADAS_NAME
                
                # Extraer info adicional de la CURP
                info_curp = extract_info_from_curp(curp_encontrada)
                if info_curp:
                    result['sexo'] = info_curp.get('sexo', '')
                    # result['fecha_nacimiento'] = info_curp.get('fecha_nacimiento', '')
            else:
                logger.warning("⚠️ No se encontró CURP válida")
                result['status'] = 'SIN_CURP'
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
            # NUEVO ENFOQUE: Procesar basándose en el Sheet, no en Drive
            logger.info(f"\n📊 Leyendo archivos pendientes desde Sheet...")
            pending_files = self.sheets_manager.get_pending_files()
            
            if not pending_files:
                logger.info("ℹ️ No hay archivos PENDIENTE_OCR para procesar")
                return True
            
            logger.info(f"📋 {len(pending_files)} archivos con estado PENDIENTE_OCR")
            
            # Para cada archivo pendiente, buscar en Drive
            files_to_process = []
            for filename in pending_files:
                logger.info(f"🔍 Buscando '{filename}' en Drive...")
                
                # Buscar primero en ENTRADAS
                file_in_entradas = self.drive_manager.find_file_by_name(filename, FOLDER_ENTRADA_NAME)
                if file_in_entradas:
                    files_to_process.append(file_in_entradas)
                    logger.info(f"   ✅ Encontrado en ENTRADAS")
                    continue
                
                # Buscar en REVISIÓN
                file_in_revision = self.drive_manager.find_file_by_name(filename, FOLDER_REVISION_NAME)
                if file_in_revision:
                    files_to_process.append(file_in_revision)
                    logger.info(f"   ✅ Encontrado en REVISIÓN")
                    continue
                    
                # Buscar en PROCESADAS (por si fue movido)
                file_in_procesadas = self.drive_manager.find_file_by_name(filename, FOLDER_PROCESADAS_NAME)
                if file_in_procesadas:
                    files_to_process.append(file_in_procesadas)
                    logger.info(f"   ✅ Encontrado en PROCESADAS")
                    continue
                
                logger.warning(f"   ⚠️ Archivo '{filename}' no encontrado en Drive")
            
            if not files_to_process:
                logger.info("ℹ️ No se encontraron archivos en Drive para procesar")
                return True
            
            logger.info(f"📋 {len(files_to_process)} archivos encontrados en Drive para procesar")
            
            # Crear directorio temporal
            with tempfile.TemporaryDirectory() as temp_dir:
                logger.info(f"📁 Directorio temporal: {temp_dir}")
                
                # Procesar cada archivo
                for i, file_info in enumerate(files_to_process, 1):
                    logger.info(f"\n{'#' * 80}")
                    logger.info(f"Archivo {i}/{len(files_to_process)}")
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
                    
                    # 5. Guardar resultados
                    logger.info("💾 Guardando resultados...")
                    
                    # Preparar datos para Sheets - KEYS MUST MATCH sheets_manager.update_entry_by_filename
                    sheet_data = {
                        'curp': result['curp'],
                        'confidence': f"{result['confidence']:.2f}",
                        'nombre': result.get('nombre', ''),
                        'sexo': result.get('sexo', ''),
                        'raw_text': result['raw_text'].replace('\n', ' ').replace('\r', ' '),
                        'status': result['status']
                    }
                    
                    # Actualizar hoja (buscar por nombre de archivo)
                    if self.sheets_manager.update_entry_by_filename(result['file_name'], sheet_data):
                        # Stats are already updated based on result['success'] and result['status']
                        pass
                    else:
                        logger.error(f"❌ Error al actualizar registro para {result['file_name']}")
                        # If update fails, it's an error in sheets operation, not necessarily image processing
                        # The original stats update logic for image processing success/failure remains.
                        # We might want to add a specific stat for sheets update errors if needed.
                    
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
