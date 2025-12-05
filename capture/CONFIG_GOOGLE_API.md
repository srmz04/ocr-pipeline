# 🔧 Configuración de Google APIs

## 📋 Resumen de Progreso

### ✅ Completado:
- Frontend base v1.0 (cámara, validación, UX)
- Módulo `google-api.js` (OAuth2 client)
- `uploader.js` actualizado con Drive/Sheets APIs
- `config.js` preparado para credenciales

### ⚠️ Pendiente:
- Obtener credenciales de Google Cloud
- Configurar OAuth2
- Probar integración completa

---

## 🔑 Paso 1: Obtener Credenciales de Google Cloud

### A. API Key

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto (ocr-vacunacion)
3. **APIs & Services** → **Credentials**
4. Click **+ CREATE CREDENTIALS** → **API Key**
5. Copia el API Key generado
6. **IMPORTANTE**: Restringir el API Key:
   - Application restrictions: HTTP referers
   - Website restrictions: `http://localhost:9000`, `https://srmz04.github.io/*`
   - API restrictions: Google Drive API, Google Sheets API

### B. OAuth 2.0 Client ID

1. En la misma página de Credentials
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Application type: **Web application**
4. Name: `OCR Capture Frontend`
5. Authorized JavaScript origins:
   ```
   http://localhost:9000
   https://srmz04.github.io
   ```
6. Authorized redirect URIs: (dejar vacío para ahora)
7. Click **CREATE**
8. Copia el **Client ID** (formato: `xxxxx.apps.googleusercontent.com`)

---

## 📝 Paso 2: Configurar credenciales en el código

Edita `capture/config.js`:

```javascript
const CONFIG = {
    // Google API - CONFIGURAR ESTAS CREDENCIALES
    GOOGLE_API_KEY: 'TU_API_KEY_AQUI',                     // Del paso 1.A
    GOOGLE_CLIENT_ID: 'TU_CLIENT_ID_AQUI.apps.googleusercontent.com',  // Del paso 1.B
    DRIVE_FOLDER_ID: '1pIqnbmu3SGwZkv6ZL6OzUbNzJ4UHYCq0',    // ✅ Ya configurado
    SPREADSHEET_ID: 'TU_SPREADSHEET_ID_AQUI',               // Del Google Sheet
    
    // ... resto de config
};
```

### ¿Dónde encontrar SPREADSHEET_ID?

De la URL de tu Google Sheet:
```
https://docs.google.com/spreadsheets/d/ESTE_ES_EL_ID/edit
                                      ^^^^^^^^^^^^^^^^
```

---

## 🧪 Paso 3: Probar Integración

Una vez configuradas las credenciales:

1. Abrir en navegador: `http://localhost:9000`
2. La app solicitará permiso para acceder a Drive/Sheets
3. Hacer click en "Allow" en el popup de Google OAuth
4. Capturar una foto de prueba
5. Verificar que se sube a Drive (carpeta ENTRADAS)
6. Verificar que se registra en Sheets (REGISTRO_MASTER)

---

## 🐛 Problemas Conocidos

### Error: "Module declaration names may only use quotes"

**Causa**: Los archivos `app.js` y `uploader.js` tienen fragmentos de markdown (```) al inicio

**Solución temporal**: Edita manualmente y elimina la línea 1:
- En `app.js`: eliminar ` ```javascript` de la línea 1
- En `uploader.js`: ya corregido

### Error: "Google API not loaded"

**Causa**: Credenciales no configuradas o incorrectas

**Solución**:
1. Verificar que `GOOGLE_API_KEY` y `GOOGLE_CLIENT_ID` están correctamente copiados
2. Verificar que las APIs están habilitadas en Google Cloud Console
3. Verificar restricciones del API Key

---

## 📊 Estructura Final de Datos

### Drive: Carpeta ENTRADAS
```
MACROCENTRO/
└── ENTRADAS/
    ├── captura_1733400123456.jpg
    ├── captura_1733400234567.jpg
    └── ...
```

### Sheets: REGISTRO_MASTER
| Columna | Valor | Fuente |
|---------|-------|--------|
| FECHA_HORA_CAPTURA | 2025-12-05T08:30:00Z | Auto |
| TIPO_DOCUMENTO | WEB_CAPTURE | Auto |
| NOMBRE | (vacío) | OCR Backend |
| ... | ... | OCR Backend |
| BIOLOGICO | TDAP | Usuario |
| DOSIS | 1ª | Usuario |
| STATUS | PENDIENTE_OCR | Auto |
| LINK_FOTO | https://drive.google.com/... | Auto |

---

## 🚀 Siguiente Fase

Una vez que las APIs funcionen:

1. **Limpiar código** - Arreglar markdown artifacts
2. **Probar flujo completo** - Captura → Drive → Sheets
3. **Service Worker** - Modo offline
4. **Deploy GitHub Pages** - URL pública
5. **Pruebas reales** - Con usuarios en celulares

---

## 💡 Alternativa Rápida (Si hay problemas)

Si la integración de APIs es compleja para este momento:

**Opción A**: Mantener versión simulada
- Guardar fotos como base64 en localStorage
- Mock de subida exitosa
- Permitir descarga manual de fotos

**Opción B**: Backend simple
- Crear endpoint Flask/Express simple
- Frontend envía foto vía POST
- Backend sube a Drive/Sheets

**Opción C**: Continuar en próxima sesión
- Frontend base ya funciona ✅
- APIs quedan para siguiente iteración
- Usar mientras con simulación

---

**Estado Actual:**
- Frontend: 95% completo ✅
- APIs: Código listo, falta configuración ⏳
- Testing: Pendiente 🔜

**Tiempo estimado para completar APIs:** 30-60 min (con credenciales listas)
