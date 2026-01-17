// Configuration for the capture app
const CONFIG = {
    // Google API - CREDENCIALES CONFIGURADAS ✅
    GOOGLE_API_KEY: 'AIzaSyBgS9f8i0NHkH6b0AYZy6musOhEOYadW4w',
    GOOGLE_CLIENT_ID: '640594634744-skq9inktjis8t7s2hd5rknrljkms0c9b.apps.googleusercontent.com',
    // Google Apps Script Proxy URL (v6 - OCR with Vision API enabled)
    PROXY_URL: 'https://script.google.com/macros/s/AKfycbw-8a5zVFGMDZ1i-hMPIGKumNmzVsNrqMF6QtHQ8e7fQiItoOCHwhQVJdzT9VGVHCC6/exec',
    DRIVE_FOLDER_ID: '16u48oAakKNZU3T1ttzvb9AqS8-IIQE_t', // Carpeta ENTRADAS
    SPREADSHEET_ID: '1BiWRVISIADl9mRzOJABQLtlLLm7VebRYtfd2CRCoqXI', // REGISTRO_MASTER

    // Validation thresholds - RELAXED FOR TESTING
    MIN_RESOLUTION: 640, // Was 1200
    MIN_BRIGHTNESS: 40,  // Was 80
    MAX_BRIGHTNESS: 250, // Was 180
    MIN_SHARPNESS: 10,   // Was 100
    MIN_CONFIDENCE: 0.3, // Was 0.6
    // Productos (Vacunas) disponibles
    PRODUCTOS: [
        { name: 'VITAMINAS ACD', dosis: ['Refuerzo Anual'] },
        { name: 'BCG', dosis: ['Única'] },
        { name: 'Hepatitis B', dosis: ['Primera', 'Segunda', 'Tercera'] },
        { name: 'Hexavalente', dosis: ['Primera', 'Segunda', 'Tercera', 'Cuarta'] },
        { name: 'Rotavirus', dosis: ['Primera', 'Segunda', 'Tercera'] },
        { name: 'Neumocócica Conjugada', dosis: ['Primera', 'Segunda', 'Refuerzo'] },
        { name: 'Influenza', dosis: ['Primera', 'Segunda', 'Revacunación'] },
        { name: 'SRP (Triple Viral)', dosis: ['Primera', 'Segunda'] },
        { name: 'DPT', dosis: ['Refuerzo'] },
        { name: 'VPH', dosis: ['Única'] },
        { name: 'COVID', dosis: ['1ra', '2da', 'Refuerzo Anual'] },
        { name: 'SR', dosis: ['Cero', 'Primera', 'Segunda', 'Refuerzo'] },
        { name: 'TD', dosis: ['Primera', 'Segunda', 'Tercera'] }
    ],

    // UI Settings
    AUTO_CAPTURE_DELAY: 1000, // ms to wait before auto-capture
    TOAST_DURATION: 3000,

    // Storage keys
    STORAGE_PRODUCTO: 'lastProducto',
    STORAGE_DOSIS: 'lastDosis',
    STORAGE_COUNT: 'countToday',
    STORAGE_DATE: 'date',
};

// Export for use in other modules
window.CONFIG = CONFIG;
