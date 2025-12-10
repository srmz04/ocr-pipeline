/**
 * Tesseract.js OCR Engine
 * 100% client-side OCR - no external APIs, no cost
 */

class TesseractOCR {
    constructor() {
        this.worker = null;
        this.isReady = false;
        this.isLoading = false;
    }

    /**
     * Initialize Tesseract worker (lazy load on first use)
     */
    async initialize(progressCallback = null) {
        if (this.isReady) return true;
        if (this.isLoading) {
            // Wait for existing initialization
            while (this.isLoading) {
                await new Promise(r => setTimeout(r, 100));
            }
            return this.isReady;
        }

        this.isLoading = true;

        try {
            console.log('[OCR] Initializing Tesseract.js...');

            // Create worker with Spanish language
            this.worker = await Tesseract.createWorker('spa', 1, {
                logger: (m) => {
                    if (progressCallback && m.progress) {
                        progressCallback(m.progress, m.status);
                    }
                    console.log('[OCR]', m.status, Math.round((m.progress || 0) * 100) + '%');
                }
            });

            this.isReady = true;
            this.isLoading = false;
            console.log('[OCR] Tesseract ready!');
            return true;

        } catch (error) {
            console.error('[OCR] Init error:', error);
            this.isLoading = false;
            return false;
        }
    }

    /**
     * Run OCR on image
     * @param {Blob|string} image - Image blob or base64 string
     * @returns {Object} - { success, rawText, extractedData }
     */
    async recognize(image) {
        if (!this.isReady) {
            const initialized = await this.initialize();
            if (!initialized) {
                return { success: false, error: 'Failed to initialize OCR' };
            }
        }

        try {
            console.log('[OCR] Starting recognition...');
            const result = await this.worker.recognize(image);
            const rawText = result.data.text;

            console.log('[OCR] Raw text length:', rawText.length);
            console.log('[OCR] Confidence:', result.data.confidence);

            // Extract structured data
            const extractedData = this.extractData(rawText);

            return {
                success: true,
                rawText: rawText,
                confidence: result.data.confidence,
                extractedData: extractedData
            };

        } catch (error) {
            console.error('[OCR] Recognition error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Extract structured data from raw OCR text
     */
    extractData(text) {
        const data = {
            curp: '',
            nombre: '',
            fechaNacimiento: '',
            edad: '',
            sexo: ''
        };

        // Normalize text
        const normalizedText = text.toUpperCase().replace(/\n/g, ' ');

        // 1. Extract CURP (18-character pattern)
        const curpPattern = /[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d/;
        const curpMatch = normalizedText.match(curpPattern);
        if (curpMatch) {
            data.curp = curpMatch[0];

            // Derive data from CURP
            const curpData = this.parseCURP(data.curp);
            if (curpData) {
                data.fechaNacimiento = curpData.fechaNacimiento;
                data.edad = curpData.edad;
                data.sexo = curpData.sexo;
            }
        }

        // 2. Try to extract name
        const nombrePatterns = [
            /NOMBRE[:\s]+([A-ZÁÉÍÓÚÑ\s]{3,50})/,
            /([A-ZÁÉÍÓÚÑ]{2,20}\s+[A-ZÁÉÍÓÚÑ]{2,20}\s+[A-ZÁÉÍÓÚÑ]{2,20})/
        ];

        for (const pattern of nombrePatterns) {
            const match = normalizedText.match(pattern);
            if (match && match[1]) {
                data.nombre = match[1].trim();
                break;
            }
        }

        // 3. Extract date patterns
        if (!data.fechaNacimiento) {
            const datePattern = /(\d{2})[\/\-](\d{2})[\/\-](\d{4})/;
            const dateMatch = normalizedText.match(datePattern);
            if (dateMatch) {
                data.fechaNacimiento = dateMatch[0];
            }
        }

        // 4. Extract age if mentioned
        if (!data.edad) {
            const agePattern = /(\d{1,3})\s*A[ÑN]OS/;
            const ageMatch = normalizedText.match(agePattern);
            if (ageMatch) {
                data.edad = ageMatch[1];
            }
        }

        return data;
    }

    /**
     * Parse CURP to extract embedded data
     */
    parseCURP(curp) {
        if (!curp || curp.length !== 18) return null;

        try {
            // Extract date from positions 5-10 (YYMMDD)
            const yearStr = curp.substring(4, 6);
            const monthStr = curp.substring(6, 8);
            const dayStr = curp.substring(8, 10);

            const year = parseInt(yearStr);
            const month = parseInt(monthStr);
            const day = parseInt(dayStr);

            // Determine century
            const fullYear = year <= 29 ? 2000 + year : 1900 + year;
            const fechaNacimiento = `${dayStr}/${monthStr}/${fullYear}`;

            // Calculate age
            const today = new Date();
            const birthDate = new Date(fullYear, month - 1, day);
            let edad = today.getFullYear() - birthDate.getFullYear();
            const m = today.getMonth() - birthDate.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                edad--;
            }

            // Extract sex
            const sexoChar = curp.charAt(10);
            const sexo = sexoChar === 'H' ? 'MASCULINO' : sexoChar === 'M' ? 'FEMENINO' : '';

            return { fechaNacimiento, edad: edad.toString(), sexo };

        } catch (e) {
            console.error('[OCR] Parse CURP error:', e);
            return null;
        }
    }

    /**
     * Terminate worker to free memory
     */
    async terminate() {
        if (this.worker) {
            await this.worker.terminate();
            this.worker = null;
            this.isReady = false;
        }
    }
}

// Global instance
window.ocrEngine = new TesseractOCR();
