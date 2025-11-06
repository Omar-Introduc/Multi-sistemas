package com.shibasito.service;

import com.shibasito.model.Prestamo;
import com.shibasito.repository.PrestamoRepository;
import com.shibasito.serviciobancolp1.ServicioBancoLp1Application;
import org.junit.jupiter.api.Test;
import org.springframework.amqp.core.AmqpTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

import java.math.BigDecimal;

import static org.mockito.Mockito.verify;

@SpringBootTest(classes = ServicioBancoLp1Application.class)
public class PrestamoServiceTest {

    @Autowired
    private PrestamoService prestamoService;

    @MockBean
    private AmqpTemplate rabbitTemplate;

    @MockBean
    private PrestamoRepository prestamoRepository;

    @Test
    public void testCreatePrestamo() {
        Prestamo prestamo = new Prestamo();
        prestamo.setIdCliente("12345678");
        prestamo.setMonto(new BigDecimal("1000.0"));

        prestamoService.createPrestamo(prestamo);

        // Verify that the service attempted to send the expected message
        String expectedMessage = "{\"dni\": \"12345678\"}";
        verify(rabbitTemplate).convertAndSend("bank_direct", "bank.validate.loan", expectedMessage);
    }
}
