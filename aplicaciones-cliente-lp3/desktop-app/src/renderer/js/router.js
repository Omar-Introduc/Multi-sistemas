// Router para navegación de páginas
class Router {
  constructor() {
    this.routes = {};
    this.currentRoute = null;
    this.pageCache = new Map();
    this.init();
  }

  init() {
    // Registrar rutas
    this.registerRoutes();
    
    // Configurar navegación inicial
    this.setupInitialNavigation();
    
    // Configurar manejo de cambios de hash
    this.setupHashNavigation();
  }

  registerRoutes() {
    this.routes = {
      'login': {
        component: LoginPage,
        title: 'Iniciar Sesión'
      },
      'dashboard': {
        component: DashboardPage,
        title: 'Dashboard',
        requiresAuth: true
      },
      'cuentas': {
        component: CuentasPage,
        title: 'Cuentas Bancarias',
        requiresAuth: true
      },
      'transacciones': {
        component: TransaccionesPage,
        title: 'Transacciones',
        requiresAuth: true
      },
      'prestamos': {
        component: PrestamosPage,
        title: 'Préstamos',
        requiresAuth: true
      },
      'qr-generator': {
        component: QRGeneratorPage,
        title: 'Generador QR',
        requiresAuth: true
      }
    };
  }

  setupInitialNavigation() {
    // Determinar ruta inicial
    let initialRoute = 'dashboard';
    
    // Verificar si hay usuario autenticado
    const checkAuth = async () => {
      try {
        const currentUser = await window.electronAPI.store.get('currentUser');
        if (!currentUser) {
          initialRoute = 'login';
        }
      } catch (error) {
        console.warn('Could not check authentication:', error);
        initialRoute = 'login';
      }
    };

    checkAuth().then(() => {
      this.navigate(initialRoute);
    });
  }

  setupHashNavigation() {
    // Manejar cambios en el hash de la URL
    window.addEventListener('hashchange', () => {
      const hash = window.location.hash.substring(1);
      if (hash && hash !== this.currentRoute) {
        this.navigate(hash);
      }
    });
  }

  async navigate(routeName, options = {}) {
    try {
      const route = this.routes[routeName];
      
      if (!route) {
        console.warn(`Route '${routeName}' not found`);
        this.navigate('dashboard'); // Fallback
        return;
      }

      // Verificar autenticación si es requerida
      if (route.requiresAuth) {
        const isAuthenticated = await this.checkAuthentication();
        if (!isAuthenticated) {
          this.navigate('login');
          return;
        }
      }

      // Mostrar loading si es necesario
      if (options.showLoading) {
        this.showLoading();
      }

      // Obtener o crear componente
      const component = await this.getPageComponent(routeName, route.component);
      
      // Actualizar URL
      this.updateURL(routeName);
      
      // Renderizar página
      await this.renderPage(component, options);
      
      // Actualizar estado
      this.currentRoute = routeName;
      
      // Actualizar título
      this.updatePageTitle(route.title);
      
      // Ocultar loading
      if (options.showLoading) {
        this.hideLoading();
      }

      // Callback de navegación exitosa
      if (options.onNavigate) {
        options.onNavigate(routeName);
      }

      console.log(`Navigated to: ${routeName}`);

    } catch (error) {
      console.error('Navigation error:', error);
      this.showError('Error cargando la página: ' + error.message);
    }
  }

  async checkAuthentication() {
    try {
      const currentUser = await window.electronAPI.store.get('currentUser');
      return currentUser !== null;
    } catch (error) {
      console.warn('Authentication check failed:', error);
      return false;
    }
  }

  async getPageComponent(routeName, ComponentClass) {
    // Verificar cache
    if (this.pageCache.has(routeName)) {
      return this.pageCache.get(routeName);
    }

    // Crear nueva instancia del componente
    const component = new ComponentClass();
    this.pageCache.set(routeName, component);
    
    return component;
  }

