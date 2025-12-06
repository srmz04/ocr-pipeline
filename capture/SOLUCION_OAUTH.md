# 🔐 Solución: Error 403 access_denied (OAuth)

¡Buenas noticias! El botón de captura **YA FUNCIONA** (por eso te salió la ventana de login).
El error que ves ahora es de seguridad de Google: tu App está en modo "Pruebas" y tu email no está en la lista de invitados.

## 🛠️ Pasos para Autorizar tu Email

1. Ve a: [**Google Cloud Console > Pantalla de consentimiento**](https://console.cloud.google.com/apis/credentials/consent)
   *(O busca "OAuth consent screen" en el buscador de arriba)*

2. Mira el **"Estado de la publicación"** (Publishing status).
   - Seguramente dice **"Testing"** (Prueba).

3. Baja hasta la sección **"Test users"** (Usuarios de prueba).
   - Haz clic en el botón **+ ADD USERS** (Agregar usuarios).

4. **Escribe tu correo electrónico** (el mismo con el que intentas iniciar sesión en la ventana que falló).
   - Haz clic en **SAVE** (Guardar).

---

## 🔄 Prueba Final

1. Vuelve a `http://localhost:9000`.
2. Refresca la página.
3. Selecciona Biológico + Dosis.
4. Dale a **CAPTURAR**.
5. Cuando salga la ventana de Google, selecciona tu cuenta.
6. Si te sale una pantalla de "Google hasn't verified this app" (Google no ha verificado esta app), dale a:
   - **Advanced** (Avanzado)
   - **Go to ocr-vacunacion (unsafe)** (Ir a... no seguro).

¡Y listo! Debería subir la foto.
