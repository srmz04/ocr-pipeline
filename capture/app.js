class CaptureApp {
    constructor() {
        this.apiClient = new GoogleAPIClient();
        this.camera = new CameraManager();
        this.validator = new QualityValidator(this.camera);
        this.uploader = null; // Initialized after API client

        this.selectedProducto = null;
        this.selectedDosis = null;
        this.productQueue = []; // Queue for multiple products

        this.elements = {};
        this.initializeElements();
        this.attachEventListeners();
        this.loadState();
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
            captureBtn: document.getElementById('captureBtn'),
            historyBtn: document.getElementById('historyBtn'),
            helpBtn: document.getElementById('helpBtn'),
            historySidebar: document.getElementById('historySidebar'),
            helpModal: document.getElementById('helpModal'),
            loadingOverlay: document.getElementById('loadingOverlay'),
            toast: document.getElementById('toast'),
            countToday: document.getElementById('countToday'),
            lastTime: document.getElementById('lastTime'),
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

        // Capture button
        this.elements.captureBtn.addEventListener('click', () => {
            this.handleCapture();
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
    }

    async init() {
        this.showLoading('Iniciando...');

        // 🚀 PUBLIC MODE: Use Proxy Uploader directly
        // No Google Auth required on client side
        console.log('Using Public Proxy Uploader');
        this.uploader = new ProxyUploader();
        await this.uploader.initialize();

        this.showLoading('Iniciando cámara...');

        const cameraOk = await this.camera.initialize();
        if (!cameraOk) {
            this.hideLoading();
            return;
        }

        // Start quality validation
        this.validator.startContinuousValidation((result) => {
            this.updateStatus(result);
            this.updateCaptureButton(result.valid);
        });

        this.hideLoading();
        this.showToast('¡Listo para capturar!');
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

        // Enable "Capture" button when queue has items
        const hasQueueItems = this.productQueue.length > 0;
        this.elements.captureBtn.disabled = !hasQueueItems;

        // Update capture button text to show count
        if (hasQueueItems) {
            this.elements.captureBtn.querySelector('.capture-text').textContent =
                `CAPTURAR (${this.productQueue.length})`;
        } else {
            this.elements.captureBtn.querySelector('.capture-text').textContent = 'CAPTURAR';
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

    async handleCapture() {
        if (this.productQueue.length === 0) {
            this.showToast('⚠️ Agrega productos primero');
            return;
        }

        try {
            this.showLoading('Capturando...');
            this.vibrate(100);

            // Capture ONE photo for all items
            const blob = await this.camera.captureBlob();

            this.showLoading(`Subiendo ${this.productQueue.length} producto(s)...`);

            // Prepare queue for proxy (format: array of {producto, dosis})
            const queueForProxy = this.productQueue.map(item => ({
                producto: item.producto,
                dosis: item.dosis
            }));

            // Upload photo with entire queue - proxy writes ONE row with multiple columns
            const driveResult = await this.uploader.uploadPhoto(
                blob,
                null,  // metadata (fallback, not used when queue is present)
                queueForProxy  // queue array for multi-column format
            );

            if (!driveResult.success) {
                throw new Error('Error al subir foto');
            }

            this.hideLoading();

            // Update count (add all items)
            const itemCount = this.productQueue.length;
            for (let i = 0; i < itemCount; i++) {
                this.incrementCount();
            }

            // Success feedback
            this.vibrate([100, 50, 100]);
            this.showToast(`✅ ${itemCount} producto(s) guardado(s)`);

            // Clear queue after successful upload
            this.clearQueue();

            // Update last time
            this.updateLastTime();

        } catch (error) {
            console.error('Capture error:', error);
            this.hideLoading();
            this.showToast('❌ Error: ' + error.message, 'error');
        }
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
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CaptureApp();
    window.app.init();
});
