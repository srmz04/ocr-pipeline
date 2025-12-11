# 📋 Guía de Configuración Manual - ZeroCost OCR Pipeline

Esta guía te llevará paso a paso por la configuración inicial del sistema.

---

## 🎯 Objetivo

Configurar Google Cloud Platform, Google Drive, Google Sheets y GitHub para que el pipeline OCR funcione automáticamente.

---

## ⏱️ Tiempo Estimado

- **Primera vez**: 30-45 minutos
- **Con experiencia en GCP**: 15-20 minutos

---

## 📝 Requisitos Previos

- [ ] Cuenta de Google (Gmail)
- [ ] Cuenta de GitHub
- [ ] Acceso a Google Drive
- [ ] Permisos para crear proyectos en Google Cloud

---

## 🔧 Paso 1: Google Cloud Platform (15 min)

### 1.1 Crear Proyecto en GCP

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Clic en el selector de proyectos (arriba a la izquierda)
3. Clic en "Nuevo Proyecto"
4. **Nombre del proyecto**: `OCR-Vacunacion` (o el que prefieras)
5. Clic en "Crear"
6. **Espera** a que se cree el proyecto (30-60 segundos)

### 1.2 Habilitar APIs

1. En el menú lateral, ve a **"APIs y servicios" > "Biblioteca"**
2. Busca y habilita las siguientes APIs:

   **a) Google Drive API**
   - Busca: "Google Drive API"
   - Clic en el resultado
   - Clic en "Habilitar"
   - Espera a que se habilite

   **b) Google Sheets API**
   - Busca: "Google Sheets API"
   - Clic en el resultado
   - Clic en "Habilitar"
   - Espera a que se habilite

### 1.3 Crear Service Account

1. Ve a **"IAM y administración" > "Cuentas de servicio"**
2. Clic en **"Crear cuenta de servicio"**
3. **Detalles de la cuenta de servicio**:
   - **Nombre**: `ocr-pipeline-bot`
   - **ID**: (se genera automáticamente)
   - **Descripción**: `Bot para procesamiento OCR automático`
4. Clic en **"Crear y continuar"**
5. **Otorgar acceso**:
   - **Rol**: Selecciona `Editor` (o `Propietario` si tienes permisos)
   - Clic en **"Continuar"**
6. **Otorgar acceso a usuarios** (opcional):
   - Deja en blanco
   - Clic en **"Listo"**

### 1.4 Generar Clave JSON

1. En la lista de cuentas de servicio, encuentra `ocr-pipeline-bot`
2. Clic en los **3 puntos** (⋮) a la derecha
3. Selecciona **"Administrar claves"**
4. Clic en **"Agregar clave" > "Crear clave nueva"**
5. Selecciona **"JSON"**
6. Clic en **"Crear"**
7. **Se descargará un archivo JSON** (ej: `ocr-vacunacion-abc123.json`)
8. **¡IMPORTANTE!** Guarda este archivo en un lugar seguro, lo necesitarás después

### 1.5 Copiar Email de Service Account

1. En la lista de cuentas de servicio, copia el **email** de `ocr-pipeline-bot`
2. Se ve algo así: `ocr-pipeline-bot@ocr-vacunacion-123456.iam.gserviceaccount.com`
3. **Guárdalo en un bloc de notas**, lo usarás en los siguientes pasos

---

## 📁 Paso 2: Google Drive (10 min)

### 2.1 Crear Estructura de Carpetas

