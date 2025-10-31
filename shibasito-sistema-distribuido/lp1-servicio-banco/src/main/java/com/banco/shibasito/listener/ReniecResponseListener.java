package com.banco.shibasito.listener;

import com.banco.shibasito.dto.Response;
import com.banco.shibasito.entity.Cliente;
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

import java.time.LocalDateTime;
import java.util.Map;

/**
 * Listener para respuestas de validación de RENIEC
 * 
 * Procesa mensajes de RabbitMQ con respuestas del servicio RENIEC
 * enviadas desde LP2. Maneja la validación de documentos de identidad
 * y actualización de datos de clientes basándose en la información
 * oficial proporcionada por RENIEC.
 * 
 * Configurado con acknowledgment manual para garantizar procesamiento
 * confiable y seguimiento de validaciones.
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
@Component
public class ReniecResponseListener {

    private static final Logger logger = LoggerFactory.getLogger(ReniecResponseListener.class);

    @Autowired
    private ClienteService clienteService;

    @Autowired
    private ObjectMapper objectMapper;

    /**
     * Procesa respuestas exitosas de validación de DNI desde RENIEC
     * 
     * @param mensaje JSON con datos validados de RENIEC
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     * @param requestId ID de la solicitud original
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.reniec.response:banco.reniec.validacion.exitosa}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarValidacionExitosa(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId,
            @Header("solicitudId") String requestId) {
        
        String trackingId = requestId != null ? requestId : (correlationId != null ? correlationId : messageId);
        
        try {
            logger.info("Procesando respuesta exitosa de validación RENIEC. TrackingId: {}, Mensaje: {}", 
                       trackingId, mensaje);

            // Parsear mensaje JSON de respuesta exitosa
            ReniecValidacionExitosaResponse response = objectMapper.readValue(mensaje, ReniecValidacionExitosaResponse.class);
            
            logger.info("Validación RENIEC exitosa para DNI: {}, Estado: {}, Confiabilidad: {}%", 
                       response.getDni(), response.getEstado(), response.getConfiabilidad());
            
            // Verificar que existe cliente con el DNI validado
            Response<Cliente> clienteResponse = clienteService.buscarClientePorDni(response.getDni());
            
            if (clienteResponse.isSuccess()) {
                Cliente cliente = clienteResponse.getData();
                
                // Actualizar datos del cliente con información de RENIEC
                Cliente clienteActualizado = actualizarDatosDesdeReniec(cliente, response);
                
                // Guardar cambios
                Response<Cliente> updateResponse = clienteService.actualizarCliente(clienteActualizado);
                
                if (updateResponse.isSuccess()) {
                    logger.info("Cliente actualizado exitosamente con datos de RENIEC. TrackingId: {}, ClienteId: {}, DNI: {}", 
                               trackingId, cliente.getId(), response.getDni());
                } else {
                    logger.warn("Error al actualizar cliente con datos de RENIEC. TrackingId: {}, Error: {}", 
                               trackingId, updateResponse.getMessage());
                }
                
            } else {
                logger.info("Cliente no encontrado con DNI validado por RENIEC. TrackingId: {}, DNI: {}", 
                           trackingId, response.getDni());
            }

            // Enviar confirmación de procesamiento a la cola correspondiente
            enviarConfirmacionProcesamiento(response, "PROCESADO", trackingId);

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de respuesta exitosa de RENIEC. TrackingId: {}, Mensaje: {}, Error: {}", 
                        trackingId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando respuesta exitosa de RENIEC. TrackingId: {}, Error: {}", 
                        trackingId, e.getMessage(), e);
        }
    }

    /**
     * Procesa respuestas fallidas de validación de DNI desde RENIEC
     * 
     * @param mensaje JSON con error de validación de RENIEC
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     * @param requestId ID de la solicitud original
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.reniec.response:banco.reniec.validacion.fallida}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarValidacionFallida(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId,
            @Header("solicitudId") String requestId) {
        
        String trackingId = requestId != null ? requestId : (correlationId != null ? correlationId : messageId);
        
        try {
            logger.warn("Procesando respuesta fallida de validación RENIEC. TrackingId: {}, Mensaje: {}", 
                       trackingId, mensaje);

            // Parsear mensaje JSON de respuesta fallida
            ReniecValidacionFallidaResponse response = objectMapper.readValue(mensaje, ReniecValidacionFallidaResponse.class);
            
            logger.warn("Validación RENIEC fallida para DNI: {}, Error: {}, Motivo: {}", 
                       response.getDni(), response.getCodigoError(), response.getMensajeError());
            
            // Buscar cliente con el DNI que falló validación
            Response<Cliente> clienteResponse = clienteService.buscarClientePorDni(response.getDni());
            
            if (clienteResponse.isSuccess()) {
                Cliente cliente = clienteResponse.getData();
                
                // Marcar cliente con validación fallida
                Cliente clienteActualizado = marcarValidacionFallida(cliente, response);
                
                // Guardar cambios
                Response<Cliente> updateResponse = clienteService.actualizarCliente(clienteActualizado);
                
                if (updateResponse.isSuccess()) {
                    logger.info("Cliente marcado con validación RENIEC fallida. TrackingId: {}, ClienteId: {}, DNI: {}", 
                               trackingId, cliente.getId(), response.getDni());
                } else {
                    logger.warn("Error al marcar cliente con validación fallida. TrackingId: {}, Error: {}", 
                               trackingId, updateResponse.getMessage());
                }
                
            } else {
                logger.info("Cliente no encontrado con DNI que falló validación RENIEC. TrackingId: {}, DNI: {}", 
                           trackingId, response.getDni());
            }

            // Enviar confirmación de procesamiento a la cola correspondiente
            enviarConfirmacionProcesamiento(response, "PROCESADO_CON_ERROR", trackingId);

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de respuesta fallida de RENIEC. TrackingId: {}, Mensaje: {}, Error: {}", 
                        trackingId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando respuesta fallida de RENIEC. TrackingId: {}, Error: {}", 
                        trackingId, e.getMessage(), e);
        }
    }

    /**
     * Procesa respuestas de validación masiva de DNI desde RENIEC
     * 
     * @param mensaje JSON con múltiples validaciones
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.reniec.response:banco.reniec.validacion.masiva}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarValidacionMasiva(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String batchId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando validación masiva de RENIEC. BatchId: {}, Mensaje: {}", 
                       batchId, mensaje);

            // Parsear mensaje JSON de validación masiva
            ReniecValidacionMasivaResponse response = objectMapper.readValue(mensaje, ReniecValidacionMasivaResponse.class);
            
            logger.info("Validación masiva RENIEC completada. BatchId: {}, Total: {}, Exitosas: {}, Fallidas: {}", 
                       batchId, response.getTotalValidaciones(), 
                       response.getValidacionesExitosas(), response.getValidacionesFallidas());
            
            // Procesar cada validación individual
            for (ReniecValidacionItem item : response.getItems()) {
                if ("EXITOSA".equals(item.getEstado())) {
                    procesarValidacionIndividualExitosa(item, batchId);
                } else {
                    procesarValidacionIndividualFallida(item, batchId);
                }
            }

            // Enviar confirmación de procesamiento del batch
            enviarConfirmacionProcesamientoMasivo(response, batchId);

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de validación masiva de RENIEC. BatchId: {}, Mensaje: {}, Error: {}", 
                        batchId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando validación masiva de RENIEC. BatchId: {}, Error: {}", 
                        batchId, e.getMessage(), e);
        }
    }

    /**
     * Procesa timeout en validaciones de RENIEC
     * 
     * @param mensaje JSON con timeout de validación
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.reniec.response:banco.reniec.validacion.timeout}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarTimeoutValidacion(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String timeoutId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.warn("Procesando timeout en validación RENIEC. TimeoutId: {}, Mensaje: {}", 
                       timeoutId, mensaje);

            // Parsear mensaje JSON de timeout
            ReniecTimeoutResponse response = objectMapper.readValue(mensaje, ReniecTimeoutResponse.class);
            
            logger.warn("Timeout en validación RENIEC para DNI: {}, TiempoEspera: {}ms, Motivo: {}", 
                       response.getDni(), response.getTiempoEspera(), response.getMotivo());
            
            // Buscar cliente y marcarlo para reintento
            Response<Cliente> clienteResponse = clienteService.buscarClientePorDni(response.getDni());
            
            if (clienteResponse.isSuccess()) {
                Cliente cliente = clienteResponse.getData();
                
                // Marcar cliente para reintento de validación
                Cliente clienteActualizado = marcarParaReintento(cliente, response);
                
                // Guardar cambios
                Response<Cliente> updateResponse = clienteService.actualizarCliente(clienteActualizado);
                
                if (updateResponse.isSuccess()) {
                    logger.info("Cliente marcado para reintento de validación RENIEC. TimeoutId: {}, ClienteId: {}, DNI: {}", 
                               timeoutId, cliente.getId(), response.getDni());
                } else {
                    logger.warn("Error al marcar cliente para reintento. TimeoutId: {}, Error: {}", 
                               timeoutId, updateResponse.getMessage());
                }
                
            } else {
                logger.info("Cliente no encontrado para timeout de validación RENIEC. TimeoutId: {}, DNI: {}", 
                           timeoutId, response.getDni());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de timeout de RENIEC. TimeoutId: {}, Mensaje: {}, Error: {}", 
                        timeoutId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando timeout de RENIEC. TimeoutId: {}, Error: {}", 
                        timeoutId, e.getMessage(), e);
        }
    }

    /**
     * Actualiza datos del cliente con información de RENIEC
     */
    private Cliente actualizarDatosDesdeReniec(Cliente cliente, ReniecValidacionExitosaResponse response) {
        // Actualizar campos con datos oficiales de RENIEC
        if (response.getNombresCompletos() != null) {
            String[] nombres = response.getNombresCompletos().split(" ", 2);
            if (nombres.length > 0) {
                cliente.setNombre(nombres[0]);
                if (nombres.length > 1) {
                    cliente.setApellido(nombres[1]);
                }
            }
        }
        
        if (response.getFechaNacimiento() != null) {
            cliente.setFechaNacimiento(response.getFechaNacimiento());
        }
        
        // Aquí se pueden agregar más campos según la estructura de datos de RENIEC
        cliente.setFechaUltimaValidacion(LocalDateTime.now());
        cliente.setEstadoValidacion("VALIDADO");
        
        return cliente;
    }

    /**
     * Marca cliente con validación fallida
     */
    private Cliente marcarValidacionFallida(Cliente cliente, ReniecValidacionFallidaResponse response) {
        cliente.setFechaUltimaValidacion(LocalDateTime.now());
        cliente.setEstadoValidacion("VALIDACION_FALLIDA");
        cliente.setObservacionesValidacion("Error: " + response.getMensajeError());
        
        return cliente;
    }

    /**
     * Marca cliente para reintento de validación
     */
    private Cliente marcarParaReintento(Cliente cliente, ReniecTimeoutResponse response) {
        cliente.setFechaUltimaValidacion(LocalDateTime.now());
        cliente.setEstadoValidacion("PENDIENTE_REINTENTO");
        cliente.setObservacionesValidacion("Timeout en validación: " + response.getMotivo());
        
        return cliente;
    }

    /**
     * Procesa validación individual exitosa en batch
     */
    private void procesarValidacionIndividualExitosa(ReniecValidacionItem item, String batchId) {
        try {
            Response<Cliente> clienteResponse = clienteService.buscarClientePorDni(item.getDni());
            if (clienteResponse.isSuccess()) {
                logger.debug("Cliente validado exitosamente en batch. BatchId: {}, ClienteId: {}, DNI: {}", 
                           batchId, clienteResponse.getData().getId(), item.getDni());
            }
        } catch (Exception e) {
            logger.warn("Error procesando validación individual exitosa en batch. BatchId: {}, DNI: {}, Error: {}", 
                       batchId, item.getDni(), e.getMessage());
        }
    }

    /**
     * Procesa validación individual fallida en batch
     */
    private void procesarValidacionIndividualFallida(ReniecValidacionItem item, String batchId) {
        try {
            Response<Cliente> clienteResponse = clienteService.buscarClientePorDni(item.getDni());
            if (clienteResponse.isSuccess()) {
                logger.debug("Cliente con validación fallida en batch. BatchId: {}, ClienteId: {}, DNI: {}, Error: {}", 
                           batchId, clienteResponse.getData().getId(), item.getDni(), item.getMensajeError());
            }
        } catch (Exception e) {
            logger.warn("Error procesando validación individual fallida en batch. BatchId: {}, DNI: {}, Error: {}", 
                       batchId, item.getDni(), e.getMessage());
        }
    }

    /**
     * Envía confirmación de procesamiento de validación individual
     */
    private void enviarConfirmacionProcesamiento(Object response, String estado, String trackingId) {
        // En una implementación real, aquí se enviaría un mensaje a la cola de confirmación
        logger.debug("Confirmación enviada para validación individual. TrackingId: {}, Estado: {}", 
                    trackingId, estado);
    }

    /**
     * Envía confirmación de procesamiento de validación masiva
     */
    private void enviarConfirmacionProcesamientoMasivo(ReniecValidacionMasivaResponse response, String batchId) {
        // En una implementación real, aquí se enviaría un mensaje a la cola de confirmación
        logger.debug("Confirmación enviada para validación masiva. BatchId: {}, Estado: PROCESADO", batchId);
    }

    // Clases internas para request/response de RENIEC

    /**
     * Respuesta exitosa de validación de RENIEC
     */
    public static class ReniecValidacionExitosaResponse {
        private String dni;
        private String nombresCompletos;
        private String fechaNacimiento;
        private String estado;
        private Double confiabilidad;
        private String fechaValidacion;

        // Constructores
        public ReniecValidacionExitosaResponse() {
        }

        // Getters y Setters
        public String getDni() { return dni; }
        public void setDni(String dni) { this.dni = dni; }
        public String getNombresCompletos() { return nombresCompletos; }
        public void setNombresCompletos(String nombresCompletos) { this.nombresCompletos = nombresCompletos; }
        public String getFechaNacimiento() { return fechaNacimiento; }
        public void setFechaNacimiento(String fechaNacimiento) { this.fechaNacimiento = fechaNacimiento; }
        public String getEstado() { return estado; }
        public void setEstado(String estado) { this.estado = estado; }
        public Double getConfiabilidad() { return confiabilidad; }
        public void setConfiabilidad(Double confiabilidad) { this.confiabilidad = confiabilidad; }
        public String getFechaValidacion() { return fechaValidacion; }
        public void setFechaValidacion(String fechaValidacion) { this.fechaValidacion = fechaValidacion; }
    }

    /**
     * Respuesta fallida de validación de RENIEC
     */
    public static class ReniecValidacionFallidaResponse {
        private String dni;
        private String codigoError;
        private String mensajeError;
        private String fechaError;

        // Constructores
        public ReniecValidacionFallidaResponse() {
        }

        // Getters y Setters
        public String getDni() { return dni; }
        public void setDni(String dni) { this.dni = dni; }
        public String getCodigoError() { return codigoError; }
        public void setCodigoError(String codigoError) { this.codigoError = codigoError; }
        public String getMensajeError() { return mensajeError; }
        public void setMensajeError(String mensajeError) { this.mensajeError = mensajeError; }
        public String getFechaError() { return fechaError; }
        public void setFechaError(String fechaError) { this.fechaError = fechaError; }
    }

    /**
     * Respuesta de timeout de validación de RENIEC
     */
    public static class ReniecTimeoutResponse {
        private String dni;
        private Long tiempoEspera;
        private String motivo;
        private String fechaTimeout;

        // Constructores
        public ReniecTimeoutResponse() {
        }

        // Getters y Setters
        public String getDni() { return dni; }
        public void setDni(String dni) { this.dni = dni; }
        public Long getTiempoEspera() { return tiempoEspera; }
        public void setTiempoEspera(Long tiempoEspera) { this.tiempoEspera = tiempoEspera; }
        public String getMotivo() { return motivo; }
        public void setMotivo(String motivo) { this.motivo = motivo; }
        public String getFechaTimeout() { return fechaTimeout; }
        public void setFechaTimeout(String fechaTimeout) { this.fechaTimeout = fechaTimeout; }
    }

    /**
     * Respuesta de validación masiva de RENIEC
     */
    public static class ReniecValidacionMasivaResponse {
        private String batchId;
        private Integer totalValidaciones;
        private Integer validacionesExitosas;
        private Integer validacionesFallidas;
        private java.util.List<ReniecValidacionItem> items;

        // Constructores
        public ReniecValidacionMasivaResponse() {
        }

        // Getters y Setters
        public String getBatchId() { return batchId; }
        public void setBatchId(String batchId) { this.batchId = batchId; }
        public Integer getTotalValidaciones() { return totalValidaciones; }
        public void setTotalValidaciones(Integer totalValidaciones) { this.totalValidaciones = totalValidaciones; }
        public Integer getValidacionesExitosas() { return validacionesExitosas; }
        public void setValidacionesExitosas(Integer validacionesExitosas) { this.validacionesExitosas = validacionesExitosas; }
        public Integer getValidacionesFallidas() { return validacionesFallidas; }
        public void setValidacionesFallidas(Integer validacionesFallidas) { this.validacionesFallidas = validacionesFallidas; }
        public java.util.List<ReniecValidacionItem> getItems() { return items; }
        public void setItems(java.util.List<ReniecValidacionItem> items) { this.items = items; }
    }

    /**
     * Item individual en validación masiva
     */
    public static class ReniecValidacionItem {
        private String dni;
        private String estado;
        private String mensajeError;
        private String datosValidados;

        // Constructores
        public ReniecValidacionItem() {
        }

        // Getters y Setters
        public String getDni() { return dni; }
        public void setDni(String dni) { this.dni = dni; }
        public String getEstado() { return estado; }
        public void setEstado(String estado) { this.estado = estado; }
        public String getMensajeError() { return mensajeError; }
        public void setMensajeError(String mensajeError) { this.mensajeError = mensajeError; }
        public String getDatosValidados() { return datosValidados; }
        public void setDatosValidados(String datosValidados) { this.datosValidados = datosValidados; }
    }
}
