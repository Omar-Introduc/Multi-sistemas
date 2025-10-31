/**
 * Página Dashboard - Sistema Bancario Desktop
 * Incluye estadísticas, gráficos y resumen de actividad
 */

class DashboardPage {
    constructor() {
        this.data = {
            totalBalance: 0,
            activeAccounts: 0,
            monthlyTransactions: 0,
            pendingLoans: 0,
            accounts: [],
            transactions: [],
            charts: {}
        };
        this.refreshInterval = null;
    }

    /**
     * Renderizar la página dashboard
     */
    async render() {
        try {
            // Mostrar loading
            this.showLoading();

            // Cargar datos
            await this.loadData();

            // Actualizar UI
            this.updateStats();
            this.loadRecentTransactions();
            this.loadAccounts();
            this.setupCharts();

            // Configurar auto-refresh
            this.setupAutoRefresh();

            this.hideLoading();
            return this.getHTML();

        } catch (error) {
            this.hideLoading();
            this.handleError('Error al cargar el dashboard', error);
            return this.getErrorHTML(error.message);
        }
    }

    /**
     * Obtener HTML de la página
     */
    getHTML() {
        return `
            <div id="dashboard-content" class="dashboard-container">
                <!-- Stats Grid -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon primary">
                            <i class="fas fa-wallet"></i>
                        </div>
                        <div class="stat-content">
                            <h4>Saldo Total</h4>
                            <div class="stat-value" id="totalBalance">S/ 0.00</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon success">
                            <i class="fas fa-credit-card"></i>
                        </div>
                        <div class="stat-content">
                            <h4>Cuentas Activas</h4>
                            <div class="stat-value" id="activeAccounts">0</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon warning">
                            <i class="fas fa-exchange-alt"></i>
                        </div>
                        <div class="stat-content">
                            <h4>Transacciones del Mes</h4>
                            <div class="stat-value" id="monthlyTransactions">0</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon error">
                            <i class="fas fa-money-bill-wave"></i>
                        </div>
                        <div class="stat-content">
                            <h4>Préstamos Pendientes</h4>
                            <div class="stat-value" id="pendingLoans">0</div>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="section">
                    <div class="section-header">
                        <h3>Acciones Rápidas</h3>
                    </div>
                    <div class="quick-actions">
                        <div class="quick-action" onclick="app.navigateTo('cuentas')">
                            <div class="quick-action-icon">
                                <i class="fas fa-plus-circle"></i>
                            </div>
                            <h4>Nueva Cuenta</h4>
                            <p>Crear una nueva cuenta bancaria</p>
                        </div>
                        
                        <div class="quick-action" onclick="showTransferModal()">
                            <div class="quick-action-icon">
                                <i class="fas fa-paper-plane"></i>
                            </div>
                            <h4>Transferir</h4>
                            <p>Enviar dinero a otra cuenta</p>
                        </div>
                        
                        <div class="quick-action" onclick="app.navigateTo('qr-generator')">
                            <div class="quick-action-icon">
                                <i class="fas fa-qrcode"></i>
                            </div>
                            <h4>Generar QR</h4>
                            <p>Crear código QR para pagos</p>
                        </div>
                        
                        <div class="quick-action" onclick="app.navigateTo('prestamos')">
                            <div class="quick-action-icon">
                                <i class="fas fa-hand-holding-usd"></i>
                            </div>
                            <h4>Solicitar Préstamo</h4>
                            <p>Aplicar para un nuevo préstamo</p>
                        </div>
                    </div>
                </div>

                <!-- Recent Transactions -->
                <div class="section">
                    <div class="section-header">
                        <h3>Transacciones Recientes</h3>
                        <button class="btn btn-outline" onclick="app.navigateTo('transacciones')">
                            Ver Todas
                        </button>
                    </div>
                    <div class="transaction-list" id="recentTransactions">
                        <!-- Las transacciones se cargarán dinámicamente -->
                    </div>
                </div>

                <!-- Accounts Overview -->
                <div class="section">
                    <div class="section-header">
                        <h3>Resumen de Cuentas</h3>
                        <button class="btn btn-outline" onclick="app.navigateTo('cuentas')">
                            Gestionar Cuentas
                        </button>
                    </div>
                    <div class="accounts-grid" id="accountsGrid">
                        <!-- Las cuentas se cargarán dinámicamente -->
                    </div>
                </div>

                <!-- Charts Section -->
                <div class="section">
                    <div class="section-header">
                        <h3>Análisis Financiero</h3>
                    </div>
                    <div class="charts-grid">
                        <div class="chart-container">
                            <h4>Ingresos vs Gastos (Últimos 6 meses)</h4>
                            <canvas id="incomeExpenseChart"></canvas>
                        </div>
                        
                        <div class="chart-container">
                            <h4>Distribución por Tipo de Cuenta</h4>
                            <canvas id="accountTypeChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Cargar datos desde la API
     */
    async loadData() {
        try {
            const [accounts, transactions, loans] = await Promise.all([
                API.getAccounts(),
                API.getTransactions(),
                API.getLoans ? API.getLoans() : []
            ]);

            this.data.accounts = accounts;
            this.data.transactions = transactions;
            this.data.pendingLoans = loans.filter(l => l.status === 'pending').length;

            // Calcular estadísticas
            this.data.totalBalance = accounts.reduce((total, account) => 
                total + (parseFloat(account.balance) || 0), 0
            );
            
            this.data.activeAccounts = accounts.length;
            
            // Transacciones del mes actual
            const currentMonth = new Date().getMonth();
            const currentYear = new Date().getFullYear();
            this.data.monthlyTransactions = transactions.filter(t => {
                const transactionDate = new Date(t.date);
                return transactionDate.getMonth() === currentMonth && 
                       transactionDate.getFullYear() === currentYear;
            }).length;

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.loadDemoData();
        }
    }

    /**
     * Cargar datos de demostración
     */
    loadDemoData() {
        this.data = {
            totalBalance: 25430.50,
            activeAccounts: 3,
            monthlyTransactions: 12,
            pendingLoans: 1,
            accounts: [
                {
                    id: '1',
                    type: 'Cuenta Corriente',
                    number: '****1234',
                    balance: 15430.50,
                    status: 'active'
                },
                {
                    id: '2',
                    type: 'Cuenta de Ahorros',
                    number: '****5678',
                    balance: 10000.00,
                    status: 'active'
                }
            ],
            transactions: [
                {
                    id: 'TXN001',
                    date: new Date(),
                    description: 'Pago - Supermercado ABC',
                    category: 'Alimentación',
                    amount: -45.20,
                    status: 'completed'
                },
                {
                    id: 'TXN002',
                    date: new Date(Date.now() - 86400000),
                    description: 'Transferencia Recibida',
                    category: 'Transferencia',
                    amount: 1200.00,
                    status: 'completed'
                }
            ]
        };
    }

    /**
     * Actualizar estadísticas
     */
    updateStats() {
        const totalBalance = document.getElementById('totalBalance');
        const activeAccounts = document.getElementById('activeAccounts');
        const monthlyTransactions = document.getElementById('monthlyTransactions');
        const pendingLoans = document.getElementById('pendingLoans');

        if (totalBalance) {
            totalBalance.textContent = this.formatCurrency(this.data.totalBalance);
        }
        if (activeAccounts) {
            activeAccounts.textContent = this.data.activeAccounts;
        }
        if (monthlyTransactions) {
            monthlyTransactions.textContent = this.data.monthlyTransactions;
        }
        if (pendingLoans) {
            pendingLoans.textContent = this.data.pendingLoans;
        }
    }

    /**
     * Cargar transacciones recientes
     */
    loadRecentTransactions() {
        const container = document.getElementById('recentTransactions');
        if (!container) return;

        if (this.data.transactions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <i class="fas fa-inbox"></i>
                    </div>
                    <h3>No hay transacciones</h3>
                    <p>Las transacciones aparecerán aquí cuando realices operaciones</p>
                </div>
            `;
            return;
        }

