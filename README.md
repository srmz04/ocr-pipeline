# 🔬 ZeroCost OCR Pipeline

Sistema automatizado de OCR serverless para procesamiento de credenciales (INE/Cartilla) con extracción de CURP, utilizando GitHub Actions, Tesseract, EasyOCR y Google Drive/Sheets.

## 🎯 Características

- ✅ **Costo $0** - Usa GitHub Actions (2,000 min/mes gratis)
- 🤖 **OCR Híbrido** - Tesseract + EasyOCR para máxima precisión
- ✔️ **Validación CURP** - Regex + cálculo de dígito verificador
- 📊 **Dashboard Automático** - Métricas en tiempo real en Google Sheets
- 🔄 **Procesamiento Inteligente** - Carpetas separadas por estado (Procesadas/Errores/Revisión)
- 🚫 **Detección de Duplicados** - Evita registros repetidos
- 📈 **Logging Completo** - Trazabilidad de cada imagen procesada

## 📁 Estructura del Proyecto

```
REGISTRO/
├── .github/
│   └── workflows/
│       └── ocr_pipeline.yml       # GitHub Actions workflow
├── src/
│   ├── auth.py                    # Autenticación GCP
│   ├── image_processor.py         # Preprocesamiento de imágenes
│   ├── ocr_engine.py              # OCR híbrido (Tesseract + EasyOCR)
│   ├── curp_validator.py          # Validación de CURP
│   ├── drive_manager.py           # Gestión de Google Drive
│   ├── sheets_manager.py          # Gestión de Google Sheets
│   └── main_ocr.py                # Script principal
├── config.py                      # Configuración centralizada
├── requirements.txt               # Dependencias Python
├── .gitignore                     # Archivos ignorados
└── README.md                      # Este archivo
```

## 🚀 Instalación y Configuración

### Paso 1: Configurar Google Cloud Platform

1. **Crear un proyecto en GCP**
   - Ve a [Google Cloud Console](https://console.cloud.google.com/)
   - Crea un nuevo proyecto (ej: "OCR-Vacunacion")

2. **Habilitar APIs necesarias**
   ```
   - Google Drive API
   - Google Sheets API
   ```

3. **Crear Service Account**
   - Ve a "IAM & Admin" > "Service Accounts"
   - Clic en "Create Service Account"
   - Nombre: `ocr-pipeline-bot`
   - Rol: `Editor` (o permisos específicos de Drive/Sheets)
   - Clic en "Create Key" > JSON
   - **Guarda el archivo JSON** (lo necesitarás después)

### Paso 2: Configurar Google Drive

1. **Crear estructura de carpetas en Drive**
   ```
   MACROCENTRO/
   ├── ENTRADA/          # Aquí subes las fotos nuevas
   ├── PROCESADAS/       # Fotos procesadas exitosamente
   ├── ERRORES/          # Fotos con errores de OCR
   └── REVISIÓN/         # Fotos con CURP de baja confianza
   ```

2. **Compartir carpetas con Service Account**
   - Abre cada carpeta
   - Clic en "Compartir"
   - Agrega el email de la Service Account (ej: `ocr-pipeline-bot@proyecto.iam.gserviceaccount.com`)
   - Permisos: **Editor**

### Paso 3: Configurar Google Sheets

1. **Crear hoja de cálculo**
   - Nombre: `REGISTRO_MASTER`
   - El script creará automáticamente 2 hojas:
     - `REGISTRO_MASTER` - Datos de registros
     - `DASHBOARD` - Métricas en tiempo real

2. **Compartir con Service Account**
   - Clic en "Compartir"
   - Agrega el email de la Service Account
   - Permisos: **Editor**

### Paso 4: Configurar GitHub Repository

1. **Crear repositorio en GitHub**
   ```bash
   cd /ruta/a/REGISTRO
   git init
   git add .
   git commit -m "Initial commit: OCR Pipeline"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/ocr-pipeline.git
   git push -u origin main
   ```

2. **Configurar GitHub Secrets**
   - Ve a tu repositorio en GitHub
   - Settings > Secrets and variables > Actions
   - Clic en "New repository secret"
   
   **Secretos necesarios:**
   
   a) `GCP_CREDENTIALS`
   - Abre el archivo JSON de la Service Account
   - Copia **TODO** el contenido
   - Pégalo en el valor del secreto
   
   b) `SPREADSHEET_NAME`
   - Valor: `REGISTRO_MASTER` (o el nombre de tu hoja)

