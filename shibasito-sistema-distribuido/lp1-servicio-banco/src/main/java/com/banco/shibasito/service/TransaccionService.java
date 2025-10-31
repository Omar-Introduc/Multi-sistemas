package com.banco.shibasito.service;

import com.banco.shibasito.dto.Response;
import com.banco.shibasito.entity.Cuenta;
import com.banco.shibasito.entity.Transaccion;
import com.banco.shibasito.repository.TransaccionRepository;
import com.banco.shibasito.repository.CuentaRepository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Servicio de negocio para la gestión de transacciones
 * Maneja la lógica de negocio relacionada con transacciones bancarias
 */
@Service
@Transactional
public class TransaccionService {
    
    @Autowired
    private TransaccionRepository transaccionRepository;
    
    @Autowired
    private CuentaRepository cuentaRepository;
    
    @Autowired
    private BancoRabbitMQService rabbitMQService;
    
    /**
     * Procesa una transacción (depósito, retiro o transferencia)
     * @param numeroCuenta Número de la cuenta
     * @param tipo Tipo de transacción
     * @param monto Monto de la transacción
     * @param descripcion Descripción de la transacción
     * @param transaccionRequest
     * @return Response con el resultado de la transacción
     */
    public Response<Transaccion> procesarTransaccion(com.banco.shibasito.dto.TransaccionRequest transaccionRequest) {
        try {
            Transaccion.TipoTransaccion tipo;
            try {
                tipo = Transaccion.TipoTransaccion.valueOf(transaccionRequest.getTipoTransaccion());
            } catch (IllegalArgumentException | NullPointerException e) {
                return Response.error("Tipo de transacción no válido: " + transaccionRequest.getTipoTransaccion(), "TIPO_INVALIDO");
            }

            // Validaciones
            Response<Transaccion> validacion = validarTransaccion(transaccionRequest.getCuentaOrigen(), tipo, transaccionRequest.getMonto());
            if (!validacion.isSuccess()) {
                return validacion;
            }

            // Verificar que la cuenta existe
            Optional<Cuenta> cuentaOpt = cuentaRepository.findByNumero(transaccionRequest.getCuentaOrigen());
            if (!cuentaOpt.isPresent()) {
                return Response.error("No se encontró cuenta con número: " + transaccionRequest.getCuentaOrigen(), "CUENTA_NO_ENCONTRADA");
            }

            Cuenta cuenta = cuentaOpt.get();

            // Verificar que la cuenta está activa
            if (cuenta.getEstado() != Cuenta.Estado.ACTIVA) {
                return Response.error("No se puede procesar transacción en cuenta inactiva", "CUENTA_INACTIVA");
            }

            Transaccion transaccion = null;

            // Procesar según el tipo de transacción
            switch (tipo) {
                case DEPOSITO:
                    transaccion = procesarDeposito(cuenta, transaccionRequest.getMonto(), transaccionRequest.getDescripcion());
                    break;
                case RETIRO:
                    transaccion = procesarRetiro(cuenta, transaccionRequest.getMonto(), transaccionRequest.getDescripcion());
                    break;
                case TRANSFERENCIA:
                    transaccion = procesarTransferencia(cuenta, transaccionRequest.getMonto(), transaccionRequest.getDescripcion(), transaccionRequest.getCuentaDestino());
                    break;
                default:
                    return Response.error("Tipo de transacción no soportado: " + transaccionRequest.getTipoTransaccion(), "TIPO_NO_SOPORTADO");
            }

            if (transaccion != null) {
                // Enviar mensaje a RabbitMQ
                rabbitMQService.enviarEventoTransaccionProcesada(transaccion);

                return Response.success("Transacción procesada exitosamente", transaccion);
            } else {
                return Response.error("No se pudo procesar la transacción", "TRANSACCION_FALLIDA");
            }

        } catch (Exception e) {
            return Response.error("Error al procesar transacción: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Crea una transacción sin procesar (estado pendiente)
     * @param numeroCuenta Número de la cuenta
     * @param tipo Tipo de transacción
     * @param monto Monto de la transacción
     * @param descripcion Descripción de la transacción
     * @return Response con la transacción creada
     */
    public Response<Transaccion> crearTransaccion(String numeroCuenta, Transaccion.TipoTransaccion tipo, 
                                                BigDecimal monto, String descripcion) {
        try {
            if (numeroCuenta == null || numeroCuenta.trim().isEmpty()) {
                return Response.error("El número de cuenta es obligatorio", "NUMERO_CUENTA_REQUERIDO");
            }
            
            if (tipo == null) {
                return Response.error("El tipo de transacción es obligatorio", "TIPO_TRANSACCION_REQUERIDO");
            }
            
            if (monto == null || monto.compareTo(BigDecimal.ZERO) <= 0) {
                return Response.error("El monto debe ser mayor a cero", "MONTO_INVALIDO");
            }
            
            Optional<Cuenta> cuentaOpt = cuentaRepository.findByNumero(numeroCuenta);
            if (!cuentaOpt.isPresent()) {
                return Response.error("No se encontró cuenta con número: " + numeroCuenta, "CUENTA_NO_ENCONTRADA");
            }
            
            // Crear transacción en estado pendiente
            Transaccion transaccion = new Transaccion();
            transaccion.setCuenta(cuentaOpt.get());
            transaccion.setTipo(tipo);
            transaccion.setMonto(monto);
            transaccion.setDescripcion(descripcion != null ? descripcion : "Transacción creada");
            transaccion.setEstado(Transaccion.Estado.PENDIENTE);
            transaccion.setFecha(LocalDateTime.now());
            
            Transaccion transaccionGuardada = transaccionRepository.save(transaccion);
            
            return Response.success("Transacción creada exitosamente", transaccionGuardada);
            
        } catch (Exception e) {
            return Response.error("Error al crear transacción: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Busca una transacción por su ID
     * @param id ID de la transacción
     * @return Response con la transacción encontrada o mensaje de error
     */
    public Response<Transaccion> buscarPorId(Long id) {
        try {
            if (id == null || id <= 0) {
                return Response.error("ID de transacción inválido", "ID_INVALIDO");
            }
            
            Optional<Transaccion> transaccion = transaccionRepository.findById(id);
            
            if (transaccion.isPresent()) {
                return Response.success("Transacción encontrada", transaccion.get());
            } else {
                return Response.error("No se encontró transacción con ID: " + id, "TRANSACCION_NO_ENCONTRADA");
            }
            
        } catch (Exception e) {
            return Response.error("Error al buscar transacción: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Lista transacciones por cuenta en un período
     * @param numeroCuenta Número de la cuenta
     * @param fechaInicio Fecha de inicio
     * @param fechaFin Fecha de fin
     * @return Response con la lista de transacciones
     */
    public Response<List<Transaccion>> listarTransacciones(String numeroCuenta, LocalDate fechaInicio, LocalDate fechaFin) {
        try {
            Optional<Cuenta> cuentaOpt = cuentaRepository.findByNumero(numeroCuenta);
            if (!cuentaOpt.isPresent()) {
                return Response.error("No se encontró cuenta con número: " + numeroCuenta, "CUENTA_NO_ENCONTRADA");
            }
            
            List<Transaccion> transacciones;
            
            if (fechaInicio != null && fechaFin != null) {
                transacciones = transaccionRepository.findByCuentaAndFechaBetween(
                        cuentaOpt.get(),
                        fechaInicio.atStartOfDay(),
                        fechaFin.atTime(23, 59, 59)
                );
            } else {
                transacciones = transaccionRepository.findByCuentaOrderByFechaDesc(cuentaOpt.get());
            }
            
            return Response.success("Transacciones obtenidas exitosamente", transacciones);
            
        } catch (Exception e) {
            return Response.error("Error al listar transacciones: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Lista transacciones por tipo
     * @param tipo Tipo de transacción
     * @return Response con la lista de transacciones
     */
    public Response<List<Transaccion>> listarPorTipo(Transaccion.TipoTransaccion tipo) {
        try {
            if (tipo == null) {
                return Response.error("El tipo de transacción es obligatorio", "TIPO_TRANSACCION_REQUERIDO");
            }
            
            List<Transaccion> transacciones = transaccionRepository.findByTipoOrderByFechaDesc(tipo);
            
            return Response.success("Transacciones obtenidas exitosamente", transacciones);
            
        } catch (Exception e) {
            return Response.error("Error al listar transacciones por tipo: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Lista transacciones por estado
     * @param estado Estado de la transacción
     * @return Response con la lista de transacciones
     */
    public Response<List<Transaccion>> listarPorEstado(Transaccion.Estado estado) {
        try {
            if (estado == null) {
                return Response.error("El estado de transacción es obligatorio", "ESTADO_TRANSACCION_REQUERIDO");
            }
            
            List<Transaccion> transacciones = transaccionRepository.findByEstadoOrderByFechaDesc(estado);
            
            return Response.success("Transacciones obtenidas exitosamente", transacciones);
            
        } catch (Exception e) {
            return Response.error("Error al listar transacciones por estado: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Cancela una transacción pendiente
     * @param id ID de la transacción
     * @param motivo Motivo de la cancelación
     * @return Response con el resultado de la operación
     */
    public Response<String> cancelarTransaccion(Long id, String motivo) {
        try {
            Optional<Transaccion> transaccionOpt = transaccionRepository.findById(id);
            if (!transaccionOpt.isPresent()) {
                return Response.error("No se encontró transacción con ID: " + id, "TRANSACCION_NO_ENCONTRADA");
            }
            
            Transaccion transaccion = transaccionOpt.get();
            
            if (transaccion.getEstado() != Transaccion.Estado.PENDIENTE) {
                return Response.error("Solo se pueden cancelar transacciones pendientes", "TRANSACCION_NO_CANCELABLE");
            }
            
            transaccion.setEstado(Transaccion.Estado.CANCELADA);
            transaccion.setMotivoFallo(motivo != null ? motivo : "Cancelada por el usuario");
            
            transaccionRepository.save(transaccion);
            
            return Response.success("Transacción cancelada exitosamente");
            
        } catch (Exception e) {
            return Response.error("Error al cancelar transacción: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Procesa un depósito
     */
    private Transaccion procesarDeposito(Cuenta cuenta, BigDecimal monto, String descripcion) {
        // Realizar depósito
        cuenta.depositar(monto);
        cuentaRepository.save(cuenta);
        
        // Crear transacción
        Transaccion transaccion = new Transaccion(monto, Transaccion.TipoTransaccion.DEPOSITO, 
                descripcion != null ? descripcion : "Depósito", cuenta);
        transaccion.setEstado(Transaccion.Estado.COMPLETADA);
        
        return transaccionRepository.save(transaccion);
    }
    
    /**
     * Procesa un retiro
     */
    private Transaccion procesarRetiro(Cuenta cuenta, BigDecimal monto, String descripcion) {
        // Verificar si se puede realizar el retiro
        if (!cuenta.puedeRetirar(monto)) {
            Transaccion transaccionFallida = new Transaccion(monto, Transaccion.TipoTransaccion.RETIRO,
                    descripcion != null ? descripcion : "Retiro", cuenta);
            transaccionFallida.setEstado(Transaccion.Estado.FALLIDA);
            transaccionFallida.setMotivoFallo("Saldo insuficiente o límite mínimo no alcanzado");
            return transaccionRepository.save(transaccionFallida);
        }
        
        // Realizar retiro
        cuenta.retirar(monto);
        cuentaRepository.save(cuenta);
        
        // Crear transacción
        Transaccion transaccion = new Transaccion(monto, Transaccion.TipoTransaccion.RETIRO,
                descripcion != null ? descripcion : "Retiro", cuenta);
        transaccion.setEstado(Transaccion.Estado.COMPLETADA);
        
        return transaccionRepository.save(transaccion);
    }
    
    /**
     * Procesa una transferencia
     */
    private Transaccion procesarTransferencia(Cuenta cuentaOrigen, BigDecimal monto, String descripcion, String cuentaDestinoNumero) {
        if (cuentaDestinoNumero == null || cuentaDestinoNumero.trim().isEmpty()) {
            Transaccion transaccionFallida = new Transaccion(monto, Transaccion.TipoTransaccion.TRANSFERENCIA,
                    descripcion != null ? descripcion : "Transferencia", cuentaOrigen);
            transaccionFallida.setEstado(Transaccion.Estado.FALLIDA);
            transaccionFallida.setMotivoFallo("Cuenta destino no especificada");
            return transaccionRepository.save(transaccionFallida);
        }
        
        Optional<Cuenta> cuentaDestinoOpt = cuentaRepository.findByNumero(cuentaDestinoNumero);
        if (!cuentaDestinoOpt.isPresent()) {
            Transaccion transaccionFallida = new Transaccion(monto, Transaccion.TipoTransaccion.TRANSFERENCIA,
                    descripcion != null ? descripcion : "Transferencia", cuentaOrigen);
            transaccionFallida.setEstado(Transaccion.Estado.FALLIDA);
            transaccionFallida.setMotivoFallo("Cuenta destino no encontrada: " + cuentaDestinoNumero);
            return transaccionRepository.save(transaccionFallida);
        }
        
        Cuenta cuentaDestino = cuentaDestinoOpt.get();
        
        // Verificar que la cuenta destino está activa
        if (cuentaDestino.getEstado() != Cuenta.Estado.ACTIVA) {
            Transaccion transaccionFallida = new Transaccion(monto, Transaccion.TipoTransaccion.TRANSFERENCIA,
                    descripcion != null ? descripcion : "Transferencia", cuentaOrigen);
            transaccionFallida.setEstado(Transaccion.Estado.FALLIDA);
            transaccionFallida.setMotivoFallo("Cuenta destino inactiva");
            return transaccionRepository.save(transaccionFallida);
        }
        
        // Verificar saldo en cuenta origen
        if (!cuentaOrigen.puedeRetirar(monto)) {
            Transaccion transaccionFallida = new Transaccion(monto, Transaccion.TipoTransaccion.TRANSFERENCIA,
                    descripcion != null ? descripcion : "Transferencia", cuentaOrigen);
            transaccionFallida.setEstado(Transaccion.Estado.FALLIDA);
            transaccionFallida.setMotivoFallo("Saldo insuficiente en cuenta origen");
            return transaccionRepository.save(transaccionFallida);
        }
        
        // Realizar transferencia
        cuentaOrigen.retirar(monto);
        cuentaDestino.depositar(monto);
        
        cuentaRepository.save(cuentaOrigen);
        cuentaRepository.save(cuentaDestino);
        
        // Crear transacción en cuenta origen
        Transaccion transaccion = new Transaccion(monto, Transaccion.TipoTransaccion.TRANSFERENCIA,
                descripcion != null ? descripcion : "Transferencia a " + cuentaDestinoNumero, cuentaOrigen);
        transaccion.setEstado(Transaccion.Estado.COMPLETADA);
        
        return transaccionRepository.save(transaccion);
    }
    
    /**
     * Valida los datos de una transacción
     */
    private Response<Transaccion> validarTransaccion(String numeroCuenta, Transaccion.TipoTransaccion tipo, BigDecimal monto) {
        if (numeroCuenta == null || numeroCuenta.trim().isEmpty()) {
            return Response.error("El número de cuenta es obligatorio", "NUMERO_CUENTA_REQUERIDO");
        }
        
        if (tipo == null) {
            return Response.error("El tipo de transacción es obligatorio", "TIPO_TRANSACCION_REQUERIDO");
        }
        
        if (monto == null || monto.compareTo(BigDecimal.ZERO) <= 0) {
            return Response.error("El monto debe ser mayor a cero", "MONTO_INVALIDO");
        }
        
        // Validaciones específicas por tipo
        if (tipo == Transaccion.TipoTransaccion.RETIRO && monto.compareTo(new BigDecimal("10000.00")) > 0) {
            return Response.error("El monto máximo para retiros es $10,000.00", "MONTO_EXCEDE_LIMITE");
        }
        
        return Response.success("Validación exitosa");
    }

    public Response<List<Transaccion>> obtenerHistorialTransacciones(Long id, LocalDateTime startDate, LocalDateTime endDate) {
        Optional<Cuenta> cuenta = cuentaRepository.findById(id);
        if (cuenta.isPresent()) {
            List<Transaccion> transacciones = transaccionRepository.findByCuentaAndFechaBetween(cuenta.get(), startDate, endDate);
            return Response.success("Historial de transacciones obtenido exitosamente", transacciones);
        }
        return Response.error("Cuenta no encontrada", null);
    }

    public Response<Transaccion> obtenerTransaccionPorId(Long id) {
        Optional<Transaccion> transaccion = transaccionRepository.findById(id);
        return transaccion.map(value -> Response.success("Transacción encontrada", value)).orElseGet(() -> Response.error("Transacción no encontrada", null));
    }
}