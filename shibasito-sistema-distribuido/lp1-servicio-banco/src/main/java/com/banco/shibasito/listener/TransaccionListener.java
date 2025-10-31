package com.banco.shibasito.listener;

import com.banco.shibasito.dto.Response;
import com.banco.shibasito.dto.TransaccionRequest;
import com.banco.shibasito.dto.TransaccionResponse;
import com.banco.shibasito.entity.Transaccion;
import com.banco.shibasito.service.TransaccionService;
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

import java.util.Map;

/**
 * Listener para procesamiento de transacciones de clientes
 * 
 * Procesa mensajes de RabbitMQ relacionados con transacciones bancarias
 * enviadas desde LP3 y otros servicios del sistema. Maneja transferencias,
 * depósitos, retiros y consultas de saldo de manera asíncrona.
 * 
 * Configurado con acknowledgment manual para garantizar procesamiento
 * confiable y seguimiento de transacciones.
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
@Component
public class TransaccionListener {

    private static final Logger logger = LoggerFactory.getLogger(TransaccionListener.class);

    @Autowired
    private TransaccionService transaccionService;

    @Autowired
    private ObjectMapper objectMapper;

    /**
     * Procesa solicitudes de transferencias entre cuentas
     * 
     * @param mensaje JSON con datos de la transferencia
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.transaccion.request:banco.transaccion.solicitud.transferencia}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarSolicitudTransferencia(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String requestId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando solicitud de transferencia. RequestId: {}, Mensaje: {}", 
                       requestId, mensaje);

            // Parsear mensaje JSON
            TransferenciaRequest request = objectMapper.readValue(mensaje, TransferenciaRequest.class);
            
            // Crear objeto TransaccionRequest
            TransaccionRequest transaccionRequest = new TransaccionRequest();
            transaccionRequest.setCuentaOrigen(request.getCuentaOrigen());
            transaccionRequest.setCuentaDestino(request.getCuentaDestino());
            transaccionRequest.setMonto(request.getMonto());
            transaccionRequest.setTipoTransaccion("TRANSFERENCIA");
            transaccionRequest.setDescripcion(request.getDescripcion());

            // Procesar transferencia
            Response<TransaccionResponse> response = transaccionService.procesarTransaccion(transaccionRequest);

            if (response.isSuccess()) {
                logger.info("Transferencia procesada exitosamente. RequestId: {}, TransaccionId: {}, Monto: {}", 
                           requestId, response.getData().getId(), response.getData().getMonto());
            } else {
                logger.warn("Error al procesar transferencia. RequestId: {}, Error: {}, Código: {}", 
                           requestId, response.getMessage(), response.getErrorCode());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de solicitud de transferencia. RequestId: {}, Mensaje: {}, Error: {}", 
                        requestId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de transferencia. RequestId: {}, Error: {}", 
                        requestId, e.getMessage(), e);
        }
    }

    /**
     * Procesa solicitudes de depósitos a cuentas
     * 
     * @param mensaje JSON con datos del depósito
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.transaccion.request:banco.transaccion.solicitud.deposito}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarSolicitudDeposito(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String requestId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando solicitud de depósito. RequestId: {}, Mensaje: {}", 
                       requestId, mensaje);

            // Parsear mensaje JSON
            DepositoRequest request = objectMapper.readValue(mensaje, DepositoRequest.class);
            
            // Crear objeto TransaccionRequest
            TransaccionRequest transaccionRequest = new TransaccionRequest();
            transaccionRequest.setCuentaOrigen("CAJERO");  // Cuenta del cajero/sistema
            transaccionRequest.setCuentaDestino(request.getCuentaDestino());
            transaccionRequest.setMonto(request.getMonto());
            transaccionRequest.setTipoTransaccion("DEPOSITO");
            transaccionRequest.setDescripcion(request.getDescripcion());

            // Procesar depósito
            Response<TransaccionResponse> response = transaccionService.procesarTransaccion(transaccionRequest);

            if (response.isSuccess()) {
                logger.info("Depósito procesado exitosamente. RequestId: {}, TransaccionId: {}, Cuenta: {}, Monto: {}", 
                           requestId, response.getData().getId(), response.getData().getCuentaDestino(), response.getData().getMonto());
            } else {
                logger.warn("Error al procesar depósito. RequestId: {}, Error: {}, Código: {}", 
                           requestId, response.getMessage(), response.getErrorCode());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de solicitud de depósito. RequestId: {}, Mensaje: {}, Error: {}", 
                        requestId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de depósito. RequestId: {}, Error: {}", 
                        requestId, e.getMessage(), e);
        }
    }

    /**
     * Procesa solicitudes de retiros de cuentas
     * 
     * @param mensaje JSON con datos del retiro
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.transaccion.request:banco.transaccion.solicitud.retiro}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarSolicitudRetiro(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String requestId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando solicitud de retiro. RequestId: {}, Mensaje: {}", 
                       requestId, mensaje);

            // Parsear mensaje JSON
            RetiroRequest request = objectMapper.readValue(mensaje, RetiroRequest.class);
            
            // Crear objeto TransaccionRequest
            TransaccionRequest transaccionRequest = new TransaccionRequest();
            transaccionRequest.setCuentaOrigen(request.getCuentaOrigen());
            transaccionRequest.setCuentaDestino("CAJERO");  // Cuenta del cajero/sistema
            transaccionRequest.setMonto(request.getMonto());
            transaccionRequest.setTipoTransaccion("RETIRO");
            transaccionRequest.setDescripcion(request.getDescripcion());

            // Procesar retiro
            Response<TransaccionResponse> response = transaccionService.procesarTransaccion(transaccionRequest);

            if (response.isSuccess()) {
                logger.info("Retiro procesado exitosamente. RequestId: {}, TransaccionId: {}, Cuenta: {}, Monto: {}", 
                           requestId, response.getData().getId(), response.getData().getCuentaOrigen(), response.getData().getMonto());
            } else {
                logger.warn("Error al procesar retiro. RequestId: {}, Error: {}, Código: {}", 
                           requestId, response.getMessage(), response.getErrorCode());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de solicitud de retiro. RequestId: {}, Mensaje: {}, Error: {}", 
                        requestId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de retiro. RequestId: {}, Error: {}", 
                        requestId, e.getMessage(), e);
        }
    }

    /**
     * Procesa solicitudes de consulta de historial de transacciones
     * 
     * @param mensaje JSON con criterios de búsqueda
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.transaccion.request:banco.transaccion.solicitud.historial}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarSolicitudHistorial(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String requestId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando solicitud de historial de transacciones. RequestId: {}, Mensaje: {}", 
                       requestId, mensaje);

            // Parsear mensaje JSON
            HistorialRequest request = objectMapper.readValue(mensaje, HistorialRequest.class);
            
            // Procesar consulta de historial
            Response response = transaccionService.obtenerHistorialTransacciones(
                    request.getCuentaId(), 
                    request.getFechaInicio(), 
                    request.getFechaFin()
            );

            if (response.isSuccess()) {
                logger.info("Historial de transacciones obtenido exitosamente. RequestId: {}, Cuenta: {}, Registros: {}", 
                           requestId, request.getCuentaId(), 
                           response.getData() != null ? ((java.util.List) response.getData()).size() : 0);
            } else {
                logger.warn("Error al obtener historial de transacciones. RequestId: {}, Error: {}, Código: {}", 
                           requestId, response.getMessage(), response.getErrorCode());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de solicitud de historial. RequestId: {}, Mensaje: {}, Error: {}", 
                        requestId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de historial. RequestId: {}, Error: {}", 
                        requestId, e.getMessage(), e);
        }
    }

    /**
     * Procesa eventos de reversión de transacciones
     * 
     * @param mensaje JSON con datos de reversión
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.transaccion.request:banco.transaccion.solicitud.reversion}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarSolicitudReversion(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String requestId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando solicitud de reversión de transacción. RequestId: {}, Mensaje: {}", 
                       requestId, mensaje);

            // Parsear mensaje JSON
            ReversionRequest request = objectMapper.readValue(mensaje, ReversionRequest.class);
            
            // Buscar transacción original
            Response<Transaccion> transaccionResponse = transaccionService.obtenerTransaccionPorId(request.getTransaccionId());
            
            if (!transaccionResponse.isSuccess()) {
                logger.warn("Transacción original no encontrada para reversión. RequestId: {}, TransaccionId: {}", 
                           requestId, request.getTransaccionId());
                return;
            }

            Transaccion transaccionOriginal = transaccionResponse.getData();
            
            // Crear transacción de reversión
            TransaccionRequest reversoRequest = new TransaccionRequest();
            reversoRequest.setCuentaOrigen(transaccionOriginal.getCuentaDestino());
            reversoRequest.setCuentaDestino(transaccionOriginal.getCuentaOrigen());
            reversoRequest.setMonto(transaccionOriginal.getMonto());
            reversoRequest.setTipoTransaccion("REVERSION");
            reversoRequest.setDescripcion("Reversión de transacción: " + request.getMotivo());

            // Procesar reversión
            Response<TransaccionResponse> response = transaccionService.procesarTransaccion(reversoRequest);

            if (response.isSuccess()) {
                logger.info("Reversión procesada exitosamente. RequestId: {}, TransaccionOriginalId: {}, TransaccionReversaId: {}", 
                           requestId, request.getTransaccionId(), response.getData().getId());
            } else {
                logger.warn("Error al procesar reversión. RequestId: {}, Error: {}, Código: {}", 
                           requestId, response.getMessage(), response.getErrorCode());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de solicitud de reversión. RequestId: {}, Mensaje: {}, Error: {}", 
                        requestId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de reversión. RequestId: {}, Error: {}", 
                        requestId, e.getMessage(), e);
        }
    }

    // Clases internas para request/response

    /**
     * Clase para representar solicitud de transferencia
     */
    public static class TransferenciaRequest {
        private String cuentaOrigen;
        private String cuentaDestino;
        private Double monto;
        private String descripcion;

        // Constructores
        public TransferenciaRequest() {
        }

        // Getters y Setters
        public String getCuentaOrigen() { return cuentaOrigen; }
        public void setCuentaOrigen(String cuentaOrigen) { this.cuentaOrigen = cuentaOrigen; }
        public String getCuentaDestino() { return cuentaDestino; }
        public void setCuentaDestino(String cuentaDestino) { this.cuentaDestino = cuentaDestino; }
        public Double getMonto() { return monto; }
        public void setMonto(Double monto) { this.monto = monto; }
        public String getDescripcion() { return descripcion; }
        public void setDescripcion(String descripcion) { this.descripcion = descripcion; }
    }

    /**
     * Clase para representar solicitud de depósito
     */
    public static class DepositoRequest {
        private String cuentaDestino;
        private Double monto;
        private String descripcion;

        // Constructores
        public DepositoRequest() {
        }

        // Getters y Setters
        public String getCuentaDestino() { return cuentaDestino; }
        public void setCuentaDestino(String cuentaDestino) { this.cuentaDestino = cuentaDestino; }
        public Double getMonto() { return monto; }
        public void setMonto(Double monto) { this.monto = monto; }
        public String getDescripcion() { return descripcion; }
        public void setDescripcion(String descripcion) { this.descripcion = descripcion; }
    }

    /**
     * Clase para representar solicitud de retiro
     */
    public static class RetiroRequest {
        private String cuentaOrigen;
        private Double monto;
        private String descripcion;

        // Constructores
        public RetiroRequest() {
        }

        // Getters y Setters
        public String getCuentaOrigen() { return cuentaOrigen; }
        public void setCuentaOrigen(String cuentaOrigen) { this.cuentaOrigen = cuentaOrigen; }
        public Double getMonto() { return monto; }
        public void setMonto(Double monto) { this.monto = monto; }
        public String getDescripcion() { return descripcion; }
        public void setDescripcion(String descripcion) { this.descripcion = descripcion; }
    }

    /**
     * Clase para representar solicitud de historial
     */
    public static class HistorialRequest {
        private Long cuentaId;
        private java.time.LocalDateTime fechaInicio;
        private java.time.LocalDateTime fechaFin;

        // Constructores
        public HistorialRequest() {
        }

        // Getters y Setters
        public Long getCuentaId() { return cuentaId; }
        public void setCuentaId(Long cuentaId) { this.cuentaId = cuentaId; }
        public java.time.LocalDateTime getFechaInicio() { return fechaInicio; }
        public void setFechaInicio(java.time.LocalDateTime fechaInicio) { this.fechaInicio = fechaInicio; }
        public java.time.LocalDateTime getFechaFin() { return fechaFin; }
        public void setFechaFin(java.time.LocalDateTime fechaFin) { this.fechaFin = fechaFin; }
    }

    /**
     * Clase para representar solicitud de reversión
     */
    public static class ReversionRequest {
        private Long transaccionId;
        private String motivo;

        // Constructores
        public ReversionRequest() {
        }

        // Getters y Setters
        public Long getTransaccionId() { return transaccionId; }
        public void setTransaccionId(Long transaccionId) { this.transaccionId = transaccionId; }
        public String getMotivo() { return motivo; }
        public void setMotivo(String motivo) { this.motivo = motivo; }
    }
}
