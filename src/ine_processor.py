"""
INE Processor Adapter
Adapta el motor de OCR robusto (ocr_engine.py) a la interfaz requerida por INESheetsManager.
"""
import logging
from dataclasses import dataclass
from src.ocr_engine import extract_text_hybrid
from src.robust_extractor import RobustExtractor
from src.curp_validator import extract_info_from_curp

logger = logging.getLogger(__name__)

@dataclass
class Field:
    value: str
    confidence: float

class INEOCRProcessor:
    def __init__(self, debug=False):
        self.debug = debug

    def process_ine_image(self, image_path=None, raw_text=None):
        """
        Procesa una imagen de INE y retorna datos estructurados.
        
        Args:
            image_path (str): Ruta al archivo de imagen.
            raw_text (str): Texto crudo (opcional, ignorado si se pasa image_path para usar Zonal OCR).
            
        Returns:
            dict: Resultados estructurados con confianza.
        """
        # 1. Ejecutar OCR Híbrido (Zonal + Preprocessing)
        # Si se pasa image_path, extract_text_hybrid usará Zonal OCR.
        # Si solo se pasa raw_text (caso legacy), no podemos usar Zonal.
        
        strategy = "Legacy_Raw"
        confidence = 0.0
        text_to_process = raw_text or ""
        
        if image_path:
            text_to_process, confidence, strategy = extract_text_hybrid(None, image_path=image_path)
        
        # 2. Extraer Entidades usando RobustExtractor
        # CURP
        curp = RobustExtractor.find_curp_fuzzy(text_to_process)
        curp_conf = confidence if curp else 0.0
        
        # Info derivada de CURP
        sexo = ""
        fecha_nacimiento = ""
        if curp:
            info = extract_info_from_curp(curp)
            if info:
                sexo = info.get('sexo', '')
                # fecha_nacimiento = info.get('fecha_nacimiento', '') # Si estuviera disponible
        
        # TODO: Implementar extracción real de estos campos usando Zonal OCR o Regex
        # Por ahora devolvemos placeholders o búsqueda básica
        
        results = {
            'overall_confidence': confidence * 100, # Convertir a 0-100
            'strategy': strategy,
            'fields': {
                'curp': Field(curp or "", curp_conf * 100),
                'nombre': Field("", 0.0), # Pendiente: Implementar extracción de nombre
                'sexo': Field(sexo, curp_conf * 100),
                'fecha_nacimiento': Field(fecha_nacimiento, 0.0),
                'clave_elector': Field("", 0.0),
                'estado': Field("", 0.0),
                'municipio': Field("", 0.0),
                'localidad': Field("", 0.0),
                'seccion': Field("", 0.0),
                'vigencia': Field("", 0.0),
                'domicilio': Field("", 0.0)
            }
        }
        
        return results
