import React, { useState } from 'react';
import { useTransactionFlow, useNotification } from '../hooks/useAsyncManager';
import { TransactionFlow, TransactionStep } from '../types/response.types';

export const TransactionFlowDemo: React.FC = () => {
  const [selectedFlow, setSelectedFlow] = useState<string>('simple');
  const {
    executing,
    progress,
    currentStep,
    error,
    result,
    startFlow,
    cancelFlow
  } = useTransactionFlow({
    showProgress: true,
    onComplete: (data) => {
      console.log('Transacción completada:', data);
    },
    onError: (errorMsg) => {
      console.error('Error en transacción:', errorMsg);
    }
  });

  const { success, error: showError, info } = useNotification();

  // Crear diferentes tipos de flujos
  const createSimpleFlow = (): TransactionFlow => ({
    id: `simple_${Date.now()}`,
    name: 'Flujo Simple',
    steps: [
      {
        id: 'init',
        name: 'Inicialización',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          return { initialized: true };
        }
      },
      {
        id: 'process',
        name: 'Procesamiento',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 2000));
          return { processed: true };
        },
        dependencies: ['init']
      },
      {
        id: 'complete',
        name: 'Finalización',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 500));
          return { completed: true };
        },
        dependencies: ['process']
      }
    ],
    currentStep: 0,
    status: 'pending',
    createdAt: Date.now(),
    updatedAt: Date.now()
  });

  const createComplexFlow = (): TransactionFlow => ({
    id: `complex_${Date.now()}`,
    name: 'Flujo Complejo con Rollback',
    steps: [
      {
        id: 'validate',
        name: 'Validación de Datos',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 800));
          // Simular validación que puede fallar
          if (Math.random() > 0.7) {
            throw new Error('Validación falló');
          }
          return { validated: true };
        }
      },
      {
        id: 'create_user',
        name: 'Crear Usuario',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 1500));
          return { userCreated: true, userId: 'user_123' };
        },
        rollback: async () => {
          await new Promise(resolve => setTimeout(resolve, 500));
          console.log('Rollback: Usuario removido');
        },
        dependencies: ['validate']
      },
      {
        id: 'send_email',
        name: 'Enviar Email de Bienvenida',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          return { emailSent: true };
        },
        rollback: async () => {
          await new Promise(resolve => setTimeout(resolve, 300));
          console.log('Rollback: Email cancelado');
        },
        dependencies: ['create_user']
      },
      {
        id: 'setup_profile',
        name: 'Configurar Perfil (Opcional)',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 1200));
          return { profileSetup: true };
        },
        dependencies: ['create_user']
      }
    ],
    currentStep: 0,
    status: 'pending',
    createdAt: Date.now(),
    updatedAt: Date.now()
  });

  const createParallelFlow = (): TransactionFlow => ({
    id: `parallel_${Date.now()}`,
    name: 'Flujo con Pasos Paralelos',
    steps: [
      {
        id: 'prepare',
        name: 'Preparación',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          return { prepared: true };
        }
      },
      {
        id: 'fetch_user',
        name: 'Obtener Datos de Usuario',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 1500));
          return { userData: { id: 1, name: 'Usuario Ejemplo' } };
        },
        dependencies: ['prepare']
      },
      {
        id: 'fetch_settings',
        name: 'Obtener Configuraciones',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 1200));
          return { settings: { theme: 'dark', language: 'es' } };
        },
        dependencies: ['prepare']
      },
      {
        id: 'combine_data',
        name: 'Combinar Datos',
        action: async () => {
          await new Promise(resolve => setTimeout(resolve, 800));
          return { combined: true };
        },
        dependencies: ['fetch_user', 'fetch_settings']
      }
    ],
    currentStep: 0,
    status: 'pending',
    createdAt: Date.now(),
    updatedAt: Date.now()
  });

  const getSelectedFlow = (): TransactionFlow => {
    switch (selectedFlow) {
      case 'simple':
        return createSimpleFlow();
      case 'complex':
        return createComplexFlow();
      case 'parallel':
        return createParallelFlow();
      default:
        return createSimpleFlow();
    }
  };

  const executeFlow = async () => {
    const flow = getSelectedFlow();
    info('Iniciando Transacción', `Ejecutando: ${flow.name}`);
    await startFlow(flow);
  };

  const executeWithSimulatedError = async () => {
    const flow: TransactionFlow = {
      id: `error_${Date.now()}`,
      name: 'Flujo con Error Simulado',
      steps: [
        {
          id: 'start',
          name: 'Inicio',
          action: async () => {
            await new Promise(resolve => setTimeout(resolve, 500));
            return { started: true };
          }
        },
        {
          id: 'fail',
          name: 'Paso que Falla',
          action: async () => {
            await new Promise(resolve => setTimeout(resolve, 1000));
            throw new Error('Error simulado en la transacción');
          },
          dependencies: ['start']
        },
        {
          id: 'never_reach',
          name: 'Este paso nunca se ejecutará',
          action: async () => {
            return { unreachable: true };
          },
          dependencies: ['fail']
        }
      ],
      currentStep: 0,
      status: 'pending',
      createdAt: Date.now(),
      updatedAt: Date.now()
    };

    await startFlow(flow);
  };

  return (
    <div className="transaction-flow-demo p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Demo de Flujos de Transacción</h2>

      {/* Selector de flujo */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">Seleccionar Tipo de Flujo</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => setSelectedFlow('simple')}
            className={`p-3 rounded-lg border-2 transition-colors ${
              selectedFlow === 'simple'
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <h4 className="font-semibold">Flujo Simple</h4>
            <p className="text-sm text-gray-600 mt-1">
              Secuencia básica de pasos
            </p>
          </button>

          <button
            onClick={() => setSelectedFlow('complex')}
            className={`p-3 rounded-lg border-2 transition-colors ${
              selectedFlow === 'complex'
                ? 'border-orange-500 bg-orange-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <h4 className="font-semibold">Flujo Complejo</h4>
            <p className="text-sm text-gray-600 mt-1">
              Con rollback y validaciones
            </p>
          </button>

          <button
            onClick={() => setSelectedFlow('parallel')}
            className={`p-3 rounded-lg border-2 transition-colors ${
              selectedFlow === 'parallel'
                ? 'border-purple-500 bg-purple-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <h4 className="font-semibold">Flujo Paralelo</h4>
            <p className="text-sm text-gray-600 mt-1">
              Pasos con dependencias paralelas
            </p>
          </button>
        </div>
      </div>

      {/* Información del flujo seleccionado */}
      <div className="bg-gray-50 p-4 rounded-lg mb-6">
        <h4 className="font-semibold mb-2">Flujo Seleccionado:</h4>
        <p className="text-gray-700">{getSelectedFlow().name}</p>
        <p className="text-sm text-gray-600 mt-1">
          {getSelectedFlow().steps.length} pasos
        </p>
      </div>

      {/* Botones de acción */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={executeFlow}
          disabled={executing}
          className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50"
        >
          {executing ? 'Ejecutando...' : 'Ejecutar Flujo'}
        </button>

        <button
          onClick={executeWithSimulatedError}
          disabled={executing}
          className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 disabled:opacity-50"
        >
          Ejecutar con Error
        </button>

        {executing && (
          <button
            onClick={cancelFlow}
            className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
          >
            Cancelar
          </button>
        )}
      </div>

      {/* Estado de ejecución */}
      {executing && (
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg mb-6">
          <h4 className="font-semibold text-blue-800 mb-3">Ejecutando Transacción</h4>
          
          {/* Barra de progreso */}
          <div className="mb-3">
            <div className="flex justify-between text-sm text-blue-600 mb-1">
              <span>Progreso</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Paso actual */}
          {currentStep && (
            <div className="text-blue-700">
              <span className="font-medium">Paso actual:</span> {currentStep}
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-lg mb-6">
          <h4 className="font-semibold text-red-800">Error en Transacción</h4>
          <p className="text-red-600">{error}</p>
          <p className="text-sm text-red-500 mt-1">
            El sistema intentará hacer rollback automáticamente
          </p>
        </div>
      )}

      {/* Resultado */}
      {result && (
        <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
          <h4 className="font-semibold text-green-800 mb-2">Transacción Completada</h4>
          <p className="text-green-600 mb-3">El flujo se ejecutó exitosamente</p>
          
          <details className="mt-3">
            <summary className="cursor-pointer text-green-700 font-medium">
              Ver resultado detallado
            </summary>
            <pre className="text-sm bg-white p-3 rounded border mt-2 overflow-auto max-h-40">
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
};

export default TransactionFlowDemo;