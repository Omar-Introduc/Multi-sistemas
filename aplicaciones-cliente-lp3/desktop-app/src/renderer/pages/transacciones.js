/**
 * Página Transacciones - Sistema Bancario Desktop
 * Historial de transacciones con filtros avanzados y búsqueda
 */

class TransaccionesPage {
    constructor() {
        this.data = {
            transactions: [],
            filteredTransactions: [],
            accounts: [],
            filters: {
                dateFrom: '',
                dateTo: '',
                type: 'all',
                category: 'all',
                status: 'all',
                minAmount: '',
                maxAmount: '',
                account: 'all',
                search: ''
            },
            sortBy: 'date',
            sortOrder: 'desc'
        };
        this.currentPage = 1;
        this.itemsPerPage = 15;
        this.totalPages = 1;
        this.stats = {
            totalTransactions: 0,
            totalIncome: 0,
            totalExpenses: 0,
            netAmount: 0
        };
    }

    /**
     * Renderizar la página de transacciones
     */
    async render() {
        try {
            this.showLoading();
            await this.loadData();
            this.applyFilters();
            this.hideLoading();
            return this.getHTML();

        } catch (error) {
            this.hideLoading();
            this.handleError('Error al cargar las transacciones', error);
            return this.getErrorHTML(error.message);
        }
    }

