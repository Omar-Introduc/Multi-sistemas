package com.shibasito.banco.config;

import org.springframework.amqp.core.Queue;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    @Bean
    public Queue solicitudQueue() {
        return new Queue("solicitud_prestamo");
    }

    @Bean
    public Queue respuestaQueue() {
        return new Queue("respuesta_prestamo");
    }
}
