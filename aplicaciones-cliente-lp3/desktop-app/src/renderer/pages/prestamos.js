/**
 * Página Préstamos - Sistema Bancario Desktop
 * Solicitud y gestión de préstamos con cálculos y validaciones
 */

class PrestamosPage {
    constructor() {
        this.data = {
            loans: [],
            loanTypes: [
                {
                    id: 'personal',
                    name: 'Préstamo Personal',
                    minAmount: 1000,
                    maxAmount: 50000,
                    minTerm: 6,
                    maxTerm: 60,
                    interestRate: 0.15,
                    description: 'Préstamo para uso personal sin garantías'
                },
                {
                    id: 'hipotecario',
                    name: 'Préstamo Hipotecario',
                    minAmount: 50000,
                    maxAmount: 500000,
                    minTerm: 60,
                    maxTerm: 360,
                    interestRate: 0.08,
                    description: 'Préstamo para compra de vivienda con garantía hipotecaria'
                },
                {
                    id: 'vehicular',
                    name: 'Préstamo Vehicular',
                    minAmount: 15000,
                    maxAmount: 150000,
                    minTerm: 12,
                    maxTerm: 84,
                    interestRate: 0.12,
                    description: 'Préstamo para compra de vehículo con garantía vehicular'
                },
                {
                    id: 'empresarial',
                    name: 'Préstamo Empresarial',
                    minAmount: 10000,
                    maxAmount: 1000000,
                    minTerm: 12,
                    maxTerm: 120,
                    interestRate: 0.10,
                    description: 'Préstamo para desarrollo y crecimiento empresarial'
                }
            ],
            formData: {
                type: '',
                amount: '',
                term: '',
                purpose: '',
                income: '',
                existingLoans: '',
                collateral: ''
            },
            calculations: {
                monthlyPayment: 0,
                totalAmount: 0,
                totalInterest: 0,
                interestRate: 0
            }
        };
        this.currentTab = 'list';
    }

    /**
     * Renderizar la página de préstamos
     */
    async render() {
        try {
            this.showLoading();
            await this.loadLoans();
            this.hideLoading();
            return this.getHTML();

        } catch (error) {
            this.hideLoading();
            this.handleError('Error al cargar los préstamos', error);
            return this.getErrorHTML(error.message);
        }
    }