    /**
     * Obtener HTML de la página
     */
    getHTML() {
        return `
            <div id="transacciones-content" class="transacciones-container">
                <!-- Header -->
                <div class="page-header">
                    <div class="page-title">
                        <h1><i class="fas fa-exchange-alt"></i> Historial de Transacciones</h1>
                        <p>Revisa y filtra todas tus transacciones bancarias</p>
                    </div>
                    <div class="page-actions">
                        <button class="btn btn-outline" onclick="transaccionesPage.exportTransactions()">
                            <i class="fas fa-download"></i> Exportar
                        </button>
                        <button class="btn btn-primary" onclick="transaccionesPage.showNewTransactionModal()">
                            <i class="fas fa-plus"></i> Nueva Transacción
                        </button>
                    </div>
                </div>

                <!-- Estadísticas rápidas -->
                <div class="stats-summary">
                    <div class="stat-card">
                        <div class="stat-icon primary">
                            <i class="fas fa-list"></i>
                        </div>
                        <div class="stat-content">
                            <h4>Total Transacciones</h4>
                            <div class="stat-value" id="totalTransactions">0</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon success">
                            <i class="fas fa-arrow-up"></i>
                        </div>
                        <div class="stat-content">
                            <h4>Ingresos</h4>
                            <div class="stat-value" id="totalIncome">S/ 0.00</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon error">
                            <i class="fas fa-arrow-down"></i>
                        </div>
                        <div class="stat-content">
                            <h4>Gastos</h4>
                            <div class="stat-value" id="totalExpenses">S/ 0.00</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon ${this.stats.netAmount >= 0 ? 'success' : 'error'}">
                            <i class="fas fa-balance-scale"></i>
                        </div>
                        <div class="stat-content">
                            <h4>Balance Neto</h4>
                            <div class="stat-value" id="netAmount">S/ 0.00</div>
                        </div>
                    </div>
                </div>

                <!-- Filtros avanzados -->
                <div class="filters-section">
                    <div class="filters-header">
                        <h3>Filtros y Búsqueda</h3>
                        <button class="btn btn-sm btn-outline" onclick="transaccionesPage.clearAllFilters()">
                            <i class="fas fa-times"></i> Limpiar Filtros
                        </button>
                    </div>
                    
                    <div class="filters-grid">
                        <!-- Búsqueda general -->
                        <div class="filter-group full-width">
                            <label>Búsqueda:</label>
                            <div class="search-input-container">
                                <input type="text" 
                                       id="search-input" 
                                       placeholder="Buscar por descripción, categoría o referencia..." 
                                       value="${this.data.filters.search}"
                                       oninput="transaccionesPage.handleSearch(this.value)">
                                <i class="fas fa-search search-icon"></i>
                            </div>
                        </div>
                        
                        <!-- Filtros de fecha -->
                        <div class="filter-group">
                            <label>Fecha Desde:</label>
                            <input type="date" 
                                   id="date-from" 
                                   value="${this.data.filters.dateFrom}"
                                   onchange="transaccionesPage.handleDateFrom(this.value)">
                        </div>
                        
                        <div class="filter-group">
                            <label>Fecha Hasta:</label>
                            <input type="date" 
                                   id="date-to" 
                                   value="${this.data.filters.dateTo}"
                                   onchange="transaccionesPage.handleDateTo(this.value)">
                        </div>
                        
                        <!-- Filtros de cuenta -->
                        <div class="filter-group">
                            <label>Cuenta:</label>
                            <select id="account-filter" onchange="transaccionesPage.handleAccountFilter(this.value)">
                                <option value="all">Todas las cuentas</option>
                            </select>
                        </div>
                        
                        <!-- Filtro por tipo -->
                        <div class="filter-group">
                            <label>Tipo:</label>
                            <select id="type-filter" onchange="transaccionesPage.handleTypeFilter(this.value)">
                                <option value="all">Todos los tipos</option>
                                <option value="deposito">Depósito</option>
                                <option value="retiro">Retiro</option>
                                <option value="transferencia">Transferencia</option>
                                <option value="pago">Pago</option>
                            </select>
                        </div>
                        
                        <!-- Filtro por categoría -->
                        <div class="filter-group">
                            <label>Categoría:</label>
                            <select id="category-filter" onchange="transaccionesPage.handleCategoryFilter(this.value)">
                                <option value="all">Todas las categorías</option>
                                <option value="alimentacion">Alimentación</option>
                                <option value="transporte">Transporte</option>
                                <option value="salud">Salud</option>
                                <option value="educacion">Educación</option>
                                <option value="entretenimiento">Entretenimiento</option>
                                <option value="servicios">Servicios</option>
                                <option value="otros">Otros</option>
                            </select>
                        </div>
                        
                        <!-- Filtro por estado -->
                        <div class="filter-group">
                            <label>Estado:</label>
                            <select id="status-filter" onchange="transaccionesPage.handleStatusFilter(this.value)">
                                <option value="all">Todos los estados</option>
                                <option value="completed">Completadas</option>
                                <option value="pending">Pendientes</option>
                                <option value="failed">Fallidas</option>
                            </select>
                        </div>
                        
                        <!-- Filtros de monto -->
                        <div class="filter-group">
                            <label>Monto Mínimo:</label>
                            <div class="input-group">
                                <span class="input-prefix">S/</span>
                                <input type="number" 
                                       id="min-amount" 
                                       placeholder="0.00" 
                                       min="0"
                                       value="${this.data.filters.minAmount}"
                                       onchange="transaccionesPage.handleMinAmount(this.value)">
                            </div>
                        </div>
                        
                        <div class="filter-group">
                            <label>Monto Máximo:</label>
                            <div class="input-group">
                                <span class="input-prefix">S/</span>
                                <input type="number" 
                                       id="max-amount" 
                                       placeholder="999999.99" 
                                       min="0"
                                       value="${this.data.filters.maxAmount}"
                                       onchange="transaccionesPage.handleMaxAmount(this.value)">
                            </div>
                        </div>
                        
                        <!-- Ordenamiento -->
                        <div class="filter-group">
                            <label>Ordenar por:</label>
                            <select id="sort-select" onchange="transaccionesPage.handleSort(this.value)">
                                <option value="date-desc">Más recientes</option>
                                <option value="date-asc">Más antiguos</option>
                                <option value="amount-desc">Mayor monto</option>
                                <option value="amount-asc">Menor monto</option>
                                <option value="type">Tipo</option>
                                <option value="category">Categoría</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Lista de transacciones -->
                <div class="transactions-section">
                    <div class="section-header">
                        <h3>Historial de Transacciones</h3>
                        <div class="results-info">
                            Mostrando <span id="showing-count">0</span> de <span id="total-count">0</span> transacciones
                        </div>
                    </div>
                    
                    <div class="transactions-list" id="transactions-list">
                        <!-- Las transacciones se cargarán dinámicamente -->
                    </div>
                    
                    <!-- Paginación -->
                    <div class="pagination" id="pagination">
                        <!-- La paginación se cargará dinámicamente -->
                    </div>
                </div>
            </div>

            <!-- Modal para nueva transacción -->
            <div id="transaction-modal" class="modal hidden">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3 id="transaction-modal-title">Nueva Transacción</h3>
                        <button class="modal-close" onclick="transaccionesPage.closeTransactionModal()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <form id="transaction-form" class="modal-body">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="transaction-type">Tipo de Transacción *</label>
                                <select id="transaction-type" name="type" required>
                                    <option value="">Seleccionar tipo</option>
                                    <option value="deposito">Depósito</option>
                                    <option value="retiro">Retiro</option>
                                    <option value="transferencia">Transferencia</option>
                                    <option value="pago">Pago</option>
                                </select>
                                <div class="error-message" id="type-error"></div>
                            </div>
                            
                            <div class="form-group">
                                <label for="transaction-amount">Monto *</label>
                                <div class="input-group">
                                    <span class="input-prefix">S/</span>
                                    <input type="number" 
                                           id="transaction-amount" 
                                           name="amount" 
                                           min="0.01" 
                                           step="0.01"
                                           placeholder="0.00" 
                                           required>
                                </div>
                                <div class="error-message" id="amount-error"></div>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="transaction-account">Cuenta *</label>
                            <select id="transaction-account" name="accountId" required>
                                <option value="">Seleccionar cuenta</option>
                            </select>
                            <div class="error-message" id="account-error"></div>
                        </div>
                        
                        <div class="form-group">
                            <label for="transaction-category">Categoría</label>
                            <select id="transaction-category" name="category">
                                <option value="otros">Otros</option>
                                <option value="alimentacion">Alimentación</option>
                                <option value="transporte">Transporte</option>
                                <option value="salud">Salud</option>
                                <option value="educacion">Educación</option>
                                <option value="entretenimiento">Entretenimiento</option>
                                <option value="servicios">Servicios</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="transaction-description">Descripción *</label>
                            <textarea id="transaction-description" 
                                      name="description" 
                                      rows="3" 
                                      placeholder="Descripción de la transacción..." 
                                      required></textarea>
                            <div class="error-message" id="description-error"></div>
                        </div>
                        
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary" onclick="transaccionesPage.closeTransactionModal()">
                                Cancelar
                            </button>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i> Registrar Transacción
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    }

    /**
     * Cargar datos iniciales
     */
    async loadData() {
        try {
            const [transactions, accounts] = await Promise.all([
                API.getTransactions(),
                API.getAccounts()
            ]);

            this.data.transactions = transactions.map(t => ({
                ...t,
                date: t.date || new Date().toISOString(),
                category: t.category || 'otros'
            }));
            this.data.accounts = accounts;

            // Poblar selects de filtros
            this.populateFilterSelects();

        } catch (error) {
            console.error('Error loading data:', error);
            this.data.transactions = this.getDemoTransactions();
            this.data.accounts = this.getDemoAccounts();
            this.populateFilterSelects();
        }
    }

    /**
     * Poblar selects de filtros
     */
    populateFilterSelects() {
        // Poblar select de cuentas
        const accountSelect = document.getElementById('account-filter');
        if (accountSelect) {
            accountSelect.innerHTML = '<option value="all">Todas las cuentas</option>' +
                this.data.accounts.map(account => 
                    `<option value="${account.id}">${account.type} - ${account.number}</option>`
                ).join('');
        }

        const transactionAccountSelect = document.getElementById('transaction-account');
        if (transactionAccountSelect) {
            transactionAccountSelect.innerHTML = '<option value="">Seleccionar cuenta</option>' +
                this.data.accounts.map(account => 
                    `<option value="${account.id}">${account.type} - ${account.number}</option>`
                ).join('');
        }
    }

    /**
     * Obtener transacciones de demostración
     */
    getDemoTransactions() {
        return [
            {
                id: 'TXN001',
                date: new Date().toISOString(),
                description: 'Pago - Supermercado Metro',
                category: 'alimentacion',
                type: 'pago',
                amount: -85.50,
                accountId: '1',
                status: 'completed',
                reference: 'REF001'
            },
            {
                id: 'TXN002',
                date: new Date(Date.now() - 86400000).toISOString(),
                description: 'Depósito en efectivo',
                category: 'otros',
                type: 'deposito',
                amount: 500.00,
                accountId: '1',
                status: 'completed',
                reference: 'REF002'
            },
            {
                id: 'TXN003',
                date: new Date(Date.now() - 172800000).toISOString(),
                description: 'Retiro cajero automático',
                category: 'otros',
                type: 'retiro',
                amount: -200.00,
                accountId: '2',
                status: 'completed',
                reference: 'REF003'
            },
            {
                id: 'TXN004',
                date: new Date(Date.now() - 259200000).toISOString(),
                description: 'Transferencia recibida',
                category: 'otros',
                type: 'transferencia',
                amount: 1200.00,
                accountId: '1',
                status: 'completed',
                reference: 'REF004'
            },
            {
                id: 'TXN005',
                date: new Date(Date.now() - 345600000).toISOString(),
                description: 'Pago servicios públicos',
                category: 'servicios',
                type: 'pago',
                amount: -150.75,
                accountId: '2',
                status: 'completed',
                reference: 'REF005'
            }
        ];
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
     * Aplicar filtros y ordenar
     */
    applyFilters() {
        let filtered = [...this.data.transactions];

        // Aplicar todos los filtros
        filtered = filtered.filter(transaction => {
            // Filtro por búsqueda
            if (this.data.filters.search) {
                const search = this.data.filters.search.toLowerCase();
                if (!transaction.description.toLowerCase().includes(search) &&
                    !transaction.category.toLowerCase().includes(search) &&
                    !transaction.reference.toLowerCase().includes(search)) {
                    return false;
                }
            }

            // Filtro por fechas
            if (this.data.filters.dateFrom) {
                const transactionDate = new Date(transaction.date);
                const fromDate = new Date(this.data.filters.dateFrom);
                if (transactionDate < fromDate) return false;
            }

            if (this.data.filters.dateTo) {
                const transactionDate = new Date(transaction.date);
                const toDate = new Date(this.data.filters.dateTo);
                if (transactionDate > toDate) return false;
            }

            // Filtro por tipo
            if (this.data.filters.type !== 'all' && transaction.type !== this.data.filters.type) {
                return false;
            }

            // Filtro por categoría
            if (this.data.filters.category !== 'all' && transaction.category !== this.data.filters.category) {
                return false;
            }

            // Filtro por estado
            if (this.data.filters.status !== 'all' && transaction.status !== this.data.filters.status) {
                return false;
            }

            // Filtro por cuenta
            if (this.data.filters.account !== 'all' && transaction.accountId !== this.data.filters.account) {
                return false;
            }

            // Filtro por monto mínimo
            if (this.data.filters.minAmount && Math.abs(transaction.amount) < parseFloat(this.data.filters.minAmount)) {
                return false;
            }

            // Filtro por monto máximo
            if (this.data.filters.maxAmount && Math.abs(transaction.amount) > parseFloat(this.data.filters.maxAmount)) {
                return false;
            }

            return true;
        });

        // Ordenamiento
        filtered.sort((a, b) => {
            let valueA, valueB;
            
            switch (this.data.sortBy) {
                case 'date':
                    valueA = new Date(a.date);
                    valueB = new Date(b.date);
                    break;
                case 'amount':
                    valueA = Math.abs(a.amount);
                    valueB = Math.abs(b.amount);
                    break;
                case 'type':
                    valueA = a.type;
                    valueB = b.type;
                    break;
                case 'category':
                    valueA = a.category;
                    valueB = b.category;
                    break;
                default:
                    valueA = new Date(a.date);
                    valueB = new Date(b.date);
            }

            if (this.data.sortOrder === 'asc') {
                return valueA > valueB ? 1 : -1;
            } else {
                return valueA < valueB ? 1 : -1;
            }
        });

        this.data.filteredTransactions = filtered;
        this.calculateStats();
        this.updateStats();
        this.renderTransactions();
        this.renderPagination();
    }

    /**
     * Calcular estadísticas
     */
    calculateStats() {
        const transactions = this.data.filteredTransactions;
        
        this.stats.totalTransactions = transactions.length;
        this.stats.totalIncome = transactions
            .filter(t => t.amount > 0)
            .reduce((sum, t) => sum + t.amount, 0);
        this.stats.totalExpenses = transactions
            .filter(t => t.amount < 0)
            .reduce((sum, t) => sum + Math.abs(t.amount), 0);
        this.stats.netAmount = this.stats.totalIncome - this.stats.totalExpenses;
    }

    /**
     * Actualizar estadísticas en UI
     */
    updateStats() {
        document.getElementById('totalTransactions').textContent = this.stats.totalTransactions;
        document.getElementById('totalIncome').textContent = this.formatCurrency(this.stats.totalIncome);
        document.getElementById('totalExpenses').textContent = this.formatCurrency(this.stats.totalExpenses);
        document.getElementById('netAmount').textContent = this.formatCurrency(this.stats.netAmount);
        
        document.getElementById('showing-count').textContent = this.data.filteredTransactions.length;
        document.getElementById('total-count').textContent = this.data.transactions.length;
    }

    /**
     * Renderizar lista de transacciones
     */
    renderTransactions() {
        const container = document.getElementById('transactions-list');
        if (!container) return;

        if (this.data.filteredTransactions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <i class="fas fa-search"></i>
                    </div>
                    <h3>No se encontraron transacciones</h3>
                    <p>No hay transacciones que coincidan con los filtros aplicados</p>
                    <button class="btn btn-primary" onclick="transaccionesPage.clearAllFilters()">
                        <i class="fas fa-refresh"></i> Limpiar Filtros
                    </button>
                </div>
            `;
            return;
        }

        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const paginatedTransactions = this.data.filteredTransactions.slice(startIndex, endIndex);

