// Aplicación principal
class BancoDesktop {
  constructor() {
    this.currentUser = null;
    this.isLoading = true;
    this.router = new Router();
    this.init();
  }

  async init() {
    console.log('Iniciando Banco Desktop...');
    
    // Verificar si hay una sesión guardada
    await this.checkSavedSession();
    
    // Configurar event listeners
    this.setupEventListeners();
    
    // Configurar menú
    this.setupMenuHandlers();
    
    // Configurar notificaciones
    this.setupNotifications();
    
    // Ocultar pantalla de carga
    setTimeout(() => {
      this.hideLoadingScreen();
    }, 2000);
  }

  async checkSavedSession() {
    try {
      const savedUser = await window.electronAPI.store.get('currentUser');
      if (savedUser) {
        this.currentUser = savedUser;
        this.showMainApp();
        this.router.navigate('dashboard');
      } else {
        this.showLoginScreen();
      }
    } catch (error) {
      console.error('Error checking saved session:', error);
      this.showLoginScreen();
    }
  }

  setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
      loginForm.addEventListener('submit', this.handleLogin.bind(this));
    }

    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', this.handleLogout.bind(this));
    }

    // Menu toggle
    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
      menuToggle.addEventListener('click', this.toggleSidebar.bind(this));
    }

    // Navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = e.target.closest('.nav-link').dataset.page;
        this.router.navigate(page);
        this.updateActiveNavLink(page);
      });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));

    // Window events
    window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
  }

  setupMenuHandlers() {
    // Escuchar eventos del menú
    window.electronAPI.menu.onNewAccount(() => {
      this.router.navigate('cuentas');
      this.showCreateAccountModal();
    });

    window.electronAPI.menu.onNewTransaction(() => {
      this.router.navigate('transacciones');
      this.showCreateTransactionModal();
    });

    window.electronAPI.menu.onAbout(() => {
      this.showAboutDialog();
    });
  }

  setupNotifications() {
    // Configurar contenedor de notificaciones
    this.notificationContainer = document.getElementById('notification-container');
    
    // Notificaciones de RabbitMQ si está disponible
    if (window.electronAPI.rabbitmq) {
      this.setupRabbitMQNotifications();
    }
  }

  async setupRabbitMQNotifications() {
    try {
      // Intentar conectar a RabbitMQ
      const result = await window.electronAPI.rabbitmq.connect();
      if (result.success) {
        console.log('RabbitMQ connected for notifications');
        
        // Suscribirse a notificaciones
        await window.electronAPI.rabbitmq.subscribe('banco.notifications', (message) => {
          this.showNotification(message.message, message.type);
        });
      }
    } catch (error) {
      console.log('RabbitMQ not available:', error);
    }
  }

  async handleLogin(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const username = formData.get('username');
    const password = formData.get('password');
    
    const loginError = document.getElementById('login-error');
    
    try {
      this.setLoading(true);
      loginError.classList.add('hidden');
      
      // Simular autenticación (en una app real, esto sería una API call)
      const user = await this.authenticateUser(username, password);
      
      if (user) {
        this.currentUser = user;
        await window.electronAPI.store.set('currentUser', user);
        this.showMainApp();
        this.router.navigate('dashboard');
        this.showNotification('¡Bienvenido!', 'success');
      } else {
        throw new Error('Credenciales inválidas');
      }
    } catch (error) {
      console.error('Login error:', error);
      loginError.textContent = error.message;
      loginError.classList.remove('hidden');
    } finally {
      this.setLoading(false);
    }
  }

  async authenticateUser(username, password) {
    // Simulación de autenticación
    // En una aplicación real, esto se conectaría a un servidor
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Credenciales de prueba
    if ((username === 'admin' && password === 'admin123') ||
        (username === 'usuario' && password === '123456')) {
      return {
        id: 1,
        username,
        name: username === 'admin' ? 'Administrador' : 'Usuario Demo',
        email: `${username}@banco.com`,
        role: username === 'admin' ? 'admin' : 'user'
      };
    }
    
    return null;
  }

  async handleLogout() {
    try {
      await window.electronAPI.store.delete('currentUser');
      this.currentUser = null;
      this.router.navigate('login');
      this.showLoginScreen();
      this.showNotification('Sesión cerrada', 'info');
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  showMainApp() {
    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('main-app').classList.remove('hidden');
    
    if (this.currentUser) {
      document.getElementById('current-user').textContent = this.currentUser.name;
    }
  }

  showLoginScreen() {
    document.getElementById('main-app').classList.add('hidden');
    document.getElementById('login-screen').classList.remove('hidden');
  }

  hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
      loadingScreen.style.opacity = '0';
      setTimeout(() => {
        loadingScreen.classList.add('hidden');
      }, 500);
    }
    this.isLoading = false;
  }

  toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
  }

  updateActiveNavLink(page) {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.dataset.page === page) {
        link.classList.add('active');
      }
    });
  }

  handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + N: Nueva cuenta
    if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
      event.preventDefault();
      this.router.navigate('cuentas');
      this.showCreateAccountModal();
    }
    
    // Ctrl/Cmd + T: Nueva transacción
    if ((event.ctrlKey || event.metaKey) && event.key === 't') {
      event.preventDefault();
      this.router.navigate('transacciones');
      this.showCreateTransactionModal();
    }
    
    // Escape: Cerrar modales
    if (event.key === 'Escape') {
      this.closeAllModals();
    }
  }

  handleBeforeUnload(event) {
    // Limpiar recursos antes de cerrar
    if (this.currentUser) {
      // Guardar estado de la aplicación si es necesario
    }
  }

  showCreateAccountModal() {
    // Mostrar modal para crear cuenta
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal">
        <div class="modal-header">
          <h3>Nueva Cuenta</h3>
          <button class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
          <form id="create-account-form">
            <div class="form-group">
              <label for="account-type">Tipo de Cuenta</label>
              <select id="account-type" class="form-control" required>
                <option value="">Seleccionar tipo</option>
                <option value="ahorros">Ahorros</option>
                <option value="corriente">Corriente</option>
                <option value="plazo_fijo">Plazo Fijo</option>
              </select>
            </div>
            <div class="form-group">
              <label for="initial-balance">Saldo Inicial</label>
              <input type="number" id="initial-balance" class="form-control" step="0.01" min="0">
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary modal-close">Cancelar</button>
          <button type="submit" form="create-account-form" class="btn btn-primary">Crear Cuenta</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    modal.classList.remove('hidden');
    
    // Event listeners para el modal
    modal.querySelector('.modal-close').addEventListener('click', () => {
      document.body.removeChild(modal);
    });
    
    modal.querySelector('#create-account-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      await this.createAccount(new FormData(e.target));
      document.body.removeChild(modal);
    });
  }

  showCreateTransactionModal() {
    // Mostrar modal para crear transacción
    this.showNotification('Funcionalidad de transacción en desarrollo', 'info');
  }

  async createAccount(formData) {
    try {
      // Simular creación de cuenta
      const accountData = {
        type: formData.get('account-type'),
        initialBalance: parseFloat(formData.get('initial-balance')) || 0
      };
      
      this.showNotification('Cuenta creada exitosamente', 'success');
      this.router.navigate('cuentas');
    } catch (error) {
      this.showNotification('Error al crear cuenta: ' + error.message, 'error');
    }
  }

  showAboutDialog() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal">
        <div class="modal-header">
          <h3>Acerca de Banco Desktop</h3>
          <button class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="text-center">
            <h4>Banco Desktop v1.0.0</h4>
            <p>Sistema de Gestión Bancaria</p>
            <p>Desarrollado para el curso LP3</p>
            <p><strong>Características:</strong></p>
            <ul style="text-align: left;">
              <li>Gestión de cuentas bancarias</li>
              <li>Transacciones en tiempo real</li>
              <li>Generación de códigos QR</li>
              <li>Gestión de préstamos</li>
              <li>Integración con RabbitMQ</li>
              <li>Base de datos SQLite</li>
            </ul>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary modal-close">Cerrar</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    modal.classList.remove('hidden');
    
    modal.querySelector('.modal-close').addEventListener('click', () => {
      document.body.removeChild(modal);
    });
  }

  closeAllModals() {
    const modals = document.querySelectorAll('.modal-overlay');
    modals.forEach(modal => {
      if (!modal.classList.contains('hidden')) {
        document.body.removeChild(modal);
      }
    });
  }

  showNotification(message, type = 'info') {
    if (!this.notificationContainer) return;
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <span class="notification-message">${message}</span>
        <button class="notification-close">&times;</button>
      </div>
    `;
    
    this.notificationContainer.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 5000);
    
    // Manual close
    notification.querySelector('.notification-close').addEventListener('click', () => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    });
  }

  setLoading(loading) {
    // Implementar indicador de carga global si es necesario
    this.isLoading = loading;
  }

  // Métodos públicos
  getCurrentUser() {
    return this.currentUser;
  }

  isLoggedIn() {
    return this.currentUser !== null;
  }

  getRouter() {
    return this.router;
  }
}

// Inicializar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  window.bancoApp = new BancoDesktop();
});

// Estilos para notificaciones
const notificationStyles = `
  .notification-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 3000;
  }

  .notification {
    background: var(--surface-color);
    border-radius: 8px;
    box-shadow: var(--shadow-lg);
    margin-bottom: 10px;
    overflow: hidden;
    max-width: 350px;
    animation: slideInRight 0.3s ease-out;
  }

  .notification-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
  }

  .notification-message {
    flex: 1;
    font-size: 14px;
  }

  .notification-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: var(--text-secondary);
    margin-left: 10px;
  }

  .notification-success {
    border-left: 4px solid var(--success-color);
  }

  .notification-warning {
    border-left: 4px solid var(--warning-color);
  }

  .notification-error {
    border-left: 4px solid var(--error-color);
  }

  .notification-info {
    border-left: 4px solid var(--primary-color);
  }

  @keyframes slideInRight {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
`;

// Agregar estilos dinámicamente
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);
