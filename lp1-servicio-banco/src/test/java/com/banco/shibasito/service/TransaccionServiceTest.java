package com.banco.shibasito.service;

import com.banco.shibasito.dto.Response;
import com.banco.shibasito.entity.Cliente;
import com.banco.shibasito.entity.Cuenta;
import com.banco.shibasito.entity.Transaccion;
import com.banco.shibasito.repository.CuentaRepository;
import com.banco.shibasito.repository.TransaccionRepository;
import com.banco.shibasito.repository.ClienteRepository;
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

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Pruebas unitarias para TransaccionService
 * Valida la lógica de negocio del servicio de transacciones
 */
@ExtendWith(MockitoExtension.class)
class TransaccionServiceTest {

    @Mock
    private TransaccionRepository transaccionRepository;

    @Mock
    private CuentaRepository cuentaRepository;

    @Mock
    private ClienteRepository clienteRepository;

    @Mock
    private BancoRabbitMQService rabbitMQService;

    @InjectMocks
    private TransaccionService transaccionService;

    private Cliente cliente;
    private Cuenta cuentaOrigen;
    private Cuenta cuentaDestino;
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

        // Crear cuenta origen mock
        cuentaOrigen = new Cuenta();
        cuentaOrigen.setId(1L);
        cuentaOrigen.setNumero("2001234567890");
        cuentaOrigen.setSaldo(new BigDecimal("2000.00"));
        cuentaOrigen.setSaldoMinimo(new BigDecimal("100.00"));
        cuentaOrigen.setTipo(Cuenta.TipoCuenta.AHORROS);
        cuentaOrigen.setEstado(Cuenta.Estado.ACTIVA);
        cuentaOrigen.setCliente(cliente);

        // Crear cuenta destino mock
        cuentaDestino = new Cuenta();
        cuentaDestino.setId(2L);
        cuentaDestino.setNumero("2001234567891");
        cuentaDestino.setSaldo(new BigDecimal("1000.00"));
        cuentaDestino.setSaldoMinimo(new BigDecimal("100.00"));
        cuentaDestino.setTipo(Cuenta.TipoCuenta.AHORROS);
        cuentaDestino.setEstado(Cuenta.Estado.ACTIVA);
        cuentaDestino.setCliente(cliente);

