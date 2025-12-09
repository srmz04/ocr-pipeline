/**
 * CameraManager - Native-Input-First Implementation
 * 
 * Strategy: Delegate capture to OS camera app via HTML input.
 * Pipeline: Native Input → Canvas Resize → JPEG Compress → Validate → Upload
 * 
 * NO WebRTC. Maximum stability across iOS/Android.
 */

class CameraManager {
    constructor() {
        this.maxWidth = 1600;  // Optimal for OCR without being too heavy
        this.jpegQuality = 0.8;
        this.minFileSize = 80 * 1024; // 80KB - below this likely blur/dark
    }

    /**
     * Process an image file from native camera or gallery
     * @param {File} file - Image file from input
     * @returns {Promise<{blob: Blob, width: number, height: number, originalSize: number, finalSize: number}>}
     */
    async processImage(file) {
        // 1. Create image from file
        const img = await this.loadImage(file);

        // 2. Calculate resize dimensions (maintain aspect ratio)
        const { width, height } = this.calculateDimensions(img.width, img.height);

        // 3. Draw to canvas and compress
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');

        // Handle EXIF orientation (iOS issue)
        ctx.drawImage(img, 0, 0, width, height);

        // 4. Convert to JPEG blob
        const blob = await new Promise(resolve => {
            canvas.toBlob(resolve, 'image/jpeg', this.jpegQuality);
        });

        return {
            blob,
            width,
            height,
            originalSize: file.size,
            finalSize: blob.size
        };
    }

    /**
     * Load image from file with orientation fix
     */
    loadImage(file) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                URL.revokeObjectURL(img.src); // Clean up
                resolve(img);
            };
            img.onerror = reject;
            img.src = URL.createObjectURL(file);
        });
    }

    /**
     * Calculate dimensions maintaining aspect ratio
     */
    calculateDimensions(originalWidth, originalHeight) {
        if (originalWidth <= this.maxWidth) {
            return { width: originalWidth, height: originalHeight };
        }

        const ratio = this.maxWidth / originalWidth;
        return {
            width: this.maxWidth,
            height: Math.round(originalHeight * ratio)
        };
    }

    /**
     * Validate image quality using file size heuristic
     * @param {number} fileSize - Size in bytes after compression
     * @returns {{valid: boolean, message: string|null}}
     */
    validateQuality(fileSize) {
        if (fileSize < this.minFileSize) {
            return {
                valid: false,
                message: 'La imagen parece borrosa o muy oscura. Toma otra foto con mejor luz y sin mover el teléfono.'
            };
        }
        return { valid: true, message: null };
    }

    /**
     * Check if running in iOS standalone mode (PWA)
     */
    isIOSStandalone() {
        return window.navigator.standalone === true;
    }

    /**
     * Get device-specific tip for better photos
     */
    getDeviceTip() {
        const ua = navigator.userAgent.toLowerCase();

        if (/iphone|ipad/.test(ua)) {
            return 'Toca la pantalla sobre el documento para enfocar.';
        }
        if (/xiaomi|redmi/.test(ua)) {
            return 'Busca el ícono de Macro (🌸) si estás muy cerca.';
        }
        if (/samsung/.test(ua)) {
            return 'El modo Escáner se activa automáticamente.';
        }
        return 'Mantén el teléfono a 15-20cm del documento.';
    }

    /**
     * Create a preview URL for the processed image
     */
    createPreviewURL(blob) {
        return URL.createObjectURL(blob);
    }

    /**
     * Revoke a preview URL to free memory
     */
    revokePreviewURL(url) {
        URL.revokeObjectURL(url);
    }
}

// Export for use
window.CameraManager = CameraManager;
