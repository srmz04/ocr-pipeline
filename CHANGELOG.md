# Changelog

Todos los cambios notables de este proyecto se documentan aquí.

## [2.2.0] - 2026-01-17

### Nuevas Funcionalidades
- **Alerta de Subida Exitosa**: Ahora aparece una alerta nativa del navegador cuando se completa una subida correctamente, además del Toast.
- **Nueva vacuna TD**: Añadida con dosis Primera, Segunda, Tercera.

### Cambios en Esquemas de Vacunación
- **Hepatitis B**: Actualizada a 3 dosis (Primera, Segunda, Tercera).
- **SR**: Se añadió dosis "Cero" (Cero, Primera, Segunda, Refuerzo).
- **COVID**: Cambiada nomenclatura a 1ra, 2da, Refuerzo Anual.
- **OTRA**: Opción eliminada del selector de productos.

### Correcciones
- Se corrigió bug donde los botones de producto estaban hardcodeados en HTML en lugar de generarse desde config.js.
- Se implementó cache busting (versión en query params) para forzar actualizaciones.
- Se actualizó versión del Service Worker a v2.

### Archivos Modificados
- `capture/app.js`: Añadida alerta de éxito.
- `capture/config.js`: Actualizados esquemas de vacunas.
- `capture/index.html`: Corregidos botones de producto, añadido indicador de versión.
- `capture/sw.js`: Actualizada versión de caché.

---

## [1.0.0] - 2025-12-10

### Estado Inicial
- Versión inicial del sistema de captura OCR.
- Soporte para captura nativa de cámara.
- Integración con Google Drive y Sheets via Proxy.
- PWA con soporte offline.
