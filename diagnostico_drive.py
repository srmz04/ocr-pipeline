"""
Script de diagnóstico para verificar acceso a carpetas de Google Drive
"""
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🔍 DIAGNÓSTICO DE ACCESO A GOOGLE DRIVE")
print("=" * 80)

# 1. Verificar variables de entorno
print("\n1️⃣ Verificando variables de entorno...")
gcp_creds = os.environ.get('GCP_CREDENTIALS')
if gcp_creds:
    try:
        creds_dict = json.loads(gcp_creds)
        email = creds_dict.get('client_email', 'N/A')
        print(f"   ✅ GCP_CREDENTIALS encontradas")
        print(f"   📧 Service Account: {email}")
    except:
        print("   ❌ Error al parsear GCP_CREDENTIALS")
        sys.exit(1)
else:
    print("   ❌ GCP_CREDENTIALS no encontradas")
    sys.exit(1)

# 2. Verificar configuración
print("\n2️⃣ Verificando configuración...")
try:
    from config import ROOT_FOLDER_NAME, FOLDER_ENTRADA_NAME
    print(f"   ✅ ROOT_FOLDER_NAME = '{ROOT_FOLDER_NAME}'")
    print(f"   ✅ FOLDER_ENTRADA_NAME = '{FOLDER_ENTRADA_NAME}'")
except Exception as e:
    print(f"   ❌ Error al importar config: {e}")
    sys.exit(1)

# 3. Conectar a Drive
print("\n3️⃣ Conectando a Google Drive...")
try:
    from src.auth import get_drive_service
    service = get_drive_service()
    print("   ✅ Servicio de Drive inicializado")
except Exception as e:
    print(f"   ❌ Error al conectar: {e}")
    sys.exit(1)

# 4. Buscar carpetas
print(f"\n4️⃣ Buscando carpeta '{ROOT_FOLDER_NAME}'...")
try:
    # Buscar SIN filtro de padres primero
    query = f"name='{ROOT_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, owners, shared, parents, permissions)',
        pageSize=100
    ).execute()
    
    items = results.get('files', [])
    
    if not items:
        print(f"   ❌ Carpeta '{ROOT_FOLDER_NAME}' NO encontrada")
        print("\n5️⃣ Buscando TODAS las carpetas compartidas...")
        
        # Listar todas las carpetas compartidas
        query_all = "mimeType='application/vnd.google-apps.folder' and trashed=false"
        results_all = service.files().list(
            q=query_all,
            spaces='drive',
            fields='files(id, name)',
            pageSize=50
        ).execute()
        
        all_folders = results_all.get('files', [])
        print(f"\n   📁 Carpetas encontradas ({len(all_folders)}):")
        for folder in all_folders[:20]:  # Mostrar máximo 20
            print(f"      - {folder['name']} (ID: {folder['id']})")
        
        if len(all_folders) > 20:
            print(f"      ... y {len(all_folders) - 20} más")
        
        sys.exit(1)
    
    print(f"   ✅ Encontradas {len(items)} carpeta(s) con ese nombre")
    
    for i, item in enumerate(items, 1):
        print(f"\n   📁 Carpeta #{i}:")
        print(f"      ID: {item['id']}")
        print(f"      Nombre: {item['name']}")
        print(f"      Compartida: {item.get('shared', False)}")
        
        if 'owners' in item:
            owners = [o.get('emailAddress', 'N/A') for o in item['owners']]
            print(f"      Propietarios: {', '.join(owners)}")
        
        if 'permissions' in item:
            print(f"      Permisos: {len(item['permissions'])} usuarios")
            for perm in item['permissions'][:5]:
                email = perm.get('emailAddress', perm.get('id', 'N/A'))
                role = perm.get('role', 'N/A')
                print(f"         - {email}: {role}")
        
        # Buscar subcarpetas
        print(f"\n   📂 Buscando subcarpetas en '{item['name']}'...")
        sub_query = f"'{item['id']}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        sub_results = service.files().list(
            q=sub_query,
            fields='files(id, name)',
            pageSize=10
        ).execute()
        
        sub_folders = sub_results.get('files', [])
        if sub_folders:
            print(f"      Subcarpetas encontradas: {len(sub_folders)}")
            for sf in sub_folders:
                print(f"         - {sf['name']}")
        else:
            print(f"      ⚠️  No se encontraron subcarpetas")

except Exception as e:
    print(f"   ❌ Error durante búsqueda: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 80)
