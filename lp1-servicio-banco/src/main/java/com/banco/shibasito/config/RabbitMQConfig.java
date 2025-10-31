package com.banco.shibasito.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.amqp.annotation.EnableRabbit;

/**
 * Configuración de RabbitMQ para el servicio bancario
 * Incluye configuración de ConnectionFactory, exchanges, queues y bindings
 */
@Configuration
@EnableRabbit
public class RabbitMQConfig {

    @Value("${spring.rabbitmq.host:localhost}")
    private String rabbitHost;

    @Value("${spring.rabbitmq.port:5672}")
    private int rabbitPort;

    @Value("${spring.rabbitmq.username:guest}")
    private String rabbitUsername;

    @Value("${spring.rabbitmq.password:guest}")
    private String rabbitPassword;

    // Exchanges
    public static final String EXCHANGE_BANCO = "banco.exchange";
    public static final String EXCHANGE_TRANSACCIONES = "transacciones.exchange";
    public static final String EXCHANGE_NOTIFICACIONES = "notificaciones.exchange";

    // Queues
    public static final String QUEUE_PROCESAMIENTO_TRANSACCIONES = "procesamiento.transacciones.queue";
    public static final String QUEUE_NOTIFICACIONES_USUARIOS = "notificaciones.usuarios.queue";
    public static final String QUEUE_AUDITORIA = "auditoria.queue";
    public static final String QUEUEREportes = "reportes.queue";

    // Routing Keys
    public static final String ROUTING_KEY_TRANSACCION = "transaccion.procesar";
    public static final String ROUTING_KEY_NOTIFICACION = "notificacion.enviar";
    public static final String ROUTING_KEY_AUDITORIA = "auditoria.log";
    public static final String ROUTING_KEY_REPORTE = "reporte.generar";

    /**
     * Configuración del ConnectionFactory para RabbitMQ
     */
    @Bean
    public ConnectionFactory connectionFactory() {
        com.rabbitmq.client.ConnectionFactory factory = new com.rabbitmq.client.ConnectionFactory();
        factory.setHost(rabbitHost);
        factory.setPort(rabbitPort);
        factory.setUsername(rabbitUsername);
        factory.setPassword(rabbitPassword);
        return new org.springframework.amqp.rabbit.connection.CachingConnectionFactory(factory);
    }

    /**
     * Exchange principal del banco
     */
    @Bean
    public TopicExchange bancoExchange() {
        return new TopicExchange(EXCHANGE_BANCO);
    }

    /**
     * Exchange para transacciones
     */
    @Bean
    public TopicExchange transaccionesExchange() {
        return new TopicExchange(EXCHANGE_TRANSACCIONES);
    }

    /**
     * Exchange para notificaciones
     */
    @Bean
    public FanoutExchange notificacionesExchange() {
        return new FanoutExchange(EXCHANGE_NOTIFICACIONES);
    }

    /**
     * Queue para procesamiento de transacciones
     */
    @Bean
    public Queue procesamientoTransaccionesQueue() {
        return new Queue(QUEUE_PROCESAMIENTO_TRANSACCIONES, true);
    }

    /**
     * Queue para notificaciones de usuarios
     */
    @Bean
    public Queue notificacionesUsuariosQueue() {
        return new Queue(QUEUE_NOTIFICACIONES_USUARIOS, true);
    }

    /**
     * Queue para auditoría
     */
    @Bean
    public Queue auditoriaQueue() {
        return new Queue(QUEUE_AUDITORIA, true);
    }

    /**
     * Queue para reportes
     */
    @Bean
    public Queue reportesQueue() {
        return new Queue(QUEUEREportes, true);
    }

    /**
     * Binding para procesamiento de transacciones
     */
    @Bean
    public Binding procesamientoTransaccionesBinding() {
        return BindingBuilder
                .bind(procesamientoTransaccionesQueue())
                .to(transaccionesExchange())
                .with(ROUTING_KEY_TRANSACCION);
    }

    /**
     * Binding para notificaciones
     */
    @Bean
    public Binding notificacionesUsuariosBinding() {
        return BindingBuilder
                .bind(notificacionesUsuariosQueue())
                .to(notificacionesExchange())
                .with(ROUTING_KEY_NOTIFICACION);
    }

    /**
     * Binding para auditoría
     */
    @Bean
    public Binding auditoriaBinding() {
        return BindingBuilder
                .bind(auditoriaQueue())
                .to(bancoExchange())
                .with(ROUTING_KEY_AUDITORIA);
    }

    /**
     * Binding para reportes
     */
    @Bean
    public Binding reportesBinding() {
        return BindingBuilder
                .bind(reportesQueue())
                .to(bancoExchange())
                .with(ROUTING_KEY_REPORTE);
    }

    /**
     * Configuración del RabbitTemplate con conversión JSON
     */
    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(new Jackson2JsonMessageConverter());
        template.setExchange(EXCHANGE_BANCO);
        return template;
    }
}