    /**
     * Obtener HTML de la página
     */
    getHTML() {
        return `
            <div id="prestamos-content" class="prestamos-container">
                <!-- Header -->
                <div class="page-header">
                    <div class="page-title">
                        <h1><i class="fas fa-money-bill-wave"></i> Gestión de Préstamos</h1>
                        <p>Solicita y administra tus préstamos bancarios</p>
                    </div>
                    <div class="page-actions">
                        <button class="btn btn-outline" onclick="prestamosPage.exportLoans()">
                            <i class="fas fa-download"></i> Exportar
                        </button>
                        <button class="btn btn-primary" onclick="prestamosPage.showNewLoanTab()">
                            <i class="fas fa-plus"></i> Solicitar Préstamo
                        </button>
                    </div>
                </div>

                <!-- Tabs Navigation -->
                <div class="tabs-navigation">
                    <button class="tab-button ${this.currentTab === 'list' ? 'active' : ''}" 
                            onclick="prestamosPage.switchTab('list')">
                        <i class="fas fa-list"></i> Mis Préstamos
                    </button>
                    <button class="tab-button ${this.currentTab === 'request' ? 'active' : ''}" 
                            onclick="prestamosPage.switchTab('request')">
                        <i class="fas fa-plus-circle"></i> Solicitar Préstamo
                    </button>
                    <button class="tab-button ${this.currentTab === 'calculator' ? 'active' : ''}" 
                            onclick="prestamosPage.switchTab('calculator')">
                        <i class="fas fa-calculator"></i> Calculadora
                    </button>
                </div>

                <!-- Tab: Lista de préstamos -->
                <div class="tab-content ${this.currentTab === 'list' ? 'active' : ''}" id="loans-list-tab">
                    <div class="loans-summary">
                        <div class="summary-card">
                            <div class="summary-icon primary">
                                <i class="fas fa-handshake"></i>
                            </div>
                            <div class="summary-content">
                                <h4>Préstamos Activos</h4>
                                <div class="summary-value" id="activeLoans">0</div>
                            </div>
                        </div>
                        
                        <div class="summary-card">
                            <div class="summary-icon warning">
                                <i class="fas fa-credit-card"></i>
                            </div>
                            <div class="summary-content">
                                <h4>Deuda Total</h4>
                                <div class="summary-value" id="totalDebt">S/ 0.00</div>
                            </div>
                        </div>
                        
                        <div class="summary-card">
                            <div class="summary-icon success">
                                <i class="fas fa-calendar-check"></i>
                            </div>
                            <div class="summary-content">
                                <h4>Pagos del Mes</h4>
                                <div class="summary-value" id="monthlyPayments">S/ 0.00</div>
                            </div>
                        </div>
                        
                        <div class="summary-card">
                            <div class="summary-icon info">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <div class="summary-content">
                                <h4>Tasa Promedio</h4>
                                <div class="summary-value" id="averageRate">0%</div>
                            </div>
                        </div>
                    </div>

                    <div class="loans-list-section">
                        <div class="section-header">
                            <h3>Mis Préstamos</h3>
                            <div class="filters">
                                <select id="loan-status-filter" onchange="prestamosPage.filterLoansByStatus(this.value)">
                                    <option value="all">Todos los estados</option>
                                    <option value="active">Activos</option>
                                    <option value="pending">Pendientes</option>
                                    <option value="approved">Aprobados</option>
                                    <option value="rejected">Rechazados</option>
                                    <option value="paid">Pagados</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="loans-list" id="loans-list">
                            <!-- Los préstamos se cargarán dinámicamente -->
                        </div>
                    </div>
                </div>

                <!-- Tab: Solicitud de préstamo -->
                <div class="tab-content ${this.currentTab === 'request' ? 'active' : ''}" id="loan-request-tab">
                    <div class="request-form-container">
                        <div class="form-header">
                            <h3>Solicitar Nuevo Préstamo</h3>
                            <p>Completa el formulario para solicitar tu préstamo</p>
                        </div>
                        
                        <form id="loan-request-form" class="loan-request-form">
                            <!-- Tipo de préstamo -->
                            <div class="form-section">
                                <h4>Tipo de Préstamo</h4>
                                <div class="loan-types-grid">
                                    ${this.data.loanTypes.map(type => `
                                        <div class="loan-type-card" data-type="${type.id}">
                                            <div class="loan-type-header">
                                                <input type="radio" 
                                                       id="type-${type.id}" 
                                                       name="loanType" 
                                                       value="${type.id}"
                                                       onchange="prestamosPage.selectLoanType('${type.id}')">
                                                <label for="type-${type.id}">
                                                    <h5>${type.name}</h5>
                                                    <p>${type.description}</p>
                                                </label>
                                            </div>
                                            <div class="loan-type-details">
                                                <div class="detail-item">
                                                    <span class="label">Monto:</span>
                                                    <span class="value">S/ ${type.minAmount.toLocaleString()} - S/ ${type.maxAmount.toLocaleString()}</span>
                                                </div>
                                                <div class="detail-item">
                                                    <span class="label">Plazo:</span>
                                                    <span class="value">${type.minTerm} - ${type.maxTerm} meses</span>
                                                </div>
                                                <div class="detail-item">
                                                    <span class="label">Tasa:</span>
                                                    <span class="value">${(type.interestRate * 100).toFixed(1)}% anual</span>
                                                </div>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                                <div class="error-message" id="loan-type-error"></div>
                            </div>

                            <!-- Detalles del préstamo -->
                            <div class="form-section">
                                <h4>Detalles del Préstamo</h4>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="loan-amount">Monto Solicitado *</label>
                                        <div class="input-group">
                                            <span class="input-prefix">S/</span>
                                            <input type="number" 
                                                   id="loan-amount" 
                                                   name="amount" 
                                                   min="1000" 
                                                   step="100"
                                                   placeholder="Ingresa el monto" 
                                                   required
                                                   onchange="prestamosPage.calculateLoan()">
                                        </div>
                                        <div class="help-text" id="amount-help"></div>
                                        <div class="error-message" id="amount-error"></div>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="loan-term">Plazo (meses) *</label>
                                        <input type="number" 
                                               id="loan-term" 
                                               name="term" 
                                               min="6" 
                                               max="360" 
                                               placeholder="Número de meses" 
                                               required
                                               onchange="prestamosPage.calculateLoan()">
                                        <div class="help-text" id="term-help"></div>
                                        <div class="error-message" id="term-error"></div>
                                    </div>
                                </div>
                                
                                <div class="form-group">
                                    <label for="loan-purpose">Propósito del Préstamo *</label>
                                    <select id="loan-purpose" name="purpose" required>
                                        <option value="">Selecciona el propósito</option>
                                        <option value="personal">Gastos Personales</option>
                                        <option value="debt-consolidation">Consolidación de Deudas</option>
                                        <option value="home-improvement">Mejoras del Hogar</option>
                                        <option value="education">Educación</option>
                                        <option value="medical">Gastos Médicos</option>
                                        <option value="business">Negocio</option>
                                        <option value="vehicle">Compra de Vehículo</option>
                                        <option value="real-estate">Bienes Raíces</option>
                                        <option value="other">Otro</option>
                                    </select>
                                    <div class="error-message" id="purpose-error"></div>
                                </div>
                            </div>

                            <!-- Información financiera -->
                            <div class="form-section">
                                <h4>Información Financiera</h4>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="monthly-income">Ingresos Mensuales *</label>
                                        <div class="input-group">
                                            <span class="input-prefix">S/</span>
                                            <input type="number" 
                                                   id="monthly-income" 
                                                   name="income" 
                                                   min="0" 
                                                   step="100"
                                                   placeholder="Ingresos mensuales" 
                                                   required>
                                        </div>
                                        <div class="error-message" id="income-error"></div>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="existing-loans">Deudas Existentes</label>
                                        <div class="input-group">
                                            <span class="input-prefix">S/</span>
                                            <input type="number" 
                                                   id="existing-loans" 
                                                   name="existingLoans" 
                                                   min="0" 
                                                   step="100"
                                                   placeholder="0.00">
                                        </div>
                                        <div class="help-text">Opcional: Otras deudas que tengas</div>
                                    </div>
                                </div>
                            </div>

                            <!-- Garantías (opcional para algunos tipos) -->
                            <div class="form-section">
                                <h4>Garantías</h4>
                                <div class="form-group">
                                    <label for="collateral">Tipo de Garantía</label>
                                    <select id="collateral" name="collateral">
                                        <option value="">Sin garantía</option>
                                        <option value="real-estate">Inmueble</option>
                                        <option value="vehicle">Vehículo</option>
                                        <option value="equipment">Equipos</option>
                                        <option value="savings">Ahorros</option>
                                    </select>
                                </div>
                            </div>

                            <!-- Resumen de cálculos -->
                            <div class="form-section" id="loan-summary" style="display: none;">
                                <h4>Resumen del Préstamo</h4>
                                <div class="loan-summary-card">
                                    <div class="summary-row">
                                        <span>Monto del Préstamo:</span>
                                        <span id="summary-amount">S/ 0.00</span>
                                    </div>
                                    <div class="summary-row">
                                        <span>Plazo:</span>
                                        <span id="summary-term">0 meses</span>
                                    </div>
                                    <div class="summary-row">
                                        <span>Tasa de Interés:</span>
                                        <span id="summary-rate">0% anual</span>
                                    </div>
                                    <div class="summary-row">
                                        <span>Pago Mensual:</span>
                                        <span id="summary-monthly-payment" class="highlight">S/ 0.00</span>
                                    </div>
                                    <div class="summary-row">
                                        <span>Total a Pagar:</span>
                                        <span id="summary-total">S/ 0.00</span>
                                    </div>
                                    <div class="summary-row">
                                        <span>Total de Intereses:</span>
                                        <span id="summary-interest">S/ 0.00</span>
                                    </div>
                                </div>
                            </div>

                            <div class="form-actions">
                                <button type="button" class="btn btn-secondary" onclick="prestamosPage.resetForm()">
                                    Limpiar Formulario
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-paper-plane"></i> Enviar Solicitud
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <!-- Tab: Calculadora -->
                <div class="tab-content ${this.currentTab === 'calculator' ? 'active' : ''}" id="loan-calculator-tab">
                    <div class="calculator-container">
                        <div class="calculator-header">
                            <h3>Calculadora de Préstamos</h3>
                            <p>Simula diferentes opciones de préstamo</p>
                        </div>
                        
                        <div class="calculator-form">
                            <div class="form-group">
                                <label>Tipo de Préstamo:</label>
                                <select id="calc-loan-type" onchange="prestamosPage.updateCalculatorType()">
                                    ${this.data.loanTypes.map(type => `
                                        <option value="${type.id}">${type.name}</option>
                                    `).join('')}
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label>Monto del Préstamo:</label>
                                <div class="input-group">
                                    <span class="input-prefix">S/</span>
                                    <input type="number" 
                                           id="calc-amount" 
                                           value="25000" 
                                           min="1000" 
                                           max="1000000" 
                                           step="1000"
                                           onchange="prestamosPage.calculateLoan()">
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label>Plazo (meses):</label>
                                <input type="range" 
                                       id="calc-term" 
                                       min="6" 
                                       max="360" 
                                       value="60"
                                       oninput="prestamosPage.updateTermDisplay(this.value)">
                                <div class="range-display">
                                    <span id="calc-term-display">60 meses</span>
                                </div>
                            </div>
                            
                            <div class="calc-results">
                                <div class="result-card">
                                    <h4>Pago Mensual</h4>
                                    <div class="result-value" id="calc-monthly-payment">S/ 0.00</div>
                                </div>
                                
                                <div class="result-card">
                                    <h4>Total a Pagar</h4>
                                    <div class="result-value" id="calc-total-payment">S/ 0.00</div>
                                </div>
                                
                                <div class="result-card">
                                    <h4>Total Intereses</h4>
                                    <div class="result-value" id="calc-total-interest">S/ 0.00</div>
                                </div>
                            </div>
                            
                            <div class="amortization-schedule">
                                <h4>Tabla de Amortización (Primeros 12 meses)</h4>
                                <div class="schedule-table" id="amortization-table">
                                    <!-- La tabla se generará dinámicamente -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal para ver detalles del préstamo -->
            <div id="loan-details-modal" class="modal hidden">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Detalles del Préstamo</h3>
                        <button class="modal-close" onclick="prestamosPage.closeLoanDetailsModal()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body" id="loan-details-content">
                        <!-- El contenido se cargará dinámicamente -->
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Cargar préstamos desde la API
     */
    async loadLoans() {
        try {
            const loans = await API.getLoans ? await API.getLoans() : this.getDemoLoans();
            this.data.loans = loans;
            this.updateSummary();
            this.renderLoansList();
        } catch (error) {
            console.error('Error loading loans:', error);
            this.data.loans = this.getDemoLoans();
            this.updateSummary();
            this.renderLoansList();
        }
    }

    /**
     * Obtener préstamos de demostración
     */
    getDemoLoans() {
        return [
            {
                id: 'LOAN001',
                type: 'personal',
                typeName: 'Préstamo Personal',
                amount: 15000,
                term: 36,
                interestRate: 0.15,
                monthlyPayment: 558.43,
                totalAmount: 20103.48,
                totalInterest: 5103.48,
                status: 'active',
                purpose: 'Consolidación de Deudas',
                dateRequested: '2024-01-15T00:00:00Z',
                dateApproved: '2024-01-20T00:00:00Z',
                startDate: '2024-01-25T00:00:00Z',
                remainingBalance: 12345.67,
                nextPaymentDate: '2024-11-25T00:00:00Z',
                paymentsMade: 8,
                income: 5000,
                existingLoans: 2000
            },
            {
                id: 'LOAN002',
                type: 'vehicular',
                typeName: 'Préstamo Vehicular',
                amount: 45000,
                term: 60,
                interestRate: 0.12,
                monthlyPayment: 1034.45,
                totalAmount: 62067.00,
                totalInterest: 17067.00,
                status: 'active',
                purpose: 'Compra de Vehículo',
                dateRequested: '2024-03-10T00:00:00Z',
                dateApproved: '2024-03-15T00:00:00Z',
                startDate: '2024-03-20T00:00:00Z',
                remainingBalance: 38500.23,
                nextPaymentDate: '2024-11-20T00:00:00Z',
                paymentsMade: 6,
                income: 8500,
                existingLoans: 500
            },
            {
                id: 'LOAN003',
                type: 'personal',
                typeName: 'Préstamo Personal',
                amount: 8000,
                term: 24,
                interestRate: 0.15,
                monthlyPayment: 400.15,
                totalAmount: 9603.60,
                totalInterest: 1603.60,
                status: 'paid',
                purpose: 'Mejoras del Hogar',
                dateRequested: '2023-08-01T00:00:00Z',
                dateApproved: '2023-08-05T00:00:00Z',
                startDate: '2023-08-10T00:00:00Z',
                endDate: '2025-08-10T00:00:00Z',
                remainingBalance: 0,
                nextPaymentDate: null,
                paymentsMade: 24,
                income: 4200,
                existingLoans: 0
            },
            {
                id: 'LOAN004',
                type: 'hipotecario',
                typeName: 'Préstamo Hipotecario',
                amount: 180000,
                term: 240,
                interestRate: 0.08,
                monthlyPayment: 1503.64,
                totalAmount: 360873.60,
                totalInterest: 180873.60,
                status: 'pending',
                purpose: 'Compra de Vivienda',
                dateRequested: '2024-10-20T00:00:00Z',
                dateApproved: null,
                startDate: null,
                remainingBalance: 180000,
                nextPaymentDate: null,
                paymentsMade: 0,
                income: 12000,
                existingLoans: 0
            }
        ];
    }

    /**
     * Cambiar tab activo
     */
    switchTab(tabName) {
        this.currentTab = tabName;
        this.render(); // Re-renderizar para mostrar el tab correcto
        
        if (tabName === 'calculator') {
            setTimeout(() => {
                this.initializeCalculator();
            }, 100);
        }
    }

    /**
     * Mostrar tab de nueva solicitud
     */
    showNewLoanTab() {
        this.switchTab('request');
    }

    /**
     * Seleccionar tipo de préstamo
     */
    selectLoanType(typeId) {
        this.data.formData.type = typeId;
        const selectedType = this.data.loanTypes.find(t => t.id === typeId);
        
        if (selectedType) {
            // Actualizar límites de los inputs
            const amountInput = document.getElementById('loan-amount');
            const termInput = document.getElementById('loan-term');
            
            if (amountInput) {
                amountInput.min = selectedType.minAmount;
                amountInput.max = selectedType.maxAmount;
                amountInput.placeholder = `Mínimo S/ ${selectedType.minAmount.toLocaleString()}`;
            }
            
            if (termInput) {
                termInput.min = selectedType.minTerm;
                termInput.max = selectedType.maxTerm;
                termInput.placeholder = `Entre ${selectedType.minTerm} y ${selectedType.maxTerm} meses`;
            }

            // Actualizar textos de ayuda
            document.getElementById('amount-help').textContent = 
                `Monto entre S/ ${selectedType.minAmount.toLocaleString()} y S/ ${selectedType.maxAmount.toLocaleString()}`;
            document.getElementById('term-help').textContent = 
                `Plazo entre ${selectedType.minTerm} y ${selectedType.maxTerm} meses`;

            // Marcar la tarjeta como seleccionada
            document.querySelectorAll('.loan-type-card').forEach(card => {
                card.classList.remove('selected');
            });
            document.querySelector(`[data-type="${typeId}"]`).classList.add('selected');
        }
    }

    /**
     * Calcular préstamo
     */
    calculateLoan() {
        const amount = parseFloat(document.getElementById('loan-amount')?.value) || 0;
        const term = parseInt(document.getElementById('loan-term')?.value) || 0;
        const type = this.data.formData.type;

        if (amount && term && type) {
            const loanType = this.data.loanTypes.find(t => t.id === type);
            if (loanType) {
                const monthlyRate = loanType.interestRate / 12;
                const monthlyPayment = amount * (monthlyRate * Math.pow(1 + monthlyRate, term)) / 
                                     (Math.pow(1 + monthlyRate, term) - 1);
                const totalAmount = monthlyPayment * term;
                const totalInterest = totalAmount - amount;

                this.data.calculations = {
                    monthlyPayment,
                    totalAmount,
                    totalInterest,
                    interestRate: loanType.interestRate
                };

                this.updateLoanSummary();
            }
        }
    }

    /**
     * Actualizar resumen del préstamo
     */
    updateLoanSummary() {
        const summary = document.getElementById('loan-summary');
        if (summary && this.data.calculations.monthlyPayment > 0) {
            document.getElementById('summary-amount').textContent = this.formatCurrency(parseFloat(document.getElementById('loan-amount').value));
            document.getElementById('summary-term').textContent = `${document.getElementById('loan-term').value} meses`;
            document.getElementById('summary-rate').textContent = `${(this.data.calculations.interestRate * 100).toFixed(1)}% anual`;
            document.getElementById('summary-monthly-payment').textContent = this.formatCurrency(this.data.calculations.monthlyPayment);
            document.getElementById('summary-total').textContent = this.formatCurrency(this.data.calculations.totalAmount);
            document.getElementById('summary-interest').textContent = this.formatCurrency(this.data.calculations.totalInterest);
            
            summary.style.display = 'block';
        }
    }

    /**
     * Inicializar calculadora
     */
    initializeCalculator() {
        this.updateCalculatorType();
        this.calculateLoanForCalculator();
    }

    /**
     * Actualizar tipo en calculadora
     */
    updateCalculatorType() {
        const typeId = document.getElementById('calc-loan-type').value;
        const loanType = this.data.loanTypes.find(t => t.id === typeId);
        
        if (loanType) {
            const amountInput = document.getElementById('calc-amount');
            const termInput = document.getElementById('calc-term');
            
            if (amountInput) {
                amountInput.min = loanType.minAmount;
                amountInput.max = loanType.maxAmount;
            }
            
            if (termInput) {
                termInput.min = loanType.minTerm;
                termInput.max = loanType.maxTerm;
            }
            
            this.calculateLoanForCalculator();
        }
    }

    /**
     * Calcular préstamo para calculadora
     */
    calculateLoanForCalculator() {
        const amount = parseFloat(document.getElementById('calc-amount').value);
        const term = parseInt(document.getElementById('calc-term').value);
        const typeId = document.getElementById('calc-loan-type').value;
        const loanType = this.data.loanTypes.find(t => t.id === typeId);

        if (amount && term && loanType) {
            const monthlyRate = loanType.interestRate / 12;
            const monthlyPayment = amount * (monthlyRate * Math.pow(1 + monthlyRate, term)) / 
                                 (Math.pow(1 + monthlyRate, term) - 1);
            const totalAmount = monthlyPayment * term;
            const totalInterest = totalAmount - amount;

            document.getElementById('calc-monthly-payment').textContent = this.formatCurrency(monthlyPayment);
            document.getElementById('calc-total-payment').textContent = this.formatCurrency(totalAmount);
            document.getElementById('calc-total-interest').textContent = this.formatCurrency(totalInterest);

            this.generateAmortizationSchedule(amount, term, monthlyRate, monthlyPayment);
        }
    }

    /**
     * Actualizar display del plazo
     */
    updateTermDisplay(value) {
        document.getElementById('calc-term-display').textContent = `${value} meses`;
        this.calculateLoanForCalculator();
    }

    /**
     * Generar tabla de amortización
     */
    generateAmortizationSchedule(amount, term, monthlyRate, monthlyPayment) {
        let balance = amount;
        const schedule = [];

        for (let i = 1; i <= Math.min(12, term); i++) {
            const interestPayment = balance * monthlyRate;
            const principalPayment = monthlyPayment - interestPayment;
            balance -= principalPayment;

            schedule.push({
                month: i,
                payment: monthlyPayment,
                principal: principalPayment,
                interest: interestPayment,
                balance: Math.max(0, balance)
            });
        }

        const tableContainer = document.getElementById('amortization-table');
        if (tableContainer) {
            tableContainer.innerHTML = `
                <table class="amortization-table">
                    <thead>
                        <tr>
                            <th>Mes</th>
                            <th>Pago</th>
                            <th>Capital</th>
                            <th>Interés</th>
                            <th>Saldo</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${schedule.map(row => `
                            <tr>
                                <td>${row.month}</td>
                                <td>${this.formatCurrency(row.payment)}</td>
                                <td>${this.formatCurrency(row.principal)}</td>
                                <td>${this.formatCurrency(row.interest)}</td>
                                <td>${this.formatCurrency(row.balance)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    }

    /**
     * Actualizar resumen
     */
    updateSummary() {
        const activeLoans = this.data.loans.filter(l => l.status === 'active');
        const totalDebt = activeLoans.reduce((sum, loan) => sum + loan.remainingBalance, 0);
        const monthlyPayments = activeLoans.reduce((sum, loan) => sum + loan.monthlyPayment, 0);
        const averageRate = activeLoans.length > 0 ? 
            activeLoans.reduce((sum, loan) => sum + loan.interestRate, 0) / activeLoans.length : 0;

        document.getElementById('activeLoans').textContent = activeLoans.length;
        document.getElementById('totalDebt').textContent = this.formatCurrency(totalDebt);
        document.getElementById('monthlyPayments').textContent = this.formatCurrency(monthlyPayments);
        document.getElementById('averageRate').textContent = `${(averageRate * 100).toFixed(1)}%`;
    }

    /**
     * Renderizar lista de préstamos
     */
    renderLoansList() {
        const container = document.getElementById('loans-list');
        if (!container) return;

        if (this.data.loans.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <i class="fas fa-handshake"></i>
                    </div>
                    <h3>No tienes préstamos</h3>
                    <p>Solicita tu primer préstamo para comenzar</p>
                    <button class="btn btn-primary" onclick="prestamosPage.showNewLoanTab()">
                        <i class="fas fa-plus"></i> Solicitar Préstamo
                    </button>
                </div>
            `;
            return;
        }

        container.innerHTML = this.data.loans.map(loan => `
            <div class="loan-card">
                <div class="loan-header">
                    <div class="loan-info">
                        <h4>${loan.typeName}</h4>
                        <div class="loan-meta">
                            <span class="meta-item">
                                <i class="fas fa-hashtag"></i>
                                ${loan.id}
                            </span>
                            <span class="meta-item">
                                <i class="fas fa-calendar"></i>
                                Solicitado: ${this.formatDate(loan.dateRequested)}
                            </span>
                        </div>
                    </div>
                    <div class="loan-status">
                        <span class="status-badge status-${loan.status}">
                            ${this.getStatusName(loan.status)}
                        </span>
                    </div>
                </div>
                
                <div class="loan-details">
                    <div class="detail-grid">
                        <div class="detail-item">
                            <small>Monto Original</small>
                            <div class="detail-value">${this.formatCurrency(loan.amount)}</div>
                        </div>
                        
                        <div class="detail-item">
                            <small>Saldo Restante</small>
                            <div class="detail-value">${this.formatCurrency(loan.remainingBalance)}</div>
                        </div>
                        
                        <div class="detail-item">
                            <small>Pago Mensual</small>
                            <div class="detail-value">${this.formatCurrency(loan.monthlyPayment)}</div>
                        </div>
                        
                        <div class="detail-item">
                            <small>Plazo</small>
                            <div class="detail-value">${loan.term} meses</div>
                        </div>
                    </div>
                    
                    <div class="loan-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${this.getLoanProgress(loan)}%"></div>
                        </div>
                        <div class="progress-text">
                            ${loan.paymentsMade || 0} de ${loan.term} pagos realizados
                        </div>
                    </div>
                    
                    ${loan.nextPaymentDate ? `
                        <div class="next-payment">
                            <small>Próximo Pago</small>
                            <div class="next-payment-date">
                                <i class="fas fa-calendar-alt"></i>
                                ${this.formatDate(loan.nextPaymentDate)}
                            </div>
                        </div>
                    ` : ''}
                </div>
                
                <div class="loan-actions">
                    <button class="btn btn-sm btn-outline" onclick="prestamosPage.viewLoanDetails('${loan.id}')">
                        <i class="fas fa-eye"></i> Ver Detalles
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="prestamosPage.downloadStatement('${loan.id}')">
                        <i class="fas fa-download"></i> Estado de Cuenta
                    </button>
                    ${loan.status === 'active' ? `
                        <button class="btn btn-sm btn-primary" onclick="prestamosPage.makePayment('${loan.id}')">
                            <i class="fas fa-credit-card"></i> Pagar
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    /**
     * Filtrar préstamos por estado
     */
    filterLoansByStatus(status) {
        const loans = status === 'all' ? this.data.loans : 
                     this.data.loans.filter(loan => loan.status === status);
        
        // Mostrar solo los préstamos filtrados
        const container = document.getElementById('loans-list');
        if (container) {
            // Aquí se podría implementar la lógica de filtrado visual
            // Por simplicidad, recargamos la lista
            this.renderLoansList();
        }
    }

    /**
     * Enviar solicitud de préstamo
     */
    async handleLoanRequest(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const loanData = {
            type: this.data.formData.type,
            amount: parseFloat(formData.get('amount')),
            term: parseInt(formData.get('term')),
            purpose: formData.get('purpose'),
            income: parseFloat(formData.get('income')),
            existingLoans: parseFloat(formData.get('existingLoans')) || 0,
            collateral: formData.get('collateral')
        };

        if (!this.validateLoanRequest(loanData)) {
            return;
        }

        try {
            this.showFormLoading(true);
            
            const response = await API.requestLoan(loanData);
            
            if (response.success) {
                window.bancoApp?.showNotification('Solicitud de préstamo enviada exitosamente', 'success');
                this.resetForm();
                this.switchTab('list');
                await this.loadLoans();
            }

        } catch (error) {
            this.handleError('Error al enviar la solicitud', error);
        } finally {
            this.showFormLoading(false);
        }
    }

    /**
     * Validar solicitud de préstamo
     */
    validateLoanRequest(data) {
        let isValid = true;

        if (!data.type) {
            this.showError('loan-type-error', 'Debes seleccionar un tipo de préstamo');
            isValid = false;
        }

        if (!data.amount || data.amount <= 0) {
            this.showError('amount-error', 'El monto debe ser mayor a 0');
            isValid = false;
        }

        if (!data.term || data.term <= 0) {
            this.showError('term-error', 'El plazo debe ser mayor a 0');
            isValid = false;
        }

        if (!data.purpose) {
            this.showError('purpose-error', 'Debes especificar el propósito del préstamo');
            isValid = false;
        }

        if (!data.income || data.income <= 0) {
            this.showError('income-error', 'Los ingresos son requeridos');
            isValid = false;
        }

        // Validaciones específicas del tipo
        if (data.type) {
            const loanType = this.data.loanTypes.find(t => t.id === data.type);
            if (loanType) {
                if (data.amount < loanType.minAmount || data.amount > loanType.maxAmount) {
                    this.showError('amount-error', `El monto debe estar entre S/ ${loanType.minAmount.toLocaleString()} y S/ ${loanType.maxAmount.toLocaleString()}`);
                    isValid = false;
                }
                
                if (data.term < loanType.minTerm || data.term > loanType.maxTerm) {
                    this.showError('term-error', `El plazo debe estar entre ${loanType.minTerm} y ${loanType.maxTerm} meses`);
                    isValid = false;
                }
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
     * Mostrar/ocultar loading del formulario
     */
    showFormLoading(show) {
        const submitButton = document.querySelector('#loan-request-form button[type="submit"]');
        if (submitButton) {
            if (show) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
            } else {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Solicitud';
            }
        }
    }

    /**
     * Resetear formulario
     */
    resetForm() {
        const form = document.getElementById('loan-request-form');
        if (form) {
            form.reset();
        }
        
        // Limpiar datos y UI
        this.data.formData = {
            type: '',
            amount: '',
            term: '',
            purpose: '',
            income: '',
            existingLoans: '',
            collateral: ''
        };
        
        this.data.calculations = {
            monthlyPayment: 0,
            totalAmount: 0,
            totalInterest: 0,
            interestRate: 0
        };
        
        // Ocultar resumen
        const summary = document.getElementById('loan-summary');
        if (summary) {
            summary.style.display = 'none';
        }
        
        // Deseleccionar tarjetas de tipo
        document.querySelectorAll('.loan-type-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        this.clearErrors();
    }

    /**
     * Ver detalles del préstamo
     */
    viewLoanDetails(loanId) {
        const loan = this.data.loans.find(l => l.id === loanId);
        if (!loan) return;

        const modal = document.getElementById('loan-details-modal');
        const content = document.getElementById('loan-details-content');

        content.innerHTML = `
            <div class="loan-details-content">
                <div class="detail-header">
                    <h4>${loan.typeName}</h4>
                    <span class="status-badge status-${loan.status}">${this.getStatusName(loan.status)}</span>
                </div>
                
                <div class="detail-grid">
                    <div class="detail-item">
                        <small>ID del Préstamo</small>
                        <div>${loan.id}</div>
                    </div>
                    <div class="detail-item">
                        <small>Monto Original</small>
                        <div>${this.formatCurrency(loan.amount)}</div>
                    </div>
                    <div class="detail-item">
                        <small>Saldo Restante</small>
                        <div>${this.formatCurrency(loan.remainingBalance)}</div>
                    </div>
                    <div class="detail-item">
                        <small>Tasa de Interés</small>
                        <div>${(loan.interestRate * 100).toFixed(1)}% anual</div>
                    </div>
                    <div class="detail-item">
                        <small>Plazo</small>
                        <div>${loan.term} meses</div>
                    </div>
                    <div class="detail-item">
                        <small>Pago Mensual</small>
                        <div>${this.formatCurrency(loan.monthlyPayment)}</div>
                    </div>
                    <div class="detail-item">
                        <small>Total a Pagar</small>
                        <div>${this.formatCurrency(loan.totalAmount)}</div>
                    </div>
                    <div class="detail-item">
                        <small>Total Intereses</small>
                        <div>${this.formatCurrency(loan.totalInterest)}</div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h5>Historial de Pagos</h5>
                    <div class="payment-history">
                        ${this.generatePaymentHistory(loan)}
                    </div>
                </div>
            </div>
        `;

        modal.classList.remove('hidden');
    }

    /**
     * Cerrar modal de detalles
     */
    closeLoanDetailsModal() {
        const modal = document.getElementById('loan-details-modal');
        modal.classList.add('hidden');
    }

    /**
     * Generar historial de pagos
     */
    generatePaymentHistory(loan) {
        const payments = [];
        for (let i = 1; i <= (loan.paymentsMade || 0); i++) {
            const paymentDate = new Date(loan.startDate);
            paymentDate.setMonth(paymentDate.getMonth() + i - 1);
            
            payments.push({
                number: i,
                date: paymentDate.toISOString(),
                amount: loan.monthlyPayment,
                status: 'paid'
            });
        }

        return payments.length > 0 ? `
            <div class="payment-table">
                <table>
                    <thead>
                        <tr>
                            <th>Pago #</th>
                            <th>Fecha</th>
                            <th>Monto</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${payments.map(payment => `
                            <tr>
                                <td>${payment.number}</td>
                                <td>${this.formatDate(payment.date)}</td>
                                <td>${this.formatCurrency(payment.amount)}</td>
                                <td><span class="status-badge status-paid">Pagado</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        ` : '<p>No hay pagos realizados aún.</p>';
    }

    /**
     * Exportar préstamos
     */
    exportLoans() {
        try {
            const csv = this.generateLoansCSV();
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', `prestamos_${new Date().toISOString().split('T')[0]}.csv`);
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            window.bancoApp?.showNotification('Préstamos exportados exitosamente', 'success');
        } catch (error) {
            this.handleError('Error al exportar préstamos', error);
        }
    }

    /**
     * Generar CSV de préstamos
     */
    generateLoansCSV() {
        const headers = ['ID', 'Tipo', 'Monto', 'Plazo', 'Estado', 'Pago Mensual', 'Saldo Restante', 'Fecha Solicitud'];
        const rows = this.data.loans.map(loan => [
            loan.id,
            loan.typeName,
            loan.amount,
            loan.term,
            this.getStatusName(loan.status),
            loan.monthlyPayment,
            loan.remainingBalance,
            this.formatDate(loan.dateRequested)
        ]);
        
        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    /**
     * Descargar estado de cuenta
     */
    downloadStatement(loanId) {
        window.bancoApp?.showNotification(`Descargando estado de cuenta para ${loanId}`, 'info');
    }

    /**
     * Realizar pago
     */
    makePayment(loanId) {
        window.bancoApp?.showNotification(`Procesando pago para ${loanId}`, 'info');
    }

    /**
     * Utilidades
     */
    getLoanProgress(loan) {
        if (!loan.paymentsMade || !loan.term) return 0;
        return (loan.paymentsMade / loan.term) * 100;
    }

    getStatusName(status) {
        const names = {
            'pending': 'Pendiente',
            'approved': 'Aprobado',
            'active': 'Activo',
            'paid': 'Pagado',
            'rejected': 'Rechazado',
            'cancelled': 'Cancelado'
        };
        return names[status] || status;
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('es-PE', {
            style: 'currency',
            currency: 'PEN'
        }).format(amount);
    }

    formatDate(dateString) {
        return new Intl.DateTimeFormat('es-PE', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
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
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>Error al cargar los préstamos</h3>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">
                    <i class="fas fa-refresh"></i> Reintentar
                </button>
            </div>
        `;
    }
}

// Instanciar página globalmente
window.prestamosPage = new PrestamosPage();