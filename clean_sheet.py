import logging
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

from src.auth import get_sheets_client
from config import SHEET_NAME, REGISTRO_HEADERS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def clean_sheet():
    logger.info("🧹 INICIANDO LIMPIEZA DE SHEET...")
    
    try:
        # 1. Conectar
        client = get_sheets_client()
        spreadsheet = client.open("REGISTRO_MASTER")
        sheet = spreadsheet.worksheet(SHEET_NAME)
        
        # 2. Leer todo
        logger.info("📥 Leyendo datos actuales...")
        all_values = sheet.get_all_values()
        
        if not all_values:
            logger.info("⚠️ Hoja vacía.")
            return

        logger.info(f"📊 Filas encontradas: {len(all_values)}")
        
        # 3. Filtrar
        # Mantener header y filas que tengan fecha válida en columna A
        cleaned_rows = []
        header = all_values[0]
        cleaned_rows.append(header) # Siempre mantener header
        
        deleted_count = 0
        
        for row in all_values[1:]:
            # Criterio: La columna A (Fecha) debe tener algo y parecer una fecha (contener 2024 o 2025)
            # O la columna B (Archivo) debe tener texto
            if not row:
                continue
                
            col_a = row[0].strip() if len(row) > 0 else ""
            
            # Si la columna A está vacía, es basura (spillover)
            if not col_a:
                deleted_count += 1
                continue
                
            # Si la columna A tiene fecha válida, la guardamos
            if "2024" in col_a or "2025" in col_a:
                # Opcional: Limpiar el texto de la columna G (Texto Crudo) por si acaso
                if len(row) > 6:
                    row[6] = row[6].replace('\n', ' ').replace('\r', ' ').strip()
                cleaned_rows.append(row)
            else:
                # Si tiene texto pero no fecha, asumimos basura
                deleted_count += 1
        
        logger.info(f"🗑️ Filas basura detectadas: {deleted_count}")
        logger.info(f"✅ Filas válidas a conservar: {len(cleaned_rows)}")
        
        # 4. Escribir de nuevo (Sobrescribir)
        if deleted_count > 0:
            logger.info("💾 Sobrescribiendo hoja con datos limpios...")
            sheet.clear()
            sheet.update(cleaned_rows)
            logger.info("✨ ¡LIMPIEZA COMPLETADA!")
        else:
            logger.info("✅ La hoja ya estaba limpia.")

    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    clean_sheet()
