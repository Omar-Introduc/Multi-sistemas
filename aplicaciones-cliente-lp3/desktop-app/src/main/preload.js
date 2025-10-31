const { contextBridge, ipcRenderer } = require('electron');

// API expuesta de forma segura al renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // Store management
  store: {
    get: (key) => ipcRenderer.invoke('store:get', key),
    set: (key, value) => ipcRenderer.invoke('store:set', key, value),
    delete: (key) => ipcRenderer.invoke('store:delete', key)
  },

  // Window controls
  window: {
    quit: () => ipcRenderer.invoke('app:quit'),
    minimize: () => ipcRenderer.invoke('window:minimize'),
    maximize: () => ipcRenderer.invoke('window:maximize')
  },

  // Menu events
  menu: {
    onNewAccount: (callback) => ipcRenderer.on('menu-new-account', callback),
    onNewTransaction: (callback) => ipcRenderer.on('menu-new-transaction', callback),
    onAbout: (callback) => ipcRenderer.on('menu-about', callback),
    removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
  },

  // Database operations
  database: {
    init: () => ipcRenderer.invoke('db:init'),
    query: (sql, params) => ipcRenderer.invoke('db:query', sql, params),
    create: (table, data) => ipcRenderer.invoke('db:create', table, data),
    read: (table, conditions) => ipcRenderer.invoke('db:read', table, conditions),
    update: (table, data, conditions) => ipcRenderer.invoke('db:update', table, data, conditions),
    delete: (table, conditions) => ipcRenderer.invoke('db:delete', table, conditions)
  },

  // RabbitMQ operations
  rabbitmq: {
    connect: (config) => ipcRenderer.invoke('rabbitmq:connect', config),
    publish: (exchange, routingKey, message) => ipcRenderer.invoke('rabbitmq:publish', exchange, routingKey, message),
    subscribe: (queue, callback) => ipcRenderer.invoke('rabbitmq:subscribe', queue, callback)
  },

  // QR Code generation
  qrcode: {
    generate: (text) => ipcRenderer.invoke('qrcode:generate', text)
  },

  // HTTP requests
  http: {
    get: (url, config) => ipcRenderer.invoke('http:get', url, config),
    post: (url, data, config) => ipcRenderer.invoke('http:post', url, data, config),
    put: (url, data, config) => ipcRenderer.invoke('http:put', url, data, config),
    delete: (url, config) => ipcRenderer.invoke('http:delete', url, config)
  },

  // PTY (pseudo-terminal)
  pty: {
    spawn: (command, args, options) => ipcRenderer.invoke('pty:spawn', command, args, options),
    write: (pid, data) => ipcRenderer.invoke('pty:write', pid, data),
    kill: (pid) => ipcRenderer.invoke('pty:kill', pid)
  }
});

// Hacer disponible window.electronAPI en el contexto del renderer
window.electronAPI = window.electronAPI || {};
