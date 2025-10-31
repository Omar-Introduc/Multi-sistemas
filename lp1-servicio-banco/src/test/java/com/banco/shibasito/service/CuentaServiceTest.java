package com.banco.shibasito.service;

import com.banco.shibasito.dto.Response;
import com.banco.shibasito.entity.Cliente;
import com.banco.shibasito.entity.Cuenta;
import com.banco.shibasito.entity.Transaccion;
import com.banco.shibasito.repository.CuentaRepository;
import com.banco.shibasito.repository.ClienteRepository;
import com.banco.shibasito.repository.TransaccionRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Pruebas unitarias para CuentaService
 * Valida la lógica de negocio del servicio de cuentas
 */
@ExtendWith(MockitoExtension.class)
class CuentaServiceTest {

    @Mock
    private CuentaRepository cuentaRepository;

    @Mock
    private ClienteRepository clienteRepository;

    @Mock
    private TransaccionRepository transaccionRepository;

    @Mock
    private BancoRabbitMQService rabbitMQService;

    @InjectMocks
    private CuentaService cuentaService;

    private Cliente cliente;
    private Cuenta cuenta;
    private Transaccion transaccion;

    @BeforeEach
    void setUp() {
        // Crear cliente mock
        cliente = new Cliente();
        cliente.setId(1L);
        cliente.setDni("12345678");
        cliente.setNombre("Juan");
        cliente.setApellido("Pérez");
        cliente.setEmail("juan.perez@test.com");
        cliente.setEstado(Cliente.Estado.ACTIVO);

        // Crear cuenta mock
        cuenta = new Cuenta();
        cuenta.setId(1L);
        cuenta.setNumero("2001234567890");
        cuenta.setSaldo(new BigDecimal("1500.00"));
        cuenta.setSaldoMinimo(new BigDecimal("100.00"));
        cuenta.setTipo(Cuenta.TipoCuenta.AHORROS);
        cuenta.setEstado(Cuenta.Estado.ACTIVA);
        cuenta.setCliente(cliente);
        cuenta.setTransacciones(new ArrayList<>());

        // Crear transacción mock
        transaccion = new Transaccion();
        transaccion.setId(1L);
        transaccion.setCuenta(cuenta);
        transaccion.setTipo(Transaccion.Tipo.DEPOSITO);
        transaccion.setMonto(new BigDecimal("500.00"));
        transaccion.setDescripcion("Depósito de prueba");
        transaccion.setFecha(LocalDateTime.now());
        transaccion.setEstado(Transaccion.Estado.COMPLETADA);
    }

    @Test
    void testCrearCuenta_Success() {
        // Given
        String numero = "2001234567890";
        String dniCliente = "12345678";
        Cuenta.TipoCuenta tipo = Cuenta.TipoCuenta.AHORROS;
        BigDecimal saldoInicial = new BigDecimal("1000.00");

        when(clienteRepository.findByDni(dniCliente)).thenReturn(Optional.of(cliente));
        when(cuentaRepository.findByNumero(numero)).thenReturn(Optional.empty());
        when(cuentaRepository.save(any(Cuenta.class))).thenReturn(cuenta);

        // When
        Response<Cuenta> response = cuentaService.crearCuenta(numero, dniCliente, tipo, saldoInicial);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("Cuenta creada exitosamente", response.getMessage());
        assertNotNull(response.getData());
        verify(rabbitMQService).enviarEventoCuentaCreada(any(Cuenta.class));
    }

    @Test
    void testCrearCuenta_ClienteNotFound() {
        // Given
        String dniInexistente = "99999999";
        when(clienteRepository.findByDni(dniInexistente)).thenReturn(Optional.empty());

        // When
        Response<Cuenta> response = cuentaService.crearCuenta("2001234567890", dniInexistente, 
                Cuenta.TipoCuenta.AHORROS, new BigDecimal("1000.00"));

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CLIENTE_NO_ENCONTRADO", response.getCode());
        verify(cuentaRepository, never()).save(any());
        verify(rabbitMQService, never()).enviarEventoCuentaCreada(any());
    }

