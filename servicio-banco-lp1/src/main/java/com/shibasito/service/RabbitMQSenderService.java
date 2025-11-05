package com.shibasito.service;

import org.springframework.amqp.core.AmqpTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class RabbitMQSenderService {

    @Autowired
    private AmqpTemplate rabbitTemplate;

    private String exchange = "bank_direct";
    private String routingkey = "bank.validate.loan";

    public void send(String message) {
        rabbitTemplate.convertAndSend(exchange, routingkey, message);
    }
}
