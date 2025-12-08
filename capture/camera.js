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

        // 1. Get dimensions of video stream (actual resolution)
        const videoWidth = this.video.videoWidth;
        const videoHeight = this.video.videoHeight;

        // 2. Get dimensions of displayed video (CSS pixels)
        // Note: The video object might be larger than the container due to object-fit: cover
        const container = document.querySelector('.camera-container');
        const containerWidth = container.offsetWidth;
        const containerHeight = container.offsetHeight;

        // Calculate scale factor between video stream and displayed video (object-fit: cover logic)
        const scaleX = containerWidth / videoWidth;
        const scaleY = containerHeight / videoHeight;
        const scale = Math.max(scaleX, scaleY); // Cover effect uses the larger scale

        const displayedVideoWidth = videoWidth * scale;
        const displayedVideoHeight = videoHeight * scale;

        // 3. Get dimensions of guide frame (CSS pixels) relative to container
        const guideFrame = document.querySelector('.guide-frame');
        const guideRect = guideFrame.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();

        // Calculate guide frame position relative to the container
        const guideRelativeTop = guideRect.top - containerRect.top;
        const guideRelativeLeft = guideRect.left - containerRect.left;

        // 4. Calculate crop coordinates on the actual video stream
        // We need to map CSS coordinates back to video stream coordinates

        // Offset of the displayed video relative to container (centered)
        const videoOffsetX = (displayedVideoWidth - containerWidth) / 2;
        const videoOffsetY = (displayedVideoHeight - containerHeight) / 2;

        // Calculate coordinates in the displayed video space
        const cropX_CSS = videoOffsetX + guideRelativeLeft;
        const cropY_CSS = videoOffsetY + guideRelativeTop;

        // Convert to actual video stream coordinates
        let sourceX = cropX_CSS / scale;
        let sourceY = cropY_CSS / scale;
        let sourceWidth = guideRect.width / scale;
        let sourceHeight = guideRect.height / scale;

        // Add a safety margin (e.g. 10%) to account for edge cases
        const margin = 0.1;
        sourceX = Math.max(0, sourceX - (sourceWidth * margin));
        sourceY = Math.max(0, sourceY - (sourceHeight * margin));
        sourceWidth = Math.min(videoWidth - sourceX, sourceWidth * (1 + 2 * margin));
        sourceHeight = Math.min(videoHeight - sourceY, sourceHeight * (1 + 2 * margin));

        // Set canvas size to the cropped area (high resolution)
        canvas.width = sourceWidth;
        canvas.height = sourceHeight;

        const ctx = canvas.getContext('2d');

        // Draw only the cropped portion
        ctx.drawImage(
            this.video,
            sourceX, sourceY, sourceWidth, sourceHeight, // Source rectangle
            0, 0, canvas.width, canvas.height            // Destination rectangle
        );

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
