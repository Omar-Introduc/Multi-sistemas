package com.banco.shibasito.listener;

import com.banco.shibasito.dto.Response;
import com.banco.shibasito.dto.PrestamoRequest;
import com.banco.shibasito.dto.PrestamoResponse;
import com.banco.shibasito.entity.Prestamo;
import com.banco.shibasito.entity.Cliente;
import com.banco.shibasito.service.PrestamoService;
import com.banco.shibasito.service.ClienteService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.config.SimpleRabbitListenerContainerFactory;
import org.springframework.amqp.rabbit.listener.exception.ListenerExecutionFailedException;
import org.springframework.amqp.support.AmqpHeaders;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.Map;

/**
 * Listener para procesamiento de solicitudes de préstamos
 * 
 * Procesa mensajes de RabbitMQ relacionados con solicitudes de préstamos
 * bancarias enviadas desde LP3 y otros servicios del sistema. Maneja
 * solicitudes, evaluaciones, aprobaciones y rechazos de préstamos.
 * 
 * Configurado con acknowledgment manual para garantizar procesamiento
 * confiable y seguimiento de solicitudes de préstamos.
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
@Component
public class PrestamoListener {

    private static final Logger logger = LoggerFactory.getLogger(PrestamoListener.class);

    @Autowired
    private PrestamoService prestamoService;

    @Autowired
    private ClienteService clienteService;

    @Autowired
    private ObjectMapper objectMapper;

    /**
     * Procesa solicitudes de nuevos préstamos
     * 
     * @param mensaje JSON con datos de la solicitud de préstamo
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.prestamo.request:banco.prestamo.solicitud.nuevo}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarSolicitudNuevoPrestamo(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String requestId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando solicitud de nuevo préstamo. RequestId: {}, Mensaje: {}", 
                       requestId, mensaje);

            // Parsear mensaje JSON
            SolicitudPrestamoRequest request = objectMapper.readValue(mensaje, SolicitudPrestamoRequest.class);
            
            // Verificar que el cliente existe
            Response<Cliente> clienteResponse = clienteService.obtenerClientePorId(request.getClienteId());
            
            if (!clienteResponse.isSuccess()) {
                logger.warn("Cliente no encontrado para solicitud de préstamo. RequestId: {}, ClienteId: {}", 
                           requestId, request.getClienteId());
                return;
            }

            // Crear objeto PrestamoRequest
            PrestamoRequest prestamoRequest = new PrestamoRequest();
            prestamoRequest.setClienteId(request.getClienteId());
            prestamoRequest.setMonto(request.getMonto());
            prestamoRequest.setPlazoMeses(request.getPlazoMeses());
            prestamoRequest.setTipoPrestamo(request.getTipoPrestamo());
            prestamoRequest.setTasaInteres(request.getTasaInteres());
            prestamoRequest.setProposito(request.getProposito());

            // Procesar solicitud de préstamo
            Response<PrestamoResponse> response = prestamoService.solicitarPrestamo(prestamoRequest);

            if (response.isSuccess()) {
                logger.info("Solicitud de préstamo procesada exitosamente. RequestId: {}, PrestamoId: {}, ClienteId: {}, Monto: {}, Estado: {}", 
                           requestId, response.getData().getId(), request.getClienteId(), 
                           response.getData().getMonto(), response.getData().getEstado());
            } else {
                logger.warn("Error al procesar solicitud de préstamo. RequestId: {}, Error: {}, Código: {}", 
                           requestId, response.getMessage(), response.getErrorCode());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de solicitud de préstamo. RequestId: {}, Mensaje: {}, Error: {}", 
                        requestId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de préstamo. RequestId: {}, Error: {}", 
                        requestId, e.getMessage(), e);
        }
    }

    /**
     * Procesa solicitudes de evaluación de préstamos
     * 
     * @param mensaje JSON con datos de evaluación
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.prestamo.request:banco.prestamo.solicitud.evaluacion}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarSolicitudEvaluacion(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String requestId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando solicitud de evaluación de préstamo. RequestId: {}, Mensaje: {}", 
                       requestId, mensaje);

            // Parsear mensaje JSON
            EvaluacionPrestamoRequest request = objectMapper.readValue(mensaje, EvaluacionPrestamoRequest.class);
            
            // Buscar préstamo existente
            Response<Prestamo> prestamoResponse = prestamoService.obtenerPrestamoPorId(request.getPrestamoId());
            
            if (!prestamoResponse.isSuccess()) {
                logger.warn("Préstamo no encontrado para evaluación. RequestId: {}, PrestamoId: {}", 
                           requestId, request.getPrestamoId());
                return;
            }

            Prestamo prestamo = prestamoResponse.getData();
            
            // Realizar evaluación automática
            EvaluacionResult evaluacion = realizarEvaluacionAutomatica(prestamo, request);
            
            // Actualizar estado del préstamo basado en la evaluación
            String nuevoEstado = evaluacion.isAprobado() ? "APROBADO" : "RECHAZADO";
            
            Response<PrestamoResponse> response = prestamoService.evaluarPrestamo(
                    request.getPrestamoId(), 
                    evaluacion.getPuntuacionCrediticia(), 
                    nuevoEstado,
                    evaluacion.getObservaciones()
            );

            if (response.isSuccess()) {
                logger.info("Evaluación de préstamo completada. RequestId: {}, PrestamoId: {}, Estado: {}, Puntuación: {}", 
                           requestId, request.getPrestamoId(), nuevoEstado, evaluacion.getPuntuacionCrediticia());
            } else {
                logger.warn("Error al evaluar préstamo. RequestId: {}, Error: {}, Código: {}", 
                           requestId, response.getMessage(), response.getErrorCode());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de solicitud de evaluación. RequestId: {}, Mensaje: {}, Error: {}", 
                        requestId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de evaluación. RequestId: {}, Error: {}", 
                        requestId, e.getMessage(), e);
        }
    }

    /**
     * Procesa solicitudes de amortización de préstamos
     * 
     * @param mensaje JSON con datos de amortización
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.prestamo.request:banco.prestamo.solicitud.amortizacion}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarSolicitudAmortizacion(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String requestId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando solicitud de amortización de préstamo. RequestId: {}, Mensaje: {}", 
                       requestId, mensaje);

            // Parsear mensaje JSON
            AmortizacionRequest request = objectMapper.readValue(mensaje, AmortizacionRequest.class);
            
            // Buscar préstamo existente
            Response<Prestamo> prestamoResponse = prestamoService.obtenerPrestamoPorId(request.getPrestamoId());
            
            if (!prestamoResponse.isSuccess()) {
                logger.warn("Préstamo no encontrado para amortización. RequestId: {}, PrestamoId: {}", 
                           requestId, request.getPrestamoId());
                return;
            }

            // Procesar amortización
            Response response = prestamoService.procesarAmortizacion(
                    request.getPrestamoId(), 
                    request.getMonto(), 
                    request.getFechaPago()
            );

            if (response.isSuccess()) {
                logger.info("Amortización procesada exitosamente. RequestId: {}, PrestamoId: {}, Monto: {}, FechaPago: {}", 
                           requestId, request.getPrestamoId(), request.getMonto(), request.getFechaPago());
            } else {
                logger.warn("Error al procesar amortización. RequestId: {}, Error: {}, Código: {}", 
                           requestId, response.getMessage(), response.getErrorCode());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de solicitud de amortización. RequestId: {}, Mensaje: {}, Error: {}", 
                        requestId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de amortización. RequestId: {}, Error: {}", 
                        requestId, e.getMessage(), e);
        }
    }

    /**
     * Procesa solicitudes de consulta de estado de préstamos
     * 
     * @param mensaje JSON con criterios de búsqueda
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.prestamo.request:banco.prestamo.solicitud.consulta}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarSolicitudConsulta(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String requestId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando solicitud de consulta de préstamo. RequestId: {}, Mensaje: {}", 
                       requestId, mensaje);

            // Parsear mensaje JSON
            ConsultaPrestamoRequest request = objectMapper.readValue(mensaje, ConsultaPrestamoRequest.class);
            
            Response response;
            
            // Determinar tipo de consulta
            if (request.getPrestamoId() != null) {
                response = prestamoService.obtenerPrestamoPorId(request.getPrestamoId());
            } else if (request.getClienteId() != null) {
                response = prestamoService.obtenerPrestamosPorCliente(request.getClienteId());
            } else {
                logger.warn("Solicitud de consulta sin criterios válidos. RequestId: {}", requestId);
                return;
            }

            if (response.isSuccess()) {
                logger.info("Consulta de préstamo exitosa. RequestId: {}, TipoConsulta: {}", 
                           requestId, request.getPrestamoId() != null ? "Por ID" : "Por Cliente");
            } else {
                logger.warn("Error en consulta de préstamo. RequestId: {}, Error: {}, Código: {}", 
                           requestId, response.getMessage(), response.getErrorCode());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de solicitud de consulta. RequestId: {}, Mensaje: {}, Error: {}", 
                        requestId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de consulta. RequestId: {}, Error: {}", 
                        requestId, e.getMessage(), e);
        }
    }

    /**
     * Realiza evaluación automática del préstamo
     */
    private EvaluacionResult realizarEvaluacionAutomatica(Prestamo prestamo, EvaluacionPrestamoRequest request) {
        // Simulación de evaluación automática
        // En una implementación real, esto consultaría historial crediticio, capacidad de pago, etc.
        
        double puntuacion = 0.0;
        String observaciones = "";
        boolean aprobado = false;

        // Factores de evaluación simplificados
        if (prestamo.getMonto() != null && request.getIngresosMensuales() != null) {
            double ratioDeudaIngreso = prestamo.getMonto() / request.getIngresosMensuales();
            if (ratioDeudaIngreso <= 0.3) {
                puntuacion += 40;
            } else if (ratioDeudaIngreso <= 0.5) {
                puntuacion += 20;
            } else {
                puntuacion += 5;
                observaciones += "Ratio deuda-ingreso alto. ";
            }
        }

        if ("EMPLEADO".equals(request.getTipoEmpleo()) || "PROFESIONAL".equals(request.getTipoEmpleo())) {
            puntuacion += 30;
            observaciones += "Ingresos estables. ";
        }

        if (request.getAntiguedadLaboral() != null && request.getAntiguedadLaboral() >= 12) {
            puntuacion += 20;
            observaciones += "Antigüedad laboral adecuada. ";
        }

        if (request.getScoreCrediticio() != null) {
            puntuacion += request.getScoreCrediticio() / 10.0; // Normalizar score
        }

        aprobado = puntuacion >= 70;

        return new EvaluacionResult(aprobado, puntuacion, observaciones);
    }

    // Clases internas para request/response

    /**
     * Clase para representar solicitud de nuevo préstamo
     */
    public static class SolicitudPrestamoRequest {
        private Long clienteId;
        private Double monto;
        private Integer plazoMeses;
        private String tipoPrestamo;
        private Double tasaInteres;
        private String proposito;

        // Constructores
        public SolicitudPrestamoRequest() {
        }

        // Getters y Setters
        public Long getClienteId() { return clienteId; }
        public void setClienteId(Long clienteId) { this.clienteId = clienteId; }
        public Double getMonto() { return monto; }
        public void setMonto(Double monto) { this.monto = monto; }
        public Integer getPlazoMeses() { return plazoMeses; }
        public void setPlazoMeses(Integer plazoMeses) { this.plazoMeses = plazoMeses; }
        public String getTipoPrestamo() { return tipoPrestamo; }
        public void setTipoPrestamo(String tipoPrestamo) { this.tipoPrestamo = tipoPrestamo; }
        public Double getTasaInteres() { return tasaInteres; }
        public void setTasaInteres(Double tasaInteres) { this.tasaInteres = tasaInteres; }
        public String getProposito() { return proposito; }
        public void setProposito(String proposito) { this.proposito = proposito; }
    }

    /**
     * Clase para representar solicitud de evaluación
     */
    public static class EvaluacionPrestamoRequest {
        private Long prestamoId;
        private Double ingresosMensuales;
        private String tipoEmpleo;
        private Integer antiguedadLaboral;
        private Integer scoreCrediticio;

        // Constructores
        public EvaluacionPrestamoRequest() {
        }

        // Getters y Setters
        public Long getPrestamoId() { return prestamoId; }
        public void setPrestamoId(Long prestamoId) { this.prestamoId = prestamoId; }
        public Double getIngresosMensuales() { return ingresosMensuales; }
        public void setIngresosMensuales(Double ingresosMensuales) { this.ingresosMensuales = ingresosMensuales; }
        public String getTipoEmpleo() { return tipoEmpleo; }
        public void setTipoEmpleo(String tipoEmpleo) { this.tipoEmpleo = tipoEmpleo; }
        public Integer getAntiguedadLaboral() { return antiguedadLaboral; }
        public void setAntiguedadLaboral(Integer antiguedadLaboral) { this.antiguedadLaboral = antiguedadLaboral; }
        public Integer getScoreCrediticio() { return scoreCrediticio; }
        public void setScoreCrediticio(Integer scoreCrediticio) { this.scoreCrediticio = scoreCrediticio; }
    }

    /**
     * Clase para representar solicitud de amortización
     */
    public static class AmortizacionRequest {
        private Long prestamoId;
        private Double monto;
        private java.time.LocalDateTime fechaPago;

        // Constructores
        public AmortizacionRequest() {
        }

        // Getters y Setters
        public Long getPrestamoId() { return prestamoId; }
        public void setPrestamoId(Long prestamoId) { this.prestamoId = prestamoId; }
        public Double getMonto() { return monto; }
        public void setMonto(Double monto) { this.monto = monto; }
        public java.time.LocalDateTime getFechaPago() { return fechaPago; }
        public void setFechaPago(java.time.LocalDateTime fechaPago) { this.fechaPago = fechaPago; }
    }

    /**
     * Clase para representar solicitud de consulta
     */
    public static class ConsultaPrestamoRequest {
        private Long prestamoId;
        private Long clienteId;

        // Constructores
        public ConsultaPrestamoRequest() {
        }

        // Getters y Setters
        public Long getPrestamoId() { return prestamoId; }
        public void setPrestamoId(Long prestamoId) { this.prestamoId = prestamoId; }
        public Long getClienteId() { return clienteId; }
        public void setClienteId(Long clienteId) { this.clienteId = clienteId; }
    }

    /**
     * Clase para representar resultado de evaluación
     */
    public static class EvaluacionResult {
        private boolean aprobado;
        private double puntuacionCrediticia;
        private String observaciones;

        public EvaluacionResult(boolean aprobado, double puntuacionCrediticia, String observaciones) {
            this.aprobado = aprobado;
            this.puntuacionCrediticia = puntuacionCrediticia;
            this.observaciones = observaciones;
        }

        // Getters
        public boolean isAprobado() { return aprobado; }
        public double getPuntuacionCrediticia() { return puntuacionCrediticia; }
        public String getObservaciones() { return observaciones; }
    }
}
