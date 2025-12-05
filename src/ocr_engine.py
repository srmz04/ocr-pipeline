"""
Módulo de OCR híbrido: Tesseract + EasyOCR
"""
import logging
import pytesseract
import easyocr
import numpy as np
from PIL import Image

from config import TESSERACT_CONFIG, EASYOCR_LANGS, EASYOCR_GPU

logger = logging.getLogger(__name__)

# Inicializar EasyOCR reader (se carga una sola vez)
_easyocr_reader = None


def get_easyocr_reader():
    """
    Obtiene o inicializa el reader de EasyOCR (singleton).
    
    Returns:
        easyocr.Reader: Reader de EasyOCR
    """
    global _easyocr_reader
    
    if _easyocr_reader is None:
        logger.info("Inicializando EasyOCR reader...")
        _easyocr_reader = easyocr.Reader(
            EASYOCR_LANGS,
            gpu=EASYOCR_GPU,
            verbose=False
        )
        logger.info("✅ EasyOCR reader inicializado")
    
    return _easyocr_reader


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


def extract_text_easyocr(image):
    """
    Extrae texto de una imagen usando EasyOCR (fallback).
    
    Args:
        image (numpy.ndarray): Imagen preprocesada
    
    Returns:
        tuple: (texto_extraído, confianza_promedio)
    """
    try:
        reader = get_easyocr_reader()
        
        # EasyOCR espera imagen en formato RGB
        if len(image.shape) == 2:  # Escala de grises
            image_rgb = np.stack([image] * 3, axis=-1)
        else:
            image_rgb = image
        
        # Extraer texto
        results = reader.readtext(image_rgb)
        
        # Combinar todo el texto
        texts = [result[1] for result in results]
        text = " ".join(texts)
        
        # Calcular confianza promedio
        confidences = [result[2] for result in results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        logger.debug(f"EasyOCR: {len(text)} caracteres extraídos, confianza: {avg_confidence:.2f}")
        
        return text, avg_confidence
        
    except Exception as e:
        logger.error(f"❌ Error en EasyOCR: {e}")
        return "", 0.0


def extract_text_hybrid(image, use_easyocr_fallback=True):
    """
    Extrae texto usando un enfoque híbrido:
    1. Intenta con Tesseract primero
    2. Si la confianza es baja (<0.5), intenta con EasyOCR
    3. Retorna el resultado con mayor confianza
    
    Args:
        image (numpy.ndarray): Imagen preprocesada
        use_easyocr_fallback (bool): Si usar EasyOCR como fallback
    
    Returns:
        tuple: (texto_extraído, confianza, método_usado)
    """
    # Intentar con Tesseract
    text_tesseract, conf_tesseract = extract_text_tesseract(image)
    
    # Si la confianza es alta, retornar directamente
    if conf_tesseract >= 0.7:
        logger.info(f"✅ Tesseract exitoso (confianza: {conf_tesseract:.2f})")
        return text_tesseract, conf_tesseract, "Tesseract"
    
    # Si la confianza es baja y se permite EasyOCR, intentar con EasyOCR
    if use_easyocr_fallback and conf_tesseract < 0.5:
        logger.info(f"⚠️ Confianza baja en Tesseract ({conf_tesseract:.2f}), intentando con EasyOCR...")
        text_easyocr, conf_easyocr = extract_text_easyocr(image)
        
        # Comparar resultados
        if conf_easyocr > conf_tesseract:
            logger.info(f"✅ EasyOCR mejor resultado (confianza: {conf_easyocr:.2f})")
            return text_easyocr, conf_easyocr, "EasyOCR"
    
    # Retornar resultado de Tesseract por defecto
    logger.info(f"✅ Usando Tesseract (confianza: {conf_tesseract:.2f})")
    return text_tesseract, conf_tesseract, "Tesseract"


def extract_text_from_file(image_path, use_easyocr_fallback=True):
    """
    Extrae texto de un archivo de imagen (wrapper completo).
    
    Args:
        image_path (str): Ruta al archivo de imagen
        use_easyocr_fallback (bool): Si usar EasyOCR como fallback
    
    Returns:
        tuple: (texto_extraído, confianza, método_usado)
    """
    try:
        # Cargar imagen con PIL
        with Image.open(image_path) as img:
            # Convertir a numpy array
            image_np = np.array(img)
            
            # Extraer texto
            return extract_text_hybrid(image_np, use_easyocr_fallback)
            
    except Exception as e:
        logger.error(f"❌ Error al extraer texto de {image_path}: {e}")
        return "", 0.0, "Error"
