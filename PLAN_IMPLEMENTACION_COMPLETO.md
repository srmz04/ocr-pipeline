# 🎯 Plan de Implementación: Solución Completa Multi-Documento

## 📋 Requisitos Actualizados

### Tipos de Documentos Soportados
1. ✅ **INE** (Credencial de Elector)
2. ✅ **Cartilla de Vacunación**
3. ✅ **Acta de Nacimiento** (opcional)
4. ✅ **Pasaporte** (opcional)
5. ✅ **Cualquier documento con datos personales**

### Datos a Extraer (TODO lo posible)
- **Identificación**: CURP, RFC, Clave de Elector
- **Nombre completo**: Nombre(s), Apellido Paterno, Apellido Materno
- **Demografía**: Fecha de Nacimiento, Edad, Sexo
- **Ubicación**: Estado, Municipio, Localidad, Dirección
- **Otros**: Tipo de documento, Número de folio, etc.

---

## 🏗️ Arquitectura Mejorada

### 1. Frontend de Captura (PWA)

```
┌─────────────────────────────────────────────┐
│  📱 INTERFAZ MÓVIL                          │
├─────────────────────────────────────────────┤
│                                             │
│  Paso 1: TIPO DE DOCUMENTO                 │
│  ┌───┐ ┌───┐ ┌───┐                         │
│  │INE│ │CVN│ │OTR│  (Cartilla/Otro)        │
│  └───┘ └───┘ └───┘                         │
│                                             │
│  Paso 2: CAPTURA CON VALIDACIÓN             │
│  • Detección automática de documento       │
│  • Validación de calidad en tiempo real    │
│  • Guías visuales adaptativas              │
│                                             │
│  Paso 3: DATOS DE VACUNACIÓN                │
│  • Biológico aplicado                      │
│  • Dosis (1ª, 2ª, refuerzo)                │
│  • Observaciones                           │
│                                             │
│  Paso 4: CONFIRMACIÓN                       │
│  • Preview de foto                         │
│  • Resumen de datos                        │
│  • [Enviar]                                │
└─────────────────────────────────────────────┘
```

### 2. Backend OCR (GitHub Actions)

```python
Pipeline Multi-Documento:

1. Clasificación de Documento
   - Detectar tipo (INE/Cartilla/Otro)
   - Aplicar estrategia específica

2. Extracción Inteligente
   - CURP: regex + validación
   - Nombre: NER (Named Entity Recognition)
   - Fecha: regex + validación
   - Otros: extracción por campos

3. Post-Procesamiento
   - Cálculo de edad
   - Normalización de nombres
   - Validación cruzada de datos

4. Almacenamiento
   ├── Google Sheets (datos estructurados)
   └── Google Drive (fotos originales)
```

---

## 📊 Nuevos Campos en Google Sheets

### Estructura de `REGISTRO_MASTER`

| Campo | Tipo | Origen | Validación |
|-------|------|--------|------------|
| `ID_REGISTRO` | Auto | Sistema | Único |
| `FECHA_HORA_CAPTURA` | DateTime | Sistema | - |
| `TIPO_DOCUMENTO` | Enum | Manual | INE/CARTILLA/OTRO |
| `NOMBRE` | Text | OCR | - |
| `APELLIDO_PATERNO` | Text | OCR | - |
| `APELLIDO_MATERNO` | Text | OCR | - |
| `NOMBRE_COMPLETO` | Text | OCR/Calculado | - |
| `CURP` | Text(18) | OCR | Regex + dígito |
| `FECHA_NACIMIENTO` | Date | OCR | YYYY-MM-DD |
| `EDAD` | Integer | Calculado | - |
| `SEXO` | Char(1) | OCR/CURP | H/M |
| `ESTADO` | Text | OCR | - |
| `MUNICIPIO` | Text | OCR | - |
| `CLAVE_ELECTOR` | Text | OCR (si INE) | - |
| `BIOLOGICO` | Text | Manual | - |
| `DOSIS` | Enum | Manual | 1/2/R |
| `CONFIANZA_OCR` | Float | Sistema | 0.0-1.0 |
| `TEXTO_EXTRAIDO` | Text | OCR | (primeros 1000 chars) |
| `STATUS` | Enum | Sistema | OK/REVISAR/ERROR |
| `LINK_FOTO` | URL | Drive | - |
| `OPERADOR` | Text | Manual | (opcional) |
| `OBSERVACIONES` | Text | Manual | - |

---

## 🔍 Módulos de Extracción Mejorados

### Módulo 1: Clasificador de Documentos

