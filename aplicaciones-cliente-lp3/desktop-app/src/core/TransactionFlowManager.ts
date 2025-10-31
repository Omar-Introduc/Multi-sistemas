import { EventEmitter } from 'events';
import {
  TransactionFlow,
  TransactionStep,
  ApiResponse,
  ProgressInfo
} from '../types/response.types';

export interface FlowOptions {
  timeout?: number;
  parallel?: boolean;
  rollbackOnError?: boolean;
  autoCleanup?: boolean;
}

export interface FlowExecutionContext {
  flowId: string;
  currentStep: number;
  totalSteps: number;
  results: Map<string, any>;
  errors: Map<string, Error>;
  startTime: number;
  options: FlowOptions;
}

export class TransactionFlowManager extends EventEmitter {
  private static instance: TransactionFlowManager;
  private activeFlows: Map<string, FlowExecutionContext> = new Map();
  private completedFlows: TransactionFlow[] = [];
  private maxCompletedFlows = 100;

  private constructor() {
    super();
  }

  public static getInstance(): TransactionFlowManager {
    if (!TransactionFlowManager.instance) {
      TransactionFlowManager.instance = new TransactionFlowManager();
    }
    return TransactionFlowManager.instance;
  }

  /**
   * Ejecuta un flujo de transacción completo
   */
  public async executeFlow(
    flow: TransactionFlow,
    options: FlowOptions = {}
  ): Promise<ApiResponse> {
    const flowId = flow.id;
    const startTime = Date.now();

    // Validar flujo
    this.validateFlow(flow);

    // Crear contexto de ejecución
    const context: FlowExecutionContext = {
      flowId,
      currentStep: 0,
      totalSteps: flow.steps.length,
      results: new Map(),
      errors: new Map(),
      startTime,
      options: {
        timeout: 300000, // 5 minutos por defecto
        parallel: false,
        rollbackOnError: true,
        autoCleanup: true,
        ...options
      }
    };

    // Actualizar estado del flujo
    this.updateFlowStatus(flow, 'running', context);

    try {
      this.activeFlows.set(flowId, context);
      this.emit('flow:started', { flow, context });

      // Ejecutar pasos del flujo
      const results = await this.executeSteps(flow, context);

      // Actualizar estado a completado
      this.updateFlowStatus(flow, 'completed', context);
      flow.result = results;
      flow.updatedAt = Date.now();

      // Agregar a flujos completados
      this.completedFlows.push(flow);
      this.maintainHistoryLimit();

      // Emitir eventos finales
      this.emit('flow:completed', { flow, context, results, duration: Date.now() - startTime });

      return {
        success: true,
        data: results,
        message: `Flujo '${flow.name}' completado exitosamente`,
        timestamp: Date.now(),
        requestId: flowId
      };

    } catch (error) {
      // Actualizar estado a fallido
      this.updateFlowStatus(flow, 'failed', context);
      flow.error = error instanceof Error ? error.message : 'Error desconocido';
      flow.updatedAt = Date.now();

      // Intentar rollback si está configurado
      if (context.options.rollbackOnError) {
        await this.rollbackFlow(flow, context);
      }

      // Emitir evento de error
      this.emit('flow:failed', { 
        flow, 
        context, 
        error, 
        duration: Date.now() - startTime 
      });

      return {
        success: false,
        error: flow.error,
        timestamp: Date.now(),
        requestId: flowId
      };

    } finally {
      // Limpiar flujo activo
      this.activeFlows.delete(flowId);

      // Auto-cleanup si está habilitado
      if (context.options.autoCleanup) {
        setTimeout(() => {
          this.cleanupFlow(flowId);
        }, 300000); // 5 minutos después
      }
    }
  }

  /**
   * Ejecuta los pasos del flujo
   */
  private async executeSteps(flow: TransactionFlow, context: FlowExecutionContext): Promise<any> {
    const results: any = {};

    for (let i = 0; i < flow.steps.length; i++) {
      const step = flow.steps[i];
      context.currentStep = i;

      // Actualizar progreso
      this.updateFlowProgress(flow, context);

      // Verificar dependencias
      await this.checkDependencies(step, context);

      try {
        // Ejecutar paso
        this.emit('step:started', { flow, context, step });
        
        const stepResult = await this.executeStep(step, context);
        context.results.set(step.id, stepResult);
        results[step.id] = stepResult;

        // Emitir progreso de paso
        this.emit('step:completed', { 
          flow, 
          context, 
          step, 
          result: stepResult,
          progress: this.calculateProgress(context)
        });

      } catch (error) {
        context.errors.set(step.id, error as Error);
        this.emit('step:failed', { flow, context, step, error });

        // Si el paso es crítico, detener flujo
        if (!this.isStepOptional(step)) {
          throw new Error(`Paso crítico falló: ${step.name}`);
        }

        // Continuar con siguiente paso si es opcional
        continue;
      }
    }

    return results;
  }

