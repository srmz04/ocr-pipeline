# 🔑 Configuración de Google Cloud - Paso a Paso

## 📍 Paso 1: Verificar Proyecto en Google Cloud Console

1. Abre tu navegador y ve a: https://console.cloud.google.com
2. Verifica que estás en el proyecto correcto: **ocr-vacunacion**
   - Mira en la parte superior, debería decir el nombre del proyecto

---

## 🔐 Paso 2: Habilitar las APIs Necesarias

### A. Habilitar Google Drive API

1. En el menú lateral: **APIs & Services** → **Library**
2. Busca: `Google Drive API`
3. Click en el resultado
4. Click **ENABLE** (Habilitar)
5. Espera a que se active (unos segundos)

### B. Habilitar Google Sheets API

1. De vuelta en **Library**
2. Busca: `Google Sheets API`
3. Click en el resultado
4. Click **ENABLE**
5. Espera confirmación

---

## 🔑 Paso 3: Crear API Key

1. En el menú lateral: **APIs & Services** → **Credentials**
2. Click en **+ CREATE CREDENTIALS** (arriba)
3. Selecciona: **API Key**
4. Se generará una key automáticamente
5. **IMPORTANTE**: Click en **RESTRICT KEY** inmediatamente

### Configurar Restricciones del API Key:

**Application restrictions:**
- Selecciona: **HTTP referrers (web sites)**
- Agrega estos referrers:
  ```
  http://localhost:9000/*
  http://localhost:*
  https://srmz04.github.io/*
  ```

**API restrictions:**
- Selecciona: **Restrict key**
- Marca solo:
  - ✅ Google Drive API
  - ✅ Google Sheets API

6. Click **SAVE**
7. **Copia el API Key** (formato: `AIzaSy...`)

---

## 🎫 Paso 4: Crear OAuth 2.0 Client ID

### A. Configurar Pantalla de Consentimiento (si no está hecho)

1. En **APIs & Services** → **OAuth consent screen**
2. Si pide configurar:
   - User Type: **External**
   - Click **CREATE**
   - App name: `Captura Vacunación`
   - User support email: tu email
   - Developer contact: tu email
   - Click **SAVE AND CONTINUE**
   - Scopes: Click **SAVE AND CONTINUE** (sin agregar nada)
   - Test users: Agrega tu email
   - Click **SAVE AND CONTINUE**

### B. Crear Client ID

1. Ve a: **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Application type: **Web application**
4. Name: `Captura Frontend`
5. **Authorized JavaScript origins**:
   ```
   http://localhost:9000
   http://localhost:8080
   http://localhost:3000
   https://srmz04.github.io
   ```
6. **Authorized redirect URIs**: (dejar vacío por ahora)
7. Click **CREATE**
8. **Copia el Client ID** (formato: `123456-abc.apps.googleusercontent.com`)

---

## 📝 Paso 5: Obtener Spreadsheet ID

1. Abre tu Google Sheet: `REGISTRO_MASTER` o el que uses
2. Mira la URL:
   ```
   https://docs.google.com/spreadsheets/d/ESTE_ES_EL_SPREADSHEET_ID/edit
   ```
3. Copia el ID entre `/d/` y `/edit`

---

## ⚙️ Paso 6: Configurar en el Código

Ahora voy a actualizar `config.js` con tus credenciales.

**Dime cuando tengas:**
1. ✅ API Key (AIzaSy...)
2. ✅ Client ID (123456-abc.apps.googleusercontent.com)
3. ✅ Spreadsheet ID (ya lo tengo si es el mismo sheet)

---

## 🧪 Paso 7: Probar

Una vez configurado:
1. Refrescar `http://localhost:9000`
2. Debería pedir permiso para acceder a Drive/Sheets
3. Aceptar los permisos
4. ¡Capturar y subir!

---

**¿Estás listo para empezar?** 
Avísame cuando completes cada paso y te guío en el siguiente.
