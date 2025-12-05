# 🚀 UX Final: Selector Rápido Sin Configuración

## 📱 Interfaz Definitiva

```
┌──────────────────────────────────────┐
│ 📷 Captura              [←] [?]      │ ← Mínimo
├──────────────────────────────────────┤
│                                      │
│  ╔══════════════════════════════╗   │
│  ║                              ║   │
│  ║     [Vista de Cámara]        ║   │
│  ║                              ║   │
│  ║  🟢 INE detectada - Listo    ║   │
│  ║                              ║   │
│  ║  ┌────────────────────┐      ║   │
│  ║  │  Marco adaptativo  │      ║   │
│  ║  └────────────────────┘      ║   │
│  ╚══════════════════════════════╝   │
│                                      │
├─ BIOLÓGICO ─────────────────────────┤
│  [TDAP] [Neumococo] [Influenza]     │ ← 1 toque
│  [Sarampión] [Hepatitis] [Otro...]  │
│                                      │
├─ DOSIS (si aplica) ─────────────────┤
│  [1ª] [2ª] [3ª] [Refuerzo] [Única] │ ← 1 toque
│                                      │
│         [● CAPTURAR]                 │ ← Total: 3 toques máx
│                                      │
│  Hoy: 47  Última: 14:23             │
└──────────────────────────────────────┘
```

---

## ⚡ Flujo Ultra-Simplificado

### Flujo Completo (3 toques máximo)

```
1. Abrir app → Cámara activa
2. Encuadrar documento → Auto-detecta
3. [Toque 1] Seleccionar biológico (ej: TDAP)
4. [Toque 2] Seleccionar dosis (ej: 1ª)
5. [Toque 3] CAPTURAR
   
Total: 3 toques, ~10 segundos
```

### Optimización: Último Usado Pre-seleccionado

```
┌─ BIOLÓGICO ─────────────────────────┐
│  [TDAP✓] [Neumococo] [Influenza]   │ ← Último usado marcado
│  [Sarampión] [Hepatitis] [Otro...]  │
│                                      │
├─ DOSIS ─────────────────────────────┤
│  [1ª✓] [2ª] [3ª] [Refuerzo]        │ ← Última usada marcada
└──────────────────────────────────────┘

Si el siguiente paciente recibe lo mismo:
→ Solo [CAPTURAR] = 1 toque
```

---

## 🎨 Diseño de Selectores

### Chips de Biológico (Horizontal Scroll)

```html
<div class="bio-selector">
  <button class="bio-chip active">TDAP</button>
  <button class="bio-chip">Neumococo</button>
  <button class="bio-chip">Influenza</button>
  <button class="bio-chip">Sarampión</button>
  <button class="bio-chip">Hepatitis B</button>
  <button class="bio-chip">BCG</button>
  <button class="bio-chip">Rotavirus</button>
  <button class="bio-chip">Otro...</button>
</div>
```

**CSS**:
```css
.bio-chip {
  display: inline-block;
  padding: 12px 20px;
  margin: 4px;
  border-radius: 20px;
  background: #f0f0f0;
  border: 2px solid transparent;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s;
}

.bio-chip.active {
  background: #4CAF50;
  color: white;
  border-color: #45a049;
  transform: scale(1.05);
}
```

### Chips de Dosis (Auto-adapta según biológico)

```javascript
const dosisSchemes = {
  'TDAP': ['1ª', '2ª', 'Refuerzo'],
  'Neumococo': ['1ª', '2ª', '3ª', 'Refuerzo'],
  'Influenza': ['Única', 'Anual'],
  'Sarampión': ['1ª', '2ª'],
  'Hepatitis B': ['1ª', '2ª', '3ª']
};

// Al seleccionar biológico, actualiza opciones de dosis
function updateDosisOptions(biologico) {
  const dosis = dosisSchemes[biologico] || ['1ª', '2ª', '3ª'];
  renderDosisChips(dosis);
}
```

---

## 🚀 Comportamiento Inteligente

