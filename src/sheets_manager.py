"""
Módulo de gestión de Google Sheets
"""
import logging
from datetime import datetime
import gspread
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound

from config import (
    SHEET_NAME,
    DASHBOARD_SHEET_NAME,
    REGISTRO_HEADERS,
    DASHBOARD_HEADERS
)

logger = logging.getLogger(__name__)


class SheetsManager:
    """Gestor de operaciones con Google Sheets"""
    
    def __init__(self, client, spreadsheet_name=None):
        """
        Inicializa el gestor de Sheets.
        
        Args:
            client: Cliente de gspread
            spreadsheet_name (str, optional): Nombre del spreadsheet
        """
        self.client = client
        self.spreadsheet = None
        self.registro_sheet = None
        self.dashboard_sheet = None
        self.spreadsheet_name = spreadsheet_name

    @staticmethod
    def clean_text_for_sheet(text):
        """Limpia texto para evitar romper formato CSV/Sheets"""
        if not isinstance(text, str):
            return text
        # Reemplazar newlines y tabs con espacios
        return text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()
        
    def initialize_spreadsheet(self, spreadsheet_name=None):
        """
        Inicializa la conexión al spreadsheet.
        
        Args:
            spreadsheet_name (str, optional): Nombre del spreadsheet
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        if spreadsheet_name:
            self.spreadsheet_name = spreadsheet_name
        
        if not self.spreadsheet_name:
            logger.error("❌ Nombre de spreadsheet no especificado")
            return False
        
        try:
            self.spreadsheet = self.client.open(self.spreadsheet_name)
            logger.info(f"✅ Spreadsheet '{self.spreadsheet_name}' abierto")
            
            # Inicializar hoja de registro
            try:
                self.registro_sheet = self.spreadsheet.worksheet(SHEET_NAME)
                logger.info(f"✅ Hoja '{SHEET_NAME}' encontrada")
            except WorksheetNotFound:
                logger.warning(f"⚠️ Hoja '{SHEET_NAME}' no encontrada, creando...")
                self.registro_sheet = self.spreadsheet.add_worksheet(
                    title=SHEET_NAME,
                    rows=1000,
                    cols=len(REGISTRO_HEADERS)
                )
                self.registro_sheet.append_row(REGISTRO_HEADERS)
                logger.info(f"✅ Hoja '{SHEET_NAME}' creada")
            
            # Inicializar hoja de dashboard
            try:
                self.dashboard_sheet = self.spreadsheet.worksheet(DASHBOARD_SHEET_NAME)
                logger.info(f"✅ Hoja '{DASHBOARD_SHEET_NAME}' encontrada")
            except WorksheetNotFound:
                logger.warning(f"⚠️ Hoja '{DASHBOARD_SHEET_NAME}' no encontrada, creando...")
                self.dashboard_sheet = self.spreadsheet.add_worksheet(
                    title=DASHBOARD_SHEET_NAME,
                    rows=100,
                    cols=len(DASHBOARD_HEADERS)
                )
                self.dashboard_sheet.append_row(DASHBOARD_HEADERS)
                logger.info(f"✅ Hoja '{DASHBOARD_SHEET_NAME}' creada")
            
            return True
            
        except SpreadsheetNotFound:
            logger.error(f"❌ Spreadsheet '{self.spreadsheet_name}' no encontrado")
            return False
        except Exception as e:
            logger.error(f"❌ Error al inicializar spreadsheet: {e}")
            return False
    
    def update_entry_by_filename(self, filename, data):
        """
        Actualiza una fila existente buscando por nombre de archivo.
        Si no existe, NO crea una nueva (el frontend ya la creó).
        
        Args:
            filename (str): Nombre del archivo a buscar
            data (dict): Datos a actualizar (curp, confidence, nombre, sexo, raw_text, status)
        
        Returns:
            bool: True si tuvo éxito
        """
        if not self.registro_sheet:
            logger.error("❌ Hoja de registro no inicializada")
            return False
            
        try:
            # Strip common Drive copy prefixes to match original filename
            search_filename = filename
            prefixes_to_strip = ['Copia de Copia de ', 'Copia de ', 'Copy of Copy of ', 'Copy of ']
            for prefix in prefixes_to_strip:
                if filename.startswith(prefix):
                    search_filename = filename[len(prefix):]
                    logger.info(f"   Stripped prefix: '{filename}' -> '{search_filename}'")
                    break
            
            # Buscar la celda que contiene el nombre del archivo (columna B = 2)
            logger.info(f"🔍 Buscando archivo: {search_filename}")
            cell = self.registro_sheet.find(search_filename, in_column=2)
            
            if not cell:
                logger.warning(f"⚠️ Archivo {filename} NO encontrado. El frontend debió haberlo creado.")
                return False
            
            row_idx = cell.row
            logger.info(f"✅ Archivo encontrado en fila {row_idx}. Actualizando celdas...")
            
            # Actualizar celda por celda de forma simple y directa
            # Columnas: A=Fecha, B=Archivo, C=CURP, D=Confianza, E=Nombre, F=Sexo, G=Texto, H=Status
            if 'curp' in data and data['curp']:
                self.registro_sheet.update_cell(row_idx, 3, data['curp'])
                logger.info(f"   C{row_idx} = CURP: {data['curp']}")
            
            if 'confidence' in data:
                self.registro_sheet.update_cell(row_idx, 4, str(data['confidence']))
                
            if 'nombre' in data and data['nombre']:
                self.registro_sheet.update_cell(row_idx, 5, data['nombre'])
                
            if 'sexo' in data and data['sexo']:
                self.registro_sheet.update_cell(row_idx, 6, data['sexo'])
                
            if 'raw_text' in data:
                clean_text = SheetsManager.clean_text_for_sheet(data['raw_text'])[:49000]
                self.registro_sheet.update_cell(row_idx, 7, clean_text)
                
            if 'status' in data:
                self.registro_sheet.update_cell(row_idx, 8, data['status'])
            
            logger.info(f"✅ Fila {row_idx} actualizada exitosamente")
            return True
                
        except Exception as e:
            logger.error(f"❌ Error al actualizar registro: {e}")
            import traceback
            traceback.print_exc()
            return False

    def add_registro(self, data):
        """
        Agrega un registro a la hoja de datos.
        
        Args:
            data (dict): Diccionario con los datos del registro
        
        Returns:
            bool: True si el registro fue agregado exitosamente
        """
        if not self.registro_sheet:
            logger.error("❌ Hoja de registro no inicializada")
            return False
        
        try:
            # Preparar fila según headers
            row = [
                data.get('fecha_hora', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                data.get('nombre_archivo', ''),
                data.get('curp_detectada', 'X'),
                data.get('confianza_ocr', 0.0),
                data.get('nombre_extraido', ''),
                data.get('sexo_extraido', ''),
                SheetsManager.clean_text_for_sheet(data.get('texto_crudo', '')),
                data.get('status', 'PROCESADO'),
                data.get('link_foto', ''),
                data.get('biologico', ''),
                data.get('dosis', '')
            ]
            
            self.registro_sheet.append_row(row)
            logger.debug(f"✅ Registro agregado: {data.get('nombre_archivo')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al agregar registro: {e}")
            return False
    
    def update_dashboard(self, metrics):
        """
        Actualiza el dashboard con métricas.
        
        Args:
            metrics (dict): Diccionario con métricas
        
        Returns:
            bool: True si la actualización fue exitosa
        """
        if not self.dashboard_sheet:
            logger.error("❌ Hoja de dashboard no inicializada")
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Limpiar dashboard (excepto headers)
            self.dashboard_sheet.clear()
            self.dashboard_sheet.append_row(DASHBOARD_HEADERS)
            
            # Agregar métricas
            rows = []
            for metric_name, metric_value in metrics.items():
                rows.append([metric_name, metric_value, timestamp])
            
            if rows:
                self.dashboard_sheet.append_rows(rows)
            
            logger.info(f"✅ Dashboard actualizado con {len(rows)} métricas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al actualizar dashboard: {e}")
            return False
    
    def get_total_registros(self):
        """
        Obtiene el total de registros en la hoja.
        
        Returns:
            int: Número total de registros (sin contar header)
        """
        if not self.registro_sheet:
            return 0
        
        try:
            all_values = self.registro_sheet.get_all_values()
            # Restar 1 por el header
            return len(all_values) - 1 if len(all_values) > 0 else 0
        except Exception as e:
            logger.error(f"❌ Error al obtener total de registros: {e}")
            return 0
    
    def check_curp_exists(self, curp):
        """
        Verifica si una CURP ya existe en la hoja.
        
        Args:
            curp (str): CURP a verificar
        
        Returns:
            bool: True si la CURP ya existe
        """
        if not self.registro_sheet or not curp:
            return False
        
        try:
            # Buscar en la columna de CURP (columna 3)
            cell = self.registro_sheet.find(curp, in_column=3)
            return cell is not None
        except Exception as e:
            logger.debug(f"CURP no encontrada o error: {e}")
            return False