### Paso 5: Activar GitHub Actions

1. **Verificar que Actions esté habilitado**
   - Ve a la pestaña "Actions" en tu repositorio
   - Si está deshabilitado, haz clic en "Enable Actions"

2. **Ejecutar manualmente (primera vez)**
   - Ve a "Actions" > "OCR Pipeline"
   - Clic en "Run workflow"
   - Selecciona la rama `main`
   - Clic en "Run workflow"

## 🔧 Uso

### Flujo de Trabajo

1. **Subir fotos a Drive**
   - Toma fotos de credenciales (INE/Cartilla)
   - Súbelas a la carpeta `ENTRADA/` en Google Drive

2. **Procesamiento Automático**
   - GitHub Actions ejecuta cada 10 minutos (horario laboral México)
   - El script:
     - Descarga imágenes de `ENTRADA/`
     - Preprocesa con OpenCV
     - Extrae texto con Tesseract/EasyOCR
     - Valida CURP
     - Actualiza Google Sheets
     - Mueve imagen a carpeta correspondiente

3. **Revisar Resultados**
   - Abre `REGISTRO_MASTER` en Google Sheets
   - Hoja `REGISTRO_MASTER`: Todos los registros
   - Hoja `DASHBOARD`: Métricas en tiempo real

### Estados de Procesamiento

| Carpeta | Descripción |
|---------|-------------|
| `PROCESADAS` | CURP válida con alta confianza (≥70%) |
| `REVISIÓN` | CURP válida pero baja confianza (<70%), duplicados, o sin CURP |
| `ERRORES` | Error al procesar imagen (corrupta, muy pequeña, etc.) |

## 📊 Columnas en Google Sheets

| Columna | Descripción |
|---------|-------------|
| `FECHA_HORA` | Timestamp del procesamiento |
| `NOMBRE_ARCHIVO` | Nombre de la foto |
| `CURP_DETECTADA` | CURP extraída (o "X" si no se encontró) |
| `CONFIANZA_OCR` | Confianza del OCR (0.00 - 1.00) |
| `NOMBRE_EXTRAIDO` | Nombre extraído (futuro) |
| `SEXO_EXTRAIDO` | Sexo extraído de la CURP (H/M) |
| `TEXTO_CRUDO` | Texto completo extraído (primeros 500 caracteres) |
| `STATUS` | Estado del procesamiento |
| `LINK_FOTO` | Link directo a la foto en Drive |

## 🐛 Troubleshooting

### Error: "Carpeta no encontrada"
- Verifica que las carpetas en Drive tengan los nombres exactos
- Asegúrate de compartir con la Service Account

### Error: "Spreadsheet no encontrado"
- Verifica el nombre en el secreto `SPREADSHEET_NAME`
- Asegúrate de compartir con la Service Account

### Error: "GCP_CREDENTIALS inválido"
- Verifica que copiaste **TODO** el JSON (incluye `{` y `}`)
- No modifiques el formato del JSON

### No se procesan imágenes
- Verifica que las imágenes estén en formato JPG/PNG
- Revisa los logs en GitHub Actions

### Baja precisión de OCR
- Asegúrate de que las fotos sean claras y bien iluminadas
- Evita reflejos y sombras
- Toma fotos de frente (no inclinadas)

## 📈 Optimizaciones

### Ajustar Horario de Ejecución

Edita `.github/workflows/ocr_pipeline.yml`:

```yaml
schedule:
  # Cada 5 minutos (más frecuente)
  - cron: '*/5 14-23 * * *'
  
  # Solo de lunes a viernes
  - cron: '*/10 14-23 * * 1-5'
```

### Aumentar Límite de Archivos

Edita `config.py`:

```python
MAX_FILES_PER_RUN = 100  # Procesar más archivos por ejecución
```

### Ajustar Umbral de Confianza

Edita `config.py`:

```python
CONFIDENCE_THRESHOLD = 0.8  # Más estricto (menos falsos positivos)
CONFIDENCE_THRESHOLD = 0.5  # Más permisivo (menos revisión manual)
```

## 📝 Licencia

Este proyecto es de uso interno para la campaña de vacunación.

## 🤝 Soporte

Para problemas o preguntas, contacta al equipo de desarrollo.

---

**Desarrollado con ❤️ para eliminar el trabajo manual y cumplir con el requisito de "usar IA" del jefe** 😉