    @Test
    void testCrearCuenta_DuplicateAccountNumber() {
        // Given
        String numero = "2001234567890";
        String dniCliente = "12345678";

        when(clienteRepository.findByDni(dniCliente)).thenReturn(Optional.of(cliente));
        when(cuentaRepository.findByNumero(numero)).thenReturn(Optional.of(cuenta));

        // When
        Response<Cuenta> response = cuentaService.crearCuenta(numero, dniCliente, 
                Cuenta.TipoCuenta.AHORROS, new BigDecimal("1000.00"));

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CUENTA_DUPLICADA", response.getCode());
        verify(cuentaRepository, never()).save(any());
        verify(rabbitMQService, never()).enviarEventoCuentaCreada(any());
    }

    @Test
    void testConsultarSaldo_Success() {
        // Given
        String numero = "2001234567890";
        when(cuentaRepository.findByNumero(numero)).thenReturn(Optional.of(cuenta));

        // When
        Response<BigDecimal> response = cuentaService.consultarSaldo(numero);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(new BigDecimal("1500.00"), response.getData());
        assertEquals("Saldo consultado exitosamente", response.getMessage());
    }

    @Test
    void testConsultarSaldo_AccountNotFound() {
        // Given
        String numeroInexistente = "9999999999999";
        when(cuentaRepository.findByNumero(numeroInexistente)).thenReturn(Optional.empty());

        // When
        Response<BigDecimal> response = cuentaService.consultarSaldo(numeroInexistente);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CUENTA_NO_ENCONTRADA", response.getCode());
    }

    @Test
    void testConsultarSaldo_InactiveAccount() {
        // Given
        cuenta.setEstado(Cuenta.Estado.INACTIVA);
        String numero = "2001234567890";
        when(cuentaRepository.findByNumero(numero)).thenReturn(Optional.of(cuenta));

        // When
        Response<BigDecimal> response = cuentaService.consultarSaldo(numero);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CUENTA_INACTIVA", response.getCode());
    }

    @Test
    void testDepositar_Success() {
        // Given
        String numero = "2001234567890";
        BigDecimal monto = new BigDecimal("500.00");
        String descripcion = "Depósito de prueba";

        when(cuentaRepository.findByNumero(numero)).thenReturn(Optional.of(cuenta));
        when(cuentaRepository.save(any(Cuenta.class))).thenReturn(cuenta);
        when(transaccionRepository.save(any(Transaccion.class))).thenReturn(transaccion);

        // When
        Response<String> response = cuentaService.depositar(numero, monto, descripcion);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("Depósito realizado exitosamente", response.getMessage());
        verify(rabbitMQService).enviarEventoTransaccionProcesada(any(Transaccion.class));
        verify(transaccionRepository).save(any(Transaccion.class));
    }

    @Test
    void testDepositar_InvalidAmount() {
        // Given
        String numero = "2001234567890";
        BigDecimal montoInvalido = new BigDecimal("-100.00");

        // When
        Response<String> response = cuentaService.depositar(numero, montoInvalido, "Depósito");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("MONTO_INVALIDO", response.getCode());
        verify(cuentaRepository, never()).findByNumero(any());
        verify(transaccionRepository, never()).save(any());
    }

    @Test
    void testDepositar_AccountNotFound() {
        // Given
        String numeroInexistente = "9999999999999";
        BigDecimal monto = new BigDecimal("500.00");

        when(cuentaRepository.findByNumero(numeroInexistente)).thenReturn(Optional.empty());

        // When
        Response<String> response = cuentaService.depositar(numeroInexistente, monto, "Depósito");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CUENTA_NO_ENCONTRADA", response.getCode());
    }

