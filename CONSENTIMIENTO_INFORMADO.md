# 📋 Consentimiento Informado - Registro Fotográfico

## ⚖️ Aspectos Legales y Éticos

### Importancia del Consentimiento Informado

El registro fotográfico de credenciales (INE/Cartilla) implica la **captura y procesamiento de datos personales sensibles**. Es **OBLIGATORIO** obtener el consentimiento informado de cada persona antes de tomar la fotografía.

---

## 📄 Formato de Consentimiento Informado (Papel)

### Plantilla Sugerida

```
═══════════════════════════════════════════════════════════════
                    CONSENTIMIENTO INFORMADO
           REGISTRO FOTOGRÁFICO - CAMPAÑA DE VACUNACIÓN
═══════════════════════════════════════════════════════════════

Fecha: ___/___/______                    Folio: _______________

DATOS DEL TITULAR

Nombre completo: ________________________________________________

CURP: ___________________________________________________________

Edad: _______  Sexo: M ( ) F ( )


DECLARACIÓN DE CONSENTIMIENTO

Yo, el/la titular arriba mencionado/a, declaro que:

1. He sido informado/a de manera clara y comprensible sobre el 
   propósito del registro fotográfico de mi credencial oficial.

2. Entiendo que la fotografía será utilizada EXCLUSIVAMENTE para:
   ☑ Registro de vacunación
   ☑ Extracción automática de datos (nombre, CURP, sexo)
   ☑ Almacenamiento en base de datos centralizada

3. Autorizo expresamente:
   ☑ La toma de fotografía de mi credencial oficial (INE/Cartilla)
   ☑ El procesamiento automático mediante tecnología OCR
   ☑ El almacenamiento de mis datos en Google Drive/Sheets
   ☑ El uso de mis datos para fines estadísticos de la campaña

4. He sido informado/a de mis derechos ARCO:
   • Acceso: Consultar mis datos personales
   • Rectificación: Corregir datos incorrectos
   • Cancelación: Solicitar eliminación de mis datos
   • Oposición: Oponerse al tratamiento de mis datos

5. Entiendo que puedo ejercer mis derechos ARCO contactando a:
   Responsable: _______________________________________________
   Correo: ____________________________________________________
   Teléfono: __________________________________________________


PROTECCIÓN DE DATOS

• Los datos serán tratados conforme a la Ley Federal de Protección
  de Datos Personales en Posesión de Particulares.
• Las fotografías serán almacenadas de forma segura y encriptada.
• Solo personal autorizado tendrá acceso a los datos.
• Los datos NO serán compartidos con terceros sin autorización.
• Los datos serán conservados por el tiempo necesario para la
  campaña de vacunación y posteriormente eliminados.


FIRMA DEL TITULAR

_____________________________        _____________________________
Firma del Titular                    Huella Digital (opcional)


TESTIGOS (opcional)

_____________________________        _____________________________
Nombre y Firma Testigo 1             Nombre y Firma Testigo 2


DATOS DEL OPERADOR

Nombre del operador: ____________________________________________

Firma del operador: _____________________________________________

═══════════════════════════════════════════════════════════════
```

---

## 🔧 Implementación del Proceso

### Flujo de Trabajo con Consentimiento

```
1. Llegada del beneficiario
   ↓
2. Explicación del proceso (30 seg)
   ↓
3. Firma de consentimiento informado
   ↓
4. Toma de fotografía de credencial
   ↓
5. Subida a carpeta ENTRADA/ en Drive
   ↓
6. Archivo de consentimiento físico
   ↓
7. Procesamiento automático (OCR)
```

### Tiempos Estimados

| Actividad | Tiempo |
|-----------|--------|
| Explicación | 30 seg |
| Firma de consentimiento | 20 seg |
| Toma de foto | 10 seg |
| **Total por persona** | **~1 min** |

---

## 📦 Almacenamiento de Consentimientos

### Opciones de Almacenamiento

#### Opción 1: Archivo Físico (Recomendado para bajo volumen)

- **Carpeta física** con separadores por fecha
- Organización: `AAAA-MM-DD/Folio_XXXX.pdf`
- Escaneo periódico (semanal) para respaldo digital

#### Opción 2: Digitalización Inmediata (Recomendado para alto volumen)

