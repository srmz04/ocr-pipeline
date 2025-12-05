# 🔍 Análisis del Problema de OCR - INE

## 📊 Caso Analizado

**Archivo**: `ine r` (482x614 pixels PNG)  
**Resultado**: ❌ SIN_CURP con confianza 0.42 (42%)

### Texto Extraído (fragmentos relevantes):

```
INSTITUTO NACIONAL ELECTORAL
RAMIREZ SOTO SILVANO
04/02/1985
CLAVE DE ELECTOR: RMSTSLESO20410H300
CURP: RASSOG0204HDGMTLOS
```

---

## 🐛 Problemas Identificados

### 1. **CURP Fragmentada** ⚠️
- El OCR **SÍ leyó la CURP**: `RASSOG0204HDGMTLOS`
- Pero está **incompleta** (17 caracteres en lugar de 18)
- El regex actual requiere **exactamente 18 caracteres**
- Formato esperado: `[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[A-Z0-9][0-9]`

### 2. **Confianza Baja (42%)** 📉
Causas probables:
- **Resolución baja** (482x614 es pequeño para una credencial)
- **Hologramas o reflejos** en la foto
- **Ángulo inclinado** de la foto
- **Iluminación desigual**
- **Textura del plástico** interfiere con OCR

### 3. **Texto Desord enado** 🌀
- Muchos espacios y saltos de línea
- Caracteres especiales mezclados
- Tesseract confundido por el diseño complejo del INE

---

## ✅ Soluciones Propuestas

### Solución 1: **Extracción más flexible de CURP** (RÁPIDO)

Modificar `curp_validator.py` para:

1. **Buscar CURP con longitud variable** (17-19 caracteres)
2. **Limpiar espacios** dentro del texto de CURP
3. **Intentar reparar** CURPs incompletas

```python
# Ejemplo de mejora:
def extract_curp_flexible(text):
    # Remover saltos de línea y espacios extra
    clean_text = ' '.join(text.split())
    
    # Buscar patrón flexible (17-19 caracteres)
    pattern = r'[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]{1,3}'
    matches = re.findall(pattern, clean_text)
    
    # Filtrar solo las de 18 caracteres
    return [m for m in matches if len(m) == 18]
```

**Ventaja**: ✅ Resuelve el caso actual sin cambios mayores  
**Desventaja**: ⚠️ No mejora la calidad del OCR base

---

### Solución 2: **Mejorar Preprocesamiento** (MEDIO)

Agregar técnicas específicas para credenciales:

1. **Detección de bordes** para enderezar la foto
2. **Aumento de contraste** más agresivo
3. **Filtrado de hologramas** (eliminar reflejos brillantes)
4. **Upscaling** de la imagen (x2 o x3)
5. **Binarización local** en lugar de global

```python
# Mejoras en image_processor.py:
- Detectar y rotar credencial si está inclinada
- Aplicar filtro de desenfoque selectivo
- Aumentar resolución artificialmente
- Aplicar sharpening en zonas de texto
```

**Ventaja**: ✅ Mejora resultados para TODAS las imágenes  
**Desventaja**: ⚠️ Más complejo, requiere ajuste de parámetros

---

### Solución 3: **Múltiples Pasadas de OCR** (AVANZADO)

Ejecutar Tesseract con **diferentes configuraciones**:

1. Pasada 1: OCR normal (actual)
2. Pasada 2: Solo zona de CURP (si se detecta)
3. Pasada 3: Modo "sparse text" para CURP
4. Combinar resultados

```python
# Configuraciones de Tesseract a probar:
configs = [
    '--psm 6',  # Bloque uniforme (actual)
    '--psm 11', # Texto disperso
    '--psm 13', # Línea de texto única
]
```

**Ventaja**: ✅ Mayor probabilidad de capturar CURP  
**Desventaja**: ⚠️ 3x más lento

---

## 🎯 Recomendación Inmediata

### Opción A: **Quick Fix** (5 minutos)

Modificar el regex en `curp_validator.py` para aceptar CURPs con espacios:

```python
# Antes:
CURP_REGEX = r'\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b'

# Después:
CURP_REGEX = r'[A-Z]{4}\s?\d{6}\s?[HM]\s?[A-Z]{5}\s?[A-Z0-9]\s?\d'

# En extract_curp_from_text:
def extract_curp_from_text(text):
    # Limpiar texto
    text_clean = text.replace('\n', ' ').upper()
    matches = re.findall(CURP_REGEX, text_clean)
    # Remover espacios de las coincidencias
    return [''.join(m.split()) for m in matches if len(''.join(m.split())) == 18]
```

**Resultado esperado**: Detectaría `RASSOG0204HDGMTLOS` si tuviera 18 caracteres

---

### Opción B: **Mejor Solución** (30 minutos)

Implementar **extracción específica de CURP**:

1. Buscar la palabra "CURP" en el texto
2. Extraer los 18 caracteres siguientes
3. Validar que cumplan el formato
4. Si no funciona, usar regex global como fallback

```python
def extract_curp_smart(text):
    # Buscar "CURP:" o "CURP " en el texto
    match = re.search(r'CURP[\s:]+([A-Z0-9\s]{16,24})', text)
    if match:
        curp_candidate = ''.join(match.group(1).split())[:18]
        if len(curp_candidate) == 18:
            return [curp_candidate]
    
    # Fallback: regex normal
    return extract_curp_from_text(text)
```

---

## 📸 Recomendaciones para Captura de Fotos

Para mejorar en el futuro:

1. ✅ **Resolución mínima**: 1200x800 pixels
2. ✅ **Iluminación uniforme**: Sin sombras ni reflejos
3. ✅ **Ángulo recto**: Credencial de frente, no inclinada
4. ✅ **Fondo contraste**: Poner credencial sobre superficie oscura
5. ✅ **Enfocar la zona de CURP**: Asegurar que esté nítida

---

## 🚀 Siguiente Paso

¿Qué solución quieres implementar primero?

- **A) Quick Fix del regex** (5 min) - Ayuda de inmediato
- **B) Extracción inteligente** (30 min) - Solución más robusta
- **C) Mejorar preprocesamiento** (1-2 horas) - Solución completa

Puedo implementar cualquiera de estas opciones ahora.
