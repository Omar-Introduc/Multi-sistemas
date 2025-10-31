import React, { useState } from 'react';
import { useNotification } from '../hooks/useAsyncManager';

export const NotificationSystemDemo: React.FC = () => {
  const { 
    notifications, 
    success, 
    error, 
    warning, 
    info, 
    hide, 
    hideAll, 
    clear 
  } = useNotification();

  const [customTitle, setCustomTitle] = useState('');
  const [customMessage, setCustomMessage] = useState('');
  const [notificationType, setNotificationType] = useState<'success' | 'error' | 'warning' | 'info'>('info');

  const showNotification = () => {
    const config = {
      duration: 3000,
      persistent: false
    };

    switch (notificationType) {
      case 'success':
        success(customTitle || 'Éxito', customMessage || 'Operación completada correctamente', config);
        break;
      case 'error':
        error(customTitle || 'Error', customMessage || 'Ha ocurrido un error', { ...config, persistent: true });
        break;
      case 'warning':
        warning(customTitle || 'Advertencia', customMessage || 'Atención requerida', config);
        break;
      case 'info':
        info(customTitle || 'Información', customMessage || 'Mensaje informativo', config);
        break;
    }

    setCustomTitle('');
    setCustomMessage('');
  };

  const showBatchNotifications = () => {
    const batch = [
      { type: 'success', title: 'Lote 1', message: 'Primera notificación del lote' },
      { type: 'info', title: 'Lote 2', message: 'Segunda notificación del lote' },
      { type: 'warning', title: 'Lote 3', message: 'Tercera notificación del lote' },
      { type: 'success', title: 'Lote 4', message: 'Cuarta notificación del lote' }
    ];

    batch.forEach((notif, index) => {
      setTimeout(() => {
        switch (notif.type) {
          case 'success':
            success(notif.title, notif.message);
            break;
          case 'error':
            error(notif.title, notif.message);
            break;
          case 'warning':
            warning(notif.title, notif.message);
            break;
          case 'info':
            info(notif.title, notif.message);
            break;
        }
      }, index * 500);
    });
  };

  const showNotificationWithActions = () => {
    const notificationId = info(
      'Actualización Disponible',
      'Hay una nueva versión disponible. ¿Deseas actualizar ahora?',
      {
        persistent: true,
        actions: [
          {
            label: 'Actualizar',
            action: () => {
              info('Actualizando...', 'Descargando la nueva versión...');
              setTimeout(() => {
                success('Actualización Completa', 'La aplicación ha sido actualizada exitosamente');
              }, 2000);
            }
          },
          {
            label: 'Más Tarde',
            action: () => {
              info('Actualización Diferida', 'Te recordaremos más tarde');
            }
          }
        ]
      }
    );

    return notificationId;
  };

  const showProgressNotification = () => {
    let progress = 0;
    const notificationId = info('Procesando', 'Iniciando proceso...', { persistent: true });

    const interval = setInterval(() => {
      progress += 10;
      
      if (progress <= 100) {
        // Actualizar progreso (esto requeriría una función update en el sistema)
        // notificationSystem.update(notificationId, {
        //   message: `Procesando... (${progress}%)`
        // });
      } else {
        clearInterval(interval);
        success('Proceso Completado', 'Todas las operaciones se completaron exitosamente');
        hide(notificationId);
      }
    }, 500);
  };

  const showTemplateNotifications = () => {
    // Simular diferentes tipos de errores
    const templates = [
      { template: 'apiError', data: {} },
      { template: 'operationSuccess', data: {} },
      { template: 'progressUpdate', data: {} },
      { template: 'updateAvailable', data: {} }
    ];

    templates.forEach((template, index) => {
      setTimeout(() => {
        switch (template.template) {
          case 'apiError':
            error('Error de Conexión', 'No se pudo conectar con el servidor');
            break;
          case 'operationSuccess':
            success('Operación Exitosa', 'La operación se completó correctamente');
            break;
          case 'progressUpdate':
            info('Procesando...', 'Por favor espera mientras procesamos tu solicitud');
            break;
          case 'updateAvailable':
            info('Actualización Disponible', 'Una nueva versión está disponible');
            break;
        }
      }, index * 1000);
    });
  };

  return (
    <div className="notification-system-demo p-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Demo del Sistema de Notificaciones</h2>

      {/* Estadísticas */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-green-50 p-3 rounded-lg text-center">
          <div className="text-2xl font-bold text-green-600">
            {notifications.filter(n => n.type === 'success').length}
          </div>
          <div className="text-sm text-green-700">Éxito</div>
        </div>
        <div className="bg-red-50 p-3 rounded-lg text-center">
          <div className="text-2xl font-bold text-red-600">
            {notifications.filter(n => n.type === 'error').length}
          </div>
          <div className="text-sm text-red-700">Error</div>
        </div>
        <div className="bg-yellow-50 p-3 rounded-lg text-center">
          <div className="text-2xl font-bold text-yellow-600">
            {notifications.filter(n => n.type === 'warning').length}
          </div>
          <div className="text-sm text-yellow-700">Advertencia</div>
        </div>
        <div className="bg-blue-50 p-3 rounded-lg text-center">
          <div className="text-2xl font-bold text-blue-600">
            {notifications.filter(n => n.type === 'info').length}
          </div>
          <div className="text-sm text-blue-700">Info</div>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg text-center">
          <div className="text-2xl font-bold text-gray-600">{notifications.length}</div>
          <div className="text-sm text-gray-700">Total</div>
        </div>
      </div>

      {/* Notificaciones activas */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">Notificaciones Activas ({notifications.length})</h3>
        
        {notifications.length === 0 ? (
          <p className="text-gray-500 italic">No hay notificaciones activas</p>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {notifications.map(notification => (
              <div
                key={notification.id}
                className={`p-3 rounded-lg border-l-4 ${
                  notification.type === 'success' ? 'bg-green-50 border-green-500' :
                  notification.type === 'error' ? 'bg-red-50 border-red-500' :
                  notification.type === 'warning' ? 'bg-yellow-50 border-yellow-500' :
                  'bg-blue-50 border-blue-500'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-medium">{notification.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                    {notification.actions && (
                      <div className="flex gap-2 mt-2">
                        {notification.actions.map((action: any, index: number) => (
                          <button
                            key={index}
                            onClick={() => action.action()}
                            className="px-2 py-1 text-xs bg-white border rounded hover:bg-gray-50"
                          >
                            {action.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => hide(notification.id)}
                    className="text-gray-400 hover:text-gray-600 ml-2"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Configuración personalizada */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">Notificación Personalizada</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-2">Título:</label>
            <input
              type="text"
              value={customTitle}
              onChange={(e) => setCustomTitle(e.target.value)}
              placeholder="Ingresa el título"
              className="w-full p-2 border rounded-md"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Tipo:</label>
            <select
              value={notificationType}
              onChange={(e) => setNotificationType(e.target.value as any)}
              className="w-full p-2 border rounded-md"
            >
              <option value="success">Éxito</option>
              <option value="error">Error</option>
              <option value="warning">Advertencia</option>
              <option value="info">Información</option>
            </select>
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Mensaje:</label>
          <textarea
            value={customMessage}
            onChange={(e) => setCustomMessage(e.target.value)}
            placeholder="Ingresa el mensaje"
            rows={3}
            className="w-full p-2 border rounded-md"
          />
        </div>

        <button
          onClick={showNotification}
          className={`px-4 py-2 text-white rounded-md ${
            notificationType === 'success' ? 'bg-green-500 hover:bg-green-600' :
            notificationType === 'error' ? 'bg-red-500 hover:bg-red-600' :
            notificationType === 'warning' ? 'bg-yellow-500 hover:bg-yellow-600' :
            'bg-blue-500 hover:bg-blue-600'
          }`}
        >
          Mostrar Notificación
        </button>
      </div>

      {/* Ejemplos predefinidos */}
      <div className="bg-white p-4 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Ejemplos Predefinidos</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={showBatchNotifications}
            className="px-4 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600"
          >
            Lote de Notificaciones
          </button>
          
          <button
            onClick={showNotificationWithActions}
            className="px-4 py-2 bg-indigo-500 text-white rounded-md hover:bg-indigo-600"
          >
            Notificación con Acciones
          </button>
          
          <button
            onClick={showProgressNotification}
            className="px-4 py-2 bg-teal-500 text-white rounded-md hover:bg-teal-600"
          >
            Notificación de Progreso
          </button>
          
          <button
            onClick={showTemplateNotifications}
            className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
          >
            Templates Predefinidos
          </button>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={hideAll}
            className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
          >
            Ocultar Todas
          </button>
          
          <button
            onClick={() => clear('success')}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Limpiar Éxitos
          </button>
          
          <button
            onClick={() => clear('error')}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Limpiar Errores
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotificationSystemDemo;