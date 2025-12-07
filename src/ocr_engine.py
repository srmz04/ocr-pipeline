"""
Módulo de OCR mejorado usando Tesseract con múltiples estrategias
"""
import logging
import pytesseract
import numpy as np
import cv2
from PIL import Image

from config import TESSERACT_CONFIG, TESSERACT_CONFIG_SPARSE

logger = logging.getLogger(__name__)


def extract_text_tesseract(image, config=TESSERACT_CONFIG):
    """
    Extrae texto de una imagen usando Tesseract OCR.
    
    Args:
        image (numpy.ndarray): Imagen preprocesada
        config (str): Configuración de Tesseract
    
    Returns:
        tuple: (texto_extraído, confianza_promedio)
    """
    try:
        # Extraer texto
        text = pytesseract.image_to_string(image, config=config)
        
        # Obtener datos de confianza
        data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
        
        # Calcular confianza promedio (solo palabras con confianza > 0)
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Normalizar confianza a 0-1
        confidence_normalized = avg_confidence / 100.0
        
        return text.strip(), confidence_normalized
        
    except Exception as e:
        logger.error(f"❌ Error en Tesseract OCR: {e}")
        return "", 0.0


def preprocess_minimal(image_path):
    """Preprocesamiento mínimo - solo escala de grises"""
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray


def preprocess_contrast(image_path):
    """Preprocesamiento con mejora de contraste"""
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return enhanced


def preprocess_denoise(image_path):
    """Preprocesamiento con reducción de ruido"""
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    return denoised


def preprocess_resize(image_path):
    """Preprocesamiento con escalado 2x"""
    img = cv2.imread(image_path)
    if img is None:
        return None
    height, width = img.shape[:2]
    img_resized = cv2.resize(img, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    return gray


def extract_text_smart_crop(image_path):
    """
    Estrategia avanzada: Busca la palabra 'CURP' o 'ELECTOR' y hace OCR
    específico en la región a la derecha (donde debería estar la clave).
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return ""
            
        # Resize 2x para mejor detección
        height, width = img.shape[:2]
        img = cv2.resize(img, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Binarizar para encontrar layout
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Obtener datos de posición de palabras
        data = pytesseract.image_to_data(binary, output_type=pytesseract.Output.DICT)
        
        found_text = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            text = data['text'][i].upper().strip()
            if 'CURP' in text or 'ELECTOR' in text:
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                
                # Definir ROI a la derecha
                # Asumimos que la CURP está a la derecha de la etiqueta
                roi_x = x + w + 5
                roi_y = y - 5 # Un poco más arriba para margen
                roi_w = int(width * 0.6) # Ancho generoso
                roi_h = h + 15 # Un poco más alto
                
                # Validar límites
                h_img, w_img = binary.shape
                roi_x = max(0, min(roi_x, w_img - 1))
                roi_y = max(0, min(roi_y, h_img - 1))
                roi_w = min(roi_w, w_img - roi_x)
                roi_h = min(roi_h, h_img - roi_y)
                
                if roi_w > 10 and roi_h > 5:
                    roi = binary[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
                    
                    # OCR específico de línea única (PSM 7)
                    config_roi = '--oem 3 --psm 7 -l spa'
                    roi_text = pytesseract.image_to_string(roi, config=config_roi).strip()
                    
                    if len(roi_text) > 5:
                        logger.info(f"   SmartCrop encontró: '{roi_text}' cerca de '{text}'")
                        found_text.append(roi_text)
        
        return "\n".join(found_text)
        
    except Exception as e:
        logger.error(f"⚠️ Error en SmartCrop: {e}")
        return ""


def extract_text_hybrid(image, use_easyocr_fallback=False, image_path=None):
    """
    Extrae texto usando múltiples estrategias de OCR.
    
    Intenta varias combinaciones de preprocesamiento y configuración
    para obtener el mejor resultado posible.
    
    Args:
        image (numpy.ndarray): Imagen preprocesada (legacy)
        use_easyocr_fallback (bool): Ignorado
        image_path (str): Ruta al archivo original (para multipass)
    
    Returns:
        tuple: (texto_extraído, confianza, método_usado)
    """
    best_text = ""
    best_confidence = 0.0
    best_method = "None"
    
    strategies = []
    
    if image_path:
        # Estrategia 1: Imagen original con escala de grises (mínimo procesamiento)
        strategies.append(("Minimal+PSM3", preprocess_minimal(image_path), TESSERACT_CONFIG))
        
        # Estrategia 2: Imagen original con PSM 11 (sparse text - mejor para tarjetas)
        strategies.append(("Minimal+PSM11", preprocess_minimal(image_path), TESSERACT_CONFIG_SPARSE))
        
        # Estrategia 3: Con mejora de contraste
        strategies.append(("CLAHE+PSM3", preprocess_contrast(image_path), TESSERACT_CONFIG))
        
        # Estrategia 4: Con reducción de ruido
        strategies.append(("Denoise+PSM11", preprocess_denoise(image_path), TESSERACT_CONFIG_SPARSE))
        
        # Estrategia 5: Escalado 2x
        strategies.append(("Resize2x+PSM3", preprocess_resize(image_path), TESSERACT_CONFIG))
    else:
        # Fallback: Usar la imagen ya procesada
        strategies.append(("Legacy", image, TESSERACT_CONFIG))
    
    for method_name, processed_img, config in strategies:
        if processed_img is None:
            continue
            
        text, confidence = extract_text_tesseract(processed_img, config)
        
        logger.debug(f"   {method_name}: {len(text)} chars, conf={confidence:.2f}")
        
        # Usar el resultado con más texto (si la confianza es razonable)
        # o el de mayor confianza si todos tienen poco texto
        if len(text) > len(best_text) and confidence > 0.2:
            best_text = text
            best_confidence = confidence
            best_method = method_name
        elif confidence > best_confidence and len(text) > 100:
            best_text = text
            best_confidence = confidence
            best_method = method_name
    
    # --- SMART CROP STEP ---
    # Intentar extraer CURP con recorte inteligente y agregarlo al texto final
    if image_path:
        smart_crop_text = extract_text_smart_crop(image_path)
        if smart_crop_text:
            best_text += f"\n\n--- SMART CROP RESULTS ---\n{smart_crop_text}"
            logger.info(f"✅ SmartCrop agregó {len(smart_crop_text)} chars al resultado")
    
    logger.info(f"✅ Best OCR: {best_method} (conf={best_confidence:.2f}, {len(best_text)} chars)")
    return best_text, best_confidence, best_method


def extract_text_from_file(image_path, use_easyocr_fallback=False):
    """
    Extrae texto de un archivo de imagen usando múltiples estrategias.
    
    Args:
        image_path (str): Ruta al archivo de imagen
        use_easyocr_fallback (bool): Ignorado
    
    Returns:
        tuple: (texto_extraído, confianza, método_usado)
    """
    try:
        with Image.open(image_path) as img:
            image_np = np.array(img)
            return extract_text_hybrid(image_np, use_easyocr_fallback, image_path=image_path)
    except Exception as e:
        logger.error(f"❌ Error al extraer texto de {image_path}: {e}")
        return "", 0.0, "Error"
