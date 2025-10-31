/**
 * Página Cuentas - Sistema Bancario Desktop
 * Gestión y listado de cuentas bancarias
 */

class CuentasPage {
    constructor() {
        this.data = {
            accounts: [],
            filters: {
                type: 'all',
                status: 'all',
                search: ''
            },
            sortBy: 'balance',
            sortOrder: 'desc'
        };
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.totalPages = 1;
    }

    /**
     * Renderizar la página de cuentas
     */
    async render() {
        try {
            this.showLoading();
            await this.loadAccounts();
            this.applyFilters();
            this.hideLoading();
            return this.getHTML();

        } catch (error) {
            this.hideLoading();
            this.handleError('Error al cargar las cuentas', error);
            return this.getErrorHTML(error.message);
        }
    }

    /**
     * Obtener HTML de la página
     */
    getHTML() {
        return `
            <div id="cuentas-content" class="cuentas-container">
                <!-- Header con filtros y acciones -->
                <div class="page-header">
                    <div class="page-title">
                        <h1><i class="fas fa-credit-card"></i> Gestión de Cuentas</h1>
                        <p>Administra tus cuentas bancarias</p>
                    </div>
                    <div class="page-actions">
                        <button class="btn btn-primary" onclick="cuentasPage.showCreateAccountModal()">
                            <i class="fas fa-plus"></i> Nueva Cuenta
                        </button>
                    </div>
                </div>

                <!-- Filtros y búsqueda -->
                <div class="filters-section">
                    <div class="filters-row">
                        <div class="filter-group">
                            <label>Buscar:</label>
                            <input type="text" 
                                   id="search-input" 
                                   placeholder="Número de cuenta o tipo..." 
                                   value="${this.data.filters.search}"
                                   oninput="cuentasPage.handleSearch(this.value)">
                        </div>
                        
                        <div class="filter-group">
                            <label>Tipo:</label>
                            <select id="type-filter" onchange="cuentasPage.handleTypeFilter(this.value)">
                                <option value="all">Todos</option>
                                <option value="corriente">Cuenta Corriente</option>
                                <option value="ahorros">Cuenta de Ahorros</option>
                                <option value="plazo">Plazo Fijo</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label>Estado:</label>
                            <select id="status-filter" onchange="cuentasPage.handleStatusFilter(this.value)">
                                <option value="all">Todos</option>
                                <option value="active">Activas</option>
                                <option value="inactive">Inactivas</option>
                                <option value="blocked">Bloqueadas</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label>Ordenar por:</label>
                            <select id="sort-select" onchange="cuentasPage.handleSort(this.value)">
                                <option value="balance-desc">Mayor saldo</option>
                                <option value="balance-asc">Menor saldo</option>
                                <option value="type">Tipo de cuenta</option>
                                <option value="number">Número</option>
                                <option value="date-desc">Más recientes</option>
                                <option value="date-asc">Más antiguos</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Resumen de cuentas -->
                <div class="accounts-summary">
                    <div class="summary-card">
                        <div class="summary-icon success">
                            <i class="fas fa-wallet"></i>
                        </div>
                        <div class="summary-content">
                            <h4>Saldo Total</h4>
                            <div class="summary-value" id="totalBalance">S/ 0.00</div>
                        </div>
                    </div>
                    
                    <div class="summary-card">
                        <div class="summary-icon primary">
                            <i class="fas fa-credit-card"></i>
                        </div>
                        <div class="summary-content">
                            <h4>Total Cuentas</h4>
                            <div class="summary-value" id="totalAccounts">0</div>
                        </div>
                    </div>
                    
                    <div class="summary-card">
                        <div class="summary-icon warning">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="summary-content">
                            <h4>Cuentas Inactivas</h4>
                            <div class="summary-value" id="inactiveAccounts">0</div>
                        </div>
                    </div>
                </div>

                <!-- Lista de cuentas -->
                <div class="accounts-section">
                    <div class="section-header">
                        <h3>Cuentas Bancarias</h3>
                        <div class="results-info">
                            Mostrando <span id="showing-count">0</span> de <span id="total-count">0</span> cuentas
                        </div>
                    </div>
                    
                    <div class="accounts-list" id="accounts-list">
                        <!-- Las cuentas se cargarán dinámicamente -->
                    </div>
                    
                    <!-- Paginación -->
                    <div class="pagination" id="pagination">
                        <!-- La paginación se cargará dinámicamente -->
                    </div>
                </div>
            </div>

            <!-- Modal para crear/editar cuenta -->
            <div id="account-modal" class="modal hidden">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3 id="modal-title">Nueva Cuenta</h3>
                        <button class="modal-close" onclick="cuentasPage.closeModal()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <form id="account-form" class="modal-body">
                        <div class="form-group">
                            <label for="account-type">Tipo de Cuenta *</label>
                            <select id="account-type" name="type" required>
                                <option value="">Seleccionar tipo</option>
                                <option value="corriente">Cuenta Corriente</option>
                                <option value="ahorros">Cuenta de Ahorros</option>
                                <option value="plazo">Plazo Fijo</option>
                            </select>
                            <div class="error-message" id="type-error"></div>
                        </div>
                        
                        <div class="form-group">
                            <label for="initial-balance">Saldo Inicial *</label>
                            <div class="input-group">
                                <span class="input-prefix">S/</span>
                                <input type="number" 
                                       id="initial-balance" 
                                       name="balance" 
                                       min="0" 
                                       step="0.01"
                                       placeholder="0.00" 
                                       required>
                            </div>
                            <div class="error-message" id="balance-error"></div>
                        </div>
                        
                        <div class="form-group">
                            <label for="account-description">Descripción (Opcional)</label>
                            <textarea id="account-description" 
                                      name="description" 
                                      rows="3" 
                                      placeholder="Descripción de la cuenta..."></textarea>
                        </div>
                        
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary" onclick="cuentasPage.closeModal()">
                                Cancelar
                            </button>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i> Crear Cuenta
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    }

    /**
     * Cargar cuentas desde la API
     */
    async loadAccounts() {
        try {
            const accounts = await API.getAccounts();
            this.data.accounts = accounts.map(account => ({
                ...account,
                dateCreated: account.dateCreated || new Date().toISOString(),
                lastActivity: account.lastActivity || new Date().toISOString()
            }));
        } catch (error) {
            console.error('Error loading accounts:', error);
            this.data.accounts = this.getDemoAccounts();
        }
    }

    /**
     * Obtener cuentas de demostración
     */
    getDemoAccounts() {
        return [
            {
                id: '1',
                type: 'corriente',
                number: '2012345678901',
                balance: 15430.50,
                status: 'active',
                dateCreated: '2023-01-15T00:00:00Z',
                lastActivity: new Date().toISOString(),
                description: 'Cuenta corriente principal'
            },
            {
                id: '2',
                type: 'ahorros',
                number: '2012345678902',
                balance: 10000.00,
                status: 'active',
                dateCreated: '2023-03-20T00:00:00Z',
                lastActivity: new Date(Date.now() - 86400000).toISOString(),
                description: 'Cuenta de ahorros para emergencias'
            },
            {
                id: '3',
                type: 'plazo',
                number: '2012345678903',
                balance: 50000.00,
                status: 'active',
                dateCreated: '2023-06-10T00:00:00Z',
                lastActivity: new Date(Date.now() - 172800000).toISOString(),
                description: 'Depósito a plazo fijo - 12 meses'
            },
            {
                id: '4',
                type: 'ahorros',
                number: '2012345678904',
                balance: 2500.00,
                status: 'inactive',
                dateCreated: '2022-12-01T00:00:00Z',
                lastActivity: new Date(Date.now() - 2592000000).toISOString(),
                description: 'Cuenta de ahorros secundaria'
            }
        ];
    }

    /**
     * Aplicar filtros y ordenar
     */
    applyFilters() {
        let filtered = [...this.data.accounts];

        // Filtro por búsqueda
        if (this.data.filters.search) {
            const search = this.data.filters.search.toLowerCase();
            filtered = filtered.filter(account => 
                account.number.includes(search) || 
                account.type.toLowerCase().includes(search) ||
                (account.description && account.description.toLowerCase().includes(search))
            );
        }

        // Filtro por tipo
        if (this.data.filters.type !== 'all') {
            filtered = filtered.filter(account => account.type === this.data.filters.type);
        }

        // Filtro por estado
        if (this.data.filters.status !== 'all') {
            filtered = filtered.filter(account => account.status === this.data.filters.status);
        }

        // Ordenamiento
        filtered.sort((a, b) => {
            let valueA, valueB;
            
            switch (this.data.sortBy) {
                case 'balance':
                    valueA = a.balance;
                    valueB = b.balance;
                    break;
                case 'type':
                    valueA = a.type;
                    valueB = b.type;
                    break;
                case 'number':
                    valueA = a.number;
                    valueB = b.number;
                    break;
                case 'date':
                    valueA = new Date(a.dateCreated);
                    valueB = new Date(b.dateCreated);
                    break;
                default:
                    valueA = a.balance;
                    valueB = b.balance;
            }

            if (this.data.sortOrder === 'asc') {
                return valueA > valueB ? 1 : -1;
            } else {
                return valueA < valueB ? 1 : -1;
            }
        });

        this.filteredAccounts = filtered;
        this.updateSummary();
        this.renderAccounts();
        this.renderPagination();
    }

    /**
     * Actualizar resumen de cuentas
     */
    updateSummary() {
        const totalBalance = this.filteredAccounts.reduce((sum, account) => sum + account.balance, 0);
        const totalAccounts = this.filteredAccounts.length;
        const inactiveAccounts = this.filteredAccounts.filter(account => account.status === 'inactive').length;

        document.getElementById('totalBalance').textContent = this.formatCurrency(totalBalance);
        document.getElementById('totalAccounts').textContent = totalAccounts;
        document.getElementById('inactiveAccounts').textContent = inactiveAccounts;
        
        document.getElementById('showing-count').textContent = this.filteredAccounts.length;
        document.getElementById('total-count').textContent = this.data.accounts.length;
    }

    /**
     * Renderizar lista de cuentas
     */
    renderAccounts() {
        const container = document.getElementById('accounts-list');
        if (!container) return;

        if (this.filteredAccounts.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <i class="fas fa-credit-card"></i>
                    </div>
                    <h3>No se encontraron cuentas</h3>
                    <p>No hay cuentas que coincidan con los filtros aplicados</p>
                    <button class="btn btn-primary" onclick="cuentasPage.clearFilters()">
                        <i class="fas fa-refresh"></i> Limpiar Filtros
                    </button>
                </div>
            `;
            return;
        }

        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const paginatedAccounts = this.filteredAccounts.slice(startIndex, endIndex);

