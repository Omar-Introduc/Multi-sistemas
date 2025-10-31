package com.banco.shibasito.service;

import com.banco.shibasito.dto.Response;
import com.banco.shibasito.entity.Cliente;
import com.banco.shibasito.entity.Prestamo;
import com.banco.shibasito.repository.PrestamoRepository;
import com.banco.shibasito.repository.ClienteRepository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

/**
 * Servicio de negocio para la gestión de préstamos
 * Maneja la lógica de negocio relacionada con préstamos del banco
 */
@Service
@Transactional
public class PrestamoService {
    
    @Autowired
    private PrestamoRepository prestamoRepository;
    
    @Autowired
    private ClienteRepository clienteRepository;
    
    @Autowired
    private BancoRabbitMQService rabbitMQService;
    
    /**
     * Solicita un nuevo préstamo
     * @param prestamoRequest
     * @return Response con el préstamo solicitado o mensaje de error
     */
    public Response<Prestamo> solicitarPrestamo(com.banco.shibasito.dto.PrestamoRequest prestamoRequest) {
        try {
            // Validaciones
            Response<Prestamo> validacion = validarSolicitudPrestamo(prestamoRequest.getDni(), prestamoRequest.getMonto(), prestamoRequest.getPlazoMeses(), prestamoRequest.getProposito());
            if (!validacion.isSuccess()) {
                return validacion;
            }
            
            // Verificar que el cliente existe
            Optional<Cliente> clienteOpt = clienteRepository.findByDni(prestamoRequest.getDni());
            if (!clienteOpt.isPresent()) {
                return Response.error("No se encontró cliente con DNI: " + prestamoRequest.getDni(), "CLIENTE_NO_ENCONTRADO");
            }
            
            Cliente cliente = clienteOpt.get();
            
            // Verificar que el cliente esté activo
            if (cliente.getEstado() != Cliente.Estado.ACTIVO) {
                return Response.error("El cliente debe estar activo para solicitar un préstamo", "CLIENTE_INACTIVO");
            }
            
            // Verificar si el cliente tiene préstamos pendientes
            List<Prestamo> prestamosPendientes = prestamoRepository.findByClienteDniAndEstado(prestamoRequest.getDni(), Prestamo.Estado.PENDIENTE);
            if (!prestamosPendientes.isEmpty()) {
                return Response.error("El cliente ya tiene una solicitud de préstamo pendiente", "SOLICITUD_PENDIENTE");
            }
            
            // Verificar capacidad de pago del cliente (simplificado)
            Response<BigDecimal> capacidadPago = evaluarCapacidadPago(cliente, prestamoRequest.getMonto(), prestamoRequest.getPlazoMeses());
            if (!capacidadPago.isSuccess()) {
                return Response.error(capacidadPago.getMessage(), null);
            }
            
            // Calcular tasa de interés según monto y plazo
            BigDecimal tasaInteres = calcularTasaInteres(prestamoRequest.getMonto(), prestamoRequest.getPlazoMeses());
            
            // Crear préstamo
            Prestamo prestamo = new Prestamo();
            prestamo.setCliente(cliente);
            prestamo.setMonto(prestamoRequest.getMonto());
            prestamo.setPlazoMeses(prestamoRequest.getPlazoMeses());
            prestamo.setMotivo(prestamoRequest.getProposito());
            prestamo.setTasaInteres(tasaInteres);
            prestamo.setEstado(Prestamo.Estado.PENDIENTE);
            prestamo.setFecha(LocalDate.now());
            prestamo.setCuotasPagadas(0);
            
            // Guardar préstamo
            Prestamo prestamoGuardado = prestamoRepository.save(prestamo);
            
            // Enviar mensaje a RabbitMQ
            rabbitMQService.enviarEventoPrestamoSolicitado(prestamoGuardado);
            
            return Response.success("Solicitud de préstamo creada exitosamente", prestamoGuardado);
            
        } catch (Exception e) {
            return Response.error("Error al solicitar préstamo: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Evalúa una solicitud de préstamo
     * @param id ID del préstamo
     * @return Response con el resultado de la evaluación
     */
    public Response<Prestamo> evaluarSolicitud(Long id) {
        try {
            if (id == null || id <= 0) {
                return Response.error("ID de préstamo inválido", "ID_INVALIDO");
            }
            
            Optional<Prestamo> prestamoOpt = prestamoRepository.findById(id);
            if (!prestamoOpt.isPresent()) {
                return Response.error("No se encontró préstamo con ID: " + id, "PRESTAMO_NO_ENCONTRADO");
            }
            
            Prestamo prestamo = prestamoOpt.get();
            
            if (prestamo.getEstado() != Prestamo.Estado.PENDIENTE) {
                return Response.error("Solo se pueden evaluar solicitudes pendientes", "ESTADO_NO_EVALUABLE");
            }
            
            // Cambiar estado a EVALUANDO
            prestamo.setEstado(Prestamo.Estado.EVALUANDO);
            Prestamo prestamoEvaluado = prestamoRepository.save(prestamo);
            
            // Realizar evaluación crediticia (lógica simplificada)
            Response<String> resultadoEvaluacion = realizarEvaluacionCrediticia(prestamo);
            
            if (resultadoEvaluacion.isSuccess()) {
                return Response.success("Evaluación completada: " + resultadoEvaluacion.getData(), prestamoEvaluado);
            } else {
                return Response.error("Error en la evaluación: " + resultadoEvaluacion.getMessage(), "EVALUACION_FALLIDA");
            }
            
        } catch (Exception e) {
            return Response.error("Error al evaluar solicitud: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Aprueba un préstamo
     * @param id ID del préstamo
     * @param montoAprobado Monto aprobado (puede ser menor al solicitado)
     * @param observaciones Observaciones de la aprobación
     * @return Response con el préstamo aprobado o mensaje de error
     */
    public Response<Prestamo> aprobarPrestamo(Long id, BigDecimal montoAprobado, String observaciones) {
        try {
            if (id == null || id <= 0) {
                return Response.error("ID de préstamo inválido", "ID_INVALIDO");
            }
            
            if (montoAprobado == null || montoAprobado.compareTo(BigDecimal.ZERO) <= 0) {
                return Response.error("El monto aprobado debe ser mayor a cero", "MONTO_APROBADO_INVALIDO");
            }
            
            Optional<Prestamo> prestamoOpt = prestamoRepository.findById(id);
            if (!prestamoOpt.isPresent()) {
                return Response.error("No se encontró préstamo con ID: " + id, "PRESTAMO_NO_ENCONTRADO");
            }
            
            Prestamo prestamo = prestamoOpt.get();
            
            if (prestamo.getEstado() != Prestamo.Estado.PENDIENTE && prestamo.getEstado() != Prestamo.Estado.EVALUANDO) {
                return Response.error("Solo se pueden aprobar solicitudes pendientes o en evaluación", "ESTADO_NO_APROBABLE");
            }
            
            // Verificar que el monto aprobado no sea mayor al solicitado
            if (montoAprobado.compareTo(prestamo.getMonto()) > 0) {
                return Response.error("El monto aprobado no puede ser mayor al solicitado", "MONTO_EXCEDE_SOLICITADO");
            }
            
            // Aprobar préstamo
            prestamo.setMontoAprobado(montoAprobado);
            prestamo.setEstado(Prestamo.Estado.APROBADO);
            prestamo.setFechaAprobacion(LocalDate.now());
            
            // Calcular fecha de vencimiento
            LocalDate fechaVencimiento = prestamo.getFechaAprobacion().plusMonths(prestamo.getPlazoMeses());
            prestamo.setFechaVencimiento(fechaVencimiento);
            
            // Calcular cuota mensual
            calcularCuotaMensual(prestamo);
            
            // Guardar préstamo aprobado
            Prestamo prestamoAprobado = prestamoRepository.save(prestamo);
            
            // Enviar mensaje a RabbitMQ
            rabbitMQService.enviarEventoPrestamoAprobado(prestamoAprobado);
            
            return Response.success("Préstamo aprobado exitosamente", prestamoAprobado);
            
        } catch (Exception e) {
            return Response.error("Error al aprobar préstamo: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Rechaza un préstamo
     * @param id ID del préstamo
     * @param motivo Motivo del rechazo
     * @return Response con el resultado de la operación
     */
    public Response<String> rechazarPrestamo(Long id, String motivo) {
        try {
            if (id == null || id <= 0) {
                return Response.error("ID de préstamo inválido", "ID_INVALIDO");
            }
            
            if (motivo == null || motivo.trim().isEmpty()) {
                return Response.error("El motivo del rechazo es obligatorio", "MOTIVO_REQUERIDO");
            }
            
            Optional<Prestamo> prestamoOpt = prestamoRepository.findById(id);
            if (!prestamoOpt.isPresent()) {
                return Response.error("No se encontró préstamo con ID: " + id, "PRESTAMO_NO_ENCONTRADO");
            }
            
            Prestamo prestamo = prestamoOpt.get();
            
            if (prestamo.getEstado() != Prestamo.Estado.PENDIENTE && prestamo.getEstado() != Prestamo.Estado.EVALUANDO) {
                return Response.error("Solo se pueden rechazar solicitudes pendientes o en evaluación", "ESTADO_NO_RECHAZABLE");
            }
            
            // Rechazar préstamo
            prestamo.setEstado(Prestamo.Estado.RECHAZADO);
            prestamo.setMotivoRechazo(motivo);
            
            prestamoRepository.save(prestamo);
            
            // Enviar mensaje a RabbitMQ
            rabbitMQService.enviarEventoPrestamoRechazado(prestamo);
            
            return Response.success("Préstamo rechazado exitosamente");
            
        } catch (Exception e) {
            return Response.error("Error al rechazar préstamo: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Lista préstamos por cliente
     * @param dniCliente DNI del cliente
     * @return Response con la lista de préstamos del cliente
     */
    public Response<List<Prestamo>> listarPrestamos(String dniCliente) {
        try {
            if (dniCliente == null || dniCliente.trim().isEmpty()) {
                return Response.error("El DNI del cliente es obligatorio", "DNI_CLIENTE_REQUERIDO");
            }
            
            List<Prestamo> prestamos = prestamoRepository.findByClienteDniOrderByFechaDesc(dniCliente);
            
            return Response.success("Préstamos obtenidos exitosamente", prestamos);
            
        } catch (Exception e) {
            return Response.error("Error al listar préstamos: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Lista préstamos por estado
     * @param estado Estado de los préstamos
     * @return Response con la lista de préstamos
     */
    public Response<List<Prestamo>> listarPrestamosPorEstado(Prestamo.Estado estado) {
        try {
            if (estado == null) {
                return Response.error("El estado es obligatorio", "ESTADO_REQUERIDO");
            }
            
            List<Prestamo> prestamos = prestamoRepository.findByEstado(estado);
            
            return Response.success("Préstamos obtenidos exitosamente", prestamos);
            
        } catch (Exception e) {
            return Response.error("Error al listar préstamos por estado: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Obtiene préstamos pendientes de aprobación
     * @return Response con la lista de préstamos pendientes
     */
    public Response<List<Prestamo>> listarPendientes() {
        try {
            List<Prestamo> prestamos = prestamoRepository.findPendientesOrderByFechaAsc();
            
            return Response.success("Préstamos pendientes obtenidos exitosamente", prestamos);
            
        } catch (Exception e) {
            return Response.error("Error al listar préstamos pendientes: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Calcula la cuota mensual de un préstamo
     * @param prestamo Préstamo a calcular
     */
    private void calcularCuotaMensual(Prestamo prestamo) {
        if (prestamo.getMontoAprobado() != null && prestamo.getTasaInteres() != null && prestamo.getPlazoMeses() > 0) {
            // Cálculo simple de cuota mensual (sistema francés simplificado)
            BigDecimal tasaMensual = prestamo.getTasaInteres().divide(BigDecimal.valueOf(100), 6, BigDecimal.ROUND_HALF_UP);
            BigDecimal factor = BigDecimal.ONE.add(tasaMensual).pow(prestamo.getPlazoMeses());
            BigDecimal cuotaMensual = prestamo.getMontoAprobado().multiply(tasaMensual.multiply(factor))
                    .divide(factor.subtract(BigDecimal.ONE), 2, BigDecimal.ROUND_HALF_UP);
            
            prestamo.setCuotaMensual(cuotaMensual);
            prestamo.setSaldoPendiente(prestamo.getMontoAprobado());
        }
    }
    
    /**
     * Calcula la tasa de interés según monto y plazo
     * @param monto Monto del préstamo
     * @param plazoMeses Plazo en meses
     * @return Tasa de interés
     */
    private BigDecimal calcularTasaInteres(BigDecimal monto, int plazoMeses) {
        BigDecimal tasaBase = new BigDecimal("12.00"); // 12% base
        
        // Ajuste por monto
        if (monto.compareTo(new BigDecimal("50000")) > 0) {
            tasaBase = tasaBase.subtract(new BigDecimal("2.00")); // Descuento por monto alto
        } else if (monto.compareTo(new BigDecimal("10000")) < 0) {
            tasaBase = tasaBase.add(new BigDecimal("3.00")); // Recargo por monto bajo
        }
        
        // Ajuste por plazo
        if (plazoMeses > 36) {
            tasaBase = tasaBase.add(new BigDecimal("1.00")); // Recargo por plazo largo
        } else if (plazoMeses < 12) {
            tasaBase = tasaBase.subtract(new BigDecimal("1.00")); // Descuento por plazo corto
        }
        
        return tasaBase.max(new BigDecimal("8.00")).min(new BigDecimal("20.00")); // Entre 8% y 20%
    }
    
    /**
     * Evalúa la capacidad de pago del cliente
     * @param cliente Cliente a evaluar
     * @param monto Monto del préstamo
     * @param plazoMeses Plazo en meses
     * @return Response con resultado de la evaluación
     */
    private Response<BigDecimal> evaluarCapacidadPago(Cliente cliente, BigDecimal monto, int plazoMeses) {
        // Lógica simplificada de evaluación crediticia
        // En un sistema real, esto sería más complejo e involucraría historial crediticio, ingresos, etc.
        
        // Por ahora, simplemente verificamos que el monto no sea excesivo
        if (monto.compareTo(new BigDecimal("100000")) > 0) {
            return Response.error("El monto solicitado excede el límite máximo permitido", "MONTO_EXCESIVO");
        }
        
        // Verificar que el plazo sea razonable
        if (plazoMeses < 6 || plazoMeses > 60) {
            return Response.error("El plazo debe estar entre 6 y 60 meses", "PLAZO_INVALIDO");
        }
        
        // Calcular cuota estimada
        BigDecimal tasaEstimada = calcularTasaInteres(monto, plazoMeses);
        BigDecimal cuotaEstimada = monto.multiply(tasaEstimada.divide(BigDecimal.valueOf(100), 6, BigDecimal.ROUND_HALF_UP))
                .divide(BigDecimal.valueOf(plazoMeses), 2, BigDecimal.ROUND_HALF_UP);
        
        return Response.success("Capacidad de pago adecuada", cuotaEstimada);
    }
    
    /**
     * Realiza la evaluación crediticia del préstamo
     * @param prestamo Préstamo a evaluar
     * @return Response con resultado de la evaluación
     */
    private Response<String> realizarEvaluacionCrediticia(Prestamo prestamo) {
        try {
            // Lógica de evaluación crediticia simplificada
            // En un sistema real, esto consultaría centrales de riesgo, historial del cliente, etc.
            
            // Simular evaluación
            boolean aprobado = Math.random() > 0.3; // 70% de probabilidad de aprobación
            
            if (aprobado) {
                return Response.success("Evaluación crediticia aprobada");
            } else {
                return Response.error("Evaluación crediticia rechazada: Perfil de riesgo alto", "RIESGO_ALTO");
            }
            
        } catch (Exception e) {
            return Response.error("Error en evaluación crediticia: " + e.getMessage(), "ERROR_EVALUACION");
        }
    }
    
    /**
     * Valida los datos de una solicitud de préstamo
     * @param dniCliente DNI del cliente
     * @param monto Monto solicitado
     * @param plazoMeses Plazo en meses
     * @param motivo Motivo de la solicitud
     * @return Response con resultado de la validación
     */
    private Response<Prestamo> validarSolicitudPrestamo(String dniCliente, BigDecimal monto, int plazoMeses, String motivo) {
        if (dniCliente == null || dniCliente.trim().isEmpty()) {
            return Response.error("El DNI del cliente es obligatorio", "DNI_CLIENTE_REQUERIDO");
        }
        
        if (monto == null || monto.compareTo(BigDecimal.ZERO) <= 0) {
            return Response.error("El monto debe ser mayor a cero", "MONTO_INVALIDO");
        }
        
        if (plazoMeses <= 0) {
            return Response.error("El plazo debe ser mayor a cero", "PLAZO_INVALIDO");
        }
        
        if (motivo == null || motivo.trim().isEmpty()) {
            return Response.error("El motivo de la solicitud es obligatorio", "MOTIVO_REQUERIDO");
        }
        
        // Validaciones de negocio
        if (monto.compareTo(new BigDecimal("1000")) < 0) {
            return Response.error("El monto mínimo de préstamo es $1,000", "MONTO_MINIMO_NO_CUMPLIDO");
        }
        
        if (monto.compareTo(new BigDecimal("100000")) > 0) {
            return Response.error("El monto máximo de préstamo es $100,000", "MONTO_MAXIMO_EXCEDIDO");
        }
        
        if (plazoMeses > 60) {
            return Response.error("El plazo máximo es 60 meses", "PLAZO_MAXIMO_EXCEDIDO");
        }
        
        return Response.success("Validación exitosa");
    }

    public Response<Prestamo> obtenerPrestamoPorId(Long id) {
        Optional<Prestamo> prestamo = prestamoRepository.findById(id);
        return prestamo.map(value -> Response.success("Prestamo encontrado", value)).orElseGet(() -> Response.error("Prestamo no encontrado", null));
    }

    public Response<Prestamo> evaluarPrestamo(Long id, double v, String approved, String s) {
        Optional<Prestamo> prestamo = prestamoRepository.findById(id);
        if (prestamo.isPresent()) {
            Prestamo p = prestamo.get();
            p.setEstado(Prestamo.Estado.valueOf(approved));
            prestamoRepository.save(p);
            return Response.success("Prestamo evaluado", p);
        }
        return Response.error("Prestamo no encontrado", null);
    }

    public Response<Prestamo> procesarAmortizacion(Long id, Double aDouble, java.time.LocalDateTime now) {
        Optional<Prestamo> prestamo = prestamoRepository.findById(id);
        if (prestamo.isPresent()) {
            Prestamo p = prestamo.get();
            p.setSaldoPendiente(p.getSaldoPendiente().subtract(BigDecimal.valueOf(aDouble)));
            prestamoRepository.save(p);
            return Response.success("Amortizacion procesada", p);
        }
        return Response.error("Prestamo no encontrado", null);
    }

    public Response<List<Prestamo>> obtenerPrestamosPorCliente(Long id) {
        List<Prestamo> prestamos = prestamoRepository.findByClienteId(id);
        return Response.success("Prestamos encontrados", prestamos);
    }
}