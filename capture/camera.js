// Camera module - handles video stream and capture
class CameraManager {
    constructor() {
        this.video = document.getElementById('camera');
        this.stream = null;
        this.facingMode = 'environment'; // Rear camera by default
    }

    async initialize() {
        try {
            // standard constraints: High Res for better digital zoom
            const constraints = {
                video: {
                    facingMode: 'environment', // Force back camera
                    width: { ideal: 3840 },    // 4K ideal
                    height: { ideal: 2160 },
                    advanced: [{ focusMode: 'continuous' }]
                },
                audio: false
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;

            await new Promise((resolve) => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    resolve();
                };
            });

            return true;
        } catch (error) {
            console.error('Camera error:', error);
            return this.initializeFallback();
        }
    }

    async initializeFallback() {
        try {
            const constraints = {
                video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } }
            };
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;
            this.video.play();
            return true;
        } catch (e) {
            this.showError('No camera access');
            return false;
        }
    }

    captureFrame(zoomLevel = 1) {
        // Manual Digital Zoom Strategy
        // We crop the Source Image based on the zoomLevel slider.
        // zoomLevel 1 = Full Frame
        // zoomLevel 2 = 50% Crop (Center)

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        const vWidth = this.video.videoWidth;
        const vHeight = this.video.videoHeight;

        // Calculate Crop Dimensions based on Zoom
        // width = original / zoom
        const cropW = vWidth / zoomLevel;
        const cropH = vHeight / zoomLevel;

        // Center the crop
        const startX = (vWidth - cropW) / 2;
        const startY = (vHeight - cropH) / 2;

        // Detection of portrait mode for rotation
        const isPortrait = window.innerHeight > window.innerWidth;
        const isVideoLandscape = vWidth > vHeight;

        if (isPortrait && isVideoLandscape) {
            // Rotate output 90 deg
            canvas.width = cropH;
            canvas.height = cropW;

            ctx.translate(cropH, 0);
            ctx.rotate(Math.PI / 2);

            // Draw cropped area into rotated canvas
            ctx.drawImage(
                this.video,
                startX, startY, cropW, cropH,
                0, 0, cropW, cropH
            );
        } else {
            // Standard
            canvas.width = cropW;
            canvas.height = cropH;

            ctx.drawImage(
                this.video,
                startX, startY, cropW, cropH,
                0, 0, cropW, cropH
            );
        }

        return canvas;
    }

    captureBlob(zoomLevel = 1, quality = 0.92) {
        const canvas = this.captureFrame(zoomLevel);

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