```python
# src/document_classifier.py

def classify_document(text: str) -> DocumentType:
    """
    Clasifica el tipo de documento basándose en palabras clave
    """
    keywords = {
        'INE': ['INSTITUTO NACIONAL ELECTORAL', 'CLAVE DE ELECTOR', 'INE'],
        'CARTILLA': ['CARTILLA NACIONAL DE VACUNACION', 'SECRETARIA DE SALUD'],
        'ACTA': ['ACTA DE NACIMIENTO', 'REGISTRO CIVIL'],
        'PASAPORTE': ['PASAPORTE', 'PASSPORT', 'SRE']
    }
    
    for doc_type, words in keywords.items():
        if any(word in text.upper() for word in words):
            return DocumentType(doc_type)
    
    return DocumentType.UNKNOWN
```

### Módulo 2: Extractor Universal de Datos

```python
# src/data_extractor.py

class UniversalDataExtractor:
    """
    Extrae datos de cualquier tipo de documento
    """
    
    def extract(self, text: str, doc_type: DocumentType) -> dict:
        data = {
            'curp': self.extract_curp(text),
            'nombre_completo': self.extract_nombre(text),
            'fecha_nacimiento': self.extract_fecha(text),
            'sexo': self.extract_sexo(text),
            'ubicacion': self.extract_ubicacion(text)
        }
        
        # Aplicar estrategia específica por tipo
        if doc_type == DocumentType.INE:
            data.update(self.extract_ine_specific(text))
        elif doc_type == DocumentType.CARTILLA:
            data.update(self.extract_cartilla_specific(text))
        
        # Calcular campos derivados
        data['edad'] = self.calculate_age(data['fecha_nacimiento'])
        
        return data
    
    def extract_nombre(self, text: str) -> dict:
        """
        Extrae nombres usando NER + reglas
        """
        # Estrategia 1: Buscar patrón "NOMBRE: XXX"
        # Estrategia 2: Buscar línea después de "NOMBRE"
        # Estrategia 3: NER con spaCy (si disponible)
        pass
    
    def extract_fecha(self, text: str) -> str:
        """
        Extrae fechas en múltiples formatos
        """
        patterns = [
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        ]
        # Validar y normalizar a YYYY-MM-DD
        pass
```

### Módulo 3: Validador de Datos

```python
# src/data_validator.py

def validate_data(data: dict) -> tuple[bool, list]:
    """
    Valida que los datos extraídos sean coherentes
    """
    errors = []
    
    # Validación 1: CURP vs Fecha de Nacimiento
    if data['curp'] and data['fecha_nacimiento']:
        curp_fecha = extract_date_from_curp(data['curp'])
        if curp_fecha != data['fecha_nacimiento']:
            errors.append("CURP y fecha no coinciden")
    
    # Validación 2: CURP vs Sexo
    if data['curp'] and data['sexo']:
        curp_sexo = data['curp'][10]  # H/M
        if curp_sexo != data['sexo']:
            errors.append("CURP y sexo no coinciden")
    
    # Validación 3: Edad razonable (0-120 años)
    if data['edad'] and not (0 <= data['edad'] <= 120):
        errors.append(f"Edad fuera de rango: {data['edad']}")
    
    return (len(errors) == 0, errors)
```

---

## 🎨 Frontend: Flujo Completo

### Pantalla 1: Selección de Documento

```
┌──────────────────────────────────────┐
│  📄 ¿Qué documento vas a capturar?   │
├──────────────────────────────────────┤
│                                      │
│   ┌────────────┐  ┌────────────┐   │
│   │    🪪      │  │    📗      │   │
│   │    INE     │  │  Cartilla  │   │
│   │            │  │            │   │
│   │ [Capturar] │  │ [Capturar] │   │
│   └────────────┘  └────────────┘   │
│                                      │
│   ┌────────────┐                    │
│   │    📄      │                    │
│   │   Otro     │                    │
│   │ documento  │                    │
│   │ [Capturar] │                    │
│   └────────────┘                    │
│                                      │
└──────────────────────────────────────┘
```

### Pantalla 2: Captura (adaptativa por tipo)

```javascript
// Guías visuales específicas por documento
const guides = {
  INE: {
    aspectRatio: 1.586,  // Proporción estándar INE
    requiredFields: ['CURP', 'NOMBRE'],
    icon: '🪪'
  },
  CARTILLA: {
    aspectRatio: 1.414,  // A5
    requiredFields: ['CURP', 'NOMBRE'],
    icon: '📗'
  },
  OTRO: {
    aspectRatio: null,  // Cualquier formato
    requiredFields: ['NOMBRE'],
    icon: '📄'
  }
};
```

