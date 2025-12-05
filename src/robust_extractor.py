import re
import logging

logger = logging.getLogger(__name__)

class RobustExtractor:
    """
    Extractor robusto para CURP y otros datos, tolerante a errores de OCR.
    """

    # Mapeo de correcciones comunes OCR (letras a números y viceversa)
    COMMON_SUBS = {
        '0': 'O', '1': 'I', '2': 'Z', '5': 'S', '8': 'B', 
        '$': 'S', '(': 'C', '|': 'I', '/': 'I'
    }
    
    # Inverso para cuando esperamos números
    NUM_SUBS = {v: k for k, v in COMMON_SUBS.items()}
    NUM_SUBS.update({'O': '0', 'I': '1', 'Z': '2', 'S': '5', 'B': '8', 'G': '6', 'T': '7'})

    @staticmethod
    def clean_text(text):
        """Limpia el texto básico"""
        if not text:
            return ""
        # Reemplazar saltos de línea con espacios
        text = text.replace('\n', ' ').replace('\r', ' ')
        # Eliminar caracteres especiales raros pero mantener alfanuméricos
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text.upper()

    @staticmethod
    def find_curp_fuzzy(text):
        """
        Busca patrones que parezcan una CURP incluso con errores.
        Prioridad:
        1. Búsqueda por palabras clave (CURP, ELECTOR)
        2. Búsqueda por patrón (regex fuzzy)
        """
        if not text:
            return None
            
        # 1. Búsqueda por palabras clave (Más confiable si existe)
        keyword_curp = RobustExtractor.find_curp_by_keywords(text)
        if keyword_curp:
            return keyword_curp

        # 2. Normalizar para búsqueda profunda
        text_nospaces = re.sub(r'\s+', '', text.upper())
        
        # Buscamos ventanas de 18 caracteres
        best_curp = None
        best_score = 0
        
        for i in range(len(text_nospaces) - 17):
            candidate = text_nospaces[i:i+18]
            score, corrected = RobustExtractor.score_curp_candidate(candidate)
            
            if score > 0.8 and score > best_score:
                best_score = score
                best_curp = corrected
                
        return best_curp

    @staticmethod
    def find_curp_by_keywords(text):
        """Busca CURP cerca de palabras clave"""
        text_upper = text.upper()
        keywords = ['CURP', 'CLAVE', 'ELECTOR']
        
        for keyword in keywords:
            if keyword in text_upper:
                # Buscar en los siguientes 30 caracteres
                idx = text_upper.find(keyword)
                context = text_upper[idx:idx+50] # Tomar contexto
                
                # Limpiar contexto (quitar la keyword y chars raros)
                context_clean = re.sub(r'[^A-Z0-9]', '', context)
                
                # Buscar patrón de 18 chars en el contexto limpio
                for i in range(len(context_clean) - 17):
                    candidate = context_clean[i:i+18]
                    score, corrected = RobustExtractor.score_curp_candidate(candidate)
                    if score > 0.85: # Mayor exigencia para keyword match
                        logger.info(f"✅ CURP encontrada por keyword '{keyword}': {corrected}")
                        return corrected
        return None

    @staticmethod
    def score_curp_candidate(candidate):
        """
        Evalúa si un string de 18 chars parece una CURP y trata de corregirlo.
        Retorna (score, corrected_curp)
        """
        score = 0
        corrected = list(candidate)
        
        # Pesos
        weights = [
            1, 1, 1, 1,       # 4 letras iniciales
            2, 2, 2, 2, 2, 2, # 6 dígitos fecha
            3,                # Sexo (H/M)
            1, 1,             # Estado
            1, 1, 1,          # Consonantes
            1,                # Homoclave
            1                 # Dígito verificador
        ]
        
        max_score = sum(weights)
        current_score = 0
        
        # 1. Primeras 4 letras
        for i in range(4):
            if candidate[i].isalpha():
                current_score += weights[i]
            elif candidate[i] in RobustExtractor.COMMON_SUBS:
                # Corregir número a letra
                corrected[i] = RobustExtractor.COMMON_SUBS[candidate[i]]
                current_score += weights[i] * 0.8 # Penalización leve
                
        # 2. Fecha (6 dígitos)
        for i in range(4, 10):
            if candidate[i].isdigit():
                current_score += weights[i]
            elif candidate[i] in RobustExtractor.NUM_SUBS:
                # Corregir letra a número
                corrected[i] = RobustExtractor.NUM_SUBS[candidate[i]]
                current_score += weights[i] * 0.8
                
        # 3. Sexo (H/M)
        if candidate[10] in ['H', 'M']:
            current_score += weights[10]
        elif candidate[10] == 'N': # Error común H->N o M->N
             current_score += weights[10] * 0.5
             
        # 4. Estado (2 letras)
        # (Simplificado, solo checar si son letras)
        for i in range(11, 13):
            if candidate[i].isalpha():
                current_score += weights[i]
                
        # 5. Consonantes (3 letras)
        for i in range(13, 16):
            if candidate[i].isalpha():
                current_score += weights[i]

        # 6. Homoclave y dígito (alfanum + num)
        if candidate[16].isalnum():
            current_score += weights[16]
            
        if candidate[17].isdigit():
            current_score += weights[17]
        elif candidate[17] in RobustExtractor.NUM_SUBS:
            corrected[17] = RobustExtractor.NUM_SUBS[candidate[17]]
            current_score += weights[17] * 0.8

        final_score = current_score / max_score
        return final_score, "".join(corrected)

    @staticmethod
    def extract_from_ine_text(text):
        """Intenta extraer datos específicos de patrones INE"""
        # Buscar patrón "CLAVE DE ELECTOR"
        # A veces el OCR lo lee como "CLAVE DE ELECTOR", "CLAVE ELECTOR", "ELECTOR", etc.
        
        # Normalizar para búsqueda
        text_upper = text.upper()
        
        # Buscar CURP explícita
        curp = RobustExtractor.find_curp_fuzzy(text)
        if curp:
            return {'curp': curp, 'source': 'fuzzy_search'}
            
        return None
