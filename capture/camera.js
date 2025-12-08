// Camera module - handles video stream and capture
class CameraManager {
    constructor() {
        this.video = document.getElementById('camera');
        this.stream = null;
        this.facingMode = 'environment'; // Rear camera by default
    }

    async initialize() {
        try {
            const constraints = {
                video: {
                    facingMode: { ideal: this.facingMode }, // Use ideal to allow fallback
                    width: { ideal: 1280 }, // Lower resolution often defaults to main wide lens
                    height: { ideal: 720 }
                },
                audio: false
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;

            // Attempt to reset zoom
            const track = this.stream.getVideoTracks()[0];
            const capabilities = track.getCapabilities();
            if (capabilities.zoom) {
                try {
                    await track.applyConstraints({ advanced: [{ zoom: 1 }] });
                } catch (e) {
                    console.log('Zoom reset not supported:', e);
                }
            }

            return true;
        } catch (error) {
            console.error('Camera error:', error);
            this.showError('No se pudo acceder a la cámara');
            return false;
        }
    }

    captureFrame() {
        const canvas = document.createElement('canvas');
        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(this.video, 0, 0);

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
