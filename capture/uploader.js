class DriveUploader {
    constructor(apiClient) {
        this.apiClient = apiClient;
    }

    async initialize() {
        // Ensure API client is ready
        if (!this.apiClient.isInitialized) {
            console.warn('Google API not initialized yet');
            return false;
        }

        console.log('✅ Drive uploader initialized');
        return true;
    }

    async uploadPhoto(blob, metadata) {
        try {
            // Ensure authentication
            const isAuth = await this.apiClient.ensureAuth();
            if (!isAuth) {
                throw new Error('Autenticación cancelada');
            }

            const filename = `captura_${Date.now()}.jpg`;

            // Create metadata for Drive
            const fileMetadata = {
                name: filename,
                parents: [CONFIG.DRIVE_FOLDER_ID],
                description: `${metadata.biologico} - ${metadata.dosis}`,
            };

            // Create multipart body
            const boundary = '-------314159265358979323846';
            const delimiter = "\r\n--" + boundary + "\r\n";
            const close_delim = "\r\n--" + boundary + "--";

            const metadataBody = JSON.stringify(fileMetadata);

            // Convert blob to base64
            const reader = new FileReader();
            const base64Data = await new Promise((resolve) => {
                reader.onloadend = () => {
                    const base64 = reader.result.split(',')[1];
                    resolve(base64);
                };
                reader.readAsDataURL(blob);
            });

            // Build multipart request body
            const multipartRequestBody =
                delimiter +
                'Content-Type: application/json; charset=UTF-8\r\n\r\n' +
                metadataBody +
                delimiter +
                'Content-Type: image/jpeg\r\n' +
                'Content-Transfer-Encoding: base64\r\n\r\n' +
                base64Data +
                close_delim;

            // Upload to Drive
            const response = await gapi.client.request({
                path: '/upload/drive/v3/files',
                method: 'POST',
                params: { uploadType: 'multipart' },
                headers: {
                    'Content-Type': 'multipart/related; boundary="' + boundary + '"',
                },
                body: multipartRequestBody,
            });

            const fileId = response.result.id;

            // Make file accessible (view link)
            await gapi.client.drive.permissions.create({
                fileId: fileId,
                resource: {
                    type: 'anyone',
                    role: 'reader',
                },
            });

            return {
                success: true,
                fileId: fileId,
                filename: filename, // Return generated filename
                url: `https://drive.google.com/file/d/${fileId}/view`
            };

        } catch (error) {
            console.error('Upload error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    async uploadToSheets(data) {
        try {
            // Ensure authentication
            const isAuth = await this.apiClient.ensureAuth();
            if (!isAuth) {
                throw new Error('Autenticación cancelada');
            }

            // Prepare row data
            const now = new Date();
            const safeFilename = data.filename || `captura_${now.getTime()}.jpg`;

            const row = [
                now.toISOString(),                    // 0: FECHA_HORA
                safeFilename,                         // 1: NOMBRE_ARCHIVO
                '',                                   // 2: CURP
                '',                                   // 3: CONFIANZA
                '',                                   // 4: NOMBRE
                '',                                   // 5: SEXO
                '',                                   // 6: TEXTO
                'PENDIENTE_OCR',                      // 7: STATUS
                data.fileUrl || '',                   // 8: LINK
                data.biologico || '',                 // 9: BIOLOGICO
                data.dosis || ''                      // 10: DOSIS
            ];

            console.log('📝 Appending row:', row);

            // Append to sheet - Anchor to Column A to prevent staircase
            const response = await gapi.client.sheets.spreadsheets.values.append({
                spreadsheetId: CONFIG.SPREADSHEET_ID,
                range: 'REGISTRO_MASTER!A:A',  // CRITICAL FIX: Anchor to Col A
                valueInputOption: 'USER_ENTERED',
                insertDataOption: 'INSERT_ROWS',
                resource: {
                    values: [row]
                }
            });

            return {
                success: true,
                updatedRange: response.result.updates.updatedRange
            };

        } catch (error) {
            console.error('Sheets error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// Mock Uploader for offline/fallback mode
class MockUploader {
    async initialize() {
        console.log('⚠️ Mock Uploader initialized (Offline Mode)');
        return true;
    }

    async uploadPhoto(blob, metadata) {
        console.log('📸 Mock upload photo:', metadata);
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate delay
        return {
            success: true,
            fileId: 'mock_file_' + Date.now(),
            url: URL.createObjectURL(blob) // Local URL for preview
        };
    }

    async uploadToSheets(data) {
        console.log('📝 Mock upload to sheets:', data);
        // Save to localStorage for persistence testing
        const offlineData = JSON.parse(localStorage.getItem('offline_captures') || '[]');
        offlineData.push({
            ...data,
            timestamp: new Date().toISOString()
        });
        localStorage.setItem('offline_captures', JSON.stringify(offlineData));

        return { success: true };
    }
}

window.DriveUploader = DriveUploader;
window.MockUploader = MockUploader;
