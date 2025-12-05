#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la configuración
"""
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN")
print("=" * 80)

# Verificar imports
try:
    from config import ROOT_FOLDER_NAME, FOLDER_ENTRADA_NAME
    print(f"\n✅ Imports exitosos")
    print(f"   ROOT_FOLDER_NAME = '{ROOT_FOLDER_NAME}'")
    print(f"   FOLDER_ENTRADA_NAME = '{FOLDER_ENTRADA_NAME}'")
except Exception as e:
    print(f"\n❌ Error al importar config: {e}")
    sys.exit(1)

# Verificar que ROOT_FOLDER_NAME sea MACROCENTRO
if ROOT_FOLDER_NAME == "MACROCENTRO":
    print(f"\n✅ ROOT_FOLDER_NAME correcto: '{ROOT_FOLDER_NAME}'")
else:
    print(f"\n❌ ROOT_FOLDER_NAME incorrecto: '{ROOT_FOLDER_NAME}' (esperado: 'MACROCENTRO')")
    sys.exit(1)

# Verificar drive_manager
try:
    from src.drive_manager import DriveManager
    import inspect
    
    # Obtener signature de initialize_folders
    sig = inspect.signature(DriveManager.initialize_folders)
    default_value = sig.parameters['root_folder_name'].default
    
    print(f"\n✅ DriveManager importado correctamente")
    print(f"   initialize_folders() default: '{default_value}'")
    
    if default_value == "MACROCENTRO":
        print(f"   ✅ Default correcto")
    else:
        print(f"   ⚠️  Default incorrecto (esperado: 'MACROCENTRO')")
        
except Exception as e:
    print(f"\n❌ Error al verificar DriveManager: {e}")
    sys.exit(1)

# Verificar main_ocr
try:
    from src.main_ocr import OCRPipeline
    print(f"\n✅ OCRPipeline importado correctamente")
except Exception as e:
    print(f"\n❌ Error al importar OCRPipeline: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO COMPLETADO - CONFIGURACIÓN CORRECTA")
print("=" * 80)
print("\nSi GitHub Actions sigue fallando, el problema es:")
print("1. La carpeta MACROCENTRO no existe en Google Drive")
print("2. La carpeta no está compartida con la Service Account")
print("3. GitHub Actions está usando código cacheado (ya corregido)")