  async renderPage(component, options = {}) {
    const pageContent = document.getElementById('page-content');
    
    if (!pageContent) {
      throw new Error('Page content container not found');
    }

    // Limpiar página anterior
    pageContent.innerHTML = '';

    // Renderizar componente
    if (typeof component.render === 'function') {
      pageContent.innerHTML = await component.render();
    } else {
      pageContent.innerHTML = component.html || '<div>No content</div>';
    }

    // Ejecutar scripts del componente
    if (typeof component.mount === 'function') {
      await component.mount();
    }

    // Agregar clase de animación
    pageContent.classList.add('fade-in');
    
    // Remover clase después de la animación
    setTimeout(() => {
      pageContent.classList.remove('fade-in');
    }, 300);
  }

  updateURL(routeName) {
    // Actualizar hash sin recargar página
    if (window.location.hash !== `#${routeName}`) {
      window.history.pushState({ route: routeName }, '', `#${routeName}`);
    }
  }

  updatePageTitle(title) {
    document.title = title ? `${title} - Banco Desktop` : 'Banco Desktop';
  }

  showLoading() {
    const loadingElement = document.createElement('div');
    loadingElement.id = 'page-loading';
    loadingElement.className = 'loading';
    loadingElement.innerHTML = `
      <div class="spinner"></div>
      <p>Cargando...</p>
    `;
    
    const pageContent = document.getElementById('page-content');
    if (pageContent) {
      pageContent.innerHTML = '';
      pageContent.appendChild(loadingElement);
    }
  }

  hideLoading() {
    const loadingElement = document.getElementById('page-loading');
    if (loadingElement) {
      loadingElement.remove();
    }
  }

  showError(message) {
    const pageContent = document.getElementById('page-content');
    if (pageContent) {
      pageContent.innerHTML = `
        <div class="error-state">
          <div class="error-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <h3>Error</h3>
          <p>${message}</p>
          <button class="btn btn-primary" onclick="window.bancoApp.getRouter().navigate('dashboard')">
            Volver al Dashboard
          </button>
        </div>
      `;
    }
  }

  goBack() {
    if (window.history.length > 1) {
      window.history.back();
    } else {
      this.navigate('dashboard');
    }
  }

  goForward() {
    if (window.history.length > 1) {
      window.history.forward();
    }
  }

  getCurrentRoute() {
    return this.currentRoute;
  }

  isCurrentRoute(routeName) {
    return this.currentRoute === routeName;
  }

  // Cache management
  clearCache() {
    this.pageCache.clear();
    console.log('Page cache cleared');
  }

  preloadPage(routeName) {
    const route = this.routes[routeName];
    if (route && !this.pageCache.has(routeName)) {
      this.getPageComponent(routeName, route.component)
        .then(component => {
          console.log(`Preloaded page: ${routeName}`);
        })
        .catch(error => {
          console.warn(`Failed to preload page ${routeName}:`, error);
        });
    }
  }

  // Métodos para navegación programática
  goToDashboard() {
    this.navigate('dashboard');
  }

  goToCuentas() {
    this.navigate('cuentas');
  }

  goToTransacciones() {
    this.navigate('transacciones');
  }

  goToPrestamos() {
    this.navigate('prestamos');
  }

  goToQRGenerator() {
    this.navigate('qr-generator');
  }

  goToLogin() {
    this.navigate('login');
  }
}

// Instancia global del router
window.router = new Router();

// Métodos de navegación rápida
window.navigateTo = (route) => window.router.navigate(route);
window.goToDashboard = () => window.router.goToDashboard();
window.goToCuentas = () => window.router.goToCuentas();
window.goToTransacciones = () => window.router.goToTransacciones();
window.goToPrestamos = () => window.router.goToPrestamos();
window.goToQRGenerator = () => window.router.goToQRGenerator();
window.goToLogin = () => window.router.goToLogin();

// Agregar estilos para estados de error
const routerStyles = `
  .error-state {
    text-align: center;
    padding: 60px 20px;
  }

  .error-icon {
    font-size: 48px;
    color: var(--error-color);
    margin-bottom: 20px;
  }

  .error-state h3 {
    font-size: 24px;
    margin-bottom: 12px;
    color: var(--text-primary);
  }

  .error-state p {
    color: var(--text-secondary);
    margin-bottom: 24px;
  }

  #page-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    color: var(--text-secondary);
  }

  #page-loading p {
    margin-top: 16px;
    font-size: 14px;
  }
`;

// Agregar estilos dinámicamente
const styleSheet = document.createElement('style');
styleSheet.textContent = routerStyles;
document.head.appendChild(styleSheet);