### 1. **Memoria de Sesión**

```javascript
// Guardar en localStorage
sessionStorage.setItem('lastBiologico', 'TDAP');
sessionStorage.setItem('lastDosis', '1ª');

// Pre-seleccionar al abrir
onLoad(() => {
  const lastBio = sessionStorage.getItem('lastBiologico');
  const lastDosis = sessionStorage.getItem('lastDosis');
  
  if (lastBio) selectBiologico(lastBio);
  if (lastDosis) selectDosis(lastDosis);
});
```

### 2. **Validación Visual**

```
Estado del botón CAPTURAR:

❌ Deshabilitado (gris):
   - Calidad de foto baja
   - O biológico no seleccionado
   - O dosis no seleccionada

✅ Habilitado (verde):
   - Foto OK + Biológico + Dosis
   - Listo para capturar
```

### 3. **Feedback Instantáneo**

```javascript
// Al seleccionar biológico
onClick_Biologico = (name) => {
  selectBiologico(name);
  playClick();  // Sonido
  vibrate(50);  // Vibración corta
  
  // Auto-seleccionar primera dosis si aplica
  if (dosisSchemes[name].length === 1) {
    selectDosis(dosisSchemes[name][0]);
  }
};
```

---

## 📊 Comparativa Final

| Acción | Toques | Tiempo |
|--------|--------|--------|
| **Mismo biológico/dosis** | 1 | ~5s |
| **Cambiar solo dosis** | 2 | ~7s |
| **Cambiar biológico + dosis** | 3 | ~10s |
| **Promedio estimado** | 1.5 | ~7s |

**Capacidad**: 10 ops × 8h × 450/h = **36,000/día**

---

## 💡 Variación: Modo "Campaña"

Para campañas donde **todos reciben lo mismo**:

```
┌──────────────────────────────────────┐
│  Modo Campaña Activo: TDAP 1ª dosis │ ← Banner
├──────────────────────────────────────┤
│  [Cambiar] [Desactivar]              │
└──────────────────────────────────────┘

→ Biológico y dosis bloqueados
→ Solo CAPTURAR = 1 toque
→ Habilitar/deshabilitar con 1 toque
```

Activación rápida:
- Mantener presionado chip de biológico por 2s
- Popup: "¿Activar modo campaña para TDAP?"
- [Sí] → Todos los siguientes usan TDAP + última dosis

---

## 🎯 HTML Final Simplificado

```html
<!DOCTYPE html>
<html lang="es">
<body>
  
  <!-- Header -->
  <header>
    <h1>📷 Captura</h1>
    <button id="history">←</button>
    <button id="help">?</button>
  </header>
  
  <!-- Cámara -->
  <main>
    <video id="camera" autoplay playsinline></video>
    <div id="status">🟢 Listo</div>
  </main>
  
  <!-- Selector Biológico -->
  <section class="selector">
    <label>BIOLÓGICO</label>
    <div class="bio-chips" id="bio-selector">
      <!-- Generado dinámicamente -->
    </div>
  </section>
  
  <!-- Selector Dosis -->
  <section class="selector">
    <label>DOSIS</label>
    <div class="dosis-chips" id="dosis-selector">
      <!-- Generado según biológico -->
    </div>
  </section>
  
  <!-- Botón Captura -->
  <button id="capture" disabled>
    ● CAPTURAR
  </button>
  
  <!-- Stats -->
  <footer>
    Hoy: <span id="count">47</span>
  </footer>
  
</body>
</html>
```

---

## ✅ Ventajas de Este Diseño

1. ✅ **Cero configuración** - Todo en una pantalla
2. ✅ **Máx 3 toques** - Biológico + Dosis + Capturar
3. ✅ **Memoria automática** - Recuerda último usado
4. ✅ **Modo campaña** opcional - Para flujo continuo
5. ✅ **Visual claro** - Estado siempre visible
6. ✅ **Adaptativo** - Dosis según biológico

¿Procedo con la implementación?
