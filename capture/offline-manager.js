// Offline Manager - Handles offline queue and ZIP export
// This is a standalone module that doesn't break existing functionality

class OfflineManager {
    constructor() {
        this.STORAGE_KEY = 'offline_queue';
        this.queue = this.loadQueue();
    }

    // Load queue from localStorage
    loadQueue() {
        try {
            const data = localStorage.getItem(this.STORAGE_KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('[Offline] Error loading queue:', e);
            return [];
        }
    }

    // Save queue to localStorage
    saveQueue() {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.queue));
        } catch (e) {
            console.error('[Offline] Error saving queue:', e);
        }
    }

    // Add a capture to the offline queue
    addToQueue(imageBase64, metadata, filename) {
        const item = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            filename: filename,
            imageBase64: imageBase64,
            metadata: metadata // { queue: [{producto, dosis}, ...] }
        };
        this.queue.push(item);
        this.saveQueue();
        console.log('[Offline] Added to queue. Total:', this.queue.length);
        return item.id;
    }

    // Remove an item from queue (after successful upload)
    removeFromQueue(id) {
        this.queue = this.queue.filter(item => item.id !== id);
        this.saveQueue();
    }

    // Clear entire queue
    clearQueue() {
        this.queue = [];
        this.saveQueue();
    }

    // Get pending count
    getPendingCount() {
        return this.queue.length;
    }

    // Check if online
    isOnline() {
        return navigator.onLine;
    }

    // Attempt to sync all pending items
    async syncAll(uploadFunction) {
        if (!this.isOnline()) {
            console.log('[Offline] Cannot sync - no internet');
            return { success: false, synced: 0, failed: 0 };
        }

        const results = { success: true, synced: 0, failed: 0 };
        const itemsToSync = [...this.queue]; // Copy to avoid mutation during iteration

        for (const item of itemsToSync) {
            try {
                await uploadFunction(item);
                this.removeFromQueue(item.id);
                results.synced++;
            } catch (e) {
                console.error('[Offline] Sync failed for:', item.id, e);
                results.failed++;
                results.success = false;
            }
        }

        return results;
    }

    // ============================================
    // ZIP EXPORT - For complete offline fallback
    // ============================================

    async exportToZip() {
        if (this.queue.length === 0) {
            throw new Error('No hay capturas pendientes para exportar');
        }

        // Dynamically load JSZip from CDN
        if (typeof JSZip === 'undefined') {
            await this.loadJSZip();
        }

        const zip = new JSZip();
        const csvRows = ['FECHA,ARCHIVO,PRODUCTOS'];

        // Add each image and build CSV
        for (const item of this.queue) {
            // Add image to ZIP
            const imageData = item.imageBase64; // Already base64
            zip.file(item.filename, imageData, { base64: true });

            // Build CSV row
            const productos = item.metadata.queue
                ? item.metadata.queue.map(p => `${p.producto}(${p.dosis})`).join('; ')
                : `${item.metadata.producto || ''}(${item.metadata.dosis || ''})`;

            csvRows.push(`"${item.timestamp}","${item.filename}","${productos}"`);
        }

        // Add CSV manifest
        zip.file('registro.csv', csvRows.join('\n'));

        // Generate ZIP blob
        const zipBlob = await zip.generateAsync({ type: 'blob' });

        // Trigger download
        const url = URL.createObjectURL(zipBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `capturas_offline_${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        return this.queue.length;
    }

    // Load JSZip library dynamically
    loadJSZip() {
        return new Promise((resolve, reject) => {
            // Check if already loaded
            if (typeof JSZip !== 'undefined') {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
            script.onload = resolve;
            script.onerror = () => reject(new Error('No se pudo cargar JSZip'));
            document.head.appendChild(script);
        });
    }
}

// Export globally
window.OfflineManager = OfflineManager;