        // Crear transacción mock
        transaccion = new Transaccion();
        transaccion.setId(1L);
        transaccion.setCuenta(cuentaOrigen);
        transaccion.setTipo(Transaccion.Tipo.TRANSFERENCIA);
        transaccion.setMonto(new BigDecimal("500.00"));
        transaccion.setDescripcion("Transferencia entre cuentas");
        transaccion.setCuentaDestino(cuentaDestino);
        transaccion.setFecha(LocalDateTime.now());
        transaccion.setEstado(Transaccion.Estado.COMPLETADA);
    }

    @Test
    void testTransferir_Success() {
        // Given
        String numeroOrigen = "2001234567890";
        String numeroDestino = "2001234567891";
        BigDecimal monto = new BigDecimal("500.00");
        String descripcion = "Transferencia de prueba";

        when(cuentaRepository.findByNumero(numeroOrigen)).thenReturn(Optional.of(cuentaOrigen));
        when(cuentaRepository.findByNumero(numeroDestino)).thenReturn(Optional.of(cuentaDestino));
        when(cuentaRepository.save(any(Cuenta.class))).thenReturn(cuentaOrigen);
        when(transaccionRepository.save(any(Transaccion.class))).thenReturn(transaccion);

        // When
        Response<String> response = transaccionService.transferir(numeroOrigen, numeroDestino, monto, descripcion);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("Transferencia realizada exitosamente", response.getMessage());
        assertEquals(new BigDecimal("1500.00"), cuentaOrigen.getSaldo()); // 2000 - 500
        assertEquals(new BigDecimal("1500.00"), cuentaDestino.getSaldo()); // 1000 + 500
        verify(rabbitMQService).enviarEventoTransaccionProcesada(any(Transaccion.class));
    }

    @Test
    void testTransferir_CuentaOrigenNotFound() {
        // Given
        String numeroOrigenInexistente = "9999999999999";
        String numeroDestino = "2001234567891";
        BigDecimal monto = new BigDecimal("500.00");

        when(cuentaRepository.findByNumero(numeroOrigenInexistente)).thenReturn(Optional.empty());

        // When
        Response<String> response = transaccionService.transferir(numeroOrigenInexistente, numeroDestino, monto, "Transferencia");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CUENTA_ORIGEN_NO_ENCONTRADA", response.getCode());
        verify(transaccionRepository, never()).save(any());
        verify(rabbitMQService, never()).enviarEventoTransaccionProcesada(any());
    }

    @Test
    void testTransferir_CuentaDestinoNotFound() {
        // Given
        String numeroOrigen = "2001234567890";
        String numeroDestinoInexistente = "9999999999999";
        BigDecimal monto = new BigDecimal("500.00");

        when(cuentaRepository.findByNumero(numeroOrigen)).thenReturn(Optional.of(cuentaOrigen));
        when(cuentaRepository.findByNumero(numeroDestinoInexistente)).thenReturn(Optional.empty());

        // When
        Response<String> response = transaccionService.transferir(numeroOrigen, numeroDestinoInexistente, monto, "Transferencia");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CUENTA_DESTINO_NO_ENCONTRADA", response.getCode());
        verify(transaccionRepository, never()).save(any());
    }

    @Test
    void testTransferir_MontoInvalido() {
        // Given
        String numeroOrigen = "2001234567890";
        String numeroDestino = "2001234567891";
        BigDecimal montoInvalido = new BigDecimal("-100.00");

        // When
        Response<String> response = transaccionService.transferir(numeroOrigen, numeroDestino, montoInvalido, "Transferencia");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("MONTO_INVALIDO", response.getCode());
        verify(cuentaRepository, never()).findByNumero(any());
        verify(transaccionRepository, never()).save(any());
    }

    @Test
    void testTransferir_SaldoInsuficiente() {
        // Given
        String numeroOrigen = "2001234567890";
        String numeroDestino = "2001234567891";
        BigDecimal montoExcesivo = new BigDecimal("5000.00"); // Mayor al saldo disponible

        when(cuentaRepository.findByNumero(numeroOrigen)).thenReturn(Optional.of(cuentaOrigen));
        when(cuentaRepository.findByNumero(numeroDestino)).thenReturn(Optional.of(cuentaDestino));

        // When
        Response<String> response = transaccionService.transferir(numeroOrigen, numeroDestino, montoExcesivo, "Transferencia");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("SALDO_INSUFICIENTE", response.getCode());
        verify(transaccionRepository, never()).save(any());
    }

    @Test
    void testTransferir_CuentaOrigenInactiva() {
        // Given
        cuentaOrigen.setEstado(Cuenta.Estado.INACTIVA);
        String numeroOrigen = "2001234567890";
        String numeroDestino = "2001234567891";
        BigDecimal monto = new BigDecimal("500.00");

        when(cuentaRepository.findByNumero(numeroOrigen)).thenReturn(Optional.of(cuentaOrigen));
        when(cuentaRepository.findByNumero(numeroDestino)).thenReturn(Optional.of(cuentaDestino));

        // When
        Response<String> response = transaccionService.transferir(numeroOrigen, numeroDestino, monto, "Transferencia");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CUENTA_ORIGEN_INACTIVA", response.getCode());
        verify(transaccionRepository, never()).save(any());
    }

    @Test
    void testTransferir_CuentaDestinoInactiva() {
        // Given
        cuentaDestino.setEstado(Cuenta.Estado.INACTIVA);
        String numeroOrigen = "2001234567890";
        String numeroDestino = "2001234567891";
        BigDecimal monto = new BigDecimal("500.00");

        when(cuentaRepository.findByNumero(numeroOrigen)).thenReturn(Optional.of(cuentaOrigen));
        when(cuentaRepository.findByNumero(numeroDestino)).thenReturn(Optional.of(cuentaDestino));

        // When
        Response<String> response = transaccionService.transferir(numeroOrigen, numeroDestino, monto, "Transferencia");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CUENTA_DESTINO_INACTIVA", response.getCode());
        verify(transaccionRepository, never()).save(any());
    }

    @Test
    void testTransferir_MismasCuentas() {
        // Given
        String numero = "2001234567890";
        BigDecimal monto = new BigDecimal("500.00");

        // When
        Response<String> response = transaccionService.transferir(numero, numero, monto, "Transferencia");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CUENTAS_IGUALES", response.getCode());
        verify(cuentaRepository, never()).findByNumero(any());
        verify(transaccionRepository, never()).save(any());
    }

    @Test
    void testTransferir_RetiroMinimoNoCumplido() {
        // Given
        String numeroOrigen = "2001234567890";
        String numeroDestino = "2001234567891";
        BigDecimal monto = new BigDecimal("1900.00"); // Dejaría saldo < mínimo (100)

        when(cuentaRepository.findByNumero(numeroOrigen)).thenReturn(Optional.of(cuentaOrigen));
        when(cuentaRepository.findByNumero(numeroDestino)).thenReturn(Optional.of(cuentaDestino));

        // When
        Response<String> response = transaccionService.transferir(numeroOrigen, numeroDestino, monto, "Transferencia");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("SALDO_MINIMO_NO_CUMPLIDO", response.getCode());
        verify(transaccionRepository, never()).save(any());
    }

    @Test
    void testConsultarHistorial_Success() {
        // Given
        String numeroCuenta = "2001234567890";
        LocalDate fechaInicio = LocalDate.now().minusDays(30);
        LocalDate fechaFin = LocalDate.now();

        List<Transaccion> transacciones = List.of(transaccion);
        
        when(cuentaRepository.findByNumero(numeroCuenta)).thenReturn(Optional.of(cuentaOrigen));
        when(transaccionRepository.findByCuentaAndFechaBetween(eq(cuentaOrigen), 
                any(LocalDateTime.class), any(LocalDateTime.class))).thenReturn(transacciones);

        // When
        Response<List<Transaccion>> response = transaccionService.consultarHistorial(numeroCuenta, fechaInicio, fechaFin);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Historial obtenido exitosamente", response.getMessage());
    }

    @Test
    void testConsultarHistorial_CuentaNotFound() {
        // Given
        String numeroInexistente = "9999999999999";
        LocalDate fechaInicio = LocalDate.now().minusDays(30);
        LocalDate fechaFin = LocalDate.now();

        when(cuentaRepository.findByNumero(numeroInexistente)).thenReturn(Optional.empty());

        // When
        Response<List<Transaccion>> response = transaccionService.consultarHistorial(numeroInexistente, fechaInicio, fechaFin);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CUENTA_NO_ENCONTRADA", response.getCode());
    }

    @Test
    void testConsultarHistorial_SinFechas() {
        // Given
        String numeroCuenta = "2001234567890";
        List<Transaccion> transacciones = List.of(transaccion);
        
        when(cuentaRepository.findByNumero(numeroCuenta)).thenReturn(Optional.of(cuentaOrigen));
        when(transaccionRepository.findByCuentaOrderByFechaDesc(cuentaOrigen)).thenReturn(transacciones);

        // When
        Response<List<Transaccion>> response = transaccionService.consultarHistorial(numeroCuenta, null, null);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        verify(transaccionRepository).findByCuentaOrderByFechaDesc(cuentaOrigen);
    }

    @Test
    void testConsultarTransaccionesPorFecha_Success() {
        // Given
        String numeroCuenta = "2001234567890";
        LocalDate fecha = LocalDate.now();
        List<Transaccion> transacciones = List.of(transaccion);

        when(cuentaRepository.findByNumero(numeroCuenta)).thenReturn(Optional.of(cuentaOrigen));
        when(transaccionRepository.findByCuentaAndFechaEquals(cuentaOrigen, fecha.atStartOfDay())).thenReturn(transacciones);

        // When
        Response<List<Transaccion>> response = transaccionService.consultarTransaccionesPorFecha(numeroCuenta, fecha);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Transacciones por fecha obtenidas exitosamente", response.getMessage());
    }

    @Test
    void testConsultarTransaccionesPorTipo_Success() {
        // Given
        String numeroCuenta = "2001234567890";
        Transaccion.Tipo tipo = Transaccion.Tipo.TRANSFERENCIA;
        List<Transaccion> transacciones = List.of(transaccion);

        when(cuentaRepository.findByNumero(numeroCuenta)).thenReturn(Optional.of(cuentaOrigen));
        when(transaccionRepository.findByCuentaAndTipoOrderByFechaDesc(cuentaOrigen, tipo)).thenReturn(transacciones);

        // When
        Response<List<Transaccion>> response = transaccionService.consultarTransaccionesPorTipo(numeroCuenta, tipo);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Transacciones por tipo obtenidas exitosamente", response.getMessage());
    }

    @Test
    void testAnularTransaccion_Success() {
        // Given
        Long idTransaccion = 1L;
        transaccion.setEstado(Transaccion.Estado.COMPLETADA);
        
        when(transaccionRepository.findById(idTransaccion)).thenReturn(Optional.of(transaccion));
        when(cuentaRepository.findByNumero(cuentaOrigen.getNumero())).thenReturn(Optional.of(cuentaOrigen));
        when(transaccionRepository.save(any(Transaccion.class))).thenReturn(transaccion);

        // When
        Response<String> response = transaccionService.anularTransaccion(idTransaccion, "Error en transferencia");

        // Then
        assertTrue(response.isSuccess());
        assertEquals(Transaccion.Estado.ANULADA, transaccion.getEstado());
        assertEquals("Error en transferencia", transaccion.getMotivoAnulacion());
        verify(rabbitMQService).enviarAlerta(eq("TRANSACCION_ANULADA"), anyString(), any());
    }

    @Test
    void testAnularTransaccion_TransaccionNotFound() {
        // Given
        Long idInexistente = 999999L;
        when(transaccionRepository.findById(idInexistente)).thenReturn(Optional.empty());

        // When
        Response<String> response = transaccionService.anularTransaccion(idInexistente, "Motivo");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("TRANSACCION_NO_ENCONTRADA", response.getCode());
    }

    @Test
    void testAnularTransaccion_EstadoNoAnulable() {
        // Given
        Long idTransaccion = 1L;
        transaccion.setEstado(Transaccion.Estado.ANULADA);
        
        when(transaccionRepository.findById(idTransaccion)).thenReturn(Optional.of(transaccion));

        // When
        Response<String> response = transaccionService.anularTransaccion(idTransaccion, "Motivo");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("ESTADO_NO_ANULABLE", response.getCode());
    }

    @Test
    void testRevertirTransaccion_Success() {
        // Given
        Long idTransaccion = 1L;
        transaccion.setTipo(Transaccion.Tipo.TRANSFERENCIA);
        transaccion.setCuentaDestino(cuentaDestino);
        
        when(transaccionRepository.findById(idTransaccion)).thenReturn(Optional.of(transaccion));
        when(cuentaRepository.findByNumero(cuentaOrigen.getNumero())).thenReturn(Optional.of(cuentaOrigen));
        when(cuentaRepository.findByNumero(cuentaDestino.getNumero())).thenReturn(Optional.of(cuentaDestino));
        when(cuentaRepository.save(any(Cuenta.class))).thenReturn(cuentaOrigen);

        // When
        Response<String> response = transaccionService.revertirTransaccion(idTransaccion, "Reversión por error");

        // Then
        assertTrue(response.isSuccess());
        assertEquals(Transaccion.Estado.REVERTIDA, transaccion.getEstado());
        // Verificar que se revirtieron los saldos
        assertEquals(new BigDecimal("2000.00"), cuentaOrigen.getSaldo()); // Volvió al saldo original
        assertEquals(new BigDecimal("1000.00"), cuentaDestino.getSaldo()); // Volvió al saldo original
        verify(rabbitMQService).enviarAlerta(eq("TRANSACCION_REVERTIDA"), anyString(), any());
    }

    @Test
    void testRevertirTransaccion_TipoNoReversible() {
        // Given
        Long idTransaccion = 1L;
        transaccion.setTipo(Transaccion.Tipo.DEPOSITO); // Tipo no reversible
        
        when(transaccionRepository.findById(idTransaccion)).thenReturn(Optional.of(transaccion));

        // When
        Response<String> response = transaccionService.revertirTransaccion(idTransaccion, "Reversión");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("TIPO_NO_REVERSIBLE", response.getCode());
    }

    @Test
    void testObtenerEstadisticasTransacciones_Success() {
        // Given
        String numeroCuenta = "2001234567890";
        LocalDate fechaInicio = LocalDate.now().minusDays(30);
        LocalDate fechaFin = LocalDate.now();

        // Simular estadísticas
        List<Object[]> estadisticas = new ArrayList<>();
        estadisticas.add(new Object[]{"DEPOSITO", 10L, new BigDecimal("5000.00")});
        estadisticas.add(new Object[]{"RETIRO", 5L, new BigDecimal("2000.00")});
        estadisticas.add(new Object[]{"TRANSFERENCIA", 8L, new BigDecimal("8000.00")});

        when(cuentaRepository.findByNumero(numeroCuenta)).thenReturn(Optional.of(cuentaOrigen));
        when(transaccionRepository.getEstadisticasByCuentaAndFechaBetween(
                eq(cuentaOrigen), any(LocalDateTime.class), any(LocalDateTime.class))).thenReturn(estadisticas);

        // When
        Response<List<Object[]>> response = transaccionService.obtenerEstadisticasTransacciones(numeroCuenta, fechaInicio, fechaFin);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(3, response.getData().size());
        assertEquals("Estadísticas obtenidas exitosamente", response.getMessage());
    }

    @Test
    void testObtenerBalanceDiario_Success() {
        // Given
        String numeroCuenta = "2001234567890";
        LocalDate fecha = LocalDate.now();

        List<Object[]> balance = new ArrayList<>();
        balance.add(new Object[]{LocalDate.now(), new BigDecimal("3000.00"), new BigDecimal("1500.00")});

        when(cuentaRepository.findByNumero(numeroCuenta)).thenReturn(Optional.of(cuentaOrigen));
        when(transaccionRepository.getBalanceDiario(cuentaOrigen, fecha.atStartOfDay())).thenReturn(balance);

        // When
        Response<List<Object[]>> response = transaccionService.obtenerBalanceDiario(numeroCuenta, fecha);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Balance diario obtenido exitosamente", response.getMessage());
    }

    @Test
    void testValidarTransferencia_NullValues() {
        // When
        Response<String> response = transaccionService.validarTransferencia(null, null, null, null);

        // Then
        assertFalse(response.isSuccess());
        assertTrue(response.getMessage().contains("obligatorio"));
    }

    @Test
    void testValidarTransferencia_CuentasInactivas() {
        // Given
        cuentaOrigen.setEstado(Cuenta.Estado.INACTIVA);
        cuentaDestino.setEstado(Cuenta.Estado.BLOQUEADA);

        // When
        Response<String> response = transaccionService.validarTransferencia(
                cuentaOrigen, cuentaDestino, new BigDecimal("100.00"), "Transferencia");

        // Then
        assertFalse(response.isSuccess());
        assertTrue(response.getMessage().contains("inactiva"));
    }

    @Test
    void testValidarTransferencia_MontoExcesivo() {
        // Given
        BigDecimal montoExcesivo = new BigDecimal("0.01"); // Menor al mínimo permitido

        // When
        Response<String> response = transaccionService.validarTransferencia(
                cuentaOrigen, cuentaDestino, montoExcesivo, "Transferencia");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("MONTO_MENOR_MINIMO", response.getCode());
    }

    @Test
    void testProcesarTransaccion_ActualizarSaldos() {
        // Given
        String numeroOrigen = "2001234567890";
        String numeroDestino = "2001234567891";
        BigDecimal monto = new BigDecimal("500.00");
        String descripcion = "Transferencia de prueba";

        when(cuentaRepository.findByNumero(numeroOrigen)).thenReturn(Optional.of(cuentaOrigen));
        when(cuentaRepository.findByNumero(numeroDestino)).thenReturn(Optional.of(cuentaDestino));
        when(cuentaRepository.save(any(Cuenta.class))).thenReturn(cuentaOrigen);

        // When
        transaccionService.transferir(numeroOrigen, numeroDestino, monto, descripcion);

        // Then
        // Verificar que los saldos se actualizaron correctamente
        assertEquals(new BigDecimal("1500.00"), cuentaOrigen.getSaldo());
        assertEquals(new BigDecimal("1500.00"), cuentaDestino.getSaldo());
        verify(cuentaRepository, times(2)).save(any(Cuenta.class));
    }

    @Test
    void testGenerarNumeroReferencia_Success() {
        // When
        String referencia = transaccionService.generarNumeroReferencia();

        // Then
        assertNotNull(referencia);
        assertEquals(20, referencia.length());
        assertTrue(referencia.startsWith("TXN"));
    }

    @Test
    void testCalcularComision_Success() {
        // Given
        BigDecimal monto = new BigDecimal("1000.00");
        Transaccion.Tipo tipo = Transaccion.Tipo.TRANSFERENCIA;
        boolean esClienteVIP = false;

        // When
        BigDecimal comision = transaccionService.calcularComision(monto, tipo, esClienteVIP);

        // Then
        assertNotNull(comision);
        assertTrue(comision.compareTo(BigDecimal.ZERO) >= 0);
    }

    @Test
    void testCalcularComision_ClienteVIP() {
        // Given
        BigDecimal monto = new BigDecimal("1000.00");
        Transaccion.Tipo tipo = Transaccion.Tipo.TRANSFERENCIA;
        boolean esClienteVIP = true;

        // When
        BigDecimal comision = transaccionService.calcularComision(monto, tipo, esClienteVIP);

        // Then
        assertNotNull(comision);
        // Cliente VIP debería tener descuento en comisión
        assertTrue(comision.compareTo(transaccionService.calcularComision(monto, tipo, false)) <= 0);
    }

    @Test
    void testObtenerLimitesTransaccion_Success() {
        // Given
        Cuenta.TipoCuenta tipoCuenta = Cuenta.TipoCuenta.AHORROS;

        // When
        Object[] limites = transaccionService.obtenerLimitesTransaccion(tipoCuenta);

        // Then
        assertNotNull(limites);
        assertEquals(3, limites.length); // mínimo, máximo, límite diario
        assertTrue(((BigDecimal)limites[0]).compareTo(BigDecimal.ZERO) > 0);
        assertTrue(((BigDecimal)limites[1]).compareTo((BigDecimal)limites[0]) > 0);
        assertTrue(((BigDecimal)limites[2]).compareTo(BigDecimal.ZERO) > 0);
    }
}