1. Ve a [Google Drive](https://drive.google.com/)
2. Clic en **"Nuevo" > "Carpeta"**
3. **Nombre**: `MACROCENTRO`
4. Clic en **"Crear"**
5. **Entra** a la carpeta `MACROCENTRO`
6. Crea 4 subcarpetas (repite el proceso):
   - `ENTRADA`
   - `PROCESADAS`
   - `ERRORES`
   - `REVISIÓN`

**Estructura final:**
```
MACROCENTRO/
├── ENTRADA/
├── PROCESADAS/
├── ERRORES/
└── REVISIÓN/
```

### 2.2 Compartir Carpetas con Service Account

**Para CADA una de las 5 carpetas** (incluida `CAMPAÑA_VACUNACION`):

1. **Clic derecho** en la carpeta
2. Selecciona **"Compartir"**
3. En el campo "Agregar personas y grupos", **pega el email de la Service Account**
   - (ej: `ocr-pipeline-bot@ocr-vacunacion-123456.iam.gserviceaccount.com`)
4. **Permisos**: Selecciona **"Editor"**
5. **DESACTIVA** la casilla "Notificar a las personas"
6. Clic en **"Compartir"**

**Repite para las 5 carpetas:**
- ✅ `MACROCENTRO`
- ✅ `ENTRADA`
- ✅ `PROCESADAS`
- ✅ `ERRORES`
- ✅ `REVISIÓN`

---

## 📊 Paso 3: Google Sheets (5 min)

### 3.1 Crear Hoja de Cálculo

1. Ve a [Google Sheets](https://sheets.google.com/)
2. Clic en **"En blanco"** (crear nueva hoja)
3. **Nombre de la hoja**: `REGISTRO_MASTER`
   - Clic en "Hoja de cálculo sin título" (arriba a la izquierda)
   - Escribe: `REGISTRO_MASTER`
   - Presiona Enter

### 3.2 Compartir con Service Account

1. Clic en **"Compartir"** (botón verde arriba a la derecha)
2. En el campo "Agregar personas y grupos", **pega el email de la Service Account**
3. **Permisos**: Selecciona **"Editor"**
4. **DESACTIVA** la casilla "Notificar a las personas"
5. Clic en **"Compartir"**

### 3.3 Copiar Nombre de la Hoja

1. El nombre de tu hoja es: `REGISTRO_MASTER`
2. **Guárdalo**, lo necesitarás para GitHub

---

## 🐙 Paso 4: GitHub Repository (10 min)

### 4.1 Crear Repositorio

**Opción A: Desde la terminal (recomendado)**

```bash
cd /home/uy/Dropbox/smrz04/REGISTRO

# Inicializar git
git init

# Agregar archivos
git add .

# Commit inicial
git commit -m "Initial commit: OCR Pipeline"

# Renombrar rama a main
git branch -M main

# Agregar remote (REEMPLAZA con tu usuario)
git remote add origin https://github.com/TU_USUARIO/ocr-pipeline.git

# Push
git push -u origin main
```

**Opción B: Desde GitHub.com**

1. Ve a [GitHub](https://github.com/)
2. Clic en **"New repository"**
3. **Nombre**: `ocr-pipeline`
4. **Visibilidad**: Privado (recomendado)
5. **NO** inicialices con README
6. Clic en **"Create repository"**
7. Sigue las instrucciones de "push an existing repository"

### 4.2 Configurar GitHub Secrets

1. Ve a tu repositorio en GitHub
2. Clic en **"Settings"** (pestaña arriba)
3. En el menú lateral, ve a **"Secrets and variables" > "Actions"**
4. Clic en **"New repository secret"**

**Secreto 1: GCP_CREDENTIALS**

1. **Name**: `GCP_CREDENTIALS`
2. **Secret**:
   - Abre el archivo JSON que descargaste en el Paso 1.4
   - **Copia TODO el contenido** (desde `{` hasta `}`)
   - Pégalo en el campo "Secret"
3. Clic en **"Add secret"**

**Secreto 2: SPREADSHEET_NAME**

1. Clic en **"New repository secret"**
2. **Name**: `SPREADSHEET_NAME`
3. **Secret**: `REGISTRO_MASTER`
4. Clic en **"Add secret"**

### 4.3 Verificar Secrets

Deberías ver 2 secretos:
- ✅ `GCP_CREDENTIALS`
- ✅ `SPREADSHEET_NAME`

---

## ✅ Paso 5: Verificación (5 min)

### 5.1 Ejecutar Workflow Manualmente

1. En tu repositorio de GitHub, ve a la pestaña **"Actions"**
2. Si ves un mensaje de "Workflows disabled", clic en **"Enable Actions"**
3. En el menú lateral, selecciona **"OCR Pipeline"**
4. Clic en **"Run workflow"** (botón azul a la derecha)
5. Selecciona la rama **"main"**
6. Clic en **"Run workflow"**

### 5.2 Monitorear Ejecución

1. Espera unos segundos y **refresca la página**
2. Verás un nuevo workflow ejecutándose (punto amarillo 🟡)
3. Clic en el workflow para ver los detalles
4. Clic en **"process-images"** para ver los logs

### 5.3 Verificar Resultados

**Si NO hay imágenes en `ENTRADA/`:**
- El workflow debería completarse exitosamente ✅
- En los logs verás: "ℹ️ No hay archivos para procesar"

**Si hay imágenes en `ENTRADA/`:**
- El workflow procesará las imágenes
- Verás los logs de cada imagen
- Las imágenes se moverán a `PROCESADAS/`, `ERRORES/` o `REVISIÓN/`
- Google Sheets se actualizará con los datos

---

## 🎉 ¡Listo!

Tu pipeline OCR está configurado y funcionando. Ahora:

1. **Sube fotos** a la carpeta `ENTRADA/` en Google Drive
2. **Espera** a que GitHub Actions ejecute (cada 10 min)
3. **Revisa** los resultados en Google Sheets

---

## 🐛 Problemas Comunes

### Error: "Carpeta no encontrada"

**Causa**: Las carpetas no están compartidas con la Service Account

**Solución**:
1. Verifica que compartiste TODAS las carpetas (incluida la raíz)
2. Verifica que el email de la Service Account sea correcto
3. Permisos deben ser "Editor"

### Error: "Spreadsheet no encontrado"

**Causa**: El nombre del spreadsheet no coincide o no está compartido

**Solución**:
1. Verifica que el secreto `SPREADSHEET_NAME` sea exactamente `REGISTRO_MASTER`
2. Verifica que compartiste el spreadsheet con la Service Account

### Error: "Invalid credentials"

**Causa**: El JSON de credenciales está mal copiado

**Solución**:
1. Abre el archivo JSON en un editor de texto
2. Copia TODO el contenido (desde `{` hasta `}`)
3. Asegúrate de NO modificar el formato
4. Actualiza el secreto `GCP_CREDENTIALS` en GitHub

---

## 📞 Soporte

Si tienes problemas, revisa los logs en GitHub Actions:
1. Ve a "Actions"
2. Clic en el workflow fallido
3. Clic en "process-images"
4. Revisa los logs para ver el error específico

---

**¡Éxito con tu campaña de vacunación!** 💉✨
