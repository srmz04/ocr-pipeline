"""
Módulo de OCR usando Tesseract
Nota: EasyOCR deshabilitado para evitar error de espacio en GitHub Actions
"""
import logging
import pytesseract
import numpy as np
from PIL import Image

from config import TESSERACT_CONFIG

logger = logging.getLogger(__name__)


def extract_text_tesseract(image):
    """
    Extrae texto de una imagen usando Tesseract OCR.
    
    Args:
        image (numpy.ndarray): Imagen preprocesada
    
    Returns:
        tuple: (texto_extraído, confianza_promedio)
    """
    try:
        # Extraer texto
        text = pytesseract.image_to_string(image, config=TESSERACT_CONFIG)
        
        # Obtener datos de confianza
        data = pytesseract.image_to_data(image, config=TESSERACT_CONFIG, output_type=pytesseract.Output.DICT)
        
        # Calcular confianza promedio (solo palabras con confianza > 0)
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Normalizar confianza a 0-1
        confidence_normalized = avg_confidence / 100.0
        
        logger.debug(f"Tesseract: {len(text)} caracteres extraídos, confianza: {confidence_normalized:.2f}")
        
        return text, confidence_normalized
        
    except Exception as e:
        logger.error(f"❌ Error en Tesseract OCR: {e}")
        return "", 0.0


def extract_text_hybrid(image, use_easyocr_fallback=False):
    """
    Extrae texto usando Tesseract.
    
    Args:
        image (numpy.ndarray): Imagen preprocesada
        use_easyocr_fallback (bool): Ignorado - EasyOCR deshabilitado
    
    Returns:
        tuple: (texto_extraído, confianza, método_usado)
    """
    # Solo usar Tesseract (EasyOCR deshabilitado)
    text, confidence = extract_text_tesseract(image)
    logger.info(f"✅ Tesseract OCR (confianza: {confidence:.2f})")
    return text, confidence, "Tesseract"


def extract_text_from_file(image_path, use_easyocr_fallback=False):
    """
    Extrae texto de un archivo de imagen.
    
    Args:
        image_path (str): Ruta al archivo de imagen
        use_easyocr_fallback (bool): Ignorado - EasyOCR deshabilitado
    
    Returns:
        tuple: (texto_extraído, confianza, método_usado)
    """
    try:
        with Image.open(image_path) as img:
            image_np = np.array(img)
            return extract_text_hybrid(image_np, use_easyocr_fallback)
    except Exception as e:
        logger.error(f"❌ Error al extraer texto de {image_path}: {e}")
        return "", 0.0, "Error"