        container.innerHTML = paginatedTransactions.map(transaction => `
            <div class="transaction-card">
                <div class="transaction-header">
                    <div class="transaction-type">
                        <div class="type-icon ${transaction.type}">
                            <i class="fas ${this.getTransactionIcon(transaction.type)}"></i>
                        </div>
                        <div class="type-info">
                            <h4>${transaction.description}</h4>
                            <div class="transaction-meta">
                                <span class="meta-item">
                                    <i class="fas fa-calendar"></i>
                                    ${this.formatDateTime(transaction.date)}
                                </span>
                                <span class="meta-item">
                                    <i class="fas fa-hashtag"></i>
                                    ${transaction.reference}
                                </span>
                                <span class="meta-item">
                                    <i class="fas fa-tag"></i>
                                    ${this.getCategoryName(transaction.category)}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="transaction-amount">
                        <div class="amount ${transaction.amount >= 0 ? 'positive' : 'negative'}">
                            ${transaction.amount >= 0 ? '+' : ''}${this.formatCurrency(Math.abs(transaction.amount))}
                        </div>
                        <div class="status-badge status-${transaction.status}">
                            ${this.getStatusName(transaction.status)}
                        </div>
                    </div>
                </div>
                
                <div class="transaction-details">
                    <div class="detail-item">
                        <small>Cuenta</small>
                        <div>${this.getAccountName(transaction.accountId)}</div>
                    </div>
                    
                    <div class="detail-item">
                        <small>Tipo</small>
                        <div>${this.getTransactionTypeName(transaction.type)}</div>
                    </div>
                    
                    <div class="detail-item">
                        <small>Referencia</small>
                        <div class="reference">${transaction.reference}</div>
                    </div>
                </div>
                
                <div class="transaction-actions">
                    <button class="btn btn-sm btn-outline" onclick="transaccionesPage.viewTransactionDetails('${transaction.id}')">
                        <i class="fas fa-eye"></i> Ver Detalles
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="transaccionesPage.downloadReceipt('${transaction.id}')">
                        <i class="fas fa-download"></i> Comprobante
                    </button>
                    ${transaction.status === 'pending' ? `
                        <button class="btn btn-sm btn-warning" onclick="transaccionesPage.cancelTransaction('${transaction.id}')">
                            <i class="fas fa-times"></i> Cancelar
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    /**
     * Renderizar paginación
     */
    renderPagination() {
        const container = document.getElementById('pagination');
        if (!container) return;

        const totalPages = Math.ceil(this.data.filteredTransactions.length / this.itemsPerPage);
        this.totalPages = totalPages;

        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        let paginationHTML = '<div class="pagination-controls">';

        // Botón anterior
        if (this.currentPage > 1) {
            paginationHTML += `<button class="btn btn-sm btn-outline" onclick="transaccionesPage.goToPage(${this.currentPage - 1})">
                <i class="fas fa-chevron-left"></i> Anterior
            </button>`;
        }

        // Números de página
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `<button class="btn btn-sm ${i === this.currentPage ? 'btn-primary' : 'btn-outline'}" 
                               onclick="transaccionesPage.goToPage(${i})">${i}</button>`;
        }

        // Botón siguiente
        if (this.currentPage < totalPages) {
            paginationHTML += `<button class="btn btn-sm btn-outline" onclick="transaccionesPage.goToPage(${this.currentPage + 1})">
                Siguiente <i class="fas fa-chevron-right"></i>
            </button>`;
        }

        paginationHTML += '</div>';
        container.innerHTML = paginationHTML;
    }

