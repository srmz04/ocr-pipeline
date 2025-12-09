class CaptureApp {
    constructor() {
        this.camera = new CameraManager(); // Now a processor, not a stream manager
        this.uploader = null;
        this.offlineManager = new OfflineManager();

        this.selectedProducto = null;
        this.selectedDosis = null;
        this.productQueue = [];

        // Track current capture state
        this.currentBlob = null;
        this.currentPreviewUrl = null;

        this.elements = {};
        this.initializeElements();
        this.attachEventListeners();
        this.loadState();
        this.updateOfflineUI();

        // Show device-specific tip
        document.getElementById('deviceTip').textContent = this.camera.getDeviceTip();

        // Handle iOS Standalone mode warning
        if (this.camera.isIOSStandalone()) {
            document.getElementById('iosWarning').classList.remove('hidden');
        }
    }

    initializeElements() {
        this.elements = {
            status: document.getElementById('status'),
            productoSelector: document.getElementById('productoSelector'),
            dosisSelector: document.getElementById('dosisSelector'),
            customProductoInput: document.getElementById('customProductoInput'),
            addToQueueBtn: document.getElementById('addToQueueBtn'),
            queueContainer: document.getElementById('queueContainer'),
            queueList: document.getElementById('queueList'),
            clearQueueBtn: document.getElementById('clearQueueBtn'),
            historyBtn: document.getElementById('historyBtn'),
            helpBtn: document.getElementById('helpBtn'),
            historySidebar: document.getElementById('historySidebar'),
            helpModal: document.getElementById('helpModal'),
            loadingOverlay: document.getElementById('loadingOverlay'),
            toast: document.getElementById('toast'),
            countToday: document.getElementById('countToday'),
            lastTime: document.getElementById('lastTime'),
            // Native Input elements
            nativeCameraInput: document.getElementById('nativeCameraInput'),
            previewSection: document.getElementById('previewSection'),
            previewImage: document.getElementById('previewImage'),
            previewSize: document.getElementById('previewSize'),
            previewQuality: document.getElementById('previewQuality'),
            retakeBtn: document.getElementById('retakeBtn'),
            confirmBtn: document.getElementById('confirmBtn'),
            // Offline UI elements
            offlineBar: document.getElementById('offlineBar'),
            offlineIcon: document.getElementById('offlineIcon'),
            offlinePendingText: document.getElementById('offlinePendingText'),
            syncBtn: document.getElementById('syncBtn'),
            downloadZipBtn: document.getElementById('downloadZipBtn'),
        };
    }

    attachEventListeners() {
        // Producto chips
        this.elements.productoSelector.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                this.selectProducto(e.target.dataset.producto);
            });
        });

        // Dosis chips
        this.elements.dosisSelector.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                this.selectDosis(e.target.dataset.dosis);
            });
        });

        // 🆕 NATIVE INPUT: File change handler (triggered when user takes photo)
        this.elements.nativeCameraInput.addEventListener('change', async (e) => {
            if (e.target.files && e.target.files.length > 0) {
                await this.handleNativeCapture(e.target.files[0]);
            }
        });

        // 🆕 Preview: Retake button
        this.elements.retakeBtn.addEventListener('click', () => {
            this.cancelPreview();
        });

        // 🆕 Preview: Confirm button
        this.elements.confirmBtn.addEventListener('click', () => {
            this.confirmCapture();
        });

        // History button
        this.elements.historyBtn.addEventListener('click', () => {
            this.toggleHistory();
        });

        // Help button
        this.elements.helpBtn.addEventListener('click', () => {
            this.toggleHelp();
        });

        // Close sidebar
        document.getElementById('closeSidebar').addEventListener('click', () => {
            this.toggleHistory();
        });

        // Close help
        document.getElementById('closeHelp').addEventListener('click', () => {
            this.toggleHelp();
        });

        // Add to Queue button
        this.elements.addToQueueBtn.addEventListener('click', () => {
            this.addToQueue();
        });

        // Clear Queue button
        this.elements.clearQueueBtn.addEventListener('click', () => {
            this.clearQueue();
        });

        // Offline: Sync button
        this.elements.syncBtn.addEventListener('click', () => {
            this.syncOfflineQueue();
        });

        // Offline: Download ZIP button
        this.elements.downloadZipBtn.addEventListener('click', () => {
            this.downloadOfflineZip();
        });

        // Listen for online/offline events
        window.addEventListener('online', () => this.updateOfflineUI());
        window.addEventListener('offline', () => this.updateOfflineUI());
    }

    async init() {
        this.showLoading('Iniciando...');

        // Use Proxy Uploader directly (no Google Auth on client)
        console.log('Using Proxy Uploader - Native Input First');
        this.uploader = new ProxyUploader();
        await this.uploader.initialize();

        // No camera initialization needed - we use native input!
        
        this.hideLoading();
        this.showToast('¡Listo para capturar!');
    }

    // =====================================================
    // NATIVE INPUT CAPTURE FLOW
    // =====================================================

    /**
     * Handle file from native camera input
     * Pipeline: File → Process → Validate → Preview → (User confirms) → Upload
     */
    async handleNativeCapture(file) {
        // Check queue first
        if (this.productQueue.length === 0) {
            this.showToast('⚠️ Agrega productos primero');
            this.elements.nativeCameraInput.value = ''; // Reset input
            return;
        }

        this.showLoading('Procesando imagen...');

        try {
            // 1. Process image (resize + compress)
            const result = await this.camera.processImage(file);
            
            // 2. Store for later confirmation
            this.currentBlob = result.blob;
            
            // 3. Validate quality using file size heuristic
            const validation = this.camera.validateQuality(result.finalSize);
            
            // 4. Show preview
            this.showPreview(result, validation);
            
            this.hideLoading();
            
        } catch (error) {
            console.error('Native capture error:', error);
            this.hideLoading();
            this.showToast('❌ Error al procesar imagen: ' + error.message, 'error');
            this.elements.nativeCameraInput.value = '';
        }
    }

    /**
     * Display preview with quality info
     */
    showPreview(result, validation) {
        // Create preview URL
        this.currentPreviewUrl = this.camera.createPreviewURL(result.blob);
        this.elements.previewImage.src = this.currentPreviewUrl;
        
        // Show size info
        const sizeMB = (result.finalSize / 1024 / 1024).toFixed(2);
        const originalMB = (result.originalSize / 1024 / 1024).toFixed(2);
        this.elements.previewSize.textContent = `${result.width}x${result.height} | ${sizeMB}MB (de ${originalMB}MB)`;
        
        // Show quality indicator
        if (validation.valid) {
            this.elements.previewQuality.textContent = '✅ Calidad OK';
            this.elements.previewQuality.classList.add('valid');
            this.elements.previewQuality.classList.remove('invalid');
        } else {
            this.elements.previewQuality.textContent = '⚠️ ' + validation.message;
            this.elements.previewQuality.classList.add('invalid');
            this.elements.previewQuality.classList.remove('valid');
        }
        
        // Show preview section
        this.elements.previewSection.classList.remove('hidden');
        
        // Vibrate feedback
        this.vibrate(100);
    }

    /**
     * User wants to retake photo
     */
    cancelPreview() {
        // Clean up
        if (this.currentPreviewUrl) {
            this.camera.revokePreviewURL(this.currentPreviewUrl);
            this.currentPreviewUrl = null;
        }
        this.currentBlob = null;
        
        // Hide preview, reset input
        this.elements.previewSection.classList.add('hidden');
        this.elements.nativeCameraInput.value = '';
        
        this.showToast('Toma otra foto');
    }

    /**
     * User confirms the capture - proceed to upload
     */
    async confirmCapture() {
        if (!this.currentBlob) {
            this.showToast('❌ No hay imagen para subir');
            return;
        }

        // Hand off to processCapture (existing upload logic)
        await this.processCapture(this.currentBlob);
        
        // Clean up preview
        if (this.currentPreviewUrl) {
            this.camera.revokePreviewURL(this.currentPreviewUrl);
            this.currentPreviewUrl = null;
        }
        this.currentBlob = null;
        this.elements.previewSection.classList.add('hidden');
        this.elements.nativeCameraInput.value = '';
    }

    selectProducto(name) {
        this.selectedProducto = name;

        // Update UI
        this.elements.productoSelector.querySelectorAll('.chip').forEach(chip => {
            chip.classList.toggle('active', chip.dataset.producto === name);
        });

        // Show/hide custom input for "OTRA"
        if (name === 'OTRA') {
            this.elements.customProductoInput.classList.remove('hidden');
            this.elements.customProductoInput.focus();
        } else {
            this.elements.customProductoInput.classList.add('hidden');
            this.elements.customProductoInput.value = '';
        }

        // Update dosis options
        this.updateDosisOptions(name);

        // Save to localStorage
        localStorage.setItem(CONFIG.STORAGE_PRODUCTO, name);

        // Haptic feedback
        this.vibrate(50);

        // Check if can enable capture
        this.checkCanCapture();
    }

    updateDosisOptions(producto) {
        const prodConfig = CONFIG.PRODUCTOS.find(p => p.name === producto);
        if (!prodConfig) return;

        const container = this.elements.dosisSelector;
        container.innerHTML = '';

        prodConfig.dosis.forEach(dosis => {
            const chip = document.createElement('button');
            chip.className = 'chip';
            chip.dataset.dosis = dosis;
            chip.textContent = dosis;
            chip.addEventListener('click', () => this.selectDosis(dosis));
            container.appendChild(chip);
        });

        // Auto-select if only one option
        if (prodConfig.dosis.length === 1) {
            this.selectDosis(prodConfig.dosis[0]);
        }
    }

    selectDosis(dosis) {
        this.selectedDosis = dosis;

        // Update UI
        this.elements.dosisSelector.querySelectorAll('.chip').forEach(chip => {
            chip.classList.toggle('active', chip.dataset.dosis === dosis);
        });

        // Save to localStorage
        localStorage.setItem(CONFIG.STORAGE_DOSIS, dosis);

        // Haptic feedback
        this.vibrate(50);

        // Check if can enable capture
        this.checkCanCapture();
    }

    checkCanCapture() {
        const hasSelection = this.selectedProducto && this.selectedDosis;

        // Enable "Add to Queue" button when product and dose are selected
        this.elements.addToQueueBtn.disabled = !hasSelection;
        
        // Update status based on queue (native input doesn't need enable/disable)
        const hasQueueItems = this.productQueue.length > 0;
        if (hasQueueItems) {
            this.updateStatusText(`📋 ${this.productQueue.length} producto(s) en cola - Toca el botón verde para capturar`);
        } else if (hasSelection) {
            this.updateStatusText('✅ Producto seleccionado - Agrégalo a la cola');
        } else {
            this.updateStatusText('⬆️ Selecciona producto y dosis');
        }
    }

    updateStatusText(text) {
        if (this.elements.status) {
            this.elements.status.textContent = text;
        }
    }

    // ============================================
    // Queue Management Functions
    // ============================================

    addToQueue() {
        if (!this.selectedProducto || !this.selectedDosis) return;

        // Get final producto name (custom if OTRA)
        let finalProducto = this.selectedProducto;
        if (this.selectedProducto === 'OTRA') {
            const customValue = this.elements.customProductoInput.value.trim();
            finalProducto = customValue || 'OTRA (Sin especificar)';
        }

        // Add to queue
        this.productQueue.push({
            producto: finalProducto,
            dosis: this.selectedDosis,
            id: Date.now() // Unique ID for removal
        });

        // Render queue
        this.renderQueue();

        // Show toast
        this.showToast(`✅ ${finalProducto} agregado`);

        // Haptic feedback
        this.vibrate([50, 30, 50]);

        // Reset selection for next add
        this.selectedProducto = null;
        this.selectedDosis = null;
        this.elements.productoSelector.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        this.elements.dosisSelector.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        this.elements.customProductoInput.classList.add('hidden');
        this.elements.customProductoInput.value = '';

        // Update buttons
        this.checkCanCapture();
    }

    removeFromQueue(id) {
        this.productQueue = this.productQueue.filter(item => item.id !== id);
        this.renderQueue();
        this.checkCanCapture();
    }

    clearQueue() {
        this.productQueue = [];
        this.renderQueue();
        this.checkCanCapture();
        this.showToast('Lista limpiada');
    }

    renderQueue() {
        const container = this.elements.queueList;
        const queueContainer = this.elements.queueContainer;

        if (this.productQueue.length === 0) {
            queueContainer.classList.add('hidden');
            container.innerHTML = '';
            return;
        }

        queueContainer.classList.remove('hidden');
        container.innerHTML = this.productQueue.map(item => `
            <div class="queue-item" data-id="${item.id}">
                <span class="queue-item-text">🟢 ${item.producto} - ${item.dosis}</span>
                <button class="queue-item-remove" onclick="app.removeFromQueue(${item.id})">✕</button>
            </div>
        `).join('');
    }

    updateStatus(result) {
        const status = this.elements.status;
        status.textContent = result.message;
        status.className = `status status-${result.status}`;
    }

    updateCaptureButton(isValid) {
        // IGNORE VALIDATION RESULT - Always rely on selection
        this.checkCanCapture();
    }

    async saveOffline(blob, queueForProxy, metadataFallback, filename) {
        console.log('Falling back to offline save...');
        this.showLoading('Guardando offline...');

        try {
            // Convert blob to base64 for storage
            const reader = new FileReader();
            const base64 = await new Promise((resolve) => {
                reader.onloadend = () => resolve(reader.result.split(',')[1]);
                reader.readAsDataURL(blob);
            });

            this.offlineManager.addToQueue(base64, {
                queue: queueForProxy,
                ...metadataFallback
            }, filename);

            this.hideLoading();
            this.vibrate([50, 30, 50]);
            this.showToast(`📴 ${this.productQueue.length} guardado(s) offline`);

            // Clear queue and update UI
            const itemCount = this.productQueue.length;
            for (let i = 0; i < itemCount; i++) {
                this.incrementCount();
            }
            this.clearQueue();
            this.updateOfflineUI();
            this.updateLastTime();

        } catch (e) {
            console.error('Offline save failed:', e);
            this.hideLoading();
            this.showToast('❌ Error fatal al guardar offline', 'error');
        }
    }

    async handleLogin() {
        const username = this.elements.usernameInput.value.trim().toUpperCase();
        if (username.length < 3) {
            this.showToast('⚠️ Ingresa un usuario válido');
            return;
        }

        localStorage.setItem('user_ocr', username);
        this.elements.loginSection.classList.add('hidden');
        this.elements.cameraSection.classList.remove('hidden');
        this.checkCanCapture();
    }

    // New: Handle file from Native Camera App
    async handleNativeCapture(file) {
        if (this.productQueue.length === 0) {
            this.showToast('⚠️ Agrega productos primero');
            // Reset input so it can be triggered again
            this.elements.nativeCameraInput.value = '';
            return;
        }

        this.showLoading('Procesando foto nativa...');

        try {
            // We treat this file exactly like a captured blob
            // But we might want to resize/compress it if it's huge (mobile cams are 12MP+)
            // For now, let's just pass it through directly to the upload pipeline
            // The pipeline expects a Blob, and File extends Blob, so it works.

            // Use same pipeline as handleCapture
            await this.processCapture(file);

        } catch (error) {
            console.error('Native capture error:', error);
            this.showToast('❌ Error foto nativa: ' + error.message, 'error');
        } finally {
            this.hideLoading();
            this.elements.nativeCameraInput.value = '';
        }
    }

    async handleCapture() {
        if (this.productQueue.length === 0) {
            this.showToast('⚠️ Agrega productos primero');
            return;
        }

        try {
            this.showLoading('Capturando...');
            this.vibrate(100);

            // Get Zoom Level from UI
            const zoomLevel = parseFloat(this.elements.zoomSlider.value) || 1;

            // Capture Blob with specific zoom
            const blob = await this.camera.captureBlob(zoomLevel);

            // Hand off to common processor
            await this.processCapture(blob);

        } catch (error) {
            console.error('Capture error:', error);
            this.hideLoading();
            this.showToast('❌ Error: ' + error.message, 'error');
        }
    }

    // Common processing logic for both WebRTC and Native File
    async processCapture(blob) {
        const filename = `captura_${Date.now()}.jpg`;

        // Prepare queue for proxy (format: array of {producto, dosis})
        const queueForProxy = this.productQueue.map(item => ({
            producto: item.producto,
            dosis: item.dosis
        }));

        // FALLBACK: Send first item as metadata for old script compatibility
        const firstItem = this.productQueue[0];
        const metadataFallback = {
            producto: firstItem.producto,
            dosis: firstItem.dosis
        };

        // 1. Check if definitely offline
        if (!navigator.onLine) {
            await this.saveOffline(blob, queueForProxy, metadataFallback, filename);
            return;
        }

        // 2. Attempt Online Upload
        this.showLoading(`Subiendo ${this.productQueue.length} producto(s)...`);

        try {
            const driveResult = await this.uploader.uploadPhoto(
                blob,
                metadataFallback,
                queueForProxy
            );

            if (!driveResult.success) {
                throw new Error(driveResult.error || 'Upload failed');
            }

            // SUCCESS
            this.hideLoading();
            this.vibrate([100, 50, 100]);
            this.showToast(`✅ ${this.productQueue.length} producto(s) guardado(s)`);

            // Update state
            const itemCount = this.productQueue.length;
            for (let i = 0; i < itemCount; i++) {
                this.incrementCount();
            }
            this.clearQueue();
            this.updateLastTime();

        } catch (uploadError) {
            // 3. FALLBACK ON UPLOAD ERROR
            console.warn('Upload failed, falling back to offline:', uploadError);
            this.showToast('⚠️ Error de red, guardando offline...', 'warning');
            await this.saveOffline(blob, queueForProxy, metadataFallback, filename);
        }

        this.hideLoading(); // Ensure hidden
    }

    incrementCount() {
        const today = new Date().toDateString();
        const savedDate = localStorage.getItem(CONFIG.STORAGE_DATE);

        let count = 0;
        if (savedDate === today) {
            count = parseInt(localStorage.getItem(CONFIG.STORAGE_COUNT) || '0');
        }

        count++;
        localStorage.setItem(CONFIG.STORAGE_COUNT, count.toString());
        localStorage.setItem(CONFIG.STORAGE_DATE, today);

        this.elements.countToday.textContent = count;
    }

    updateLastTime() {
        const now = new Date();
        const time = now.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
        this.elements.lastTime.textContent = time;
    }

    loadState() {
        // Load saved producto
        const savedProd = localStorage.getItem(CONFIG.STORAGE_PRODUCTO);
        if (savedProd) {
            this.selectProducto(savedProd);
        }

        // Load saved dosis
        const savedDosis = localStorage.getItem(CONFIG.STORAGE_DOSIS);
        if (savedDosis && this.selectedProducto) {
            this.selectDosis(savedDosis);
        }

        // Load count
        const today = new Date().toDateString();
        const savedDate = localStorage.getItem(CONFIG.STORAGE_DATE);

        if (savedDate === today) {
            const count = localStorage.getItem(CONFIG.STORAGE_COUNT) || '0';
            this.elements.countToday.textContent = count;
        } else {
            this.elements.countToday.textContent = '0';
        }
    }

    toggleHistory() {
        this.elements.historySidebar.classList.toggle('hidden');
    }

    toggleHelp() {
        this.elements.helpModal.classList.toggle('hidden');
    }

    showLoading(message = 'Cargando...') {
        this.elements.loadingOverlay.querySelector('p').textContent = message;
        this.elements.loadingOverlay.classList.remove('hidden');
    }

    hideLoading() {
        this.elements.loadingOverlay.classList.add('hidden');
    }

    showToast(message, type = 'info') {
        const toast = this.elements.toast;
        toast.textContent = message;
        toast.classList.remove('hidden');

        setTimeout(() => {
            toast.classList.add('hidden');
        }, CONFIG.TOAST_DURATION);
    }

    vibrate(pattern) {
        if ('vibrate' in navigator) {
            navigator.vibrate(pattern);
        }
    }

    // ============================================
    // Offline Queue Management
    // ============================================

    updateOfflineUI() {
        const pendingCount = this.offlineManager.getPendingCount();
        const isOnline = navigator.onLine;

        if (pendingCount === 0) {
            this.elements.offlineBar.classList.add('hidden');
            return;
        }

        // Show the bar
        this.elements.offlineBar.classList.remove('hidden');

        // Update icon and text
        this.elements.offlineIcon.textContent = isOnline ? '🔄' : '📴';
        this.elements.offlinePendingText.textContent = `${pendingCount} pendiente${pendingCount > 1 ? 's' : ''}`;

        // Enable/disable sync button based on connection
        this.elements.syncBtn.disabled = !isOnline;
        this.elements.syncBtn.textContent = isOnline ? '🔄 Sincronizar' : '📴 Sin conexión';
    }

    async syncOfflineQueue() {
        if (!navigator.onLine) {
            this.showToast('📴 Sin conexión a internet');
            return;
        }

        const pendingCount = this.offlineManager.getPendingCount();
        if (pendingCount === 0) {
            this.showToast('✅ No hay pendientes');
            return;
        }

        this.showLoading(`Sincronizando ${pendingCount} captura(s)...`);

        try {
            // Define upload function for each item
            const uploadItem = async (item) => {
                // Convert base64 back to blob
                const byteCharacters = atob(item.imageBase64);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], { type: 'image/jpeg' });

                // Upload using existing uploader
                const result = await this.uploader.uploadPhoto(
                    blob,
                    item.metadata,
                    item.metadata.queue || []
                );

                if (!result.success) {
                    throw new Error('Upload failed');
                }
            };

            const results = await this.offlineManager.syncAll(uploadItem);

            this.hideLoading();
            this.updateOfflineUI();

            if (results.synced > 0) {
                this.showToast(`✅ ${results.synced} captura(s) sincronizada(s)`);
            }
            if (results.failed > 0) {
                this.showToast(`⚠️ ${results.failed} fallida(s)`, 'error');
            }
        } catch (error) {
            console.error('Sync error:', error);
            this.hideLoading();
            this.showToast('❌ Error al sincronizar', 'error');
        }
    }

    async downloadOfflineZip() {
        const pendingCount = this.offlineManager.getPendingCount();
        if (pendingCount === 0) {
            this.showToast('No hay capturas para exportar');
            return;
        }

        this.showLoading('Generando ZIP...');

        try {
            const count = await this.offlineManager.exportToZip();
            this.hideLoading();
            this.showToast(`📦 ZIP descargado con ${count} captura(s)`);
        } catch (error) {
            console.error('ZIP export error:', error);
            this.hideLoading();
            this.showToast('❌ Error: ' + error.message, 'error');
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CaptureApp();
    window.app.init();
});
