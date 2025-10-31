const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const Store = require('electron-store');
const store = new Store();

// Importar configuraciones
const db = require('./config/database');
const rabbitmq = require('./config/rabbitmq');
const utils = require('./config/utils');
const os = require('os');
const { spawn } = require('child_process');

// Manejar cierre de aplicación
app.on('before-quit', async () => {
  console.log('Cerrando aplicación...');
  await rabbitmq.close();
  db.close();
});

class AppWindow {
  constructor() {
    this.mainWindow = null;
    this.init();
  }

  init() {
    app.whenReady().then(() => {
      this.createWindow();
      this.setupMenu();
      this.setupIPC();
    });

    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createWindow();
      }
    });
  }

  createWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 1000,
      minHeight: 700,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js'),
        webSecurity: true
      },
      icon: path.join(__dirname, '../assets/icon.png'),
      show: false,
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default'
    });

    // Mostrar ventana cuando esté lista
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow.show();
      
      // Abrir DevTools en modo desarrollo
      if (process.argv.includes('--dev')) {
        this.mainWindow.webContents.openDevTools();
      }
    });

    // Cargar la aplicación
    this.mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

    // Manejar cierre de ventana
    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });
  }

  setupMenu() {
    const template = [
      {
        label: 'Archivo',
        submenu: [
          {
            label: 'Nueva Cuenta',
            accelerator: 'CmdOrCtrl+N',
            click: () => {
              this.mainWindow.webContents.send('menu-new-account');
            }
          },
          {
            label: 'Nueva Transacción',
            accelerator: 'CmdOrCtrl+T',
            click: () => {
              this.mainWindow.webContents.send('menu-new-transaction');
            }
          },
          { type: 'separator' },
          {
            label: 'Salir',
            accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
            click: () => {
              app.quit();
            }
          }
        ]
      },
      {
        label: 'Ver',
        submenu: [
          { role: 'reload', label: 'Recargar' },
          { role: 'forceReload', label: 'Forzar Recarga' },
          { role: 'toggleDevTools', label: 'Herramientas de Desarrollo' },
          { type: 'separator' },
          { role: 'resetZoom', label: 'Zoom Real' },
          { role: 'zoomIn', label: 'Aumentar Zoom' },
          { role: 'zoomOut', label: 'Reducir Zoom' },
          { type: 'separator' },
          { role: 'togglefullscreen', label: 'Pantalla Completa' }
        ]
      },
      {
        label: 'Ventana',
        submenu: [
          { role: 'minimize', label: 'Minimizar' },
          { role: 'close', label: 'Cerrar' }
        ]
      },
      {
        label: 'Ayuda',
        submenu: [
          {
            label: 'Acerca de',
            click: () => {
              this.mainWindow.webContents.send('menu-about');
            }
          }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  setupIPC() {
    // IPC handlers para comunicación segura entre main y renderer
    
    ipcMain.handle('store:get', async (event, key) => {
      return store.get(key);
    });

    ipcMain.handle('store:set', async (event, key, value) => {
      store.set(key, value);
      return true;
    });

    ipcMain.handle('store:delete', async (event, key) => {
      store.delete(key);
      return true;
    });

    ipcMain.handle('app:quit', async () => {
      app.quit();
      return true;
    });

    ipcMain.handle('window:minimize', async () => {
      if (this.mainWindow) {
        this.mainWindow.minimize();
      }
      return true;
    });

    ipcMain.handle('window:maximize', async () => {
      if (this.mainWindow) {
        if (this.mainWindow.isMaximized()) {
          this.mainWindow.unmaximize();
        } else {
          this.mainWindow.maximize();
        }
      }
      return true;
    });

    // Database handlers
    ipcMain.handle('db:query', async (event, sql, params) => {
      try {
        return await db.query(sql, params);
      } catch (error) {
        return { error: error.message };
      }
    });

    ipcMain.handle('db:create', async (event, table, data) => {
      try {
        return await db.create(table, data);
      } catch (error) {
        return { error: error.message };
      }
    });

    ipcMain.handle('db:read', async (event, table, conditions) => {
      try {
        return await db.read(table, conditions);
      } catch (error) {
        return { error: error.message };
      }
    });

    ipcMain.handle('db:update', async (event, table, data, conditions) => {
      try {
        return await db.update(table, data, conditions);
      } catch (error) {
        return { error: error.message };
      }
    });

    ipcMain.handle('db:delete', async (event, table, conditions) => {
      try {
        return await db.delete(table, conditions);
      } catch (error) {
        return { error: error.message };
      }
    });

    // QR Code handler
    ipcMain.handle('qrcode:generate', async (event, text) => {
      return await utils.generateQRCode(text);
    });

    // HTTP handlers
    ipcMain.handle('http:get', async (event, url, config) => {
      return await utils.httpRequest('get', url, null, config);
    });

    ipcMain.handle('http:post', async (event, url, data, config) => {
      return await utils.httpRequest('post', url, data, config);
    });

    ipcMain.handle('http:put', async (event, url, data, config) => {
      return await utils.httpRequest('put', url, data, config);
    });

    ipcMain.handle('http:delete', async (event, url, config) => {
      return await utils.httpRequest('delete', url, null, config);
    });

    // PTY handlers
    const ptyProcesses = new Map();

    ipcMain.handle('pty:spawn', async (event, command, args, options) => {
      try {
        const child = spawn(command, args, {
          ...options,
          stdio: ['pipe', 'pipe', 'pipe']
        });

        const pid = child.pid;
        ptyProcesses.set(pid, child);

        child.stdout.on('data', (data) => {
          event.sender.send('pty:output', { pid, data: data.toString() });
        });

        child.stderr.on('data', (data) => {
          event.sender.send('pty:error', { pid, data: data.toString() });
        });

        child.on('close', (code) => {
          event.sender.send('pty:close', { pid, code });
          ptyProcesses.delete(pid);
        });

        return { success: true, pid };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });

    ipcMain.handle('pty:write', async (event, pid, data) => {
      const process = ptyProcesses.get(pid);
      if (process) {
        process.stdin.write(data);
        return { success: true };
      }
      return { success: false, error: 'Process not found' };
    });

    ipcMain.handle('pty:kill', async (event, pid) => {
      const process = ptyProcesses.get(pid);
      if (process) {
        process.kill();
        ptyProcesses.delete(pid);
        return { success: true };
      }
      return { success: false, error: 'Process not found' };
    });
  }
}

// Inicializar aplicación
new AppWindow();