    /**
     * Manejadores de filtros
     */
    handleSearch(value) {
        this.data.filters.search = value;
        this.currentPage = 1;
        this.applyFilters();
    }

    handleDateFrom(value) {
        this.data.filters.dateFrom = value;
        this.currentPage = 1;
        this.applyFilters();
    }

    handleDateTo(value) {
        this.data.filters.dateTo = value;
        this.currentPage = 1;
        this.applyFilters();
    }

    handleAccountFilter(value) {
        this.data.filters.account = value;
        this.currentPage = 1;
        this.applyFilters();
    }

    handleTypeFilter(value) {
        this.data.filters.type = value;
        this.currentPage = 1;
        this.applyFilters();
    }

    handleCategoryFilter(value) {
        this.data.filters.category = value;
        this.currentPage = 1;
        this.applyFilters();
    }

    handleStatusFilter(value) {
        this.data.filters.status = value;
        this.currentPage = 1;
        this.applyFilters();
    }

    handleMinAmount(value) {
        this.data.filters.minAmount = value;
        this.currentPage = 1;
        this.applyFilters();
    }

    handleMaxAmount(value) {
        this.data.filters.maxAmount = value;
        this.currentPage = 1;
        this.applyFilters();
    }

    handleSort(value) {
        const [field, order] = value.split('-');
        this.data.sortBy = field;
        this.data.sortOrder = order;
        this.currentPage = 1;
        this.applyFilters();
    }

