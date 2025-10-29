package com.shibasito.banco.consumers;

import com.shibasito.banco.models.Prestamo;
import com.shibasito.banco.repositories.PrestamoRepository;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.Random;

@Component
public class SolicitudConsumer {

    @Autowired
    private RabbitTemplate rabbitTemplate;

    @Autowired
    private PrestamoRepository prestamoRepository;

    @RabbitListener(queues = "solicitud_prestamo")
    public void receiveMessage(String message) {
        System.out.println("Received loan application: " + message);

        // Simulate processing and create a Prestamo entity
        Prestamo prestamo = new Prestamo();
        prestamo.setMonto(new Random().nextDouble() * 10000); // Random loan amount
        prestamo.setPlazo(new Random().nextInt(12) + 1); // Random term between 1 and 12 months

        // Save the loan to the database
        prestamoRepository.save(prestamo);
        System.out.println("Saved new loan to the database with ID: " + prestamo.getId());

        // Send a confirmation message
        String confirmationMessage = "Loan application '" + message + "' processed and saved with ID: " + prestamo.getId();
        rabbitTemplate.convertAndSend("respuesta_prestamo", confirmationMessage);
        System.out.println("Sent confirmation: " + confirmationMessage);
    }
}
