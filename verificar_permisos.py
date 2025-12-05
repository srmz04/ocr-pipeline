#!/usr/bin/env python3
"""
Script para verificar permisos de carpetas en Google Drive
"""
import os
import sys
import json
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🔍 VERIFICACIÓN DE PERMISOS EN GOOGLE DRIVE")
print("=" * 80)

# Verificar que existan las credenciales
creds_json = os.environ.get('GCP_CREDENTIALS')
if not creds_json:
    print("\n❌ ERROR: Variable de entorno GCP_CREDENTIALS no encontrada")
    print("\n📝 Para ejecutar este script localmente:")
    print("   1. Descarga el archivo JSON de la Service Account")
    print("   2. Ejecuta:")
    print("      export GCP_CREDENTIALS=$(cat credentials.json)")
    print("      python3 verificar_permisos.py")
    sys.exit(1)

try:
    from src.auth import get_drive_service
    from config import ROOT_FOLDER_NAME, FOLDER_ENTRADA_NAME, FOLDER_PROCESADAS_NAME, FOLDER_ERRORES_NAME, FOLDER_REVISION_NAME
    
    print(f"\n📁 Buscando carpetas...")
    print(f"   Carpeta raíz: '{ROOT_FOLDER_NAME}'")
    
    # Inicializar servicio de Drive
    service = get_drive_service()
    
    # Buscar carpeta raíz
    query = f"name='{ROOT_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, permissions, owners)'
    ).execute()
    
    items = results.get('files', [])
    
    if not items:
        print(f"\n❌ ERROR: Carpeta '{ROOT_FOLDER_NAME}' NO ENCONTRADA")
        print("\n🔍 Posibles causas:")
        print("   1. La carpeta no existe en Google Drive")
        print("   2. La carpeta no está compartida con la Service Account")
        print("   3. El nombre de la carpeta es diferente (verifica mayúsculas/acentos)")
        sys.exit(1)
    
    root_folder = items[0]
    root_id = root_folder['id']
    
    print(f"\n✅ Carpeta raíz encontrada:")
    print(f"   ID: {root_id}")
    print(f"   Nombre: {root_folder['name']}")
    
    # Obtener permisos detallados
    file_details = service.files().get(
        fileId=root_id,
        fields='id, name, permissions, owners, shared'
    ).execute()
    
    print(f"\n👥 Permisos de la carpeta '{ROOT_FOLDER_NAME}':")
    
    if 'permissions' in file_details:
        for perm in file_details['permissions']:
            perm_type = perm.get('type', 'unknown')
            role = perm.get('role', 'unknown')
            email = perm.get('emailAddress', 'N/A')
            
            if perm_type == 'user' and 'gserviceaccount.com' in email:
                print(f"   ✅ Service Account: {email}")
                print(f"      Rol: {role}")
                
                if role in ['owner', 'writer', 'editor']:
                    print(f"      ✅ Permisos suficientes")
                else:
                    print(f"      ⚠️  Permisos insuficientes (necesita 'editor' o 'writer')")
    else:
        print("   ⚠️  No se pudieron obtener permisos")
    
    # Verificar subcarpetas
    print(f"\n📂 Verificando subcarpetas...")
    
    required_folders = [
        FOLDER_ENTRADA_NAME,
        FOLDER_PROCESADAS_NAME,
        FOLDER_ERRORES_NAME,
        FOLDER_REVISION_NAME
    ]
    
    all_found = True
    
    for folder_name in required_folders:
        query = f"name='{folder_name}' and '{root_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        items = results.get('files', [])
        
        if items:
            print(f"   ✅ {folder_name} (ID: {items[0]['id']})")
        else:
            print(f"   ❌ {folder_name} NO ENCONTRADA")
            all_found = False
    
    if all_found:
        print("\n" + "=" * 80)
        print("✅ VERIFICACIÓN EXITOSA - TODOS LOS PERMISOS CORRECTOS")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("⚠️  FALTAN CARPETAS - Revisa la estructura en Drive")
        print("=" * 80)
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
