import { TransactionFlow, TransactionStep } from '../types/response.types';
import { dataAggregationService } from '../services/apiServices';

/**
 * Ejemplo de flujo de transacción completo: Proceso de Checkout
 */
export function createCheckoutFlow(checkoutData: any): TransactionFlow {
  return {
    id: `checkout_${Date.now()}`,
    name: 'Proceso de Checkout Completo',
    steps: [
      {
        id: 'validate_cart',
        name: 'Validar Carrito',
        action: async () => {
          // Simular validación del carrito
          await new Promise(resolve => setTimeout(resolve, 800));
          
          if (!checkoutData.items || checkoutData.items.length === 0) {
            throw new Error('El carrito está vacío');
          }

          const total = checkoutData.items.reduce((sum: number, item: any) => 
            sum + (item.price * item.quantity), 0
          );

          return { 
            validated: true, 
            total,
            itemCount: checkoutData.items.length 
          };
        }
      },
      {
        id: 'validate_user',
        name: 'Validar Información del Usuario',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 600));
          
          if (!checkoutData.user?.email) {
            throw new Error('Email del usuario es requerido');
          }

          return { 
            userValidated: true, 
            userId: checkoutData.user.id || 'temp_user' 
          };
        },
        dependencies: ['validate_cart']
      },
      {
        id: 'check_inventory',
        name: 'Verificar Inventario',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Simular verificación de inventario
          const inventoryStatus = checkoutData.items.map((item: any) => ({
            itemId: item.id,
            available: Math.random() > 0.1, // 90% de disponibilidad
            stockLevel: Math.floor(Math.random() * 100) + 1
          }));

          const unavailableItems = inventoryStatus.filter((item: any) => !item.available);
          if (unavailableItems.length > 0) {
            throw new Error(`Items no disponibles: ${unavailableItems.map((item: any) => item.itemId).join(', ')}`);
          }

          return { inventoryChecked: true, inventoryStatus };
        },
        dependencies: ['validate_cart']
      },
      {
        id: 'calculate_shipping',
        name: 'Calcular Envío',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 700));
          
          const shippingCost = checkoutData.shipping?.method === 'express' ? 15.99 : 5.99;
          const estimatedDays = checkoutData.shipping?.method === 'express' ? 1 : 5;

          return { 
            shippingCost, 
            estimatedDays,
            shippingAddress: checkoutData.shipping?.address 
          };
        },
        dependencies: ['validate_user']
      },
      {
        id: 'process_payment',
        name: 'Procesar Pago',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          // Simular procesamiento de pago
          const paymentSuccess = Math.random() > 0.05; // 95% de éxito
          
          if (!paymentSuccess) {
            throw new Error('Error procesando el pago. Tarjeta rechazada.');
          }

          const transactionId = `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          
          return { 
            paymentProcessed: true, 
            transactionId,
            amount: checkoutData.items.reduce((sum: number, item: any) => 
              sum + (item.price * item.quantity), 0
            ) + (checkoutData.shipping?.method === 'express' ? 15.99 : 5.99)
          };
        },
        rollback: async () => {
          // Rollback: reembolsar pago si falla algo después
          await new Promise(resolve => setTimeout(resolve, 500));
          console.log('Rollback: Procesando reembolso');
        },
        dependencies: ['calculate_shipping']
      },
      {
        id: 'create_order',
        name: 'Crear Orden',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 800));
          
          const orderId = `order_${Date.now()}`;
          const orderNumber = `ORD-${Date.now()}`;
          
          const order = {
            id: orderId,
            number: orderNumber,
            userId: results.validate_user.userId,
            items: checkoutData.items,
            total: results.process_payment.amount,
            shipping: {
              cost: results.calculate_shipping.shippingCost,
              address: results.calculate_shipping.shippingAddress,
              estimatedDays: results.calculate_shipping.estimatedDays
            },
            payment: {
              transactionId: results.process_payment.transactionId,
              amount: results.process_payment.amount
            },
            status: 'confirmed',
            createdAt: new Date().toISOString()
          };

          return { orderCreated: true, order };
        },
        rollback: async (results: any) => {
          // Rollback: cancelar orden si falla algo después
          if (results.create_order?.order) {
            await new Promise(resolve => setTimeout(resolve, 300));
            console.log(`Rollback: Cancelando orden ${results.create_order.order.id}`);
          }
        },
        dependencies: ['process_payment']
      },
      {
        id: 'update_inventory',
        name: 'Actualizar Inventario',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 600));
          
          const inventoryUpdates = checkoutData.items.map((item: any) => ({
            itemId: item.id,
            quantityReserved: item.quantity,
            newStockLevel: Math.floor(Math.random() * 100) // Simular nuevo stock
          }));

          return { inventoryUpdated: true, inventoryUpdates };
        },
        rollback: async (results: any) => {
          // Rollback: restaurar inventario
          if (results.update_inventory?.inventoryUpdates) {
            await new Promise(resolve => setTimeout(resolve, 300));
            console.log('Rollback: Restaurando inventario');
          }
        },
        dependencies: ['create_order']
      },
      {
        id: 'send_confirmation',
        name: 'Enviar Confirmación',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          const order = results.create_order.order;
          
          // Simular envío de emails
          const emailConfirmation = {
            to: checkoutData.user.email,
            subject: `Confirmación de Orden ${order.number}`,
            orderId: order.id,
            sent: true
          };

          const smsConfirmation = {
            to: checkoutData.user.phone,
            message: `Orden ${order.number} confirmada. Total: $${order.total.toFixed(2)}`,
            sent: true
          };

          return { 
            confirmationsSent: true, 
            emailConfirmation,
            smsConfirmation 
          };
        },
        dependencies: ['update_inventory']
      },
      {
        id: 'analytics',
        name: 'Registrar Analytics',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 400));
          
          const analytics = {
            event: 'purchase_completed',
            orderId: results.create_order.order.id,
            totalValue: results.create_order.order.total,
            itemsCount: checkoutData.items.length,
            userId: results.validate_user.userId,
            timestamp: Date.now()
          };

          return { analyticsRecorded: true, analytics };
        },
        dependencies: ['send_confirmation']
      }
    ],
    currentStep: 0,
    status: 'pending',
    createdAt: Date.now(),
    updatedAt: Date.now()
  };
}

/**
 * Ejemplo de flujo de registro de usuario completo
 */
export function createUserRegistrationFlow(userData: any): TransactionFlow {
  return {
    id: `registration_${Date.now()}`,
    name: 'Registro Completo de Usuario',
    steps: [
      {
        id: 'validate_user_data',
        name: 'Validar Datos del Usuario',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 600));
          
          const validationErrors = [];
          
          if (!userData.email || !userData.email.includes('@')) {
            validationErrors.push('Email inválido');
          }
          
          if (!userData.password || userData.password.length < 6) {
            validationErrors.push('La contraseña debe tener al menos 6 caracteres');
          }
          
          if (!userData.name || userData.name.length < 2) {
            validationErrors.push('El nombre debe tener al menos 2 caracteres');
          }

          if (validationErrors.length > 0) {
            throw new Error(`Errores de validación: ${validationErrors.join(', ')}`);
          }

          return { dataValidated: true, validationErrors };
        }
      },
      {
        id: 'check_email_exists',
        name: 'Verificar si el Email ya Existe',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 800));
          
          // Simular verificación en base de datos
          const emailExists = Math.random() > 0.8; // 20% de probabilidad de que exista
          
          if (emailExists) {
            throw new Error('El email ya está registrado');
          }

          return { emailAvailable: true };
        },
        dependencies: ['validate_user_data']
      },
      {
        id: 'create_user_account',
        name: 'Crear Cuenta de Usuario',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 1200));
          
          // En un caso real, aquí se crearía el usuario en la base de datos
          const user = {
            id: `user_${Date.now()}`,
            email: userData.email,
            name: userData.name,
            createdAt: new Date().toISOString(),
            emailVerified: false,
            status: 'active'
          };

          return { userCreated: true, user };
        },
        rollback: async () => {
          // Rollback: eliminar usuario creado
          await new Promise(resolve => setTimeout(resolve, 500));
          console.log('Rollback: Eliminando cuenta de usuario');
        },
        dependencies: ['check_email_exists']
      },
      {
        id: 'send_verification_email',
        name: 'Enviar Email de Verificación',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          const verificationToken = `verify_${Math.random().toString(36).substr(2, 16)}`;
          
          const emailData = {
            to: userData.email,
            subject: 'Verifica tu cuenta',
            verificationToken,
            userId: results.create_user_account.user.id,
            sent: true
          };

          return { verificationEmailSent: true, emailData };
        },
        dependencies: ['create_user_account']
      },
      {
        id: 'setup_user_preferences',
        name: 'Configurar Preferencias',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 600));
          
          const defaultPreferences = {
            theme: 'light',
            language: 'es',
            notifications: {
              email: true,
              sms: false,
              push: true
            },
            privacy: {
              profileVisible: true,
              activityVisible: false
            }
          };

          return { preferencesSetup: true, defaultPreferences };
        },
        dependencies: ['create_user_account']
      },
      {
        id: 'welcome_sequence',
        name: 'Secuencia de Bienvenida',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 1500));
          
          const welcomeEmails = [
            {
              type: 'welcome',
              subject: '¡Bienvenido a nuestra plataforma!',
              scheduled: true
            },
            {
              type: 'getting_started',
              subject: 'Primeros pasos en nuestra plataforma',
              scheduled: true
            },
            {
              type: 'tips',
              subject: 'Consejos para aprovechar al máximo la plataforma',
              scheduled: true
            }
          ];

          return { welcomeSequenceSetup: true, welcomeEmails };
        },
        dependencies: ['setup_user_preferences']
      },
      {
        id: 'analytics_setup',
        name: 'Configurar Analytics de Usuario',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 400));
          
          const analyticsProfile = {
            userId: results.create_user_account.user.id,
            registrationSource: userData.source || 'direct',
            referrer: document.referrer || 'direct',
            timestamp: Date.now(),
            trackingEnabled: true
          };

          return { analyticsConfigured: true, analyticsProfile };
        },
        dependencies: ['welcome_sequence']
      },
      {
        id: 'complete_registration',
        name: 'Completar Registro',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 300));
          
          return {
            registrationComplete: true,
            user: results.create_user_account.user,
            verificationToken: results.send_verification_email.emailData.verificationToken,
            message: 'Usuario registrado exitosamente. Revisa tu email para verificar tu cuenta.'
          };
        },
        dependencies: ['analytics_setup']
      }
    ],
    currentStep: 0,
    status: 'pending',
    createdAt: Date.now(),
    updatedAt: Date.now()
  };
}

/**
 * Ejemplo de flujo de sincronización de datos
 */
export function createDataSyncFlow(syncConfig: any): TransactionFlow {
  return {
    id: `datasync_${Date.now()}`,
    name: 'Sincronización de Datos',
    steps: [
      {
        id: 'connect_sources',
        name: 'Conectar Fuentes de Datos',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          const sources = [
            { id: 'api_users', type: 'rest_api', status: 'connected' },
            { id: 'db_orders', type: 'database', status: 'connected' },
            { id: 'file_storage', type: 'filesystem', status: 'connected' }
          ];

          return { sourcesConnected: true, sources };
        }
      },
      {
        id: 'fetch_remote_data',
        name: 'Obtener Datos Remotos',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          const remoteData = {
            users: Array.from({ length: 100 }, (_, i) => ({
              id: `remote_user_${i}`,
              name: `Usuario ${i}`,
              email: `user${i}@example.com`
            })),
            orders: Array.from({ length: 250 }, (_, i) => ({
              id: `remote_order_${i}`,
              userId: `remote_user_${i % 50}`,
              amount: Math.random() * 1000,
              status: 'completed'
            }))
          };

          return { remoteDataFetched: true, remoteData };
        },
        dependencies: ['connect_sources']
      },
      {
        id: 'fetch_local_data',
        name: 'Obtener Datos Locales',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 800));
          
          const localData = {
            users: Array.from({ length: 75 }, (_, i) => ({
              id: `local_user_${i}`,
              name: `Usuario Local ${i}`,
              email: `local${i}@example.com`
            })),
            orders: Array.from({ length: 180 }, (_, i) => ({
              id: `local_order_${i}`,
              userId: `local_user_${i % 40}`,
              amount: Math.random() * 800,
              status: 'pending'
            }))
          };

          return { localDataFetched: true, localData };
        },
        dependencies: ['connect_sources']
      },
      {
        id: 'compare_and_merge',
        name: 'Comparar y Fusionar Datos',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 1500));
          
          const { remoteData, localData } = results;
          
          // Simular comparación y fusión
          const mergedData = {
            users: [
              ...remoteData.users,
              ...localData.users.filter((localUser: any) => 
                !remoteData.users.some((remoteUser: any) => remoteUser.id === localUser.id)
              )
            ],
            orders: [
              ...remoteData.orders,
              ...localData.orders.filter((localOrder: any) => 
                !remoteData.orders.some((remoteOrder: any) => remoteOrder.id === localOrder.id)
              )
            ]
          };

          const syncStats = {
            usersMerged: mergedData.users.length,
            ordersMerged: mergedData.orders.length,
            conflicts: 5, // Simular algunos conflictos
            newRecords: 25
          };

          return { dataMerged: true, mergedData, syncStats };
        },
        dependencies: ['fetch_remote_data', 'fetch_local_data']
      },
      {
        id: 'resolve_conflicts',
        name: 'Resolver Conflictos',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          const conflicts = [
            { type: 'user_email', resolved: true, resolution: 'keep_remote' },
            { type: 'order_status', resolved: true, resolution: 'keep_local' },
            { type: 'user_name', resolved: true, resolution: 'merge' }
          ];

          return { conflictsResolved: true, conflicts };
        },
        dependencies: ['compare_and_merge']
      },
      {
        id: 'validate_sync',
        name: 'Validar Sincronización',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 600));
          
          const validation = {
            dataIntegrity: 'valid',
            referentialIntegrity: 'valid',
            businessRules: 'valid',
            conflictsResolved: results.conflictsResolved.conflicts.every((c: any) => c.resolved)
          };

          const isValid = Object.values(validation).every(v => v === 'valid');

          if (!isValid) {
            throw new Error('Error en la validación de sincronización');
          }

          return { syncValidated: true, validation };
        },
        dependencies: ['resolve_conflicts']
      },
      {
        id: 'save_merged_data',
        name: 'Guardar Datos Fusionados',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 1200));
          
          const saveResults = {
            usersSaved: results.compare_and_merge.mergedData.users.length,
            ordersSaved: results.compare_and_merge.mergedData.orders.length,
            backupCreated: true,
            transactionId: `sync_${Date.now()}`
          };

          return { dataSaved: true, saveResults };
        },
        rollback: async (results: any) => {
          // Rollback: restaurar desde backup
          if (results.save_merged_data?.saveResults?.backupCreated) {
            await new Promise(resolve => setTimeout(resolve, 800));
            console.log('Rollback: Restaurando desde backup');
          }
        },
        dependencies: ['validate_sync']
      },
      {
        id: 'update_sync_log',
        name: 'Actualizar Log de Sincronización',
        action: async (results: any) => {
          await new Promise(resolve => setTimeout(resolve, 400));
          
          const syncLog = {
            syncId: results.save_merged_data.saveResults.transactionId,
            timestamp: new Date().toISOString(),
            status: 'completed',
            statistics: results.compare_and_merge.syncStats,
            conflicts: results.resolve_conflicts.conflicts.length,
            duration: Date.now() - syncConfig.startTime
          };

          return { logUpdated: true, syncLog };
        },
        dependencies: ['save_merged_data']
      }
    ],
    currentStep: 0,
    status: 'pending',
    createdAt: Date.now(),
    updatedAt: Date.now()
  };
}