  /**
   * Ejecuta un paso individual
   */
  private async executeStep(step: TransactionStep, context: FlowExecutionContext): Promise<any> {
    const timeout = step.timeout || context.options.timeout || 300000;
    
    return Promise.race([
      step.action(),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error(`Timeout en paso: ${step.name}`)), timeout)
      )
    ]);
  }

  /**
   * Verifica las dependencias de un paso
   */
  private async checkDependencies(step: TransactionStep, context: FlowExecutionContext): Promise<void> {
    if (!step.dependencies) return;

    for (const depId of step.dependencies) {
      const depResult = context.results.get(depId);
      if (depResult === undefined) {
        throw new Error(`Dependencia no satisfecha: ${depId} para paso ${step.name}`);
      }
    }
  }

  /**
   * Ejecuta rollback del flujo
   */
  private async rollbackFlow(flow: TransactionFlow, context: FlowExecutionContext): Promise<void> {
    this.emit('flow:rollback:started', { flow, context });

    // Ejecutar rollbacks en orden inverso
    const stepsWithRollback = flow.steps
      .filter(step => step.rollback)
      .reverse();

    for (const step of stepsWithRollback) {
      if (context.results.has(step.id)) {
        try {
          this.emit('step:rollback:started', { flow, context, step });
          await step.rollback!();
          this.emit('step:rollback:completed', { flow, context, step });
        } catch (error) {
          this.emit('step:rollback:failed', { flow, context, step, error });
        }
      }
    }

    this.emit('flow:rollback:completed', { flow, context });
  }

  /**
   * Valida un flujo antes de la ejecución
   */
  private validateFlow(flow: TransactionFlow): void {
    if (!flow.id) {
      throw new Error('ID de flujo es requerido');
    }

    if (!flow.name) {
      throw new Error('Nombre de flujo es requerido');
    }

    if (!flow.steps || flow.steps.length === 0) {
      throw new Error('El flujo debe tener al menos un paso');
    }

    // Validar pasos
    flow.steps.forEach((step, index) => {
      if (!step.id) {
        throw new Error(`Paso ${index + 1} debe tener un ID`);
      }

      if (!step.name) {
        throw new Error(`Paso ${index + 1} debe tener un nombre`);
      }

      if (typeof step.action !== 'function') {
        throw new Error(`Paso ${step.name} debe tener una función action`);
      }

      // Verificar dependencias
      if (step.dependencies) {
        step.dependencies.forEach(depId => {
          if (!flow.steps.find(s => s.id === depId)) {
            throw new Error(`Dependencia inválida: ${depId} en paso ${step.name}`);
          }
        });
      }
    });
  }

  /**
   * Actualiza el estado del flujo
   */
  private updateFlowStatus(
    flow: TransactionFlow,
    status: TransactionFlow['status'],
    context?: FlowExecutionContext
  ): void {
    flow.status = status;
    flow.updatedAt = Date.now();

    if (context) {
      this.emit('flow:status:changed', { flow, status, context });
    }
  }

  /**
   * Actualiza el progreso del flujo
   */
  private updateFlowProgress(flow: TransactionFlow, context: FlowExecutionContext): void {
    const progress = this.calculateProgress(context);

    const progressInfo: ProgressInfo = {
      percentage: progress.percentage,
      loaded: context.currentStep,
      total: context.totalSteps,
      message: `Ejecutando paso ${context.currentStep + 1} de ${context.totalSteps}: ${flow.steps[context.currentStep]?.name}`
    };

    this.emit('flow:progress', { flow, context, progress: progressInfo });
  }

  /**
   * Calcula el progreso del flujo
   */
  private calculateProgress(context: FlowExecutionContext): {
    percentage: number;
    current: number;
    total: number;
  } {
    const percentage = (context.currentStep / context.totalSteps) * 100;
    
    return {
      percentage: Math.round(percentage),
      current: context.currentStep,
      total: context.totalSteps
    };
  }

  /**
   * Determina si un paso es opcional
   */
  private isStepOptional(step: TransactionStep): boolean {
    // Un paso es opcional si su nombre comienza con 'opcional' o 'optional'
    return step.name.toLowerCase().includes('opcional') || 
           step.name.toLowerCase().includes('optional');
  }

  /**
   * Obtiene un flujo activo
   */
  public getActiveFlow(flowId: string): FlowExecutionContext | undefined {
    return this.activeFlows.get(flowId);
  }

  /**
   * Obtiene todos los flujos activos
   */
  public getActiveFlows(): Array<{ flowId: string; context: FlowExecutionContext }> {
    return Array.from(this.activeFlows.entries()).map(([flowId, context]) => ({
      flowId,
      context
    }));
  }

  /**
   * Cancela un flujo en ejecución
   */
  public async cancelFlow(flowId: string): Promise<boolean> {
    const context = this.activeFlows.get(flowId);
    if (!context) {
      return false;
    }

    // Actualizar estado a cancelado
    const flow = this.completedFlows.find(f => f.id === flowId) || 
                 { id: flowId, name: 'Flujo cancelado', steps: [], status: 'cancelled' as const };

    this.updateFlowStatus(flow, 'cancelled', context);

    // Limpiar del mapa de flujos activos
    this.activeFlows.delete(flowId);

    // Ejecutar rollback si está configurado
    if (context.options.rollbackOnError) {
      await this.rollbackFlow(flow, context);
    }

    this.emit('flow:cancelled', { flow, context });

    return true;
  }

  /**
   * Pausa un flujo en ejecución
   */
  public pauseFlow(flowId: string): boolean {
    const context = this.activeFlows.get(flowId);
    if (!context) {
      return false;
    }

    // Marcar como pausado (esto requeriría implementación adicional)
    this.emit('flow:paused', { flowId, context });
    
    return true;
  }

  /**
   * Reanuda un flujo pausado
   */
  public resumeFlow(flowId: string): boolean {
    // Implementación para reanudar flujos pausados
    this.emit('flow:resumed', { flowId });
    
    return true;
  }

  /**
   * Obtiene el historial de flujos completados
   */
  public getFlowHistory(limit = 50): TransactionFlow[] {
    return this.completedFlows.slice(-limit);
  }

  /**
   * Obtiene flujos por estado
   */
  public getFlowsByStatus(status: TransactionFlow['status']): TransactionFlow[] {
    return this.completedFlows.filter(flow => flow.status === status);
  }

  /**
   * Obtiene estadísticas de flujos
   */
  public getFlowStats(): {
    activeFlows: number;
    completedFlows: number;
    successRate: number;
    averageDuration: number;
    flowsByStatus: Record<string, number>;
  } {
    const completed = this.completedFlows;
    const successful = completed.filter(f => f.status === 'completed');
    
    const durations = completed
      .filter(f => f.status === 'completed')
      .map(f => f.updatedAt - f.createdAt)
      .filter(d => d > 0);

    const flowsByStatus = completed.reduce((acc, flow) => {
      acc[flow.status] = (acc[flow.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      activeFlows: this.activeFlows.size,
      completedFlows: completed.length,
      successRate: completed.length > 0 ? (successful.length / completed.length) * 100 : 0,
      averageDuration: durations.length > 0 ? 
        durations.reduce((a, b) => a + b, 0) / durations.length : 0,
      flowsByStatus
    };
  }

  /**
   * Mantiene el límite del historial
   */
  private maintainHistoryLimit(): void {
    if (this.completedFlows.length > this.maxCompletedFlows) {
      this.completedFlows = this.completedFlows.slice(-this.maxCompletedFlows);
    }
  }

  /**
   * Limpia un flujo completado
   */
  public cleanupFlow(flowId: string): void {
    const index = this.completedFlows.findIndex(f => f.id === flowId);
    if (index >= 0) {
      this.completedFlows.splice(index, 1);
      this.emit('flow:cleaned', { flowId });
    }
  }

  /**
   * Limpia todos los flujos completados
   */
  public clearHistory(): void {
    this.completedFlows = [];
    this.emit('history:cleared');
  }

  /**
   * Crea un flujo de ejemplo para testing
   */
  public static createSampleFlow(): TransactionFlow {
    return {
      id: `sample_flow_${Date.now()}`,
      name: 'Flujo de Ejemplo',
      steps: [
        {
          id: 'step_1',
          name: 'Inicializar',
          action: async () => {
            await new Promise(resolve => setTimeout(resolve, 1000));
            return { initialized: true };
          }
        },
        {
          id: 'step_2',
          name: 'Procesar Datos',
          action: async () => {
            await new Promise(resolve => setTimeout(resolve, 2000));
            return { processed: true };
          },
          dependencies: ['step_1']
        },
        {
          id: 'step_3',
          name: 'Finalizar',
          action: async () => {
            await new Promise(resolve => setTimeout(resolve, 500));
            return { finished: true };
          },
          dependencies: ['step_2']
        }
      ],
      currentStep: 0,
      status: 'pending',
      createdAt: Date.now(),
      updatedAt: Date.now()
    };
  }
}