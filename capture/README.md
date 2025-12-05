# 📱 Frontend de Captura - Guía de Uso

## 🚀 ¿Qué es esto?

Interfaz web móvil para captura rápida de documentos durante vacunación.

## ✨ Características

- ✅ **Cámara inmediata** - Abre directo en captura
- ✅ **Validación en tiempo real** - Verifica calidad automáticamente
- ✅ **Selector rápido** - Biológico y dosis en 2-3 toques
- ✅ **Memoria inteligente** - Recuerda última selección
- ✅ **Contador de pacientes** - Estadísticas del día

## 📦 Archivos

```
capture/
├── index.html      # Estructura HTML principal
├── styles.css      # Estilos responsive
├── config.js       # Configuración
├── camera.js       # Manejo de cámara
├── validator.js    # Validación de calidad
├── uploader.js     # Subida a Drive/Sheets
└── app.js          # Lógica principal
```

## 🧪 Prueba Local

```bash
# Opción 1: Python simple server
cd capture
python3 -m http.server 8000

# Abrir en: http://localhost:8000
```

Para probar en celular en la misma red:
```bash
# Encontrar IP local
ip addr show | grep inet

# Abrir en celular: http://192.168.x.x:8000
```

## 🌐 Deploy a GitHub Pages

1. Commit y push:
```bash
git add capture/
git commit -m "Add: Frontend de captura móvil"
git push
```

2. Configurar GitHub Pages:
   - Ve a repositorio → Settings → Pages
   - Source: Deploy from branch
   - Branch: main, folder: /capture
   - Save

3. La app estará en:
   ```
   https://srmz04.github.io/ocr-pipeline/
   ```

## 📱 Instalación en Celular

1. Abrir URL en navegador móvil
2. Menú → "Agregar a pantalla de inicio"
3. La app se instalará como nativa

## ⚙️ Configuración de APIs

Editar `config.js`:

```javascript
const CONFIG = {
    DRIVE_FOLDER_ID: 'TU_FOLDER_ID_AQUI',
    SPREADSHEET_ID: 'TU_SPREADSHEET_ID_AQUI',
    // ... resto de config
};
```

## 🎯 Flujo de Uso

1. **Abrir app** → Cámara activa
2. **Seleccionar biológico** → [TDAP]
3. **Seleccionar dosis** → [1ª]
4. **Encuadrar documento** → Esperar 🟢
5. **Capturar** → Listo!

## 🔧 Troubleshooting

### Cámara no funciona
- Verificar permisos del navegador
- HTTPS requerido para cámara (excepto localhost)
- GitHub Pages ya tiene HTTPS

### No se puede capturar
- Verificar que haya seleccionado biológico Y dosis
- Esperar señal verde (calidad OK)

### No sube fotos
- Verificar config de Drive API (próximamente)
- Por ahora guarda en localStorage local

## 🚀 Próximos Pasos

- [ ] Integrar Google Drive API real
- [ ] Integrar Google Sheets API
- [ ] Service Worker para modo offline
- [ ] Auto-captura cuando calidad OK
- [ ] Modo campaña (lock biológico/)

## 📊 Estado Actual

**Completado:**
- ✅ UI completa y responsive
- ✅ Camera API
- ✅ Validación de calidad en tiempo real
- ✅ Selectors de biológico/dosis
- ✅ Estado persistente (localStorage)
- ✅ Feedback visual y háptico

**Pendiente:**
- ⏳ Integración Drive/Sheets (usa simulación)
- ⏳ PWA offline support
- ⏳ Optimizaciones de rendimiento

---

**Versión:** 1.0.0-alpha  
**Última actualización:** 2025-12-05
