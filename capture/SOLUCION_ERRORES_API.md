# 🛠️ Solución de Errores API (403 Forbidden)

El error `403 Forbidden` confirma que tu **API Key existe pero tiene restricciones que bloquean el acceso**.

Sigue estos pasos exactos para arreglarlo:

## 1. Ir a la Consola de Google Cloud
Haz clic aquí: [**Google Cloud Console > Credentials**](https://console.cloud.google.com/apis/credentials)

## 2. Editar tu API Key
1. Busca tu API Key en la lista (la que empieza con `AIzaSy...`).
2. Haz clic en el **lápiz** ✏️ o en el nombre para editarla.

## 3. Revisar "API restrictions" (Restricciones de API)
Busca la sección **API restrictions** al final de la página.

*   **Si está marcado "Don't restrict key"**: 
    *   Cámbialo a **Restrict key**.
*   **Si está marcado "Restrict key"**:
    *   Haz clic en el menú desplegable **Select APIs**.
    *   Asegúrate de que estén marcadas (✅) **AMBAS**:
        *   ✅ **Google Drive API**
        *   ✅ **Google Sheets API**
    *   Si no las ves, búscalas y márcalas.
    *   Haz clic en **OK**.

## 4. Revisar "Application restrictions" (Restricciones de Aplicación)
Busca la sección **Application restrictions**.

*   Debe estar seleccionado **HTTP referrers (web sites)**.
*   En **Website restrictions**, asegúrate de tener estas URLs exactas:
    *   `http://localhost:9000/*`  <-- **IMPORTANTE: El asterisco al final**
    *   `http://localhost:9000`
    *   `https://srmz04.github.io/*`

## 5. Guardar Cambios
1. Haz clic en **SAVE** (Guardar).
2. **ESPERA 5 MINUTOS**. Los cambios en Google tardan un poco en propagarse.

---

## 🔄 Prueba Final
1. Vuelve a tu app (`http://localhost:9000`).
2. Refresca la página (`Ctrl + R`).
3. Abre la consola (`F12`) y mira si desaparecen los errores rojos.

Si sigue fallando, prueba desmarcando temporalmente todas las restricciones del API Key (selecciona "None") solo para probar si es eso.
