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
        // WYSIWYG Strategy with Rotation Correction
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        const vWidth = this.video.videoWidth;
        const vHeight = this.video.videoHeight;

        // Check if we need to rotate (Mobile browsers often give landscape stream even in portrait)
        // If window is portrait but video is landscape, we likely need rotation
        const isPortrait = window.innerHeight > window.innerWidth;
        const isVideoLandscape = vWidth > vHeight;

        if (isPortrait && isVideoLandscape) {
            // Uncommment to debug: console.log('Auto-rotating capture for portrait mode');

            // Swap dimensions for the canvas
            canvas.width = vHeight;
            canvas.height = vWidth;

            // Rotate context 90 degrees
            ctx.translate(vHeight, 0);
            ctx.rotate(Math.PI / 2);

            // Draw original video (landscape) into rotated context
            ctx.drawImage(this.video, 0, 0, vWidth, vHeight);
        } else {
            // Standard capture
            canvas.width = vWidth;
            canvas.height = vHeight;
            ctx.drawImage(this.video, 0, 0, vWidth, vHeight);
        }

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
