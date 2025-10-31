/**
 * Página QR Generator - Sistema Bancario Desktop
 * Generación y escaneo de códigos QR para transacciones bancarias
 */

class QRGeneratorPage {
    constructor() {
        this.data = {
            qrHistory: [],
            scannedQRCodes: [],
            accounts: [],
            currentMode: 'generate', // 'generate' | 'scan' | 'history'
            scanInterval: null,
            qrChart: null
        };
        this.isScanning = false;
        this.stream = null;
    }

    /**
     * Renderizar la página del generador QR
     */
    async render() {
        try {
            this.showLoading();
            await this.loadData();
            this.hideLoading();
            return this.getHTML();

        } catch (error) {
            this.hideLoading();
            this.handleError('Error al cargar el generador QR', error);
            return this.getErrorHTML(error.message);
        }
    }

    /**
     * Obtener HTML de la página
     */
    getHTML() {
        return `
            <div id="qr-generator-content" class="qr-generator-container">
                <!-- Header -->
                <div class="page-header">
                    <div class="page-title">
                        <h1><i class="fas fa-qrcode"></i> Códigos QR Bancarios</h1>
                        <p>Genera y escanea códigos QR para transacciones</p>
                    </div>
                    <div class="page-actions">
                        <button class="btn btn-outline" onclick="qrGeneratorPage.exportQRHistory()">
                            <i class="fas fa-download"></i> Exportar Historial
                        </button>
                        <button class="btn btn-primary" onclick="qrGeneratorPage.clearAllHistory()">
                            <i class="fas fa-trash"></i> Limpiar Historial
                        </button>
                    </div>
                </div>

                <!-- Mode Selection -->
                <div class="mode-selection">
                    <button class="mode-button ${this.data.currentMode === 'generate' ? 'active' : ''}" 
                            onclick="qrGeneratorPage.switchMode('generate')">
                        <i class="fas fa-plus-circle"></i>
                        <span>Generar QR</span>
                    </button>
                    <button class="mode-button ${this.data.currentMode === 'scan' ? 'active' : ''}" 
                            onclick="qrGeneratorPage.switchMode('scan')">
                        <i class="fas fa-camera"></i>
                        <span>Escanear QR</span>
                    </button>
                    <button class="mode-button ${this.data.currentMode === 'history' ? 'active' : ''}" 
                            onclick="qrGeneratorPage.switchMode('history')">
                        <i class="fas fa-history"></i>
                        <span>Historial</span>
                    </button>
                </div>

                <!-- Generate QR Mode -->
                <div class="mode-content ${this.data.currentMode === 'generate' ? 'active' : ''}" id="generate-mode">
                    <div class="generate-section">
                        <div class="form-container">
                            <h3>Generar Código QR de Pago</h3>
                            <form id="qr-form" class="qr-form">
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="qr-amount">Monto *</label>
                                        <div class="input-group">
                                            <span class="input-prefix">S/</span>
                                            <input type="number" 
                                                   id="qr-amount" 
                                                   name="amount" 
                                                   min="0.01" 
                                                   step="0.01"
                                                   placeholder="0.00" 
                                                   required>
                                        </div>
                                        <div class="error-message" id="amount-error"></div>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="qr-currency">Moneda</label>
                                        <select id="qr-currency" name="currency">
                                            <option value="PEN">Soles (PEN)</option>
                                            <option value="USD">Dólares (USD)</option>
                                            <option value="EUR">Euros (EUR)</option>
                                        </select>
                                    </div>
                                </div>

                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="qr-account">Cuenta de Origen *</label>
                                        <select id="qr-account" name="accountId" required>
                                            <option value="">Seleccionar cuenta</option>
                                        </select>
                                        <div class="error-message" id="account-error"></div>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="qr-description">Descripción</label>
                                        <input type="text" 
                                               id="qr-description" 
                                               name="description" 
                                               maxlength="100"
                                               placeholder="Concepto del pago">
                                    </div>
                                </div>

                                <div class="form-group">
                                    <label for="qr-category">Categoría</label>
                                    <select id="qr-category" name="category">
                                        <option value="general">General</option>
                                        <option value="pago">Pago</option>
                                        <option value="transferencia">Transferencia</option>
                                        <option value="servicios">Servicios</option>
                                        <option value="compra">Compra</option>
                                        <option value="donacion">Donación</option>
                                    </select>
                                </div>

                                <!-- QR Options -->
                                <div class="qr-options">
                                    <h4>Opciones del Código QR</h4>
                                    <div class="option-row">
                                        <div class="checkbox-group">
                                            <input type="checkbox" id="qr-expiry" name="setExpiry" onchange="qrGeneratorPage.toggleExpiry()">
                                            <label for="qr-expiry">Establecer fecha de expiración</label>
                                        </div>
                                        <div class="expiry-inputs" id="expiry-inputs" style="display: none;">
                                            <input type="datetime-local" id="qr-expiry-date" name="expiryDate">
                                        </div>
                                    </div>
                                    
                                    <div class="option-row">
                                        <div class="checkbox-group">
                                            <input type="checkbox" id="qr-encrypt" name="encrypt" checked>
                                            <label for="qr-encrypt">Encriptar datos sensibles</label>
                                        </div>
                                    </div>
                                    
                                    <div class="option-row">
                                        <div class="checkbox-group">
                                            <input type="checkbox" id="qr-reusable" name="reusable">
                                            <label for="qr-reusable">Código reutilizable</label>
                                        </div>
                                    </div>
                                </div>

                                <div class="form-actions">
                                    <button type="button" class="btn btn-secondary" onclick="qrGeneratorPage.clearForm()">
                                        <i class="fas fa-eraser"></i> Limpiar
                                    </button>
                                    <button type="submit" class="btn btn-primary">
                                        <i class="fas fa-qrcode"></i> Generar QR
                                    </button>
                                </div>
                            </form>
                        </div>

                        <div class="qr-result-container">
                            <h3>Vista Previa</h3>
                            <div class="qr-preview" id="qr-preview">
                                <div class="qr-placeholder">
                                    <i class="fas fa-qrcode"></i>
                                    <p>Completa el formulario para generar el código QR</p>
                                </div>
                            </div>
                            
                            <div class="qr-actions" id="qr-actions" style="display: none;">
                                <button class="btn btn-primary" onclick="qrGeneratorPage.downloadQR()">
                                    <i class="fas fa-download"></i> Descargar
                                </button>
                                <button class="btn btn-secondary" onclick="qrGeneratorPage.shareQR()">
                                    <i class="fas fa-share"></i> Compartir
                                </button>
                                <button class="btn btn-outline" onclick="qrGeneratorPage.printQR()">
                                    <i class="fas fa-print"></i> Imprimir
                                </button>
                            </div>

                            <div class="qr-info" id="qr-info" style="display: none;">
                                <h4>Información del Código QR</h4>
                                <div class="info-grid">
                                    <div class="info-item">
                                        <label>ID:</label>
                                        <span id="qr-id">-</span>
                                    </div>
                                    <div class="info-item">
                                        <label>Fecha:</label>
                                        <span id="qr-date">-</span>
                                    </div>
                                    <div class="info-item">
                                        <label>Estado:</label>
                                        <span class="status-badge status-active" id="qr-status">Activo</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Scan QR Mode -->
                <div class="mode-content ${this.data.currentMode === 'scan' ? 'active' : ''}" id="scan-mode">
                    <div class="scan-section">
                        <div class="scan-container">
                            <div class="camera-container">
                                <video id="camera-stream" autoplay muted playsinline></video>
                                <canvas id="scan-canvas" style="display: none;"></canvas>
                                <div class="scan-overlay" id="scan-overlay">
                                    <div class="scan-frame">
                                        <div class="scan-corners">
                                            <div class="corner top-left"></div>
                                            <div class="corner top-right"></div>
                                            <div class="corner bottom-left"></div>
                                            <div class="corner bottom-right"></div>
                                        </div>
                                        <div class="scan-line"></div>
                                    </div>
                                </div>
                                <div class="camera-controls">
                                    <button class="btn btn-primary" id="start-scan-btn" onclick="qrGeneratorPage.startScanning()">
                                        <i class="fas fa-camera"></i> Iniciar Escaneo
                                    </button>
                                    <button class="btn btn-secondary" id="stop-scan-btn" onclick="qrGeneratorPage.stopScanning()" style="display: none;">
                                        <i class="fas fa-stop"></i> Detener
                                    </button>
                                    <button class="btn btn-outline" id="switch-camera-btn" onclick="qrGeneratorPage.switchCamera()" style="display: none;">
                                        <i class="fas fa-sync"></i> Cambiar Cámara
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div class="scan-results" id="scan-results">
                            <h3>Resultados del Escaneo</h3>
                            <div class="scanned-info" id="scanned-info" style="display: none;">
                                <!-- La información se cargará dinámicamente -->
                            </div>
                            <div class="scan-actions" id="scan-actions" style="display: none;">
                                <button class="btn btn-primary" onclick="qrGeneratorPage.processPayment()">
                                    <i class="fas fa-check"></i> Procesar Pago
                                </button>
                                <button class="btn btn-secondary" onclick="qrGeneratorPage.saveQRCode()">
                                    <i class="fas fa-save"></i> Guardar
                                </button>
                                <button class="btn btn-outline" onclick="qrGeneratorPage.dismissScan()">
                                    <i class="fas fa-times"></i> Descartar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- History Mode -->
                <div class="mode-content ${this.data.currentMode === 'history' ? 'active' : ''}" id="history-mode">
                    <div class="history-section">
                        <div class="history-stats">
                            <div class="stat-card">
                                <div class="stat-icon primary">
                                    <i class="fas fa-qrcode"></i>
                                </div>
                                <div class="stat-content">
                                    <h4>QR Generados</h4>
                                    <div class="stat-value" id="totalGenerated">0</div>
                                </div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-icon success">
                                    <i class="fas fa-camera"></i>
                                </div>
                                <div class="stat-content">
                                    <h4>QR Escaneados</h4>
                                    <div class="stat-value" id="totalScanned">0</div>
                                </div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-icon warning">
                                    <i class="fas fa-clock"></i>
                                </div>
                                <div class="stat-content">
                                    <h4>Pendientes</h4>
                                    <div class="stat-value" id="pendingCount">0</div>
                                </div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-icon info">
                                    <i class="fas fa-chart-bar"></i>
                                </div>
                                <div class="stat-content">
                                    <h4>Valor Total</h4>
                                    <div class="stat-value" id="totalValue">S/ 0.00</div>
                                </div>
                            </div>
                        </div>

                        <div class="history-filters">
                            <div class="filter-group">
                                <label>Tipo:</label>
                                <select id="history-type-filter" onchange="qrGeneratorPage.filterHistory()">
                                    <option value="all">Todos</option>
                                    <option value="generated">Generados</option>
                                    <option value="scanned">Escaneados</option>
                                </select>
                            </div>
                            
                            <div class="filter-group">
                                <label>Estado:</label>
                                <select id="history-status-filter" onchange="qrGeneratorPage.filterHistory()">
                                    <option value="all">Todos</option>
                                    <option value="active">Activos</option>
                                    <option value="used">Usados</option>
                                    <option value="expired">Expirados</option>
                                </select>
                            </div>
                            
                            <div class="filter-group">
                                <label>Buscar:</label>
                                <input type="text" 
                                       id="history-search" 
                                       placeholder="Buscar por ID o descripción..."
                                       oninput="qrGeneratorPage.filterHistory()">
                            </div>
                        </div>

                        <div class="history-chart">
                            <h4>Actividad de Códigos QR</h4>
                            <canvas id="qr-activity-chart"></canvas>
                        </div>

                        <div class="history-list">
                            <h4>Historial de Códigos QR</h4>
                            <div id="qr-history-list">
                                <!-- El historial se cargará dinámicamente -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal para procesar pago -->
            <div id="payment-modal" class="modal hidden">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Procesar Pago QR</h3>
                        <button class="modal-close" onclick="qrGeneratorPage.closePaymentModal()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="modal-body" id="payment-modal-content">
                        <!-- El contenido se cargará dinámicamente -->
                    </div>
                    
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="qrGeneratorPage.closePaymentModal()">
                            Cancelar
                        </button>
                        <button class="btn btn-primary" id="confirm-payment-btn" onclick="qrGeneratorPage.confirmPayment()">
                            <i class="fas fa-check"></i> Confirmar Pago
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Cargar datos iniciales
     */
    async loadData() {
        try {
            const accounts = await API.getAccounts();
            this.data.accounts = accounts;

            // Poblar select de cuentas
            this.populateAccountSelect();

            // Cargar historial
            this.data.qrHistory = this.getDemoQRHistory();
            this.data.scannedQRCodes = [];

            this.updateHistoryStats();
            this.setupEventListeners();

        } catch (error) {
            console.error('Error loading data:', error);
            this.data.accounts = this.getDemoAccounts();
            this.data.qrHistory = this.getDemoQRHistory();
            this.populateAccountSelect();
            this.updateHistoryStats();
        }
    }

    /**
     * Poblar select de cuentas
     */
    populateAccountSelect() {
        const select = document.getElementById('qr-account');
        if (select) {
            select.innerHTML = '<option value="">Seleccionar cuenta</option>' +
                this.data.accounts.map(account => 
                    `<option value="${account.id}">${account.type} - ${account.number}</option>`
                ).join('');
        }
    }

    /**
     * Obtener cuentas de demostración
     */
    getDemoAccounts() {
        return [
            {
                id: '1',
                type: 'Cuenta Corriente',
                number: '****1234'
            },
            {
                id: '2',
                type: 'Cuenta de Ahorros',
                number: '****5678'
            }
        ];
    }

    /**
     * Obtener historial de demostración
     */
    getDemoQRHistory() {
        return [
            {
                id: 'QR001',
                type: 'generated',
                amount: 50.00,
                currency: 'PEN',
                description: 'Pago mercado',
                category: 'alimentacion',
                accountId: '1',
                dateCreated: new Date(Date.now() - 3600000).toISOString(),
                status: 'active',
                used: false,
                scanCount: 0
            },
            {
                id: 'QR002',
                type: 'scanned',
                amount: 120.00,
                currency: 'PEN',
                description: 'Transferencia recibida',
                category: 'transferencia',
                accountId: '2',
                dateCreated: new Date(Date.now() - 7200000).toISOString(),
                status: 'used',
                used: true,
                scanCount: 1,
                usedDate: new Date(Date.now() - 3600000).toISOString()
            },
            {
                id: 'QR003',
                type: 'generated',
                amount: 85.50,
                currency: 'PEN',
                description: 'Servicios públicos',
                category: 'servicios',
                accountId: '1',
                dateCreated: new Date(Date.now() - 86400000).toISOString(),
                status: 'expired',
                used: false,
                scanCount: 0,
                expiryDate: new Date(Date.now() - 3600000).toISOString()
            }
        ];
    }

    /**
     * Cambiar modo activo
     */
    switchMode(mode) {
        this.data.currentMode = mode;
        
        // Actualizar botones
        document.querySelectorAll('.mode-button').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.closest('.mode-button').classList.add('active');
        
        // Actualizar contenido
        document.querySelectorAll('.mode-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${mode}-mode`).classList.add('active');
        
