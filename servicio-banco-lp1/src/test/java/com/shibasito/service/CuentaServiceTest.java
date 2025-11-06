package com.shibasito.service;

import com.shibasito.exception.InsufficientFundsException;
import com.shibasito.model.Cuenta;
import com.shibasito.repository.CuentaRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.util.Optional;

@ExtendWith(MockitoExtension.class)
public class CuentaServiceTest {

    @Mock
    private CuentaRepository cuentaRepository;

    @InjectMocks
    private CuentaService cuentaService;

    @Test
    public void testRetirarDinero_FondosInsuficientes() {
        Cuenta cuenta = new Cuenta();
        cuenta.setIdCuenta("1");
        cuenta.setSaldo(new BigDecimal("100.0"));

        when(cuentaRepository.findById("1")).thenReturn(Optional.of(cuenta));

        assertThrows(InsufficientFundsException.class, () -> {
            cuentaService.retirar("1", new BigDecimal("200.0"));
        });
    }
}
