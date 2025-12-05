"""
Módulo de preprocesamiento avanzado de imágenes para OCR
"""
import cv2
import numpy as np
import logging
from PIL import Image

logger = logging.getLogger(__name__)


def preprocess_image(image_path):
    """
    Preprocesa una imagen para mejorar la precisión del OCR.
    
    Aplica las siguientes técnicas:
    1. Redimensionamiento (2x) para mejorar resolución
    2. Conversión a escala de grises
    3. Reducción de ruido (hologramas, reflejos)
    4. Binarización adaptativa
    5. Operaciones morfológicas para limpiar texto
    
    Args:
        image_path (str): Ruta a la imagen a procesar
    
    Returns:
        numpy.ndarray: Imagen preprocesada lista para OCR
    
    Raises:
        Exception: Si hay error al cargar o procesar la imagen
    """
    try:
        # Cargar imagen
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")
        
        logger.debug(f"Imagen cargada: {img.shape}")
        
        # 1. Redimensionar para mejorar OCR (2x)
        height, width = img.shape[:2]
        img_resized = cv2.resize(
            img, 
            (width * 2, height * 2), 
            interpolation=cv2.INTER_CUBIC
        )
        
        # 2. Convertir a escala de grises
        gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
        
        # 3. Reducir ruido (importante para hologramas de credenciales)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # 4. Binarización adaptativa (mejor que threshold simple)
        binary = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # 5. Operaciones morfológicas para limpiar texto
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        logger.debug("✅ Preprocesamiento completado")
        return morph
        
    except Exception as e:
        logger.error(f"❌ Error en preprocesamiento de imagen: {e}")
        raise


def preprocess_image_alternative(image_path):
    """
    Método alternativo de preprocesamiento (más agresivo).
    Se usa como fallback si el método principal falla.
    
    Args:
        image_path (str): Ruta a la imagen a procesar
    
    Returns:
        numpy.ndarray: Imagen preprocesada con método alternativo
    """
    try:
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Ecualización de histograma para mejorar contraste
        equalized = cv2.equalizeHist(gray)
        
        # Threshold de Otsu (automático)
        _, binary = cv2.threshold(
            equalized,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        logger.debug("✅ Preprocesamiento alternativo completado")
        return binary
        
    except Exception as e:
        logger.error(f"❌ Error en preprocesamiento alternativo: {e}")
        raise


def validate_image(image_path):
    """
    Valida que la imagen sea legible y tenga un tamaño razonable.
    
    Args:
        image_path (str): Ruta a la imagen
    
    Returns:
        tuple: (bool, str) - (es_válida, mensaje_error)
    """
    try:
        # Verificar que el archivo existe
        import os
        if not os.path.exists(image_path):
            return False, "El archivo no existe"
        
        # Intentar abrir con PIL
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Validar dimensiones mínimas (al menos 200x200)
            if width < 200 or height < 200:
                return False, f"Imagen muy pequeña: {width}x{height}"
            
            # Validar dimensiones máximas (máximo 10000x10000)
            if width > 10000 or height > 10000:
                return False, f"Imagen muy grande: {width}x{height}"
            
            # Validar formato
            if img.format not in ['JPEG', 'JPG', 'PNG', 'BMP', 'TIFF']:
                return False, f"Formato no soportado: {img.format}"
        
        return True, "OK"
        
    except Exception as e:
        return False, f"Error al validar imagen: {str(e)}"
