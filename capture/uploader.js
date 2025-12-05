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
            const row = [
                now.toISOString(),                    // FECHA_HORA_CAPTURA
                'WEB_CAPTURE',                        // TIPO_DOCUMENTO
                '',                                   // NOMBRE (lo llenará OCR)
                '',                                   // APELLIDO_PATERNO
                '',                                   // APELLIDO_MATERNO
                '',                                   // NOMBRE_COMPLETO
                '',                                   // CURP
                '',                                   // FECHA_NACIMIENTO
                '',                                   // EDAD
                '',                                   // SEXO
                '',                                   // ESTADO
                '',                                   // MUNICIPIO
                '',                                   // CLAVE_ELECTOR
                data.biologico,                       // BIOLOGICO
                data.dosis,                           // DOSIS
                '',                                   // CONFIANZA_OCR (lo llenará OCR)
                '',                                   // TEXTO_EXTRAIDO
                'PENDIENTE_OCR',                      // STATUS
                data.fileUrl,                         // LINK_FOTO
                data.operador || 'web',               // OPERADOR
                data.observaciones || ''              // OBSERVACIONES
            ];

            // Append to sheet
            const response = await gapi.client.sheets.spreadsheets.values.append({
                spreadsheetId: CONFIG.SPREADSHEET_ID,
                range: 'REGISTRO_MASTER!A:U',
                valueInputOption: 'USER_ENTERED',
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

window.DriveUploader = DriveUploader;
