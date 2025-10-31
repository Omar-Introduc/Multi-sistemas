package com.banco.shibasito.listener;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * Listener de eventos de RabbitMQ para el Servicio Banco
 * 
 * Escucha mensajes relacionados con operaciones bancarias
 * y procesa eventos del sistema distribuido.
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
@Component
public class BancoEventListener {

    private static final Logger logger = LoggerFactory.getLogger(BancoEventListener.class);

    private final ObjectMapper objectMapper;

    @Autowired
    public BancoEventListener(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    /**
     * Escucha eventos de nuevo cliente
     */
    @RabbitListener(queues = "banco.cliente.nuevo")
    public void procesarNuevoCliente(String mensaje) {
        try {
            logger.info("Procesando evento de nuevo cliente: {}", mensaje);
            
            ClienteEvent evento = objectMapper.readValue(mensaje, ClienteEvent.class);
            
            // Lógica para procesar nuevo cliente
            logger.info("Cliente procesado exitosamente: ID {}", evento.getClienteId());
            
        } catch (JsonProcessingException e) {
            logger.error("Error al procesar mensaje de nuevo cliente: {}", mensaje, e);
        } catch (Exception e) {
            logger.error("Error inesperado procesando nuevo cliente", e);
        }
    }

    /**
     * Escucha eventos de actualización de cliente
     */
    @RabbitListener(queues = "banco.cliente.actualizar")
    public void procesarActualizacionCliente(String mensaje) {
        try {
            logger.info("Procesando evento de actualización de cliente: {}", mensaje);
            
            ClienteEvent evento = objectMapper.readValue(mensaje, ClienteEvent.class);
            
            // Lógica para actualizar datos del cliente
            logger.info("Cliente actualizado exitosamente: ID {}", evento.getClienteId());
            
        } catch (JsonProcessingException e) {
            logger.error("Error al procesar mensaje de actualización de cliente: {}", mensaje, e);
        } catch (Exception e) {
            logger.error("Error inesperado actualizando cliente", e);
        }
    }

    /**
     * Escucha eventos de solicitud de información bancaria
     */
    @RabbitListener(queues = "banco.info.solicitud")
    public void procesarSolicitudInformacion(String mensaje) {
        try {
            logger.info("Procesando solicitud de información bancaria: {}", mensaje);
            
            InfoBancariaSolicitud evento = objectMapper.readValue(mensaje, InfoBancariaSolicitud.class);
            
            // Lógica para obtener información bancaria
            String infoBancaria = obtenerInformacionBancaria(evento.getClienteId());
            
            // Aquí se enviaría la respuesta a otra cola o exchange
            logger.info("Información bancaria obtenida para cliente: {}", evento.getClienteId());
            
        } catch (JsonProcessingException e) {
            logger.error("Error al procesar solicitud de información: {}", mensaje, e);
        } catch (Exception e) {
            logger.error("Error inesperado procesando solicitud de información", e);
        }
    }

    /**
     * Escucha eventos de transacción para conciliación
     */
    @RabbitListener(queues = "banco.transaccion.conciliacion")
    public void procesarTransaccionConciliacion(String mensaje) {
        try {
            logger.info("Procesando transacción para conciliación: {}", mensaje);
            
            TransaccionEvent evento = objectMapper.readValue(mensaje, TransaccionEvent.class);
            
            // Lógica para conciliación de transacciones
            boolean conciliada = realizarConciliacion(evento);
            
            logger.info("Conciliación de transacción completada: {}, Resultado: {}", 
                       evento.getTransaccionId(), conciliada);
            
        } catch (JsonProcessingException e) {
            logger.error("Error al procesar transacción para conciliación: {}", mensaje, e);
        } catch (Exception e) {
            logger.error("Error inesperado procesando conciliación", e);
        }
    }

    /**
     * Método auxiliar para obtener información bancaria
     */
    private String obtenerInformacionBancaria(Long clienteId) {
        // Aquí iría la lógica real para obtener información bancaria
        // Por ahora retornamos un JSON simulado
        return String.format("{\"clienteId\": %d, \"cuentas\": [], \"saldoTotal\": 0.0}", clienteId);
    }

    /**
     * Método auxiliar para realizar conciliación
     */
    private boolean realizarConciliacion(TransaccionEvent evento) {
        // Aquí iría la lógica real de conciliación
        // Por ahora simulamos una conciliación exitosa
        logger.debug("Realizando conciliación para transacción: {}", evento.getTransaccionId());
        return true;
    }

    // Clases internas para eventos
    public static class ClienteEvent {
        private Long clienteId;
        private String nombre;
        private String tipoEvento;
        private String fechaEvento;

        // Constructores
        public ClienteEvent() {
        }

        public ClienteEvent(Long clienteId, String nombre, String tipoEvento, String fechaEvento) {
            this.clienteId = clienteId;
            this.nombre = nombre;
            this.tipoEvento = tipoEvento;
            this.fechaEvento = fechaEvento;
        }

        // Getters y Setters
        public Long getClienteId() {
            return clienteId;
        }

        public void setClienteId(Long clienteId) {
            this.clienteId = clienteId;
        }

        public String getNombre() {
            return nombre;
        }

        public void setNombre(String nombre) {
            this.nombre = nombre;
        }

        public String getTipoEvento() {
            return tipoEvento;
        }

        public void setTipoEvento(String tipoEvento) {
            this.tipoEvento = tipoEvento;
        }

        public String getFechaEvento() {
            return fechaEvento;
        }

        public void setFechaEvento(String fechaEvento) {
            this.fechaEvento = fechaEvento;
        }
    }

    public static class InfoBancariaSolicitud {
        private Long clienteId;
        private String solicitudId;
        private String fechaSolicitud;

        // Constructores
        public InfoBancariaSolicitud() {
        }

        public InfoBancariaSolicitud(Long clienteId, String solicitudId, String fechaSolicitud) {
            this.clienteId = clienteId;
            this.solicitudId = solicitudId;
            this.fechaSolicitud = fechaSolicitud;
        }

        // Getters y Setters
        public Long getClienteId() {
            return clienteId;
        }

        public void setClienteId(Long clienteId) {
            this.clienteId = clienteId;
        }

        public String getSolicitudId() {
            return solicitudId;
        }

        public void setSolicitudId(String solicitudId) {
            this.solicitudId = solicitudId;
        }

        public String getFechaSolicitud() {
            return fechaSolicitud;
        }

        public void setFechaSolicitud(String fechaSolicitud) {
            this.fechaSolicitud = fechaSolicitud;
        }
    }

    public static class TransaccionEvent {
        private String transaccionId;
        private Long clienteId;
        private String tipoTransaccion;
        private Double monto;
        private String fechaTransaccion;

        // Constructores
        public TransaccionEvent() {
        }

        public TransaccionEvent(String transaccionId, Long clienteId, 
                               String tipoTransaccion, Double monto, String fechaTransaccion) {
            this.transaccionId = transaccionId;
            this.clienteId = clienteId;
            this.tipoTransaccion = tipoTransaccion;
            this.monto = monto;
            this.fechaTransaccion = fechaTransaccion;
        }

        // Getters y Setters
        public String getTransaccionId() {
            return transaccionId;
        }

        public void setTransaccionId(String transaccionId) {
            this.transaccionId = transaccionId;
        }

        public Long getClienteId() {
            return clienteId;
        }

        public void setClienteId(Long clienteId) {
            this.clienteId = clienteId;
        }

        public String getTipoTransaccion() {
            return tipoTransaccion;
        }

        public void setTipoTransaccion(String tipoTransaccion) {
            this.tipoTransaccion = tipoTransaccion;
        }

        public Double getMonto() {
            return monto;
        }

        public void setMonto(Double monto) {
            this.monto = monto;
        }

        public String getFechaTransaccion() {
            return fechaTransaccion;
        }

        public void setFechaTransaccion(String fechaTransaccion) {
            this.fechaTransaccion = fechaTransaccion;
        }
    }
}
