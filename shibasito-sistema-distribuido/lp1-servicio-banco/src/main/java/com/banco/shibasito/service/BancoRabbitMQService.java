package com.banco.shibasito.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.util.HashMap;
import java.util.Map;

/**
 * Servicio para el envío de mensajes a RabbitMQ
 * Maneja la comunicación asíncrona con otros servicios del sistema
 */
@Service
public class BancoRabbitMQService {
    
    private static final Logger logger = LoggerFactory.getLogger(BancoRabbitMQService.class);
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    private ObjectMapper objectMapper;
    
    // Exchange y routing keys
    private static final String BANCO_EXCHANGE = "banco.events";
    private static final String CLIENTE_ROUTING_KEY = "cliente.event";
    private static final String CUENTA_ROUTING_KEY = "cuenta.event";
    private static final String TRANSACCION_ROUTING_KEY = "transaccion.event";
    private static final String PRESTAMO_ROUTING_KEY = "prestamo.event";
    
    @PostConstruct
    public void init() {
        this.objectMapper = new ObjectMapper();
    }
    
    /**
     * Envía un mensaje genérico a RabbitMQ
     * @param routingKey Clave de enrutamiento
     * @param data Datos a enviar
     */
    public void enviarMensaje(String routingKey, Object data) {
        try {
            if (data == null) {
                logger.warn("Intento de enviar mensaje nulo con routing key: {}", routingKey);
                return;
            }
            
            // Crear payload del mensaje
            Map<String, Object> mensaje = crearPayload(routingKey, data);
            
            // Convertir a JSON
            String jsonMessage = objectMapper.writeValueAsString(mensaje);
            
            // Enviar mensaje
            rabbitTemplate.convertAndSend(BANCO_EXCHANGE, routingKey, jsonMessage);
            
            logger.info("Mensaje enviado exitosamente con routing key: {}", routingKey);
            
        } catch (Exception e) {
            logger.error("Error al enviar mensaje con routing key {}: {}", routingKey, e.getMessage(), e);
            // No lanzamos la excepción para no interrumpir el flujo principal
        }
    }
    
    /**
     * Envía evento de cliente creado
     * @param cliente Cliente que fue creado
     */
    public void enviarEventoClienteCreado(Object cliente) {
        enviarMensaje(CLIENTE_ROUTING_KEY + ".creado", cliente);
    }
    
    /**
     * Envía evento de cliente actualizado
     * @param cliente Cliente que fue actualizado
     */
    public void enviarEventoClienteActualizado(Object cliente) {
        enviarMensaje(CLIENTE_ROUTING_KEY + ".actualizado", cliente);
    }
    
    /**
     * Envía evento de cliente desactivado
     * @param cliente Cliente que fue desactivado
     */
    public void enviarEventoClienteDesactivado(Object cliente) {
        enviarMensaje(CLIENTE_ROUTING_KEY + ".desactivado", cliente);
    }
    
    /**
     * Envía evento de cuenta creada
     * @param cuenta Cuenta que fue creada
     */
    public void enviarEventoCuentaCreada(Object cuenta) {
        enviarMensaje(CUENTA_ROUTING_KEY + ".creada", cuenta);
    }
    
    /**
     * Envía evento de transacción procesada
     * @param transaccion Transacción procesada
     */
    public void enviarEventoTransaccionProcesada(Object transaccion) {
        enviarMensaje(TRANSACCION_ROUTING_KEY + ".procesada", transaccion);
    }
    
    /**
     * Envía evento de préstamo solicitado
     * @param prestamo Préstamo solicitado
     */
    public void enviarEventoPrestamoSolicitado(Object prestamo) {
        enviarMensaje(PRESTAMO_ROUTING_KEY + ".solicitado", prestamo);
    }
    
    /**
     * Envía evento de préstamo aprobado
     * @param prestamo Préstamo aprobado
     */
    public void enviarEventoPrestamoAprobado(Object prestamo) {
        enviarMensaje(PRESTAMO_ROUTING_KEY + ".aprobado", prestamo);
    }
    
    /**
     * Envía evento de préstamo rechazado
     * @param prestamo Préstamo rechazado
     */
    public void enviarEventoPrestamoRechazado(Object prestamo) {
        enviarMensaje(PRESTAMO_ROUTING_KEY + ".rechazado", prestamo);
    }
    
    /**
     * Envía evento de alerta o notificación
     * @param tipoAlerta Tipo de alerta
     * @param mensaje Mensaje de la alerta
     * @param datos Datos adicionales
     */
    public void enviarAlerta(String tipoAlerta, String mensaje, Map<String, Object> datos) {
        try {
            Map<String, Object> alerta = new HashMap<>();
            alerta.put("tipo", tipoAlerta);
            alerta.put("mensaje", mensaje);
            alerta.put("timestamp", System.currentTimeMillis());
            alerta.put("datos", datos);
            
            enviarMensaje("alerta." + tipoAlerta.toLowerCase(), alerta);
            
        } catch (Exception e) {
            logger.error("Error al enviar alerta: {}", e.getMessage(), e);
        }
    }
    
    /**
     * Crea el payload estándar para los mensajes
     * @param routingKey Clave de enrutamiento
     * @param data Datos del evento
     * @return Map con el payload del mensaje
     */
    private Map<String, Object> crearPayload(String routingKey, Object data) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("eventType", routingKey);
        payload.put("timestamp", System.currentTimeMillis());
        payload.put("source", "banco-service");
        payload.put("data", data);
        payload.put("version", "1.0");
        
        return payload;
    }
    
    /**
     * Prueba de conectividad con RabbitMQ
     * @return true si la conexión es exitosa, false en caso contrario
     */
    public boolean probarConectividad() {
        try {
            // Enviar mensaje de prueba
            Map<String, Object> mensajePrueba = new HashMap<>();
            mensajePrueba.put("tipo", "TEST");
            mensajePrueba.put("mensaje", "Conectividad prueba");
            mensajePrueba.put("timestamp", System.currentTimeMillis());
            
            rabbitTemplate.convertAndSend(BANCO_EXCHANGE, "test.connectivity", mensajePrueba);
            
            logger.info("Prueba de conectividad con RabbitMQ exitosa");
            return true;
            
        } catch (Exception e) {
            logger.error("Error en prueba de conectividad con RabbitMQ: {}", e.getMessage(), e);
            return false;
        }
    }
}