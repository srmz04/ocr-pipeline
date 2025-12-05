# 📱 Propuesta: Interfaz Web de Captura con Validación de Calidad

## 🎯 Objetivo

Crear una **PWA (Progressive Web App)** que:
1. ✅ Se accede desde un **link único** compartido con 10 operadores
2. ✅ Funciona en **cualquier celular** (sin instalar app)
3. ✅ **Fuerza capturas de calidad** (como apps bancarias)
4. ✅ Registra **biológico + dosis** junto con la foto
5. ✅ **Hosting 100% gratuito** en GitHub Pages
6. ✅ Se integra con **Google Drive + Sheets** existente

---

## 🏗️ Arquitectura Propuesta

### Stack Tecnológico (Todo Gratis)

```
┌─────────────────────────────────────────────────────────┐
│  📱 FRONTEND (GitHub Pages - Gratis)                    │
│  ─────────────────────────────────────────────────────  │
│  • HTML5 + CSS3 + JavaScript Vanilla                    │
│  • Camera API (HTML5)                                   │
│  • Canvas API (validación de calidad)                   │
│  • Service Worker (PWA - funciona offline)              │
│  • Responsive (móvil-first)                             │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  ☁️ BACKEND (Serverless - Gratis)                       │
│  ─────────────────────────────────────────────────────  │
│  OPCIÓN A: Google Drive API (ya configurado)            │
│  • Subida directa desde navegador                       │
│  • Google Sheets para metadata                          │
│                                                          │
│  OPCIÓN B: Firebase (Free Tier)                         │
│  • Storage: 1GB                                         │
│  • Firestore: base de datos                             │
│  • Cloud Functions: procesamiento                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  🤖 PROCESAMIENTO OCR (GitHub Actions - Gratis)         │
│  ─────────────────────────────────────────────────────  │
│  • Pipeline actual mejorado                             │
│  • Procesa fotos cada 10 minutos                        │
│  • Extrae CURP + valida                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 📱 Interfaz de Captura (Mockup)

### Pantalla 1: Cámara con Guías

```
┌──────────────────────────────────────┐
│  📷 Captura de Credencial            │
├──────────────────────────────────────┤
│                                      │
│  ╔══════════════════════════════╗   │
│  ║                              ║   │
│  ║   ┌────────────────────┐     ║   │
│  ║   │  Alinea credencial │     ║   │
│  ║   │   dentro del marco │     ║   │
│  ║   │                    │     ║   │
│  ║   │  ✅ Buena luz      │     ║   │
│  ║   │  ✅ Enfocada       │     ║   │
│  ║   └────────────────────┘     ║   │
│  ║                              ║   │
│  ╚══════════════════════════════╝   │
│                                      │
│  [●] Capturar                        │
│                                      │
│  Estado: ⚠️ Acerca el celular        │
└──────────────────────────────────────┘
```

### Pantalla 2: Registro de Biológico

```
┌──────────────────────────────────────┐
│  💉 Datos de Vacunación              │
├──────────────────────────────────────┤
│                                      │
│  📸 Preview de credencial ✅         │
│  [Miniatura de la foto capturada]    │
│                                      │
│  Biológico Aplicado:                 │
│  ┌─────────────────────────────────┐│
│  │ ▼ Seleccionar                   ││
│  │   • TDAP                         ││
│  │   • neumococo                    ││
│  │   • influenza                    ││
│  └─────────────────────────────────┘│
│                                      │
│  Dosis:                              │
│  ◉ Primera    ○ Segunda   ○ Refuerzo│
│                                      │
│  Observaciones (opcional):           │
│  ┌─────────────────────────────────┐│
│  │                                 ││
│  └─────────────────────────────────┘│
│                                      │
│         [✓ Registrar y Enviar]       │
└──────────────────────────────────────┘
```

---

## 🎨 Funcionalidades de Validación de Calidad

### 1. **Detección de Bordes** (Como apps bancarias)

```javascript
// Detecta si la credencial está correctamente encuadrada
function detectCard(imageData) {
  // Usa algoritmo Canny Edge Detection
  const edges = detectEdges(imageData);
  const cardRect = findRectangle(edges);
  
  if (cardRect.confidence > 0.8) {
    return { valid: true, message: "✅ Credencial detectada" };
  } else {
    return { valid: false, message: "⚠️ Acerca más la credencial" };
  }
}
```

### 2. **Validación de Calidad en Tiempo Real**

- ✅ **Resolución mínima**: 1200x800 pixels
- ✅ **Brillo adecuado**: Entre 80-180 (escala 0-255)
- ✅ **Nitidez**: Utilizando Laplacian variance
- ✅ **Ángulo**: Máximo 10° de inclinación
- ⚠️ **Guías visuales**: Marco amarillo/verde/rojo según calidad

### 3. **Feedback Visual**

```
Estado del preview:
🟢 Verde:  "✅ ¡Perfecto! Captura ahora"
🟡 Amarillo: "⚠️ Mejora la iluminación"
🔴 Rojo:    "❌ Muy oscuro / desenfocado"
```

---

## 🔐 Flujo de Datos

### Paso a Paso

1. **Operador abre link** → `https://srmz04.github.io/ocr-pipeline/`
2. **Permite cámara** → Navegador solicita permiso
3. **Encuadra credencial** → Sistema valida en tiempo real
4. **Captura foto** → Solo si pasa validación de calidad
5. **Llena formulario** → Biológico + dosis + observaciones
6. **Envía** → Foto sube a Drive + metadata a Sheets
7. **Confirmación** → "✅ Registro #1234 completado"
8. **Siguiente paciente** → Pantalla se resetea