### Pantalla 3: Revisión Pre-Envío

```
┌──────────────────────────────────────┐
│  ✅ Revisar Antes de Enviar          │
├──────────────────────────────────────┤
│                                      │
│  📸 [Miniatura de foto capturada]    │
│                                      │
│  📋 Datos que se registrarán:        │
│  ─────────────────────────────────── │
│  Tipo: INE (Credencial)              │
│  Biológico: TDAP                     │
│  Dosis: Primera                      │
│  Operador: Juan Pérez (opcional)     │
│  ─────────────────────────────────── │
│                                      │
│  ℹ️ Los datos personales se          │
│     extraerán automáticamente del    │
│     documento con OCR                │
│                                      │
│  [◀ Regresar]    [Enviar ✓]         │
│                                      │
└──────────────────────────────────────┘
```

---

## 📅 Plan de Implementación (10-15 horas)

### **Día 1: Frontend Base (4-5 horas)**

#### Sesión 1: Setup + Estructura (2h)
- [x] ~~Crear repositorio separado `ocr-pipeline-capture`~~
- [ ] Estructura HTML/CSS base
- [ ] Configuración de PWA (manifest.json, service worker)
- [ ] Sistema de navegación entre pantallas

#### Sesión 2: Captura de Cámara (2-3h)
- [ ] Implementar Camera API
- [ ] Guías visuales adaptativas
- [ ] Validación básica de calidad
- [ ] Preview y confirmación

---

### **Día 2: Validación de Calidad (3-4 horas)**

#### Sesión 3: Validaciones Avanzadas (2h)
- [ ] Detección de bordes (OpenCV.js)
- [ ] Validación de resolución
- [ ] Validación de iluminación
- [ ] Validación de nitidez

#### Sesión 4: UX de Validación (1-2h)
- [ ] Feedback visual en tiempo real
- [ ] Guías de mejora ("Acerca más", "Más luz")
- [ ] Bloqueo de captura si no pasa validación

---

### **Día 3: Backend OCR Mejorado (3-4 horas)**

#### Sesión 5: Extracción Multi-Campo (2h)
- [ ] Módulo de clasificación de documentos
- [ ] Extractor universal de datos
- [ ] Extracción de nombre completo
- [ ] Extracción de fecha de nacimiento

#### Sesión 6: Validación Cruzada (1-2h)
- [ ] Validador de coherencia de datos
- [ ] Calculo automático de edad
- [ ] Extracción de sexo (CURP o texto)
- [ ] Normalización de datos

---

### **Día 4: Integración y Pruebas (2-3 horas)**

#### Sesión 7: Integración (1-2h)
- [ ] Conectar frontend con Drive API
- [ ] Actualizar estructura de Google Sheets
- [ ] Integrar con pipeline OCR existente
- [ ] Deploy en GitHub Pages

#### Sesión 8: Pruebas (1h)
- [ ] Pruebas con documentos reales
- [ ] Ajustes de UX según resultados
- [ ] Validación con 2-3 usuarios

---

## 🎯 Entregables Finales

### 1. **Frontend PWA** 
- ✅ URL: `https://srmz04.github.io/ocr-pipeline-capture/`
- ✅ Funciona offline
- ✅ Instalable en celular
- ✅ Validación de calidad
- ✅ Multi-documento

### 2. **Backend Mejorado**
- ✅ Extracción de 15+ campos
- ✅ Soporte para INE, Cartilla, otros
- ✅ Validación cruzada de datos
- ✅ >85% de precisión

### 3. **Google Sheets Actualizado**
- ✅ 20 columnas de datos
- ✅ Dashboard mejorado
- ✅ Detección de duplicados por CURP

### 4. **Documentación**
- ✅ Manual de usuario (para operadores)
- ✅ Guía de troubleshooting
- ✅ Video tutorial (opcional)

---

## 🚀 ¿Empezamos?

Propongo este orden de implementación:

**AHORA (Próximas 2 horas):**
1. Crear estructura del frontend
2. Implementar captura básica con selección de tipo de documento
3. Integración con Drive API

**MAÑANA (4-6 horas):**
1. Validación de calidad completa
2. Mejorar extracción de datos (multi-campo)
3. Validación cruzada

**PASADO MAÑANA (2-4 horas):**
1. PWA + offline
2. Pruebas finales
3. Deploy y documentación

¿Te parece bien este plan?