    @Test
    void testRetirar_Success() {
        // Given
        String numero = "2001234567890";
        BigDecimal monto = new BigDecimal("200.00");
        String descripcion = "Retiro de prueba";

        when(cuentaRepository.findByNumero(numero)).thenReturn(Optional.of(cuenta));
        when(cuentaRepository.save(any(Cuenta.class))).thenReturn(cuenta);
        when(transaccionRepository.save(any(Transaccion.class))).thenReturn(transaccion);

        // When
        Response<String> response = cuentaService.retirar(numero, monto, descripcion);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("Retiro realizado exitosamente", response.getMessage());
        verify(rabbitMQService).enviarEventoTransaccionProcesada(any(Transaccion.class));
        verify(transaccionRepository).save(any(Transaccion.class));
    }

    @Test
    void testRetirar_InsufficientFunds() {
        // Given
        String numero = "2001234567890";
        BigDecimal montoExcesivo = new BigDecimal("10000.00");
        String descripcion = "Retiro de prueba";

        when(cuentaRepository.findByNumero(numero)).thenReturn(Optional.of(cuenta));

        // When
        Response<String> response = cuentaService.retirar(numero, montoExcesivo, descripcion);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("RETIRO_NO_PERMITIDO", response.getCode());
        verify(transaccionRepository, never()).save(any());
    }

    @Test
    void testRetirar_AccountNotFound() {
        // Given
        String numeroInexistente = "9999999999999";
        BigDecimal monto = new BigDecimal("200.00");

        when(cuentaRepository.findByNumero(numeroInexistente)).thenReturn(Optional.empty());

        // When
        Response<String> response = cuentaService.retirar(numeroInexistente, monto, "Retiro");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CUENTA_NO_ENCONTRADA", response.getCode());
    }

    @Test
    void testConsultarHistorial_Success() {
        // Given
        String numero = "2001234567890";
        LocalDate fechaInicio = LocalDate.now().minusDays(30);
        LocalDate fechaFin = LocalDate.now();

        List<Transaccion> transacciones = List.of(transaccion);
        
        when(cuentaRepository.findByNumero(numero)).thenReturn(Optional.of(cuenta));
        when(transaccionRepository.findByCuentaAndFechaBetween(eq(cuenta), 
                any(LocalDateTime.class), any(LocalDateTime.class))).thenReturn(transacciones);

        // When
        Response<List<Transaccion>> response = cuentaService.consultarHistorial(numero, fechaInicio, fechaFin);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Historial de transacciones obtenido exitosamente", response.getMessage());
    }

    @Test
    void testConsultarHistorial_AccountNotFound() {
        // Given
        String numeroInexistente = "9999999999999";
        LocalDate fechaInicio = LocalDate.now().minusDays(30);
        LocalDate fechaFin = LocalDate.now();

        when(cuentaRepository.findByNumero(numeroInexistente)).thenReturn(Optional.empty());

        // When
        Response<List<Transaccion>> response = cuentaService.consultarHistorial(numeroInexistente, fechaInicio, fechaFin);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CUENTA_NO_ENCONTRADA", response.getCode());
    }

    @Test
    void testBloquearCuenta_Success() {
        // Given
        String numero = "2001234567890";
        String motivo = "Sospecha de fraude";

        when(cuentaRepository.findByNumero(numero)).thenReturn(Optional.of(cuenta));
        when(cuentaRepository.save(any(Cuenta.class))).thenReturn(cuenta);

        // When
        Response<String> response = cuentaService.bloquearCuenta(numero, motivo);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("Cuenta bloqueada exitosamente", response.getMessage());
        assertEquals(Cuenta.Estado.BLOQUEADA, cuenta.getEstado());
        verify(rabbitMQService).enviarAlerta(eq("CUENTA_BLOQUEADA"), anyString(), isNull());
    }