        const recentTransactions = this.data.transactions
            .sort((a, b) => new Date(b.date) - new Date(a.date))
            .slice(0, 5);

        container.innerHTML = recentTransactions.map(transaction => `
            <div class="transaction-item">
                <div class="transaction-info">
                    <h4>${transaction.description}</h4>
                    <p>${this.formatDateTime(transaction.date)}</p>
                </div>
                <div class="transaction-amount">
                    <div class="amount ${transaction.amount >= 0 ? 'positive' : 'negative'}">
                        ${transaction.amount >= 0 ? '+' : ''}${this.formatCurrency(Math.abs(transaction.amount))}
                    </div>
                    <div class="date">${this.formatDateTime(transaction.date)}</div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Cargar cuentas
     */
    loadAccounts() {
        const container = document.getElementById('accountsGrid');
        if (!container) return;

        if (this.data.accounts.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <i class="fas fa-credit-card"></i>
                    </div>
                    <h3>No hay cuentas</h3>
                    <p>Crea tu primera cuenta para comenzar</p>
                    <button class="btn btn-primary" onclick="showCreateAccountModal()">
                        Crear Cuenta
                    </button>
                </div>
            `;
            return;
        }

        container.innerHTML = this.data.accounts.map(account => `
            <div class="account-card">
                <div class="account-header">
                    <h4>${account.type}</h4>
                    <span class="status-badge status-${account.status}">${account.status}</span>
                </div>
                <div class="account-details">
                    <div class="account-number">
                        <small>Número de Cuenta</small>
                        <strong>${account.number}</strong>
                    </div>
                    <div class="account-balance">
                        <small>Saldo Disponible</small>
                        <strong class="balance-amount">${this.formatCurrency(account.balance)}</strong>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Configurar gráficos con Chart.js
     */
    setupCharts() {
        setTimeout(() => {
            this.setupIncomeExpenseChart();
            this.setupAccountTypeChart();
        }, 100);
    }

    /**
     * Configurar gráfico de ingresos vs gastos
     */
    setupIncomeExpenseChart() {
        const ctx = document.getElementById('incomeExpenseChart');
        if (!ctx) return;

        const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'];
        const income = [5000, 6000, 4500, 7000, 5500, 4800];
        const expenses = [3200, 3800, 4100, 3500, 3900, 4200];

        this.data.charts.incomeExpense = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Ingresos',
                        data: income,
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Gastos',
                        data: expenses,
                        borderColor: '#f44336',
                        backgroundColor: 'rgba(244, 67, 54, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return 'S/ ' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Configurar gráfico de tipos de cuenta
     */
    setupAccountTypeChart() {
        const ctx = document.getElementById('accountTypeChart');
        if (!ctx) return;

        const accountTypes = this.data.accounts.reduce((acc, account) => {
            acc[account.type] = (acc[account.type] || 0) + account.balance;
            return acc;
        }, {});

        const labels = Object.keys(accountTypes);
        const data = Object.values(accountTypes);
        const colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0'];

        this.data.charts.accountType = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }

    /**
     * Configurar auto-refresh
     */
    setupAutoRefresh() {
        // Actualizar datos cada 30 segundos
        this.refreshInterval = setInterval(async () => {
            try {
                await this.loadData();
                this.updateStats();
                this.loadRecentTransactions();
                this.loadAccounts();
            } catch (error) {
                console.error('Error refreshing dashboard:', error);
            }
        }, 30000);
    }

    /**
     * Limpiar recursos
     */
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Destruir gráficos
        Object.values(this.data.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
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
                <h3>Error al cargar el dashboard</h3>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">
                    <i class="fas fa-refresh"></i> Reintentar
                </button>
            </div>
        `;
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
    formatDateTime(date) {
        return new Intl.DateTimeFormat('es-PE', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    }
}

// Funciones globales para la página
function showTransferModal() {
    window.bancoApp?.showNotification('Función de transferencia en desarrollo', 'info');
}

function showCreateAccountModal() {
    window.bancoApp?.showCreateAccountModal?.();
}

// Exportar clase
window.DashboardPage = DashboardPage;