// Uploader module - handles Google Drive upload
class DriveUploader {
    constructor() {
        this.accessToken = null;
    }

    async initialize() {
        // Initialize Google API client
        // This will be implemented with actual OAuth flow
        // For now, placeholder
        console.log('Drive uploader initialized');
    }

    async uploadPhoto(blob, metadata) {
        try {
            const filename = `captura_${Date.now()}.jpg`;

            // Create form data
            const formData = new FormData();
            formData.append('file', blob, filename);
            formData.append('metadata', JSON.stringify({
                biologico: metadata.biologico,
                dosis: metadata.dosis,
                timestamp: new Date().toISOString()
            }));

            // For MVP: upload to a simple endpoint
            // Later: implement full Google Drive API

            // Simulate upload delay
            await this.simulateUpload();

            return {
                success: true,
                fileId: 'simulated_' + Date.now(),
                url: `https://drive.google.com/file/d/simulated_${Date.now()}/view`
            };

        } catch (error) {
            console.error('Upload error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    async simulateUpload() {
        // Simula tiempo de subida
        return new Promise(resolve => setTimeout(resolve, 1500));
    }

    async uploadToSheets(data) {
        // TODO: Implement Google Sheets API integration
        console.log('Uploading to sheets:', data);

        // Save to localStorage for now
        const existing = JSON.parse(localStorage.getItem('registros') || '[]');
        existing.push({
            ...data,
            timestamp: new Date().toISOString()
        });
        localStorage.setItem('registros', JSON.stringify(existing));

        return { success: true };
    }
}

window.DriveUploader = DriveUploader;