### Backend: Dos Opciones

#### **Opción A: Google Drive API** ⭐ (Recomendado)

**Pros:**
- ✅ Ya tienes todo configurado
- ✅ Integración existente con OCR pipeline
- ✅ Sin cambios mayores
- ✅ Drive JS API funciona desde navegador

**Implementación:**
```javascript
// Subida directa desde navegador
async function uploadToSync() {
  const metadata = {
    name: `credencial_${Date.now()}.jpg`,
    parents: [ENTRADAS_FOLDER_ID]
  };
  
  const form = new FormData();
  form.append('metadata', new Blob([JSON.stringify(metadata)], 
    { type: 'application/json' }));
  form.append('file', photoBlob);
  
  await fetch('https://www.googleapis.com/upload/drive/v3/files',
    { method: 'POST', body: form, headers: ... });
}
```

#### **Opción B: Firebase** (Más moderno)

**Pros:**
- ✅ Realtime updates
- ✅ Mejor UX (actualizaciones instantáneas)
- ✅ Firestore para metadata estructurada
- ✅ Cloud Functions para automatización

**Límites Free Tier:**
- Storage: 1GB (suficiente para ~10,000 fotos)
- Firestore: 1GB
- Cloud Functions: 125K invocaciones/mes

---

## 🚀 Plan de Implementación

### **Fase 1: MVP (4-6 horas)** ⚡

**Entregables:**
1. ✅ Interfaz móvil básica con cámara
2. ✅ Validación de resolución mínima
3. ✅ Campos de biológico + dosis
4. ✅ Subida a Google Drive (carpeta ENTRADAS)
5. ✅ Registro en Google Sheets

**Tecnologías:**
- HTML5 + CSS3 (sin frameworks)
- JavaScript Vanilla
- Google Drive API v3
- GitHub Pages

**Deploy:**
```bash
https://srmz04.github.io/ocr-pipeline-capture/
```

---

### **Fase 2: Validación de Calidad (2-3 horas)** 🎯

**Entregables:**
1. ✅ Detección de bordes de credencial
2. ✅ Validación de iluminación
3. ✅ Validación de nitidez
4. ✅ Feedback visual en tiempo real
5. ✅ Solo permite captura si pasa validaciones

**Librerías:**
- OpenCV.js (en navegador)
- TensorFlow.js Lite (opcional, para detección ML)

---

### **Fase 3: PWA + Offline (1-2 horas)** 📴

**Entregables:**
1. ✅ Service Worker (funciona offline)
2. ✅ Cache de fotos si no hay internet
3. ✅ Sincronización automática al reconectar
4. ✅ Instalable como app (icono en home screen)
5. ✅ Push notifications (opcional)

---

### **Fase 4: Mejoras OCR (3-4 horas)** 🔍

**Entregables:**
1. ✅ Implementar las 3 opciones de mejora de OCR
2. ✅ Extracción inteligente de CURP
3. ✅ Múltiples pasadas de Tesseract
4. ✅ Preprocesamiento mejorado
5. ✅ Mayor tasa de éxito (>90%)

---

## 💰 Costos Totales: $0 USD

| Servicio | Límite Free | Uso Estimado | Costo |
|----------|-------------|--------------|-------|
| GitHub Pages | Ilimitado | 10 usuarios | **$0** |
| Google Drive | 15GB gratis | ~2GB fotos | **$0** |
| Google Sheets | Ilimitado | 1 hoja | **$0** |
| GitHub Actions | 2000 min/mes | ~500 min | **$0** |
| **TOTAL** | - | - | **$0** |

---

## 📊 Comparativa con Soluciones Comerciales

| Característica | Nuestra Solución | Apps Comerciales |
|----------------|------------------|------------------|
| Costo | **$0/mes** | $50-200/mes |
| Customización | **100%** | Limitada |
| Usuarios | **Ilimitados** | 5-10 incluidos |
| Storage | **15GB** | 1-5GB |
| Código | **Open source** | Propietario |
| Vendor lock-in | **No** | Sí |

---

## 🎯 Recomendación

### Te sugiero este roadmap:

**Semana 1**: 
1. ✅ Crear interfaz básica de captura (Fase 1)
2. ✅ Probar con 2-3 operadores
3. ✅ Ajustar UX según feedback

**Semana 2**:
1. ✅ Agregar validación de calidad (Fase 2)
2. ✅ Implementar mejoras de OCR (Fase 4)
3. ✅ Prueba piloto con los 10 operadores

**Semana 3**:
1. ✅ PWA para modo offline (Fase 3)
2. ✅ Optimizaciones finales
3. ✅ Producción completa

---

## ¿Empezamos?

Puedo crear:

**A) Prototipo rápido** (2 horas)
- Interfaz funcional básica
- Captura + subida a Drive
- Listo para probar

**B) MVP completo** (4-6 horas)
- Todo lo de Fase 1
- Validación básica de calidad
- Listo para usar en producción

**C) Solución completa** (10-15 horas)
- Todas las fases
- Máxima calidad de OCR
- Experiencia premium

¿Cuál prefieres?
