# 🚨 SOLUCIÓN RÁPIDA - Error de Carpeta

## Problema Detectado

El error en GitHub Actions:
```
Carpeta 'CAMPAÑA_VACUNACION' no encontrada
```

Esto significa que el código está buscando la carpeta antigua (hay un bug en el código que no detecté).

## ✅ Solución Inmediata

### Opción 1: Renombrar carpeta en Drive (MÁS RÁPIDO)

1. Ve a Google Drive
2. Busca la carpeta `CAMPAÑA_VACUNACION`
3. Clic derecho > Renombrar
4. Cambia el nombre a: `MACROCENTRO`
5. Ejecuta el workflow nuevamente en GitHub

### Opción 2: Crear carpeta nueva

1. Ve a Google Drive
2. Crea una carpeta llamada `MACROCENTRO`
3. Dentro de ella, crea:
   - `ENTRADA`
   - `PROCESADAS`
   - `ERRORES`
   - `REVISIÓN`
4. Comparte TODAS las carpetas con la Service Account
5. Ejecuta el workflow nuevamente

---

## 🔍 Análisis del Bug

Revisando el log, veo que el error dice:
```
Carpeta 'CAMPAÑA_VACUNACION' no encontrada
```

Pero nuestro código debería buscar `MACROCENTRO`. Esto indica que hay un problema con cómo se está pasando el parámetro.

Déjame revisar el código...
