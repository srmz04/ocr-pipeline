// Camera module - handles video stream and capture
class CameraManager {
    constructor() {
        this.video = document.getElementById('camera');
        this.stream = null;
        this.facingMode = 'environment'; // Rear camera by default
    }

    async initialize() {
        try {
            // Priority: High Resolution + Continuous Focus
            const constraints = {
                video: {
                    facingMode: 'environment',
                    width: { ideal: 3840 }, // Ask for 4K
                    height: { ideal: 2160 },
                    // Try to enable continuous focus if supported
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
            // Fallback for older devices
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

    captureFrame() {
        // "Smart Central Crop" Strategy
        // 1. Capture High Res Frame
        // 2. Crop the CENTER based on the Guide Frame's relative size
        // This allows user to stand back (good focus) but get a close-up result.

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        // Source Dimensions (Camera Sensor)
        const vWidth = this.video.videoWidth;
        const vHeight = this.video.videoHeight;

        // UI Dimensions (What user sees)
        const container = document.querySelector('.camera-container');
        const guide = document.querySelector('.guide-frame');

        // Calculate Scale Factor (How much of the video is covered by the guide?)
        // Since we use object-fit: contain, we need to know the 'rendered' video size
        const cWidth = container.offsetWidth;
        const cHeight = container.offsetHeight;

        // Video Ratio vs Container Ratio
        const vRatio = vWidth / vHeight;
        const cRatio = cWidth / cHeight;

        let renderedW, renderedH;

        if (cRatio > vRatio) {
            // Container is wider than video (Black bars on sides)
            renderedH = cHeight;
            renderedW = cHeight * vRatio;
        } else {
            // Container is taller than video (Black bars on top/bottom)
            renderedW = cWidth;
            renderedH = cWidth / vRatio;
        }

        // Guide Size relative to Rendered Video
        const guideW = guide.offsetWidth;
        const guideH = guide.offsetHeight;

        // Calculate Crop Factors
        // How much of the rendered video width is the guide?
        const cropFactorW = guideW / renderedW;
        const cropFactorH = guideH / renderedH;

        // Apply to Source
        const sourceCropW = vWidth * cropFactorW;
        const sourceCropH = vHeight * cropFactorH;

        // Center the crop
        const sourceX = (vWidth - sourceCropW) / 2;
        const sourceY = (vHeight - sourceCropH) / 2;

        console.log(`Cropping: ${sourceCropW}x${sourceCropH} at ${sourceX},${sourceY} from ${vWidth}x${vHeight}`);

        // Portrait Rotation Logic
        const isPortrait = window.innerHeight > window.innerWidth;
        const isVideoLandscape = vWidth > vHeight;

        if (isPortrait && isVideoLandscape) {
            // If rotating, we swap W/H in output
            canvas.width = sourceCropH;
            canvas.height = sourceCropW;

            ctx.translate(sourceCropH, 0);
            ctx.rotate(Math.PI / 2);

            ctx.drawImage(
                this.video,
                sourceX, sourceY, sourceCropW, sourceCropH, // Source Crop
                0, 0, sourceCropW, sourceCropH              // Dest (Rotated space)
            );
        } else {
            // Standard Landscape/Desktop
            canvas.width = sourceCropW;
            canvas.height = sourceCropH;

            ctx.drawImage(
                this.video,
                sourceX, sourceY, sourceCropW, sourceCropH,
                0, 0, sourceCropW, sourceCropH
            );
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
