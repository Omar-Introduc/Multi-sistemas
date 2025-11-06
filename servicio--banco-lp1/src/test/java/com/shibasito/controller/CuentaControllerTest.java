package com.shibasito.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.shibasito.dto.TransaccionRequestDTO;
import com.shibasito.exception.GlobalExceptionHandler;
import com.shibasito.exception.ResourceNotFoundException;
import com.shibasito.service.CuentaService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.math.BigDecimal;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@ExtendWith(MockitoExtension.class)
public class CuentaControllerTest {

    private MockMvc mockMvc;

    @Mock
    private CuentaService cuentaService;

    @InjectMocks
    private CuentaController cuentaController;

    private ObjectMapper objectMapper = new ObjectMapper();

    @Test
    public void testRetirarDinero_CuentaNoEncontrada() throws Exception {
        mockMvc = MockMvcBuilders.standaloneSetup(cuentaController)
                .setControllerAdvice(new GlobalExceptionHandler())
                .build();
        doThrow(new ResourceNotFoundException("Cuenta no encontrada")).when(cuentaService).retirar(any(String.class), any(BigDecimal.class));

        TransaccionRequestDTO request = new TransaccionRequestDTO();
        request.setMonto(new BigDecimal("100.0"));

        mockMvc.perform(post("/api/cuentas/1/retirar")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isNotFound());
    }
}
