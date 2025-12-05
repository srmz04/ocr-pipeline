"""
Script de prueba local para validar el pipeline OCR
NOTA: Este script requiere que configures las credenciales localmente
"""
import os
import sys
import json
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 80)
print("🧪 SCRIPT DE PRUEBA - OCR Pipeline")
print("=" * 80)

# Verificar que existe el archivo de credenciales
credentials_path = Path(__file__).parent.parent / "credentials.json"

if not credentials_path.exists():
    print("\n❌ ERROR: No se encontró el archivo 'credentials.json'")
    print("\n📝 Para ejecutar este script localmente:")
    print("   1. Descarga el archivo JSON de la Service Account de GCP")
    print("   2. Guárdalo como 'credentials.json' en la raíz del proyecto")
    print("   3. Asegúrate de que esté en .gitignore (ya está configurado)")
    print("\n⚠️  NUNCA subas credentials.json a GitHub")
    sys.exit(1)

# Cargar credenciales
with open(credentials_path, 'r') as f:
    credentials_json = f.read()

# Configurar variable de entorno
os.environ['GCP_CREDENTIALS'] = credentials_json

# Configurar nombre del spreadsheet
spreadsheet_name = input("\n📊 Nombre del Google Spreadsheet (default: REGISTRO_MASTER): ").strip()
if not spreadsheet_name:
    spreadsheet_name = "REGISTRO_MASTER"

os.environ['SPREADSHEET_NAME'] = spreadsheet_name

print(f"\n✅ Credenciales cargadas")
print(f"✅ Spreadsheet: {spreadsheet_name}")

# Preguntar si continuar
print("\n" + "=" * 80)
print("⚠️  ADVERTENCIA: Este script procesará imágenes reales en tu Google Drive")
print("=" * 80)
response = input("\n¿Deseas continuar? (s/n): ").strip().lower()

if response != 's':
    print("\n❌ Prueba cancelada")
    sys.exit(0)

# Importar y ejecutar el pipeline
print("\n🚀 Iniciando pipeline OCR...\n")

try:
    from src.main_ocr import main
    main()
except Exception as e:
    print(f"\n❌ Error al ejecutar pipeline: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
