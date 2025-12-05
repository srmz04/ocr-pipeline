"""
Script para probar OCR localmente y diagnosticar problemas
"""
import sys
from pathlib import Path
import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from src.image_processor import preprocess_image, validate_image
from src.ocr_engine import extract_text_tesseract
from src.curp_validator import extract_curp_from_text, validate_curp_complete

print("=" * 80)
print("🔍 PRUEBA DE OCR LOCAL")
print("=" * 80)

# Cargar imagen
image_path = "ine r"
print(f"\n📁 Cargando: {image_path}")

# Validar
is_valid, msg = validate_image(image_path)
print(f"Validación: {msg}")

if not is_valid:
    sys.exit(1)

# Analizar imagen original
img_original = cv2.imread(image_path)
print(f"\n📊 Análisis de imagen original:")
print(f"   Dimensiones: {img_original.shape[1]}x{img_original.shape[0]}")
gray = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
print(f"   Brillo promedio: {np.mean(gray):.1f}/255")
print(f"   Contraste (std): {np.std(gray):.1f}")

# Preprocesar
print(f"\n🔧 Preprocesando imagen...")
img_processed = preprocess_image(image_path)

# Analizar procesada
print(f"\n📊 Análisis de imagen procesada:")
print(f"   Dimensiones: {img_processed.shape[1]}x{img_processed.shape[0]}")
print(f"   Brillo promedio: {np.mean(img_processed):.1f}/255")
print(f"   Contraste (std): {np.std(img_processed):.1f}")

# Guardar imagen procesada para inspección
cv2.imwrite("ine_r_procesada.png", img_processed)
print(f"\n💾 Imagen procesada guardada: ine_r_procesada.png")

# Extraer texto
print(f"\n🔍 Extrayendo texto con Tesseract...")
text, confidence = extract_text_tesseract(img_processed)

print(f"\n📝 Texto extraído ({len(text)} caracteres, confianza {confidence:.2f}):")
print("─" * 80)
print(text[:500] if len(text) > 500 else text)
if len(text) > 500:
    print(f"... (truncado, {len(text)-500} caracteres más)")
print("─" * 80)

# Buscar CURP
print(f"\n🔎 Buscando CURP...")
curps = extract_curp_from_text(text)

if curps:
    print(f"✅ Se encontraron {len(curps)} CURP(s):")
    for curp in curps:
        is_valid, conf, msg = validate_curp_complete(curp)
        status = "✅" if is_valid else "❌"
        print(f"   {status} {curp} - {msg} (confianza: {conf:.2f})")
else:
    print("❌ No se encontraron CURPs en el texto")
    
    # Intentar búsqueda más flexible
    print("\n🔍 Buscando patrones similares a CURP...")
    import re
    
    # Buscar secuencias que se parezcan a CURP (más flexible)
    pattern_flexible = r'[A-Z]{3,4}[A-Z0-9]{10,14}'
    matches = re.findall(pattern_flexible, text)
    
    if matches:
        print(f"   Patrones encontrados (posibles CURPs mal formateadas):")
        for match in matches[:10]:  # Mostrar máximo 10
            print(f"      - {match} ({len(match)} caracteres)")
    else:
        print("   No se encontraron patrones similares")

print("\n" + "=" * 80)
print("✅ PRUEBA COMPLETADA")
print("=" * 80)
