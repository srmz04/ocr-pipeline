"""
Configuración centralizada para el pipeline OCR
"""

# Google Cloud Platform
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Nombres de carpetas en Google Drive
ROOT_FOLDER_NAME = "MACROCENTRO"  # Nombre de la carpeta raíz en Drive
FOLDER_ENTRADA_NAME = "ENTRADAS"  # ← Cambiado a plural
FOLDER_PROCESADAS_NAME = "PROCESADAS"
FOLDER_ERRORES_NAME = "ERRORES"
FOLDER_REVISION_NAME = "REVISIÓN"

# Nombre de la hoja de Google Sheets
SHEET_NAME = "REGISTRO_MASTER"
DASHBOARD_SHEET_NAME = "DASHBOARD"

# Headers para la hoja de registro
REGISTRO_HEADERS = [
    "FECHA_HORA",
    "NOMBRE_ARCHIVO",
    "CURP_DETECTADA",
    "CONFIANZA_OCR",
    "NOMBRE_EXTRAIDO",
    "SEXO_EXTRAIDO",
    "TEXTO_CRUDO",
    "STATUS",
    "LINK_FOTO",
    "BIOLOGICO",
    "DOSIS"
]

# Headers para el dashboard
DASHBOARD_HEADERS = [
    "MÉTRICA",
    "VALOR",
    "ÚLTIMA_ACTUALIZACIÓN"
]

# Configuración de OCR
# psm 3 = Fully automatic page segmentation (best for documents)
# psm 6 = Assume uniform block of text
# psm 11 = Sparse text, find as much text as possible
TESSERACT_CONFIG = '--oem 3 --psm 3 -l spa'
TESSERACT_CONFIG_SPARSE = '--oem 3 --psm 11 -l spa'  # For sparse text (INE, cards)
TESSERACT_LANG = 'spa'

# Configuración de EasyOCR
EASYOCR_LANGS = ['es', 'en']
EASYOCR_GPU = False  # GitHub Actions no tiene GPU
USE_EASYOCR_FALLBACK = False  # DESHABILITADO por defecto (ocupa mucho espacio en GitHub Actions)

# Regex para CURP (18 caracteres)
# Formato: 4 letras + 6 dígitos (YYMMDD) + H/M + 5 letras + 1 alfanumérico + 1 dígito
CURP_REGEX = r'\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b'

# Umbral de confianza para marcar como "REVISIÓN"
CONFIDENCE_THRESHOLD = 0.7

# Configuración de logging
LOG_FILE = "ocr_pipeline.log"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# Límite de archivos a procesar por ejecución (para evitar timeout en GitHub Actions)
MAX_FILES_PER_RUN = 50

# Timeout para procesamiento de cada imagen (segundos)
IMAGE_TIMEOUT = 30
