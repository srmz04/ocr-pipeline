"""
Módulo de validación de CURP con cálculo de dígito verificador
"""
import re
import logging
from datetime import datetime

from config import CURP_REGEX

logger = logging.getLogger(__name__)


def extract_curp_from_text(text):
    """
    Extrae la CURP de un texto usando expresión regular.
    
    Args:
        text (str): Texto donde buscar la CURP
    
    Returns:
        list: Lista de CURPs encontradas (puede estar vacía)
    """
    if not text:
        return []
    
    # Limpiar texto: convertir a mayúsculas y eliminar espacios extra
    text_clean = text.upper().strip()
    
    # Buscar todas las coincidencias
    matches = re.findall(CURP_REGEX, text_clean)
    
    if matches:
        logger.debug(f"CURPs encontradas: {matches}")
    
    return matches


def validate_curp_format(curp):
    """
    Valida el formato básico de una CURP (18 caracteres).
    
    Args:
        curp (str): CURP a validar
    
    Returns:
        bool: True si el formato es válido
    """
    if not curp or len(curp) != 18:
        return False
    
    return bool(re.match(CURP_REGEX, curp.upper()))


def validate_curp_date(curp):
    """
    Valida que la fecha en la CURP sea válida.
    
    La CURP contiene la fecha de nacimiento en posiciones 4-9 (YYMMDD).
    
    Args:
        curp (str): CURP a validar
    
    Returns:
        tuple: (bool, str) - (es_válida, mensaje)
    """
    if len(curp) < 10:
        return False, "CURP muy corta"
    
    try:
        # Extraer año, mes, día
        year_str = curp[4:6]
        month_str = curp[6:8]
        day_str = curp[8:10]
        
        year = int(year_str)
        month = int(month_str)
        day = int(day_str)
        
        # Determinar siglo (asumimos que >30 es 1900, <=30 es 2000)
        if year > 30:
            full_year = 1900 + year
        else:
            full_year = 2000 + year
        
        # Validar que la fecha sea válida
        datetime(full_year, month, day)
        
        return True, "Fecha válida"
        
    except ValueError as e:
        return False, f"Fecha inválida: {e}"


def calculate_curp_check_digit(curp):
    """
    Calcula el dígito verificador de una CURP (posición 18).
    
    Algoritmo oficial de la CURP:
    1. Asignar valores numéricos a cada carácter (0-9 = valor, A-Z = 10-35)
    2. Multiplicar cada valor por su posición (18, 17, 16, ...)
    3. Sumar todos los productos
    4. Calcular módulo 10
    5. Restar de 10 (si es 10, el dígito es 0)
    
    Args:
        curp (str): CURP de 17 caracteres (sin dígito verificador)
    
    Returns:
        str: Dígito verificador calculado (0-9)
    """
    if len(curp) < 17:
        return None
    
    # Diccionario de valores para caracteres
    char_values = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
        '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14,
        'F': 15, 'G': 16, 'H': 17, 'I': 18, 'J': 19,
        'K': 20, 'L': 21, 'M': 22, 'N': 23, 'Ñ': 24,
        'O': 25, 'P': 26, 'Q': 27, 'R': 28, 'S': 29,
        'T': 30, 'U': 31, 'V': 32, 'W': 33, 'X': 34,
        'Y': 35, 'Z': 36
    }
    
    try:
        # Tomar solo los primeros 17 caracteres
        curp_17 = curp[:17].upper()
        
        # Calcular suma ponderada
        total = 0
        for i, char in enumerate(curp_17):
            position = 18 - i  # Posición descendente
            value = char_values.get(char, 0)
            total += value * position
        
        # Calcular dígito verificador
        mod = total % 10
        check_digit = (10 - mod) % 10
        
        return str(check_digit)
        
    except Exception as e:
        logger.error(f"Error al calcular dígito verificador: {e}")
        return None


def validate_curp_complete(curp):
    """
    Validación completa de una CURP:
    1. Formato (18 caracteres, regex)
    2. Fecha válida
    3. Dígito verificador correcto
    
    Args:
        curp (str): CURP a validar
    
    Returns:
        tuple: (bool, float, str) - (es_válida, confianza, mensaje)
    """
    if not curp:
        return False, 0.0, "CURP vacía"
    
    curp = curp.upper().strip()
    
    # 1. Validar formato
    if not validate_curp_format(curp):
        return False, 0.0, "Formato inválido"
    
    # 2. Validar fecha
    date_valid, date_msg = validate_curp_date(curp)
    if not date_valid:
        return False, 0.3, f"Fecha inválida: {date_msg}"
    
    # 3. Validar dígito verificador
    calculated_digit = calculate_curp_check_digit(curp[:17])
    actual_digit = curp[17]
    
    if calculated_digit is None:
        return False, 0.5, "No se pudo calcular dígito verificador"
    
    if calculated_digit != actual_digit:
        return False, 0.6, f"Dígito verificador incorrecto (esperado: {calculated_digit}, encontrado: {actual_digit})"
    
    # ✅ CURP completamente válida
    return True, 1.0, "CURP válida"


def extract_info_from_curp(curp):
    """
    Extrae información de una CURP válida.
    
    Args:
        curp (str): CURP válida
    
    Returns:
        dict: Información extraída (sexo, fecha_nacimiento, estado)
    """
    if not validate_curp_format(curp):
        return None
    
    curp = curp.upper()
    
    # Extraer sexo (posición 10: H=Hombre, M=Mujer)
    sexo = "MASCULINO" if curp[10] == 'H' else "FEMENINO"
    
    # Extraer fecha de nacimiento
    year_str = curp[4:6]
    month_str = curp[6:8]
    day_str = curp[8:10]
    
    year = int(year_str)
    if year > 30:
        full_year = 1900 + year
    else:
        full_year = 2000 + year
    
    fecha_nacimiento = f"{day_str}/{month_str}/{full_year}"
    
    # Extraer estado (posiciones 11-12)
    estado_code = curp[11:13]
    
    return {
        'sexo': sexo,
        'fecha_nacimiento': fecha_nacimiento,
        'estado_code': estado_code,
        'curp': curp
    }