        if (mode === 'history') {
            setTimeout(() => {
                this.renderQRChart();
            }, 100);
        }
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Formulario QR
        const qrForm = document.getElementById('qr-form');
        if (qrForm) {
            qrForm.addEventListener('submit', (e) => this.handleQRGeneration(e));
        }

        // Preview en tiempo real
        const amountInput = document.getElementById('qr-amount');
        const descriptionInput = document.getElementById('qr-description');
        
        if (amountInput) {
            amountInput.addEventListener('input', () => this.updateQRPreview());
        }
        
        if (descriptionInput) {
            descriptionInput.addEventListener('input', () => this.updateQRPreview());
        }
    }

    /**
     * Manejar generación de QR
     */
    async handleQRGeneration(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const qrData = {
            amount: parseFloat(formData.get('amount')),
            currency: formData.get('currency'),
            accountId: formData.get('accountId'),
            description: formData.get('description') || '',
            category: formData.get('category'),
            setExpiry: formData.get('setExpiry') === 'on',
            expiryDate: formData.get('expiryDate'),
            encrypt: formData.get('encrypt') === 'on',
            reusable: formData.get('reusable') === 'on'
        };

        if (!this.validateQRData(qrData)) {
            return;
        }

        try {
            this.showFormLoading(true);
            
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            const qrCode = {
                id: 'QR' + Date.now().toString().slice(-6),
                ...qrData,
                type: 'generated',
                dateCreated: new Date().toISOString(),
                status: 'active',
                used: false,
                scanCount: 0,
                encryptedData: qrData.encrypt ? this.encryptQRData(qrData) : null
            };

            this.data.qrHistory.unshift(qrCode);
            this.renderQRCode(qrCode);
            this.updateHistoryStats();
            
            window.bancoApp?.showNotification('Código QR generado exitosamente', 'success');

        } catch (error) {
            this.handleError('Error al generar el código QR', error);
        } finally {
            this.showFormLoading(false);
        }
    }

    /**
     * Validar datos del QR
     */
    validateQRData(data) {
        let isValid = true;

        if (!data.amount || data.amount <= 0) {
            this.showError('amount-error', 'El monto debe ser mayor a 0');
            isValid = false;
        }

        if (!data.accountId) {
            this.showError('account-error', 'Debes seleccionar una cuenta');
            isValid = false;
        }

        if (data.setExpiry && data.expiryDate) {
            const expiry = new Date(data.expiryDate);
            const now = new Date();
            if (expiry <= now) {
                this.showError('amount-error', 'La fecha de expiración debe ser futura');
                isValid = false;
            }
        }

        return isValid;
    }

    /**
     * Mostrar error
     */
    showError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = message;
            element.style.display = 'block';
        }
    }

    /**
     * Limpiar errores
     */
    clearErrors() {
        const errorElements = document.querySelectorAll('.error-message');
        errorElements.forEach(element => {
            element.textContent = '';
            element.style.display = 'none';
        });
    }

    /**
     * Mostrar/ocultar inputs de expiración
     */
    toggleExpiry() {
        const checkbox = document.getElementById('qr-expiry');
        const inputs = document.getElementById('expiry-inputs');
        
        if (checkbox && inputs) {
            inputs.style.display = checkbox.checked ? 'block' : 'none';
        }
    }

    /**
     * Actualizar vista previa del QR
     */
    updateQRPreview() {
        const amount = document.getElementById('qr-amount')?.value;
        const description = document.getElementById('qr-description')?.value;
        
        if (amount && parseFloat(amount) > 0) {
            // Aquí se podría actualizar una vista previa del QR en tiempo real
            console.log('Actualizando preview:', { amount, description });
        }
    }

    /**
     * Renderizar código QR
     */
    renderQRCode(qrCode) {
        const preview = document.getElementById('qr-preview');
        const actions = document.getElementById('qr-actions');
        const info = document.getElementById('qr-info');

        if (!preview) return;

        // Generar QR usando QRCode.js
        const qrContainer = document.createElement('div');
        qrContainer.id = 'generated-qr';
        qrContainer.style.width = '200px';
        qrContainer.style.height = '200px';
        qrContainer.style.margin = '0 auto';

        preview.innerHTML = '';
        preview.appendChild(qrContainer);

        // Datos del QR (normalmente sería más complejo y encriptado)
        const qrData = {
            id: qrCode.id,
            amount: qrCode.amount,
            currency: qrCode.currency,
            description: qrCode.description,
            timestamp: qrCode.dateCreated
        };

        QRCode.toCanvas(qrContainer, JSON.stringify(qrData), {
            width: 200,
            margin: 2,
            color: {
                dark: '#000000',
                light: '#FFFFFF'
            }
        }, (error) => {
            if (error) {
                console.error('Error generating QR:', error);
                preview.innerHTML = '<p>Error al generar el código QR</p>';
            }
        });

        // Mostrar acciones e información
        if (actions) actions.style.display = 'block';
        if (info) {
            info.style.display = 'block';
            document.getElementById('qr-id').textContent = qrCode.id;
            document.getElementById('qr-date').textContent = this.formatDateTime(qrCode.dateCreated);
        }

        this.currentQRCode = qrCode;
    }

    /**
     * Limpiar formulario
     */
    clearForm() {
        const form = document.getElementById('qr-form');
        if (form) {
            form.reset();
        }
        
        this.clearErrors();
        
        // Ocultar elementos del resultado
        const preview = document.getElementById('qr-preview');
        const actions = document.getElementById('qr-actions');
        const info = document.getElementById('qr-info');
        
        if (preview) {
            preview.innerHTML = `
                <div class="qr-placeholder">
                    <i class="fas fa-qrcode"></i>
                    <p>Completa el formulario para generar el código QR</p>
                </div>
            `;
        }
        
        if (actions) actions.style.display = 'none';
        if (info) info.style.display = 'none';
    }

    /**
     * Descargar QR
     */
    downloadQR() {
        if (!this.currentQRCode) return;

        try {
            const canvas = document.querySelector('#generated-qr canvas');
            if (canvas) {
                const link = document.createElement('a');
                link.download = `qr_${this.currentQRCode.id}.png`;
                link.href = canvas.toDataURL();
                link.click();
                
                window.bancoApp?.showNotification('Código QR descargado', 'success');
            }
        } catch (error) {
            this.handleError('Error al descargar el código QR', error);
        }
    }

    /**
     * Compartir QR
     */
    shareQR() {
        if (!this.currentQRCode) return;

        if (navigator.share) {
            navigator.share({
                title: 'Código QR de Pago',
                text: `Código QR para pago de ${this.formatCurrency(this.currentQRCode.amount)}`,
                url: window.location.href
            });
        } else {
            // Fallback: copiar al portapapeles
            navigator.clipboard.writeText(JSON.stringify(this.currentQRCode));
            window.bancoApp?.showNotification('Datos del QR copiados al portapapeles', 'info');
        }
    }

    /**
     * Imprimir QR
     */
    printQR() {
        if (!this.currentQRCode) return;

        const printWindow = window.open('', '_blank');
        const canvas = document.querySelector('#generated-qr canvas');
        
        if (canvas && printWindow) {
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Código QR - ${this.currentQRCode.id}</title>
                        <style>
                            body { text-align: center; font-family: Arial; }
                            .qr-container { margin: 20px; }
                            .qr-info { margin-top: 20px; }
                        </style>
                    </head>
                    <body>
                        <h2>Código QR de Pago</h2>
                        <div class="qr-container">
                            <img src="${canvas.toDataURL()}" alt="Código QR">
                        </div>
                        <div class="qr-info">
                            <p><strong>ID:</strong> ${this.currentQRCode.id}</p>
                            <p><strong>Monto:</strong> ${this.formatCurrency(this.currentQRCode.amount)}</p>
                            <p><strong>Descripción:</strong> ${this.currentQRCode.description || 'Sin descripción'}</p>
                            <p><strong>Fecha:</strong> ${this.formatDateTime(this.currentQRCode.dateCreated)}</p>
                        </div>
                    </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.print();
        }
    }

    /**
     * Iniciar escaneo
     */
    async startScanning() {
        try {
            this.isScanning = true;
            
            // Solicitar permisos de cámara
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'environment' } 
            });
            
            const video = document.getElementById('camera-stream');
            const startBtn = document.getElementById('start-scan-btn');
            const stopBtn = document.getElementById('stop-scan-btn');
            const switchBtn = document.getElementById('switch-camera-btn');
            
            if (video) {
                video.srcObject = this.stream;
                startBtn.style.display = 'none';
                stopBtn.style.display = 'inline-block';
                switchBtn.style.display = 'inline-block';
            }
            
            // Iniciar detección de QR
            this.startQRDetection();
            
        } catch (error) {
            this.handleError('Error al acceder a la cámara', error);
            this.isScanning = false;
        }
    }

    /**
     * Detener escaneo
     */
    stopScanning() {
        this.isScanning = false;
        
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        const video = document.getElementById('camera-stream');
        const startBtn = document.getElementById('start-scan-btn');
        const stopBtn = document.getElementById('stop-scan-btn');
        const switchBtn = document.getElementById('switch-camera-btn');
        
        if (video) {
            video.srcObject = null;
        }
        
        if (startBtn) startBtn.style.display = 'inline-block';
        if (stopBtn) stopBtn.style.display = 'none';
        if (switchBtn) switchBtn.style.display = 'none';
    }

    /**
     * Cambiar cámara
     */
    async switchCamera() {
        const video = document.getElementById('camera-stream');
        if (!video || !this.stream) return;

        const tracks = this.stream.getVideoTracks();
        if (tracks.length === 0) return;

        const currentFacingMode = tracks[0].getSettings().facingMode;
        const newFacingMode = currentFacingMode === 'user' ? 'environment' : 'user';

        try {
            const newStream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: newFacingMode } 
            });
            
            // Detener stream anterior
            this.stream.getTracks().forEach(track => track.stop());
            
            // Usar nuevo stream
            this.stream = newStream;
            video.srcObject = this.stream;
            
        } catch (error) {
            this.handleError('Error al cambiar cámara', error);
        }
    }

    /**
     * Iniciar detección de QR
     */
    startQRDetection() {
        const video = document.getElementById('camera-stream');
        const canvas = document.getElementById('scan-canvas');
        
        if (!video || !canvas) return;

        const detectQR = () => {
            if (!this.isScanning) return;
            
            const context = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Aquí se implementaría la detección de QR usando una librería como jsQR
            // Por simplicidad, simularemos la detección
            setTimeout(() => {
                if (this.isScanning && Math.random() < 0.1) { // 10% probabilidad de detección
                    this.simulateQRDetection();
                }
                detectQR();
            }, 100);
        };
        
        detectQR();
    }

    /**
     * Simular detección de QR (en una implementación real se usaría jsQR)
     */
    simulateQRDetection() {
        const demoQR = {
            id: 'QR' + Math.random().toString(36).substr(2, 6).toUpperCase(),
            amount: Math.floor(Math.random() * 500) + 10,
            currency: 'PEN',
            description: 'Pago detectado',
            timestamp: new Date().toISOString()
        };
        
        this.handleQRDetected(demoQR);
    }

    /**
     * Manejar QR detectado
     */
    handleQRDetected(qrData) {
        this.stopScanning();
        
        const scannedInfo = document.getElementById('scanned-info');
        const scanActions = document.getElementById('scan-actions');
        
        if (scannedInfo) {
            scannedInfo.innerHTML = `
                <div class="scanned-details">
                    <h4><i class="fas fa-check-circle"></i> Código QR Detectado</h4>
                    <div class="details-grid">
                        <div class="detail-item">
                            <label>ID:</label>
                            <span>${qrData.id}</span>
                        </div>
                        <div class="detail-item">
                            <label>Monto:</label>
                            <span class="amount">${this.formatCurrency(qrData.amount)}</span>
                        </div>
                        <div class="detail-item">
                            <label>Descripción:</label>
                            <span>${qrData.description || 'Sin descripción'}</span>
                        </div>
                        <div class="detail-item">
                            <label>Fecha:</label>
                            <span>${this.formatDateTime(qrData.timestamp)}</span>
                        </div>
                    </div>
                </div>
            `;
            scannedInfo.style.display = 'block';
        }
        
        if (scanActions) {
            scanActions.style.display = 'flex';
        }
        
        this.detectedQR = qrData;
        window.bancoApp?.showNotification('Código QR detectado exitosamente', 'success');
    }

    /**
     * Procesar pago
     */
    processPayment() {
        if (!this.detectedQR) return;
        
        const modal = document.getElementById('payment-modal');
        const content = document.getElementById('payment-modal-content');
        
        content.innerHTML = `
            <div class="payment-details">
                <div class="payment-summary">
                    <h4>Confirmar Pago</h4>
                    <div class="summary-row">
                        <span>Monto a pagar:</span>
                        <span class="amount">${this.formatCurrency(this.detectedQR.amount)}</span>
                    </div>
                    <div class="summary-row">
                        <span>Concepto:</span>
                        <span>${this.detectedQR.description || 'Pago QR'}</span>
                    </div>
                    <div class="summary-row">
                        <span>ID del QR:</span>
                        <span>${this.detectedQR.id}</span>
                    </div>
                </div>
                
                <div class="payment-account">
                    <h5>Cuenta de origen:</h5>
                    <select id="payment-account-select">
                        ${this.data.accounts.map(account => 
                            `<option value="${account.id}">${account.type} - ${account.number}</option>`
                        ).join('')}
                    </select>
                </div>
                
                <div class="payment-pin">
                    <h5>Ingresa tu PIN de seguridad:</h5>
                    <input type="password" 
                           id="payment-pin" 
                           maxlength="6" 
                           placeholder="••••••"
                           oninput="qrGeneratorPage.validatePaymentPin()">
                </div>
            </div>
        `;
        
        modal.classList.remove('hidden');
    }

    /**
     * Validar PIN de pago
     */
    validatePaymentPin() {
        const pin = document.getElementById('payment-pin')?.value;
        const confirmBtn = document.getElementById('confirm-payment-btn');
        
        if (confirmBtn) {
            confirmBtn.disabled = !pin || pin.length < 4;
        }
    }

    /**
     * Confirmar pago
     */
    async confirmPayment() {
        const pin = document.getElementById('payment-pin')?.value;
        const accountId = document.getElementById('payment-account-select')?.value;
        
        if (!pin || pin.length < 4) {
            window.bancoApp?.showNotification('PIN inválido', 'error');
            return;
        }
        
        try {
            const confirmBtn = document.getElementById('confirm-payment-btn');
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
            
            // Simular procesamiento
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Agregar a historial
            const scannedQR = {
                ...this.detectedQR,
                type: 'scanned',
                status: 'used',
                used: true,
                usedDate: new Date().toISOString(),
                scanCount: 1,
                accountId: accountId
            };
            
            this.data.scannedQRCodes.push(scannedQR);
            this.data.qrHistory.unshift(scannedQR);
            this.updateHistoryStats();
            
            window.bancoApp?.showNotification('Pago procesado exitosamente', 'success');
            this.closePaymentModal();
            this.dismissScan();
            
        } catch (error) {
            this.handleError('Error al procesar el pago', error);
        } finally {
            const confirmBtn = document.getElementById('confirm-payment-btn');
            if (confirmBtn) {
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = '<i class="fas fa-check"></i> Confirmar Pago';
            }
        }
    }

    /**
     * Cerrar modal de pago
     */
    closePaymentModal() {
        const modal = document.getElementById('payment-modal');
        modal.classList.add('hidden');
    }

    /**
     * Guardar código QR escaneado
     */
    saveQRCode() {
        if (!this.detectedQR) return;
        
        const savedQR = {
            ...this.detectedQR,
            type: 'scanned',
            status: 'active',
            used: false,
            scanCount: 1,
            dateCreated: new Date().toISOString()
        };
        
        this.data.qrHistory.unshift(savedQR);
        this.updateHistoryStats();
        
        window.bancoApp?.showNotification('Código QR guardado', 'success');
        this.dismissScan();
    }

    /**
     * Descartar escaneo
     */
    dismissScan() {
        const scannedInfo = document.getElementById('scanned-info');
        const scanActions = document.getElementById('scan-actions');
        
        if (scannedInfo) scannedInfo.style.display = 'none';
        if (scanActions) scanActions.style.display = 'none';
        
        this.detectedQR = null;
    }

    /**
     * Actualizar estadísticas del historial
     */
    updateHistoryStats() {
        const generated = this.data.qrHistory.filter(qr => qr.type === 'generated').length;
        const scanned = this.data.qrHistory.filter(qr => qr.type === 'scanned').length;
        const pending = this.data.qrHistory.filter(qr => qr.status === 'active' && !qr.used).length;
        const totalValue = this.data.qrHistory.reduce((sum, qr) => sum + qr.amount, 0);
        
        document.getElementById('totalGenerated').textContent = generated;
        document.getElementById('totalScanned').textContent = scanned;
        document.getElementById('pendingCount').textContent = pending;
        document.getElementById('totalValue').textContent = this.formatCurrency(totalValue);
        
        this.renderQRHistoryList();
    }

    /**
     * Renderizar lista del historial
     */
    renderQRHistoryList() {
        const container = document.getElementById('qr-history-list');
        if (!container) return;
        
        if (this.data.qrHistory.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <i class="fas fa-history"></i>
                    </div>
                    <h3>No hay historial</h3>
                    <p>Genera o escanea códigos QR para ver el historial aquí</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.data.qrHistory.map(qr => `
            <div class="qr-history-item">
                <div class="qr-info">
                    <div class="qr-type ${qr.type}">
                        <i class="fas ${qr.type === 'generated' ? 'fa-plus-circle' : 'fa-camera'}"></i>
                        <span>${qr.type === 'generated' ? 'Generado' : 'Escaneado'}</span>
                    </div>
                    <div class="qr-details">
                        <h5>${qr.description || 'Sin descripción'}</h5>
                        <div class="qr-meta">
                            <span class="amount">${this.formatCurrency(qr.amount)}</span>
                            <span class="date">${this.formatDateTime(qr.dateCreated)}</span>
                            <span class="status-badge status-${qr.status}">${this.getStatusName(qr.status)}</span>
                        </div>
                    </div>
                </div>
                <div class="qr-actions">
                    <button class="btn btn-sm btn-outline" onclick="qrGeneratorPage.viewQRDetails('${qr.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="qrGeneratorPage.replicateQR('${qr.id}')">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    /**
     * Renderizar gráfico de actividad QR
     */
    renderQRChart() {
        const ctx = document.getElementById('qr-activity-chart');
        if (!ctx) return;
        
        // Datos de ejemplo para los últimos 7 días
        const labels = [];
        const generatedData = [];
        const scannedData = [];
        
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('es-PE', { weekday: 'short' }));
            
            // Datos simulados
            generatedData.push(Math.floor(Math.random() * 10) + 1);
            scannedData.push(Math.floor(Math.random() * 8) + 1);
        }
        
        if (this.data.qrChart) {
            this.data.qrChart.destroy();
        }
        
        this.data.qrChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Generados',
                        data: generatedData,
                        backgroundColor: 'rgba(33, 150, 243, 0.8)',
                        borderColor: 'rgba(33, 150, 243, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Escaneados',
                        data: scannedData,
                        backgroundColor: 'rgba(76, 175, 80, 0.8)',
                        borderColor: 'rgba(76, 175, 80, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    /**
     * Filtrar historial
     */
    filterHistory() {
        // Implementar lógica de filtrado
        this.renderQRHistoryList();
    }

    /**
     * Ver detalles del QR
     */
    viewQRDetails(qrId) {
        const qr = this.data.qrHistory.find(q => q.id === qrId);
        if (!qr) return;
        
        window.bancoApp?.showNotification(`Detalles de QR ${qrId}`, 'info');
    }

    /**
     * Replicar QR
     */
    replicateQR(qrId) {
        const qr = this.data.qrHistory.find(q => q.id === qrId);
        if (!qr) return;
        
        // Llenar formulario con datos del QR
        document.getElementById('qr-amount').value = qr.amount;
        document.getElementById('qr-description').value = qr.description;
        document.getElementById('qr-category').value = qr.category;
        document.getElementById('qr-account').value = qr.accountId;
        
        // Cambiar a modo de generación
        this.switchMode('generate');
        
        window.bancoApp?.showNotification('Datos del QR cargados en el formulario', 'info');
    }

    /**
     * Exportar historial QR
     */
    exportQRHistory() {
        try {
            const csv = this.generateQRHistoryCSV();
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', `qr_history_${new Date().toISOString().split('T')[0]}.csv`);
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            window.bancoApp?.showNotification('Historial QR exportado', 'success');
        } catch (error) {
            this.handleError('Error al exportar historial', error);
        }
    }

    /**
     * Limpiar todo el historial
     */
    clearAllHistory() {
        if (confirm('¿Estás seguro de que quieres eliminar todo el historial?')) {
            this.data.qrHistory = [];
            this.data.scannedQRCodes = [];
            this.updateHistoryStats();
            window.bancoApp?.showNotification('Historial eliminado', 'success');
        }
    }

    /**
     * Generar CSV del historial QR
     */
    generateQRHistoryCSV() {
        const headers = ['ID', 'Tipo', 'Monto', 'Moneda', 'Descripción', 'Estado', 'Fecha'];
        const rows = this.data.qrHistory.map(qr => [
            qr.id,
            qr.type === 'generated' ? 'Generado' : 'Escaneado',
            qr.amount,
            qr.currency,
            qr.description || '',
            this.getStatusName(qr.status),
            this.formatDateTime(qr.dateCreated)
        ]);
        
        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    /**
     * Encriptar datos del QR
     */
    encryptQRData(data) {
        // Implementación básica de encriptación
        // En una aplicación real se usaría una librería como CryptoJS
        const jsonString = JSON.stringify(data);
        return btoa(jsonString); // Base64 encoding como ejemplo
    }

    /**
     * Mostrar/ocultar loading del formulario
     */
    showFormLoading(show) {
        const submitButton = document.querySelector('#qr-form button[type="submit"]');
        if (submitButton) {
            if (show) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
            } else {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-qrcode"></i> Generar QR';
            }
        }
    }

    /**
     * Utilidades
     */
    getStatusName(status) {
        const names = {
            'active': 'Activo',
            'used': 'Usado',
            'expired': 'Expirado'
        };
        return names[status] || status;
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('es-PE', {
            style: 'currency',
            currency: 'PEN'
        }).format(amount);
    }

    formatDateTime(dateString) {
        return new Intl.DateTimeFormat('es-PE', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(dateString));
    }

    /**
     * Mostrar loading
     */
    showLoading() {
        const loading = document.getElementById('page-loading');
        if (loading) {
            loading.classList.remove('hidden');
        }
    }

    /**
     * Ocultar loading
     */
    hideLoading() {
        const loading = document.getElementById('page-loading');
        if (loading) {
            loading.classList.add('hidden');
        }
    }

    /**
     * Manejar errores
     */
    handleError(message, error) {
        console.error(message, error);
        if (window.bancoApp?.showNotification) {
            window.bancoApp.showNotification(message, 'error');
        }
    }

    /**
     * Obtener HTML de error
     */
    getErrorHTML(message) {
        return `
            <div class="error-container">
                <div class="error-icon">
                    <i class="fas fa-qrcode"></i>
                </div>
                <h3>Error al cargar el generador QR</h3>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">
                    <i class="fas fa-refresh"></i> Reintentar
                </button>
            </div>
        `;
    }
}

// Instanciar página globalmente
window.qrGeneratorPage = new QRGeneratorPage();