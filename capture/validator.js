// Validator module - checks image quality
class QualityValidator {
    constructor(camera) {
        this.camera = camera;
        this.isValidating = false;
        this.validationInterval = null;
    }

    startContinuousValidation(callback) {
        this.isValidating = true;

        this.validationInterval = setInterval(() => {
            if (this.isValidating) {
                const result = this.validateCurrentFrame();
                callback(result);
            }
        }, 500); // Check every 500ms
    }

    stopValidation() {
        this.isValidating = false;
        if (this.validationInterval) {
            clearInterval(this.validationInterval);
        }
    }

    validateCurrentFrame() {
        const canvas = this.camera.captureFrame();
        const ctx = canvas.getContext('2d');
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

        const checks = {
            resolution: this.checkResolution(canvas),
            brightness: this.checkBrightness(imageData),
            sharpness: this.checkSharpness(imageData),
        };

        const allValid = Object.values(checks).every(c => c.valid);

        return {
            valid: allValid,
            checks,
            message: this.getMessage(checks),
            status: allValid ? 'ready' : 'warning'
        };
    }

    checkResolution(canvas) {
        const minRes = CONFIG.MIN_RESOLUTION;
        const valid = canvas.width >= minRes;

        return {
            valid,
            value: canvas.width,
            message: valid ? 'Resolución OK' : 'Acerca más el documento'
        };
    }

    checkBrightness(imageData) {
        const data = imageData.data;
        let sum = 0;

        // Sample every 10th pixel for performance
        for (let i = 0; i < data.length; i += 40) {
            sum += (data[i] + data[i + 1] + data[i + 2]) / 3;
        }

        const avg = sum / (data.length / 40);
        const valid = avg >= CONFIG.MIN_BRIGHTNESS && avg <= CONFIG.MAX_BRIGHTNESS;

        return {
            valid,
            value: avg,
            message: this.getBrightnessMessage(avg)
        };
    }

    checkSharpness(imageData) {
        // Simple Laplacian variance for sharpness estimation
        const gray = this.toGrayscale(imageData);
        const variance = this.calculateLaplacianVariance(gray);
        const valid = variance > CONFIG.MIN_SHARPNESS;

        return {
            valid,
            value: variance,
            message: valid ? 'Enfoque OK' : 'Mantén firme el celular'
        };
    }

    toGrayscale(imageData) {
        const data = imageData.data;
        const gray = new Uint8ClampedArray(imageData.width * imageData.height);

        for (let i = 0; i < data.length; i += 4) {
            gray[i / 4] = (data[i] + data[i + 1] + data[i + 2]) / 3;
        }

        return { data: gray, width: imageData.width, height: imageData.height };
    }

    calculateLaplacianVariance(gray) {
        // Simplified Laplacian kernel
        const { data, width, height } = gray;
        let sum = 0;
        let count = 0;

        for (let y = 1; y < height - 1; y++) {
            for (let x = 1; x < width - 1; x += 5) { // Sample every 5th pixel
                const i = y * width + x;
                const lap = Math.abs(
                    -4 * data[i] +
                    data[i - 1] + data[i + 1] +
                    data[i - width] + data[i + width]
                );
                sum += lap;
                count++;
            }
        }

        return sum / count;
    }

    getBrightnessMessage(avg) {
        if (avg < CONFIG.MIN_BRIGHTNESS) return 'Muy oscuro - busca más luz';
        if (avg > CONFIG.MAX_BRIGHTNESS) return 'Muy brillante - evita reflejos';
        return 'Iluminación OK';
    }

    getMessage(checks) {
        const failed = Object.values(checks).find(c => !c.valid);
        return failed ? failed.message : '🟢 Listo para capturar';
    }
}

window.QualityValidator = QualityValidator;
