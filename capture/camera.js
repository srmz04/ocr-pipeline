// Camera module - handles video stream and capture
class CameraManager {
    constructor() {
        this.video = document.getElementById('camera');
        this.stream = null;
        this.facingMode = 'environment'; // Rear camera by default
    }

    async initialize() {
        try {
            // Standard recommended constraints for high-quality ID capture
            // We prioritize resolution to ensure text is readable
            const constraints = {
                video: {
                    facingMode: 'environment', // Force back camera
                    width: { ideal: 1920 },    // Full HD ideal
                    height: { ideal: 1080 },
                    // Try to force main lens instead of wide/ultra-wide if possible
                    advanced: [{ zoom: 1 }]
                },
                audio: false
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;

            // Wait for video to actually play to avoid empty snaps
            await new Promise((resolve) => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    resolve();
                };
            });

            return true;
        } catch (error) {
            console.error('Camera error:', error);
            this.showError('No se pudo acceder a la cámara');
            return false;
        }
    }

    captureFrame() {
        // WYSIWYG Strategy: Capture the full frame exactly as provided by the sensor.
        // The user positions the physical phone to frame the ID using the visual guides.
        // We do NO cropping here to prevent aspect ratio mismatches. 
        // We rely on the CSS 'object-fit: contain' to show the user the REAL view.

        const canvas = document.createElement('canvas');
        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;

        const ctx = canvas.getContext('2d');

        // Draw full video frame
        ctx.drawImage(this.video, 0, 0, canvas.width, canvas.height);

        return canvas;
    }

    captureBlob(quality = 0.92) {
        const canvas = this.captureFrame();

        return new Promise((resolve) => {
            canvas.toBlob((blob) => {
                resolve(blob);
            }, 'image/jpeg', quality);
        });
    }

    switchCamera() {
        this.facingMode = this.facingMode === 'environment' ? 'user' : 'environment';
        this.stop();
        this.initialize();
    }

    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }

    showError(message) {
        window.app.showToast(message, 'error');
    }
}

window.CameraManager = CameraManager;