        container.innerHTML = paginatedAccounts.map(account => `
            <div class="account-card">
                <div class="account-header">
                    <div class="account-info">
                        <h4>${this.getAccountTypeName(account.type)}</h4>
                        <div class="account-number">
                            ${this.maskAccountNumber(account.number)}
                        </div>
                    </div>
                    <div class="account-status">
                        <span class="status-badge status-${account.status}">
                            ${this.getStatusName(account.status)}
                        </span>
                    </div>
                </div>
                
                <div class="account-details">
                    <div class="detail-item">
                        <small>Saldo Disponible</small>
                        <div class="balance-amount ${account.balance >= 0 ? 'positive' : 'negative'}">
                            ${this.formatCurrency(account.balance)}
                        </div>
                    </div>
                    
                    <div class="detail-item">
                        <small>Fecha de Creación</small>
                        <div>${this.formatDate(account.dateCreated)}</div>
                    </div>
                    
                    <div class="detail-item">
                        <small>Última Actividad</small>
                        <div>${this.formatRelativeDate(account.lastActivity)}</div>
                    </div>
                </div>
                
                ${account.description ? `
                    <div class="account-description">
                        <small>Descripción</small>
                        <p>${account.description}</p>
                    </div>
                ` : ''}
                
                <div class="account-actions">
                    <button class="btn btn-sm btn-outline" onclick="cuentasPage.viewAccountDetails('${account.id}')">
                        <i class="fas fa-eye"></i> Ver Detalles
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="cuentasPage.makeTransfer('${account.id}')">
                        <i class="fas fa-exchange-alt"></i> Transferir
                    </button>
                    ${account.status === 'active' ? `
                        <button class="btn btn-sm btn-warning" onclick="cuentasPage.blockAccount('${account.id}')">
                            <i class="fas fa-lock"></i> Bloquear
                        </button>
                    ` : `
                        <button class="btn btn-sm btn-success" onclick="cuentasPage.activateAccount('${account.id}')">
                            <i class="fas fa-unlock"></i> Activar
                        </button>
                    `}
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

        const totalPages = Math.ceil(this.filteredAccounts.length / this.itemsPerPage);
        this.totalPages = totalPages;

        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        let paginationHTML = '<div class="pagination-controls">';

        // Botón anterior
        if (this.currentPage > 1) {
            paginationHTML += `<button class="btn btn-sm btn-outline" onclick="cuentasPage.goToPage(${this.currentPage - 1})">
                <i class="fas fa-chevron-left"></i> Anterior
            </button>`;
        }

        // Números de página
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `<button class="btn btn-sm ${i === this.currentPage ? 'btn-primary' : 'btn-outline'}" 
                               onclick="cuentasPage.goToPage(${i})">${i}</button>`;
        }

        // Botón siguiente
        if (this.currentPage < totalPages) {
            paginationHTML += `<button class="btn btn-sm btn-outline" onclick="cuentasPage.goToPage(${this.currentPage + 1})">
                Siguiente <i class="fas fa-chevron-right"></i>
            </button>`;
        }

        paginationHTML += '</div>';
        container.innerHTML = paginationHTML;
    }

    /**
     * Manejar búsqueda
     */
    handleSearch(value) {
        this.data.filters.search = value;
        this.currentPage = 1;
        this.applyFilters();
    }

    /**
     * Manejar filtro por tipo
     */
    handleTypeFilter(value) {
        this.data.filters.type = value;
        this.currentPage = 1;
        this.applyFilters();
    }

    /**
     * Manejar filtro por estado
     */
    handleStatusFilter(value) {
        this.data.filters.status = value;
        this.currentPage = 1;
        this.applyFilters();
    }

    /**
     * Manejar ordenamiento
     */
    handleSort(value) {
        const [field, order] = value.split('-');
        this.data.sortBy = field;
        this.data.sortOrder = order;
        this.currentPage = 1;
        this.applyFilters();
    }

    /**
     * Ir a página específica
     */
    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.currentPage = page;
            this.renderAccounts();
            this.renderPagination();
        }
    }

    /**
     * Limpiar filtros
     */
    clearFilters() {
        this.data.filters = {
            type: 'all',
            status: 'all',
            search: ''
        };
        this.currentPage = 1;
        this.applyFilters();
        
        // Resetear inputs
        document.getElementById('search-input').value = '';
        document.getElementById('type-filter').value = 'all';
        document.getElementById('status-filter').value = 'all';
        document.getElementById('sort-select').value = 'balance-desc';
    }

    /**
     * Mostrar modal de crear cuenta
     */
    showCreateAccountModal() {
        const modal = document.getElementById('account-modal');
        const form = document.getElementById('account-form');
        const title = document.getElementById('modal-title');

        title.textContent = 'Nueva Cuenta';
        form.reset();
        this.clearErrors();
        modal.classList.remove('hidden');

        // Event listener para el formulario
        form.onsubmit = (e) => this.handleCreateAccount(e);
    }

    /**
     * Cerrar modal
     */
    closeModal() {
        const modal = document.getElementById('account-modal');
        modal.classList.add('hidden');
        this.clearErrors();
    }

    /**
     * Manejar creación de cuenta
     */
    async handleCreateAccount(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const accountData = {
            type: formData.get('type'),
            balance: parseFloat(formData.get('balance')),
            description: formData.get('description') || ''
        };

        // Validaciones
        if (!this.validateAccountData(accountData)) {
            return;
        }

        try {
            this.showFormLoading(true);
            
            // Simular creación de cuenta
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            const newAccount = {
                id: Date.now().toString(),
                ...accountData,
                number: this.generateAccountNumber(),
                status: 'active',
                dateCreated: new Date().toISOString(),
                lastActivity: new Date().toISOString()
            };

            this.data.accounts.unshift(newAccount);
            this.applyFilters();
            
            window.bancoApp?.showNotification('Cuenta creada exitosamente', 'success');
            this.closeModal();

        } catch (error) {
            this.handleError('Error al crear la cuenta', error);
        } finally {
            this.showFormLoading(false);
        }
    }

    /**
     * Validar datos de cuenta
     */
    validateAccountData(data) {
        let isValid = true;

        // Validar tipo
        if (!data.type) {
            this.showError('type-error', 'El tipo de cuenta es requerido');
            isValid = false;
        }

        // Validar saldo
        if (isNaN(data.balance) || data.balance < 0) {
            this.showError('balance-error', 'El saldo debe ser un monto válido mayor o igual a 0');
            isValid = false;
        }

        return isValid;
    }

    /**
     * Mostrar error en campo
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
        const submitButton = document.querySelector('#account-form button[type="submit"]');
        if (submitButton) {
            if (show) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creando...';
            } else {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-save"></i> Crear Cuenta';
            }
        }
    }

    /**
     * Generar número de cuenta
     */
    generateAccountNumber() {
        const timestamp = Date.now().toString();
        const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
        return `20${timestamp.slice(-8)}${random}`;
    }

    /**
     * Ver detalles de cuenta
     */
    viewAccountDetails(accountId) {
        const account = this.data.accounts.find(a => a.id === accountId);
        if (account) {
            window.bancoApp?.showNotification(`Detalles de cuenta ${account.number}`, 'info');
            // Aquí se podría abrir un modal con más detalles
        }
    }

    /**
     * Hacer transferencia
     */
    makeTransfer(accountId) {
        window.bancoApp?.showNotification('Función de transferencia en desarrollo', 'info');
    }

    /**
     * Bloquear cuenta
     */
    async blockAccount(accountId) {
        try {
            const account = this.data.accounts.find(a => a.id === accountId);
            if (account) {
                account.status = 'blocked';
                this.applyFilters();
                window.bancoApp?.showNotification('Cuenta bloqueada exitosamente', 'success');
            }
        } catch (error) {
            this.handleError('Error al bloquear la cuenta', error);
        }
    }

    /**
     * Activar cuenta
     */
    async activateAccount(accountId) {
        try {
            const account = this.data.accounts.find(a => a.id === accountId);
            if (account) {
                account.status = 'active';
                this.applyFilters();
                window.bancoApp?.showNotification('Cuenta activada exitosamente', 'success');
            }
        } catch (error) {
            this.handleError('Error al activar la cuenta', error);
        }
    }

    /**
     * Obtener nombre del tipo de cuenta
     */
    getAccountTypeName(type) {
        const types = {
            'corriente': 'Cuenta Corriente',
            'ahorros': 'Cuenta de Ahorros',
            'plazo': 'Plazo Fijo'
        };
        return types[type] || type;
    }

    /**
     * Obtener nombre del estado
     */
    getStatusName(status) {
        const statuses = {
            'active': 'Activa',
            'inactive': 'Inactiva',
            'blocked': 'Bloqueada'
        };
        return statuses[status] || status;
    }

    /**
     * Enmascarar número de cuenta
     */
    maskAccountNumber(number) {
        if (number.length <= 4) return number;
        return '****' + number.slice(-4);
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
     * Formatear fecha
     */
    formatDate(dateString) {
        return new Intl.DateTimeFormat('es-PE', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(dateString));
    }

    /**
     * Formatear fecha relativa
     */
    formatRelativeDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Hoy';
        if (diffDays === 1) return 'Ayer';
        if (diffDays < 7) return `Hace ${diffDays} días`;
        if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`;
        return `Hace ${Math.floor(diffDays / 30)} meses`;
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
                <h3>Error al cargar las cuentas</h3>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">
                    <i class="fas fa-refresh"></i> Reintentar
                </button>
            </div>
        `;
    }
}

// Instanciar página globalmente
window.cuentasPage = new CuentasPage();