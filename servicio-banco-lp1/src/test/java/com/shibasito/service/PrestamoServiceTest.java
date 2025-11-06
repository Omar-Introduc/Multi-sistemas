package com.shibasito.service;

import com.shibasito.model.Prestamo;
import com.shibasito.repository.PrestamoRepository;
import com.shibasito.serviciobancolp1.ServicioBancoLp1Application;
import org.junit.jupiter.api.Test;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.assertEquals;

@SpringBootTest(classes = ServicioBancoLp1Application.class)
public class PrestamoServiceTest {

    @Autowired
    private PrestamoService prestamoService;

    @Autowired
    private RabbitTemplate rabbitTemplate;

    @MockBean
    private PrestamoRepository prestamoRepository;

    @Test
    public void testCreatePrestamo() {
        Prestamo prestamo = new Prestamo();
        prestamo.setIdCliente("12345678");
        prestamo.setMonto(new BigDecimal("1000.0"));

        prestamoService.createPrestamo(prestamo);

        // Verify that the message was sent to the queue
        String expectedMessage = "{\"dni\": \"12345678\"}";
        Object receivedMessage = rabbitTemplate.receiveAndConvert("bank.validate.loan", 5000);
        assertEquals(expectedMessage, receivedMessage);
    }
}