- Escanear consentimiento con app móvil (CamScanner, Adobe Scan)
- Subir a carpeta Drive: `MACROCENTRO/CONSENTIMIENTOS/`
- Vincular con registro en Sheets (columna: `LINK_CONSENTIMIENTO`)

#### Opción 3: Híbrido (Más Seguro)

- Firma física + foto del consentimiento
- Almacenamiento físico + digital

---

## 🔗 Vinculación con Registro Fotográfico

### Modificación a Google Sheets

Agregar columna adicional en `REGISTRO_MASTER`:

| Columna | Descripción |
|---------|-------------|
| `FOLIO_CONSENTIMIENTO` | Número de folio del consentimiento |
| `LINK_CONSENTIMIENTO` | Link a PDF escaneado en Drive |
| `FECHA_CONSENTIMIENTO` | Fecha de firma |
| `OPERADOR_REGISTRO` | Nombre del operador que tomó el consentimiento |

### Ejemplo de Registro Completo

```
FECHA_HORA: 2025-12-05 10:30:00
NOMBRE_ARCHIVO: IMG_20251205_103000.jpg
CURP_DETECTADA: GOMJ850615HDFRNN09
FOLIO_CONSENTIMIENTO: 2025-001234
LINK_CONSENTIMIENTO: https://drive.google.com/file/d/abc123.../view
FECHA_CONSENTIMIENTO: 2025-12-05
OPERADOR_REGISTRO: Juan Pérez
STATUS: PROCESADO
LINK_FOTO: https://drive.google.com/file/d/xyz789.../view
```

---

## ⚠️ Consideraciones Legales

### Obligaciones del Responsable

1. **Aviso de Privacidad**: Tener disponible el aviso de privacidad
2. **Seguridad**: Implementar medidas de seguridad física y digital
3. **Confidencialidad**: Capacitar al personal en protección de datos
4. **Retención**: Definir tiempo de conservación de datos
5. **Eliminación**: Proceso seguro de eliminación al término de la campaña

### Sanciones por Incumplimiento

El incumplimiento de la Ley de Protección de Datos puede resultar en:
- Multas económicas
- Responsabilidad civil
- Daño reputacional

---

## 📝 Checklist de Implementación

### Antes de Iniciar la Campaña

- [ ] Diseñar formato de consentimiento informado
- [ ] Imprimir formatos (estimar 2,500 + 10% extra = 2,750)
- [ ] Capacitar operadores en:
  - [ ] Explicación del proceso
  - [ ] Obtención de firma
  - [ ] Manejo de objeciones
  - [ ] Derechos ARCO
- [ ] Definir proceso de almacenamiento
- [ ] Crear carpeta `CONSENTIMIENTOS/` en Drive (si aplica)
- [ ] Agregar columnas en Google Sheets
- [ ] Preparar carpetas físicas de archivo

### Durante la Campaña

- [ ] Verificar firma antes de tomar foto
- [ ] Asignar folio consecutivo
- [ ] Archivar consentimientos diariamente
- [ ] Escanear lotes semanalmente (si aplica)

### Después de la Campaña

- [ ] Resguardar consentimientos físicos (mínimo 2 años)
- [ ] Mantener respaldos digitales encriptados
- [ ] Definir fecha de eliminación de datos
- [ ] Ejecutar eliminación segura al término del periodo

---

## 🆘 Preguntas Frecuentes

### ¿Qué hago si alguien se niega a firmar?

**Respuesta**: No se puede tomar la fotografía ni procesar sus datos. Ofrecer registro manual tradicional como alternativa.

### ¿Puedo tomar la foto sin consentimiento si es urgente?

**Respuesta**: **NO**. El consentimiento es obligatorio sin excepciones.

### ¿Qué hago con menores de edad?

**Respuesta**: El consentimiento debe ser firmado por el padre/madre o tutor legal.

### ¿Cuánto tiempo debo guardar los consentimientos?

**Respuesta**: Mínimo 2 años después de finalizada la campaña, o según normativa local.

---

## 📞 Contacto Legal

Para dudas sobre aspectos legales, consultar con:
- Departamento Jurídico de la institución
- Asesor en Protección de Datos
- INAI (Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales)

---

**IMPORTANTE**: Este documento es una guía general. Consulta con un abogado especializado en protección de datos para adaptar el consentimiento a tu caso específico y jurisdicción.
