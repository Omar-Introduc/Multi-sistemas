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

import java.util.Map;

/**
 * Listener para solicitudes de clientes desde LP3
 * 
 * Procesa mensajes de RabbitMQ relacionados con solicitudes de clientes
 * enviadas desde el microservicio LP3. Maneja la comunicación asíncrona
 * y procesamiento de solicitudes de registro y consulta de clientes.
 * 
 * Configurado con acknowledgment manual para garantizar procesamiento
 * confiable de mensajes.
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
@Component
public class ClienteRequestListener {

    private static final Logger logger = LoggerFactory.getLogger(ClienteRequestListener.class);

    @Autowired
    private ClienteService clienteService;

    @Autowired
    private ObjectMapper objectMapper;

    /**
     * Procesa solicitudes de registro de nuevos clientes desde LP3
     * 
     * @param mensaje JSON con datos del cliente
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.cliente.request:banco.cliente.solicitud.registro}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarSolicitudRegistroCliente(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String requestId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando solicitud de registro de cliente. RequestId: {}, Mensaje: {}", 
                       requestId, mensaje);

            // Parsear mensaje JSON
            ClienteRequest request = objectMapper.readValue(mensaje, ClienteRequest.class);
            
            // Crear entidad Cliente
            Cliente cliente = new Cliente();
            cliente.setDni(request.getDni());
            cliente.setNombre(request.getNombre());
            cliente.setApellido(request.getApellido());
            cliente.setEmail(request.getEmail());
            cliente.setTelefono(request.getTelefono());
            cliente.setDireccion(request.getDireccion());

            // Procesar en el servicio
            Response<Cliente> response = clienteService.crearCliente(cliente);

            if (response.isSuccess()) {
                logger.info("Cliente registrado exitosamente. RequestId: {}, ClienteId: {}, DNI: {}", 
                           requestId, response.getData().getId(), response.getData().getDni());
            } else {
                logger.warn("Error al registrar cliente. RequestId: {}, Error: {}, Código: {}", 
                           requestId, response.getMessage(), response.getErrorCode());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de solicitud de registro de cliente. RequestId: {}, Mensaje: {}, Error: {}", 
                        requestId, mensaje, e.getMessage(), e);
            
            // Enviar mensaje de error a cola de respuesta si existe
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de registro de cliente. RequestId: {}, Error: {}", 
                        requestId, e.getMessage(), e);
        }
    }

    /**
     * Procesa solicitudes de consulta de información de cliente desde LP3
     * 
     * @param mensaje JSON con criterios de búsqueda
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.cliente.request:banco.cliente.solicitud.consulta}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarSolicitudConsultaCliente(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String requestId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando solicitud de consulta de cliente. RequestId: {}, Mensaje: {}", 
                       requestId, mensaje);

            // Parsear mensaje JSON
            ClienteConsultaRequest request = objectMapper.readValue(mensaje, ClienteConsultaRequest.class);
            
            Response<Cliente> response;
            
            // Determinar tipo de consulta
            if (request.getDni() != null) {
                response = clienteService.buscarClientePorDni(request.getDni());
            } else if (request.getClienteId() != null) {
                response = clienteService.obtenerClientePorId(request.getClienteId());
            } else {
                logger.warn("Solicitud de consulta sin criterios válidos. RequestId: {}", requestId);
                return;
            }

            if (response.isSuccess()) {
                logger.info("Cliente encontrado. RequestId: {}, ClienteId: {}, DNI: {}", 
                           requestId, response.getData().getId(), response.getData().getDni());
            } else {
                logger.info("Cliente no encontrado. RequestId: {}, Criterio: {}, Error: {}", 
                           requestId, request.getDni() != null ? "DNI: " + request.getDni() : "ID: " + request.getClienteId(),
                           response.getMessage());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de solicitud de consulta de cliente. RequestId: {}, Mensaje: {}, Error: {}", 
                        requestId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de consulta de cliente. RequestId: {}, Error: {}", 
                        requestId, e.getMessage(), e);
        }
    }

    /**
     * Procesa solicitudes de actualización de datos de cliente desde LP3
     * 
     * @param mensaje JSON con datos actualizados del cliente
     * @param messageId ID del mensaje para tracking
     * @param correlationId ID de correlación para trazabilidad
     */
    @RabbitListener(
        queues = "${rabbitmq.queue.cliente.request:banco.cliente.solicitud.actualizacion}",
        containerFactory = "rabbitListenerContainerFactory"
    )
    public void procesarSolicitudActualizacionCliente(
            @Payload String mensaje,
            @Header(AmqpHeaders.MESSAGE_ID) String messageId,
            @Header(AmqpHeaders.CORRELATION_ID) String correlationId) {
        
        String requestId = correlationId != null ? correlationId : messageId;
        
        try {
            logger.info("Procesando solicitud de actualización de cliente. RequestId: {}, Mensaje: {}", 
                       requestId, mensaje);

            // Parsear mensaje JSON
            ClienteUpdateRequest request = objectMapper.readValue(mensaje, ClienteUpdateRequest.class);
            
            // Buscar cliente existente
            Response<Cliente> clienteResponse = clienteService.obtenerClientePorId(request.getClienteId());
            
            if (!clienteResponse.isSuccess()) {
                logger.warn("Cliente no encontrado para actualización. RequestId: {}, ClienteId: {}", 
                           requestId, request.getClienteId());
                return;
            }

            Cliente cliente = clienteResponse.getData();
            
            // Actualizar campos proporcionados
            if (request.getNombre() != null) cliente.setNombre(request.getNombre());
            if (request.getApellido() != null) cliente.setApellido(request.getApellido());
            if (request.getEmail() != null) cliente.setEmail(request.getEmail());
            if (request.getTelefono() != null) cliente.setTelefono(request.getTelefono());
            if (request.getDireccion() != null) cliente.setDireccion(request.getDireccion());

            // Procesar actualización
            Response<Cliente> response = clienteService.actualizarCliente(cliente);

            if (response.isSuccess()) {
                logger.info("Cliente actualizado exitosamente. RequestId: {}, ClienteId: {}, DNI: {}", 
                           requestId, response.getData().getId(), response.getData().getDni());
            } else {
                logger.warn("Error al actualizar cliente. RequestId: {}, Error: {}, Código: {}", 
                           requestId, response.getMessage(), response.getErrorCode());
            }

        } catch (JsonProcessingException e) {
            logger.error("Error al parsear JSON de solicitud de actualización de cliente. RequestId: {}, Mensaje: {}, Error: {}", 
                        requestId, mensaje, e.getMessage(), e);
            
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de actualización de cliente. RequestId: {}, Error: {}", 
                        requestId, e.getMessage(), e);
        }
    }

    // Clases internas para request/response

    /**
     * Clase para representar solicitud de registro de cliente
     */
    public static class ClienteRequest {
        private String dni;
        private String nombre;
        private String apellido;
        private String email;
        private String telefono;
        private String direccion;

        // Constructores
        public ClienteRequest() {
        }

        // Getters y Setters
        public String getDni() { return dni; }
        public void setDni(String dni) { this.dni = dni; }
        public String getNombre() { return nombre; }
        public void setNombre(String nombre) { this.nombre = nombre; }
        public String getApellido() { return apellido; }
        public void setApellido(String apellido) { this.apellido = apellido; }
        public String getEmail() { return email; }
        public void setEmail(String email) { this.email = email; }
        public String getTelefono() { return telefono; }
        public void setTelefono(String telefono) { this.telefono = telefono; }
        public String getDireccion() { return direccion; }
        public void setDireccion(String direccion) { this.direccion = direccion; }
    }

    /**
     * Clase para representar solicitud de consulta de cliente
     */
    public static class ClienteConsultaRequest {
        private Long clienteId;
        private String dni;

        // Constructores
        public ClienteConsultaRequest() {
        }

        // Getters y Setters
        public Long getClienteId() { return clienteId; }
        public void setClienteId(Long clienteId) { this.clienteId = clienteId; }
        public String getDni() { return dni; }
        public void setDni(String dni) { this.dni = dni; }
    }

    /**
     * Clase para representar solicitud de actualización de cliente
     */
    public static class ClienteUpdateRequest {
        private Long clienteId;
        private String nombre;
        private String apellido;
        private String email;
        private String telefono;
        private String direccion;

        // Constructores
        public ClienteUpdateRequest() {
        }

        // Getters y Setters
        public Long getClienteId() { return clienteId; }
        public void setClienteId(Long clienteId) { this.clienteId = clienteId; }
        public String getNombre() { return nombre; }
        public void setNombre(String nombre) { this.nombre = nombre; }
        public String getApellido() { return apellido; }
        public void setApellido(String apellido) { this.apellido = apellido; }
        public String getEmail() { return email; }
        public void setEmail(String email) { this.email = email; }
        public String getTelefono() { return telefono; }
        public void setTelefono(String telefono) { this.telefono = telefono; }
        public String getDireccion() { return direccion; }
        public void setDireccion(String direccion) { this.direccion = direccion; }
    }
}