    /**
     * Limpiar todos los filtros
     */
    clearAllFilters() {
        this.data.filters = {
            dateFrom: '',
            dateTo: '',
            type: 'all',
            category: 'all',
            status: 'all',
            minAmount: '',
            maxAmount: '',
            account: 'all',
            search: ''
        };
        this.currentPage = 1;
        this.applyFilters();
        
        // Resetear todos los inputs
        document.getElementById('search-input').value = '';
        document.getElementById('date-from').value = '';
        document.getElementById('date-to').value = '';
        document.getElementById('account-filter').value = 'all';
        document.getElementById('type-filter').value = 'all';
        document.getElementById('category-filter').value = 'all';
        document.getElementById('status-filter').value = 'all';
        document.getElementById('min-amount').value = '';
        document.getElementById('max-amount').value = '';
        document.getElementById('sort-select').value = 'date-desc';
    }

    /**
     * Ir a página específica
     */
    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.currentPage = page;
            this.renderTransactions();
            this.renderPagination();
        }
    }

    /**
     * Exportar transacciones
     */
    exportTransactions() {
        try {
            const csv = this.generateCSV(this.data.filteredTransactions);
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', `transacciones_${new Date().toISOString().split('T')[0]}.csv`);
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            window.bancoApp?.showNotification('Transacciones exportadas exitosamente', 'success');
        } catch (error) {
            this.handleError('Error al exportar transacciones', error);
        }
    }

    /**
     * Generar CSV
     */
    generateCSV(transactions) {
        const headers = ['Fecha', 'Descripción', 'Tipo', 'Categoría', 'Monto', 'Estado', 'Referencia'];
        const rows = transactions.map(t => [
            this.formatDateTime(t.date),
            t.description,
            this.getTransactionTypeName(t.type),
            this.getCategoryName(t.category),
            t.amount,
            this.getStatusName(t.status),
            t.reference
        ]);
        
        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    /**
     * Mostrar modal de nueva transacción
     */
    showNewTransactionModal() {
        const modal = document.getElementById('transaction-modal');
        const form = document.getElementById('transaction-form');
        
        form.reset();
        this.clearTransactionErrors();
        modal.classList.remove('hidden');
        
        form.onsubmit = (e) => this.handleCreateTransaction(e);
    }

    /**
     * Cerrar modal de transacción
     */
    closeTransactionModal() {
        const modal = document.getElementById('transaction-modal');
        modal.classList.add('hidden');
        this.clearTransactionErrors();
    }

    /**
     * Manejar creación de transacción
     */
    async handleCreateTransaction(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const transactionData = {
            type: formData.get('type'),
            amount: parseFloat(formData.get('amount')),
            accountId: formData.get('accountId'),
            category: formData.get('category'),
            description: formData.get('description')
        };

        if (!this.validateTransactionData(transactionData)) {
            return;
        }

        try {
            this.showFormLoading(true);
            
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            const newTransaction = {
                id: 'TXN' + Date.now(),
                ...transactionData,
                date: new Date().toISOString(),
                status: 'pending',
                reference: 'REF' + Date.now().toString().slice(-6)
            };

            this.data.transactions.unshift(newTransaction);
            this.applyFilters();
            
            window.bancoApp?.showNotification('Transacción registrada exitosamente', 'success');
            this.closeTransactionModal();

        } catch (error) {
            this.handleError('Error al registrar la transacción', error);
        } finally {
            this.showFormLoading(false);
        }
    }

    /**
     * Validar datos de transacción
     */
    validateTransactionData(data) {
        let isValid = true;

        if (!data.type) {
            this.showTransactionError('type-error', 'El tipo de transacción es requerido');
            isValid = false;
        }

        if (isNaN(data.amount) || data.amount <= 0) {
            this.showTransactionError('amount-error', 'El monto debe ser mayor a 0');
            isValid = false;
        }

        if (!data.accountId) {
            this.showTransactionError('account-error', 'La cuenta es requerida');
            isValid = false;
        }

        if (!data.description.trim()) {
            this.showTransactionError('description-error', 'La descripción es requerida');
            isValid = false;
        }

        return isValid;
    }

    /**
     * Mostrar error en campo de transacción
     */
    showTransactionError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = message;
            element.style.display = 'block';
        }
    }

    /**
     * Limpiar errores de transacción
     */
    clearTransactionErrors() {
        const errorElements = document.querySelectorAll('#transaction-form .error-message');
        errorElements.forEach(element => {
            element.textContent = '';
            element.style.display = 'none';
        });
    }

    /**
     * Mostrar/ocultar loading del formulario
     */
    showFormLoading(show) {
        const submitButton = document.querySelector('#transaction-form button[type="submit"]');
        if (submitButton) {
            if (show) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registrando...';
            } else {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-save"></i> Registrar Transacción';
            }
        }
    }

    /**
     * Ver detalles de transacción
     */
    viewTransactionDetails(transactionId) {
        window.bancoApp?.showNotification(`Detalles de transacción ${transactionId}`, 'info');
    }

    /**
     * Descargar comprobante
     */
    downloadReceipt(transactionId) {
        window.bancoApp?.showNotification(`Descargando comprobante ${transactionId}`, 'info');
    }

    /**
     * Cancelar transacción
     */
    async cancelTransaction(transactionId) {
        try {
            const transaction = this.data.transactions.find(t => t.id === transactionId);
            if (transaction) {
                transaction.status = 'cancelled';
                this.applyFilters();
                window.bancoApp?.showNotification('Transacción cancelada', 'success');
            }
        } catch (error) {
            this.handleError('Error al cancelar la transacción', error);
        }
    }

    /**
     * Utilidades para obtener nombres
     */
    getTransactionIcon(type) {
        const icons = {
            'deposito': 'fa-arrow-down',
            'retiro': 'fa-arrow-up',
            'transferencia': 'fa-exchange-alt',
            'pago': 'fa-credit-card'
        };
        return icons[type] || 'fa-question';
    }

    getTransactionTypeName(type) {
        const names = {
            'deposito': 'Depósito',
            'retiro': 'Retiro',
            'transferencia': 'Transferencia',
            'pago': 'Pago'
        };
        return names[type] || type;
    }

    getCategoryName(category) {
        const names = {
            'alimentacion': 'Alimentación',
            'transporte': 'Transporte',
            'salud': 'Salud',
            'educacion': 'Educación',
            'entretenimiento': 'Entretenimiento',
            'servicios': 'Servicios',
            'otros': 'Otros'
        };
        return names[category] || category;
    }

    getStatusName(status) {
        const names = {
            'completed': 'Completada',
            'pending': 'Pendiente',
            'failed': 'Fallida',
            'cancelled': 'Cancelada'
        };
        return names[status] || status;
    }

    getAccountName(accountId) {
        const account = this.data.accounts.find(a => a.id === accountId);
        return account ? `${account.type} - ${account.number}` : 'Cuenta desconocida';
    }

    /**
     * Formatear moneda
     */
    formatCurrency(amount) {
        return new Intl.NumberFormat('es-PE', {
            style: 'currency',
            currency: 'PEN'
        }).format(amount);
    }

    /**
     * Formatear fecha y hora
     */
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
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>Error al cargar las transacciones</h3>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">
                    <i class="fas fa-refresh"></i> Reintentar
                </button>
            </div>
        `;
    }
}

// Instanciar página globalmente
window.transaccionesPage = new TransaccionesPage();