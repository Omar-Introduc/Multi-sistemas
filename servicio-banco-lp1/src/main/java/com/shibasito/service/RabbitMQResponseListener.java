package com.shibasito.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.shibasito.model.Prestamo;
import com.shibasito.repository.PrestamoRepository;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.Map;

@Service
public class RabbitMQResponseListener {

    @Autowired
    private PrestamoRepository prestamoRepository;

    @Autowired
    private ObjectMapper objectMapper;

    @RabbitListener(queues = "bank.loan.response")
    public void receiveMessage(String message) throws IOException {
        Map<String, Object> response = objectMapper.readValue(message, Map.class);
        String dni = (String) response.get("dni");
        boolean isValid = (boolean) response.get("isValid");

        // This is a simplified approach. In a real-world scenario, you'd
        // have a more robust way to correlate the response to the original request.
        // For now, we'll find the latest loan for the given DNI and update its status.
        prestamoRepository.findFirstByClienteDniOrderByIdDesc(dni).ifPresent(prestamo -> {
            if (isValid) {
                prestamo.setEstado("activo");
            } else {
                prestamo.setEstado("rechazado");
            }
            prestamoRepository.save(prestamo);
            System.out.println("Prestamo " + prestamo.getIdPrestamo() + " actualizado a " + prestamo.getEstado());
        });
    }
}