    @Test
    void testDesbloquearCuenta_Success() {
        // Given
        String numero = "2001234567890";
        cuenta.setEstado(Cuenta.Estado.BLOQUEADA);

        when(cuentaRepository.findByNumero(numero)).thenReturn(Optional.of(cuenta));
        when(cuentaRepository.save(any(Cuenta.class))).thenReturn(cuenta);

        // When
        Response<String> response = cuentaService.desbloquearCuenta(numero);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("Cuenta desbloqueada exitosamente", response.getMessage());
        assertEquals(Cuenta.Estado.ACTIVA, cuenta.getEstado());
    }

    @Test
    void testGenerarNumeroCuenta_Ahorros() {
        // When
        String numero = cuentaService.generarNumeroCuenta(Cuenta.TipoCuenta.AHORROS);

        // Then
        assertNotNull(numero);
        assertEquals(15, numero.length());
        assertTrue(numero.startsWith("20"));
    }

    @Test
    void testGenerarNumeroCuenta_Corriente() {
        // When
        String numero = cuentaService.generarNumeroCuenta(Cuenta.TipoCuenta.CORRIENTE);

        // Then
        assertNotNull(numero);
        assertEquals(15, numero.length());
        assertTrue(numero.startsWith("10"));
    }

    @Test
    void testGenerarNumeroCuenta_PlazoFijo() {
        // When
        String numero = cuentaService.generarNumeroCuenta(Cuenta.TipoCuenta.PLAZO_FIJO);

        // Then
        assertNotNull(numero);
        assertEquals(15, numero.length());
        assertTrue(numero.startsWith("30"));
    }

    @Test
    void testCalcularSaldoMinimo_Ahorros() {
        // Given
        Cuenta.TipoCuenta tipo = Cuenta.TipoCuenta.AHORROS;

        // When
        BigDecimal saldoMinimo = cuentaService.calcularSaldoMinimo(tipo);

        // Then
        assertEquals(new BigDecimal("100.00"), saldoMinimo);
    }

    @Test
    void testCalcularSaldoMinimo_Corriente() {
        // Given
        Cuenta.TipoCuenta tipo = Cuenta.TipoCuenta.CORRIENTE;

        // When
        BigDecimal saldoMinimo = cuentaService.calcularSaldoMinimo(tipo);

        // Then
        assertEquals(new BigDecimal("500.00"), saldoMinimo);
    }

    @Test
    void testCalcularSaldoMinimo_PlazoFijo() {
        // Given
        Cuenta.TipoCuenta tipo = Cuenta.TipoCuenta.PLAZO_FIJO;

        // When
        BigDecimal saldoMinimo = cuentaService.calcularSaldoMinimo(tipo);

        // Then
        assertEquals(new BigDecimal("1000.00"), saldoMinimo);
    }

    @Test
    void testValidarCreacionCuenta_NullValues() {
        // When
        Response<Cuenta> response = cuentaService.validarCreacionCuenta(null, null, null, null);

        // Then
        assertFalse(response.isSuccess());
        assertTrue(response.getMessage().contains("obligatorio"));
    }

    @Test
    void testValidarCreacionCuenta_InvalidSaldo() {
        // Given
        BigDecimal saldoNegativo = new BigDecimal("-100.00");

        // When
        Response<Cuenta> response = cuentaService.validarCreacionCuenta("123", "456", 
                Cuenta.TipoCuenta.AHORROS, saldoNegativo);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("SALDO_INICIAL_INVALIDO", response.getCode());
    }

    @Test
    void testConsultarHistorial_SinFechas() {
        // Given
        String numero = "2001234567890";
        List<Transaccion> transacciones = List.of(transaccion);
        
        when(cuentaRepository.findByNumero(numero)).thenReturn(Optional.of(cuenta));
        when(transaccionRepository.findByCuentaOrderByFechaDesc(cuenta)).thenReturn(transacciones);

        // When
        Response<List<Transaccion>> response = cuentaService.consultarHistorial(numero, null, null);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        verify(transaccionRepository).findByCuentaOrderByFechaDesc(cuenta);
    }
}
