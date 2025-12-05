// Configuration for the capture app
const CONFIG = {
    // Google API - CREDENCIALES CONFIGURADAS ✅
    GOOGLE_API_KEY: 'AIzaSyBgS9f8i0NHkH6b0AYZy6musOhEOYadW4w',
    GOOGLE_CLIENT_ID: '640594634744-skq9inktjis8t7s2hd5rknrljkms0c9b.apps.googleusercontent.com',
    DRIVE_FOLDER_ID: '1pIqnbmu3SGwZkv6ZL6OzUbNzJ4UHYCq0', // Carpeta ENTRADAS
    SPREADSHEET_ID: '1BiWRVISIADl9mRzOJABQLtlLLm7VebRYtfd2CRCoqXI', // REGISTRO_MASTER

    // Validation thresholds
    MIN_RESOLUTION: 1200,
    MIN_BRIGHTNESS: 80,
    MAX_BRIGHTNESS: 180,
    MIN_SHARPNESS: 100,

    // Biológicos disponibles
    BIOLOGICOS: [
        { name: 'TDAP', dosis: ['1ª', '2ª', 'Refuerzo'] },
        { name: 'Neumococo', dosis: ['1ª', '2ª', '3ª', 'Refuerzo'] },
        { name: 'Influenza', dosis: ['Única', 'Anual'] },
        { name: 'Sarampión', dosis: ['1ª', '2ª'] },
        { name: 'Hepatitis B', dosis: ['1ª', '2ª', '3ª'] },
        { name: 'BCG', dosis: ['Única'] },
        { name: 'Rotavirus', dosis: ['1ª', '2ª', '3ª'] },
        { name: 'Otro', dosis: ['1ª', '2ª', '3ª', 'Refuerzo', 'Única'] }
    ],

    // UI Settings
    AUTO_CAPTURE_DELAY: 1000, // ms to wait before auto-capture
    TOAST_DURATION: 3000,

    // Storage keys
    STORAGE_BIOLOGICO: 'lastBiologico',
    STORAGE_DOSIS: 'lastDosis',
    STORAGE_COUNT: 'countToday',
    STORAGE_DATE: 'date',
};

// Export for use in other modules
window.CONFIG = CONFIG;
