"""
INESheetsManager
Gestor profesional para integración Google Sheets <-> OCR
"""
import logging
import gspread
import cv2
import os
import tempfile
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from src.ine_processor import INEOCRProcessor

logger = logging.getLogger(__name__)

class INESheetsManager:
    """
    Gestor que:
    1. Lee Sheet con status 'PENDIENTE_OCR'
    2. Descarga imagen de Drive
    3. Corre OCR inteligente
    4. Actualiza Sheet con resultados + logs
    """
    
    def __init__(self, credentials_path: str, sheet_name: str):
        """
        Args:
            credentials_path: Path a service account JSON
            sheet_name: Nombre del Sheet (ej: "INE_Registros")
        """
        self.credentials_path = credentials_path
        
        # Autenticar con Google
        scope = ['https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive']
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path, scopes=scope
            )
            
            self.gc = gspread.authorize(credentials)
            self.sheet = self.gc.open(sheet_name).sheet1
            self.drive_service = build('drive', 'v3', credentials=credentials)
            
            # Inicializar OCR processor
            self.ocr = INEOCRProcessor(debug=False)
            
            logger.info(f"✓ SheetsManager initialized for '{sheet_name}'")
        except Exception as e:
            logger.error(f"❌ Error initializing SheetsManager: {e}")
            raise

    def process_pending_rows(self):
        """
        Main loop: procesar TODAS las filas con status 'PENDIENTE_OCR'
        """
        logger.info("🔍 Scanning for pending rows...")
        
        try:
            # Leer todas las filas
            rows = self.sheet.get_all_records()
            
            pending_rows = []
            for idx, row in enumerate(rows, start=2):  # Start at 2 (row 1 es headers)
                status = str(row.get('STATUS', '')).strip().upper() # Usar STATUS (header real)
                if status == 'PENDIENTE_OCR':
                    pending_rows.append((idx, row))
            
            logger.info(f"Found {len(pending_rows)} pending rows")
            
            if not pending_rows:
                logger.info("No pending rows. Exiting.")
                return
            
            # Procesar cada uno
            for row_num, row_data in pending_rows:
                try:
                    self._process_single_row(row_num, row_data)
                except Exception as e:
                    logger.error(f"ERROR processing row {row_num}: {e}")
                    self._update_row_status(row_num, 'ERROR', str(e))
                    
        except Exception as e:
            logger.error(f"❌ Error in process_pending_rows: {e}")

    def _process_single_row(self, row_num: int, row_data: dict):
        """
        Procesar una sola fila:
        1. Obtener image_path o drive_file_id
        2. Cargar imagen
        3. Correr OCR
        4. Actualizar Sheet
        """
        logger.info(f"\n[Row {row_num}] Processing...")
        
        # Obtener nombre de archivo (que usaremos para buscar en Drive si no tenemos ID directo)
        filename = row_data.get('NOMBRE_ARCHIVO')
        
        if not filename:
            self._update_row_status(row_num, 'ERROR', 'No filename found')
            return
            
        # Descargar desde Drive (buscando por nombre)
        image_path = self._download_file_by_name(filename)
        
        if not image_path:
             self._update_row_status(row_num, 'ERROR', f'File not found in Drive: {filename}')
             return

        # Cargar imagen
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not load image")
        except Exception as e:
            self._update_row_status(row_num, 'ERROR', f'Image load failed: {e}')
            return
        
        # Correr OCR
        logger.info(f"  → Running OCR...")
        try:
            # Procesamiento inteligente
            ocr_results = self.ocr.process_ine_image(
                image_path=image_path
            )
            
            logger.info(f"  → OCR Complete: {ocr_results['overall_confidence']:.0f}% confidence")
            
            # Actualizar Sheet
            self._update_row_with_results(row_num, ocr_results)
            
        except Exception as e:
            logger.error(f"OCR Failed: {e}", exc_info=True)
            self._update_row_status(row_num, 'ERROR', f'OCR failed: {e}')
        finally:
            # Limpiar archivo temporal
            if os.path.exists(image_path):
                os.remove(image_path)

    def _download_file_by_name(self, filename: str) -> str:
        """
        Busca y descarga un archivo por nombre desde Drive.
        Retorna path temporal.
        """
        try:
            # Buscar archivo
            query = f"name = '{filename}' and trashed = false"
            results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])
            
            if not files:
                logger.warning(f"File not found: {filename}")
                return None
                
            file_id = files[0]['id']
            
            # Descargar
            request = self.drive_service.files().get_media(fileId=file_id)
            file_content = request.execute()
            
            # Guardar en temp
            fd, path = tempfile.mkstemp(suffix='.jpg')
            with os.fdopen(fd, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"  ✓ Downloaded {filename} to {path}")
            return path
            
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None

    def _update_row_with_results(self, row_num: int, ocr_results: dict):
        """
        Actualizar Sheet con resultados OCR.
        
        Mapeo de Columnas (Basado en REGISTRO_HEADERS actual + Nuevas):
        A: FECHA_HORA (No tocar)
        B: NOMBRE_ARCHIVO (No tocar)
        C: CURP_DETECTADA
        D: CONFIANZA_OCR
        E: NOMBRE_EXTRAIDO
        F: SEXO_EXTRAIDO
        G: TEXTO_CRUDO
        H: STATUS
        I: LINK_FOTO (No tocar)
        J: BIOLOGICO (No tocar)
        K: DOSIS (No tocar)
        L: OCR_STRATEGY
        M: OCR_TIMESTAMP
        N: OCR_ISSUES
        """
        
        fields = ocr_results['fields']
        
        # Preparar valores para actualizar (Columnas C a H y L a N)
        # Nota: gspread update con rango permite actualizar bloques
        
        # Bloque 1: C-H (CURP, Confianza, Nombre, Sexo, RawText, Status)
        curp = fields['curp'].value
        conf = f"{ocr_results['overall_confidence']:.2f}"
        nombre = fields['nombre'].value
        sexo = fields['sexo'].value
        raw_text = "..." # Omitimos raw text largo para limpieza, o lo ponemos truncado
        status = 'COMPLETADO' if ocr_results['overall_confidence'] >= 80 else 'REVISION'
        
        # Bloque 2: L-N (Strategy, Timestamp, Issues)
        strategy = ocr_results['strategy']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        issues = self._format_issues(fields)
        
        try:
            # Actualizar Bloque C-H (Indices 3-8, columnas C,D,E,F,G,H)
            # Rango C{row}:H{row}
            self.sheet.update(f'C{row_num}:H{row_num}', [[curp, conf, nombre, sexo, raw_text, status]])
            
            # Actualizar Bloque L-N (Indices 12-14, columnas L,M,N)
            # Rango L{row}:N{row}
            self.sheet.update(f'L{row_num}:N{row_num}', [[strategy, timestamp, issues]])
            
            logger.info(f"  ✓ Row {row_num} updated successfully")
            
        except Exception as e:
            logger.error(f"  ✗ Failed to update row: {e}")

    def _format_issues(self, fields: dict) -> str:
        """
        Formatear lista de campos con baja confianza.
        """
        issues = []
        for field_name, field in fields.items():
            if field.confidence < 80 and field.value:
                issues.append(f"{field_name}({field.confidence:.0f}%)")
        return '; '.join(issues) if issues else 'None'
    
    def _update_row_status(self, row_num: int, status: str, message: str = ''):
        """
        Actualizar solo el status de una fila (para errores).
        Columna H es STATUS. Columna N es ISSUES (usaremos esa para el mensaje).
        """
        try:
            self.sheet.update_cell(row_num, 8, status) # Col H
            self.sheet.update_cell(row_num, 14, f"ERROR: {message}") # Col N
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
