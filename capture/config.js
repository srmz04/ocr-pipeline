// Configuration for the capture app
const CONFIG = {
    // Google Drive API
    DRIVE_API_KEY: '', // Will be set from GitHub Secrets or env
    DRIVE_CLIENT_ID: '', // Will be set from GitHub Secrets or env
    DRIVE_FOLDER_ID: '1pIqnbmu3SGwZkv6ZL6OzUbNzJ4UHYCq0/ENTRADAS', // From diagnostics

    // Spreadsheet
    SPREADSHEET_ID: '', // Will be set

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
