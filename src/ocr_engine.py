"""
Módulo de OCR Profesional para INE/IFE
Implementa arquitectura robusta: Preprocessing -> Zonal OCR -> Validation -> Fallback
"""
import logging
import cv2
import numpy as np
import pytesseract
import re
from PIL import Image
from config import TESSERACT_CONFIG, TESSERACT_CONFIG_SPARSE

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self):
        # Definición de Zonas (Porcentajes del tamaño de imagen)
        # Basado en análisis de INE Tipo E/G/H
        self.ZONES = {
            'CURP': {
                'y_min': 0.30, 'y_max': 0.50,  # Tercio superior-medio
                'x_min': 0.35, 'x_max': 0.95   # Lado derecho
            },
            'SEXO': {
                'y_min': 0.35, 'y_max': 0.55,
                'x_min': 0.60, 'x_max': 0.85
            }
        }
    
    def preprocess_image(self, image_path):
        """
        Pipeline de preprocesamiento profesional:
        1. Grayscale
        2. CLAHE (Mejora contraste local)
        3. Bilateral Filter (Reducción ruido preservando bordes)
        4. Upscaling 2x (Mejora resolución para Tesseract)
        """
        try:
            # 1. Cargar y Grayscale
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"No se pudo leer la imagen: {image_path}")
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # 3. Bilateral Filter (Remueve ruido del sensor del teléfono)
            # d=9, sigmaColor=75, sigmaSpace=75 son valores estándar buenos
            denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            # 4. Upscaling 2x
            height, width = denoised.shape[:2]
            upscaled = cv2.resize(denoised, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
            
            # 5. Thresholding suave (Opcional, a veces ayuda, a veces no. 
            # Tesseract hace su propio thresholding, pero Otsu puede ayudar a limpiar fondos complejos)
            # _, binary = cv2.threshold(upscaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return upscaled # Retornamos upscaled (grayscale mejorado), dejamos que Tesseract binarice
            
        except Exception as e:
            logger.error(f"❌ Error en preprocesamiento: {e}")
            return None

    def extract_zonal(self, image, zone_key):
        """Extrae texto de una zona específica definida en self.ZONES"""
        if image is None:
            return ""
            
        try:
            h, w = image.shape[:2]
            zone = self.ZONES[zone_key]
            
            y1 = int(h * zone['y_min'])
            y2 = int(h * zone['y_max'])
            x1 = int(w * zone['x_min'])
            x2 = int(w * zone['x_max'])
            
            # Crop
            roi = image[y1:y2, x1:x2]
            
            # OCR Configuration optimizada para campo único
            # PSM 6 (Block of text) o 7 (Single line)
            config = '--oem 3 --psm 6 -l spa'
            
            text = pytesseract.image_to_string(roi, config=config)
            return text.strip()
            
        except Exception as e:
            logger.error(f"❌ Error en extracción zonal ({zone_key}): {e}")
            return ""

    def validate_curp(self, text):
        """Valida si un texto parece una CURP válida y retorna score"""
        if not text:
            return None, 0
            
        # Limpieza básica
        clean = text.upper().replace(' ', '').replace('\n', '').strip()
        
        # Correcciones comunes de OCR
        clean = clean.replace('O', '0').replace('I', '1').replace('L', '1')
        
        # Buscar patrón de CURP (18 caracteres)
        # Regex: 4 letras, 6 números, 1 letra (H/M), 2 letras (Entidad), 3 letras, 1 num/letra, 1 num
        pattern = r'[A-Z]{4}\d{6}[HM][A-Z]{2}[A-Z]{3}[A-Z0-9]\d'
        
        match = re.search(pattern, clean)
        if match:
            return match.group(0), 1.0 # Confianza alta
            
        # Búsqueda difusa (si falla el exacto)
        # Busca al menos la estructura inicial: 4 letras + fecha
        fuzzy_pattern = r'[A-Z]{4}\d{6}'
        match_fuzzy = re.search(fuzzy_pattern, clean)
        if match_fuzzy:
            # Intentar extraer 18 chars desde ahí
            start = match_fuzzy.start()
            if start + 18 <= len(clean):
                candidate = clean[start:start+18]
                return candidate, 0.7 # Confianza media
        
        return None, 0.0

    def process_file(self, image_path):
        """
        Método principal: Orquesta todo el proceso
        Returns: dict con resultados
        """
        logger.info(f"🔄 Procesando {image_path} con Motor Robusto...")
        
        # 1. Preprocessing
        processed_img = self.preprocess_image(image_path)
        if processed_img is None:
            return {'error': 'Preprocessing failed'}
            
        results = {
            'curp': None,
            'confidence': 0.0,
            'strategy': 'None',
            'raw_text': ''
        }
        
        # 2. Estrategia A: Zonal OCR (La preferida)
        logger.debug("   Estrategia A: Zonal OCR")
        zonal_text = self.extract_zonal(processed_img, 'CURP')
        curp, conf = self.validate_curp(zonal_text)
        
        if curp and conf > 0.6:
            logger.info(f"   ✅ CURP encontrada por Zonal: {curp}")
            results['curp'] = curp
            results['confidence'] = conf
            results['strategy'] = 'Zonal'
            results['raw_text'] = zonal_text
            return results
            
        # 3. Estrategia B: Full Image OCR (Fallback)
        logger.debug("   Estrategia B: Full Image OCR")
        full_text = pytesseract.image_to_string(processed_img, config=TESSERACT_CONFIG)
        curp_full, conf_full = self.validate_curp(full_text)
        
        if curp_full:
            logger.info(f"   ✅ CURP encontrada por Full OCR: {curp_full}")
            results['curp'] = curp_full
            results['confidence'] = conf_full
            results['strategy'] = 'Full_Fallback'
            results['raw_text'] = full_text
            return results
            
        # 4. Estrategia C: SmartCrop (Legacy/Keyword based) - Último recurso
        # (Opcional, si queremos mantenerlo como red de seguridad)
        
        logger.warning("   ⚠️ No se encontró CURP válida")
        results['raw_text'] = full_text # Guardar lo que se leyó para debug
        results['strategy'] = 'Failed'
        
        return results

# Instancia global para uso fácil
engine = OCREngine()

def extract_text_hybrid(image, use_easyocr_fallback=False, image_path=None):
    """Wrapper para mantener compatibilidad con main_ocr.py"""
    if not image_path:
        return "", 0.0, "NoPath"
        
    result = engine.process_file(image_path)
    
    # Adaptar retorno a lo que espera main_ocr.py: (text, confidence, method)
    # Nota: main_ocr espera el texto completo en el primer argumento para buscar otros datos
    # pero aquí priorizamos la CURP. Retornaremos el raw_text para que RobustExtractor
    # (si se sigue usando fuera) pueda buscar, pero inyectaremos la CURP encontrada al inicio.
    
    final_text = result['raw_text']
    if result['curp']:
        final_text = f"CURP: {result['curp']}\n\n{final_text}"
        
    return final_text, result['confidence'], result['strategy']
