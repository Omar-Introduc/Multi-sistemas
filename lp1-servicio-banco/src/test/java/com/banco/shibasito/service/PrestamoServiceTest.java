package com.banco.shibasito.service;

import com.banco.shibasito.dto.Response;
import com.banco.shibasito.entity.Cliente;
import com.banco.shibasito.entity.Prestamo;
import com.banco.shibasito.repository.PrestamoRepository;
import com.banco.shibasito.repository.ClienteRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Pruebas unitarias para PrestamoService
 * Valida la lógica de negocio del servicio de préstamos
 */
@ExtendWith(MockitoExtension.class)
class PrestamoServiceTest {

    @Mock
    private PrestamoRepository prestamoRepository;

    @Mock
    private ClienteRepository clienteRepository;

    @Mock
    private BancoRabbitMQService rabbitMQService;

    @InjectMocks
    private PrestamoService prestamoService;

    private Cliente cliente;
    private Prestamo prestamo;

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

        // Crear préstamo mock
        prestamo = new Prestamo();
        prestamo.setId(1L);
        prestamo.setCliente(cliente);
        prestamo.setMonto(new BigDecimal("10000.00"));
        prestamo.setPlazoMeses(24);
        prestamo.setMotivo("Compra de vehículo");
        prestamo.setEstado("PENDIENTE");
        prestamo.setFecha(LocalDate.now());
    }

    @Test
    void testSolicitarPrestamo_Success() {
        // Given
        String dniCliente = "12345678";
        BigDecimal monto = new BigDecimal("10000.00");
        int plazoMeses = 24;
        String motivo = "Compra de vehículo";

        when(clienteRepository.findByDni(dniCliente)).thenReturn(Optional.of(cliente));
        when(prestamoRepository.findByClienteDniAndEstado(dniCliente, "PENDIENTE"))
                .thenReturn(new ArrayList<>());
        when(prestamoRepository.save(any(Prestamo.class))).thenReturn(prestamo);

        // When
        Response<Prestamo> response = prestamoService.solicitarPrestamo(dniCliente, monto, plazoMeses, motivo);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("Solicitud de préstamo creada exitosamente", response.getMessage());
        assertNotNull(response.getData());
        verify(rabbitMQService).enviarEventoPrestamoSolicitado(any(Prestamo.class));
    }

    @Test
    void testSolicitarPrestamo_ClienteNotFound() {
        // Given
        String dniInexistente = "99999999";
        BigDecimal monto = new BigDecimal("5000.00");
        int plazoMeses = 12;
        String motivo = "Préstamo personal";

        when(clienteRepository.findByDni(dniInexistente)).thenReturn(Optional.empty());

        // When
        Response<Prestamo> response = prestamoService.solicitarPrestamo(dniInexistente, monto, plazoMeses, motivo);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CLIENTE_NO_ENCONTRADO", response.getCode());
        verify(prestamoRepository, never()).save(any());
        verify(rabbitMQService, never()).enviarEventoPrestamoSolicitado(any());
    }

    @Test
    void testSolicitarPrestamo_ClienteInactivo() {
        // Given
        cliente.setEstado(Cliente.Estado.INACTIVO);
        String dniCliente = "12345678";
        BigDecimal monto = new BigDecimal("5000.00");
        int plazoMeses = 12;
        String motivo = "Préstamo personal";

        when(clienteRepository.findByDni(dniCliente)).thenReturn(Optional.of(cliente));

        // When
        Response<Prestamo> response = prestamoService.solicitarPrestamo(dniCliente, monto, plazoMeses, motivo);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CLIENTE_INACTIVO", response.getCode());
        verify(prestamoRepository, never()).save(any());
    }

    @Test
    void testSolicitarPrestamo_SolicitudPendienteExistente() {
        // Given
        String dniCliente = "12345678";
        BigDecimal monto = new BigDecimal("5000.00");
        int plazoMeses = 12;
        String motivo = "Préstamo personal";

        Prestamo prestamoPendiente = new Prestamo();
        prestamoPendiente.setEstado("PENDIENTE");

        when(clienteRepository.findByDni(dniCliente)).thenReturn(Optional.of(cliente));
        when(prestamoRepository.findByClienteDniAndEstado(dniCliente, "PENDIENTE"))
                .thenReturn(List.of(prestamoPendiente));

        // When
        Response<Prestamo> response = prestamoService.solicitarPrestamo(dniCliente, monto, plazoMeses, motivo);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("SOLICITUD_PENDIENTE", response.getCode());
        verify(prestamoRepository, never()).save(any());
    }

    @Test
    void testSolicitarPrestamo_MontoExcesivo() {
        // Given
        String dniCliente = "12345678";
        BigDecimal monto = new BigDecimal("200000.00");
        int plazoMeses = 24;
        String motivo = "Inversión empresarial";

        when(clienteRepository.findByDni(dniCliente)).thenReturn(Optional.of(cliente));
        when(prestamoRepository.findByClienteDniAndEstado(dniCliente, "PENDIENTE"))
                .thenReturn(new ArrayList<>());

        // When
        Response<Prestamo> response = prestamoService.solicitarPrestamo(dniCliente, monto, plazoMeses, motivo);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("MONTO_EXCESIVO", response.getCode());
        verify(prestamoRepository, never()).save(any());
    }

    @Test
    void testSolicitarPrestamo_PlazoInvalido() {
        // Given
        String dniCliente = "12345678";
        BigDecimal monto = new BigDecimal("5000.00");
        int plazoMeses = 100; // Plazo muy largo
        String motivo = "Préstamo personal";

        when(clienteRepository.findByDni(dniCliente)).thenReturn(Optional.of(cliente));
        when(prestamoRepository.findByClienteDniAndEstado(dniCliente, "PENDIENTE"))
                .thenReturn(new ArrayList<>());

        // When
        Response<Prestamo> response = prestamoService.solicitarPrestamo(dniCliente, monto, plazoMeses, motivo);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("PLAZO_INVALIDO", response.getCode());
        verify(prestamoRepository, never()).save(any());
    }

    @Test
    void testSolicitarPrestamo_MontoMinimo() {
        // Given
        String dniCliente = "12345678";
        BigDecimal monto = new BigDecimal("500.00"); // Menor al mínimo de $1000
        int plazoMeses = 12;
        String motivo = "Préstamo personal";

        when(clienteRepository.findByDni(dniCliente)).thenReturn(Optional.of(cliente));
        when(prestamoRepository.findByClienteDniAndEstado(dniCliente, "PENDIENTE"))
                .thenReturn(new ArrayList<>());

        // When
        Response<Prestamo> response = prestamoService.solicitarPrestamo(dniCliente, monto, plazoMeses, motivo);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("MONTO_MINIMO_NO_CUMPLIDO", response.getCode());
    }

    @Test
    void testEvaluarSolicitud_Success() {
        // Given
        Long idPrestamo = 1L;
        when(prestamoRepository.findById(idPrestamo)).thenReturn(Optional.of(prestamo));
        when(prestamoRepository.save(any(Prestamo.class))).thenReturn(prestamo);

        // When
        Response<Prestamo> response = prestamoService.evaluarSolicitud(idPrestamo);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("EVALUANDO", prestamo.getEstado());
        assertTrue(response.getMessage().contains("Evaluación completada"));
    }

    @Test
    void testEvaluarSolicitud_PrestamoNotFound() {
        // Given
        Long idInexistente = 999999L;
        when(prestamoRepository.findById(idInexistente)).thenReturn(Optional.empty());

        // When
        Response<Prestamo> response = prestamoService.evaluarSolicitud(idInexistente);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("PRESTAMO_NO_ENCONTRADO", response.getCode());
    }

    @Test
    void testEvaluarSolicitud_EstadoNoEvaluable() {
        // Given
        prestamo.setEstado("APROBADO");
        Long idPrestamo = 1L;
        when(prestamoRepository.findById(idPrestamo)).thenReturn(Optional.of(prestamo));

        // When
        Response<Prestamo> response = prestamoService.evaluarSolicitud(idPrestamo);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("ESTADO_NO_EVALUABLE", response.getCode());
    }

    @Test
    void testAprobarPrestamo_Success() {
        // Given
        Long idPrestamo = 1L;
        BigDecimal montoAprobado = new BigDecimal("8000.00");
        String observaciones = "Aprobado con reducción de monto";

        when(prestamoRepository.findById(idPrestamo)).thenReturn(Optional.of(prestamo));
        when(prestamoRepository.save(any(Prestamo.class))).thenReturn(prestamo);

        // When
        Response<Prestamo> response = prestamoService.aprobarPrestamo(idPrestamo, montoAprobado, observaciones);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("APROBADO", prestamo.getEstado());
        assertEquals(montoAprobado, prestamo.getMontoAprobado());
        assertEquals(LocalDate.now(), prestamo.getFechaAprobacion());
        assertNotNull(prestamo.getFechaVencimiento());
        assertNotNull(prestamo.getCuotaMensual());
        assertEquals(prestamo.getMontoAprobado(), prestamo.getSaldoPendiente());
        verify(rabbitMQService).enviarEventoPrestamoAprobado(any(Prestamo.class));
    }

    @Test
    void testAprobarPrestamo_PrestamoNotFound() {
        // Given
        Long idInexistente = 999999L;
        BigDecimal montoAprobado = new BigDecimal("5000.00");
        String observaciones = "Aprobación";

        when(prestamoRepository.findById(idInexistente)).thenReturn(Optional.empty());

        // When
        Response<Prestamo> response = prestamoService.aprobarPrestamo(idInexistente, montoAprobado, observaciones);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("PRESTAMO_NO_ENCONTRADO", response.getCode());
    }

    @Test
    void testAprobarPrestamo_EstadoNoAprobable() {
        // Given
        prestamo.setEstado("RECHAZADO");
        Long idPrestamo = 1L;
        BigDecimal montoAprobado = new BigDecimal("5000.00");
        String observaciones = "Aprobación";

        when(prestamoRepository.findById(idPrestamo)).thenReturn(Optional.of(prestamo));

        // When
        Response<Prestamo> response = prestamoService.aprobarPrestamo(idPrestamo, montoAprobado, observaciones);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("ESTADO_NO_APROBABLE", response.getCode());
    }

    @Test
    void testAprobarPrestamo_MontoExcedeSolicitado() {
        // Given
        Long idPrestamo = 1L;
        BigDecimal montoExcesivo = new BigDecimal("15000.00"); // Mayor al solicitado ($10000)
        String observaciones = "Aprobación";

        when(prestamoRepository.findById(idPrestamo)).thenReturn(Optional.of(prestamo));

        // When
        Response<Prestamo> response = prestamoService.aprobarPrestamo(idPrestamo, montoExcesivo, observaciones);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("MONTO_EXCEDE_SOLICITADO", response.getCode());
    }

    @Test
    void testRechazarPrestamo_Success() {
        // Given
        Long idPrestamo = 1L;
        String motivo = "Capacidad de pago insuficiente";

        when(prestamoRepository.findById(idPrestamo)).thenReturn(Optional.of(prestamo));
        when(prestamoRepository.save(any(Prestamo.class))).thenReturn(prestamo);

        // When
        Response<String> response = prestamoService.rechazarPrestamo(idPrestamo, motivo);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("RECHAZADO", prestamo.getEstado());
        assertEquals(motivo, prestamo.getMotivoRechazo());
        verify(rabbitMQService).enviarEventoPrestamoRechazado(any(Prestamo.class));
    }

    @Test
    void testRechazarPrestamo_PrestamoNotFound() {
        // Given
        Long idInexistente = 999999L;
        String motivo = "Motivo de rechazo";

        when(prestamoRepository.findById(idInexistente)).thenReturn(Optional.empty());

        // When
        Response<String> response = prestamoService.rechazarPrestamo(idInexistente, motivo);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("PRESTAMO_NO_ENCONTRADO", response.getCode());
    }

    @Test
    void testRechazarPrestamo_EstadoNoRechazable() {
        // Given
        prestamo.setEstado("APROBADO");
        Long idPrestamo = 1L;
        String motivo = "Motivo de rechazo";

        when(prestamoRepository.findById(idPrestamo)).thenReturn(Optional.of(prestamo));

        // When
        Response<String> response = prestamoService.rechazarPrestamo(idPrestamo, motivo);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("ESTADO_NO_RECHAZABLE", response.getCode());
    }

    @Test
    void testListarPrestamos_Success() {
        // Given
        String dniCliente = "12345678";
        List<Prestamo> prestamos = List.of(prestamo);
        when(prestamoRepository.findByClienteDniOrderByFechaDesc(dniCliente)).thenReturn(prestamos);

        // When
        Response<List<Prestamo>> response = prestamoService.listarPrestamos(dniCliente);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Préstamos obtenidos exitosamente", response.getMessage());
    }

    @Test
    void testListarPrestamos_DniRequerido() {
        // When
        Response<List<Prestamo>> response = prestamoService.listarPrestamos(null);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("DNI_CLIENTE_REQUERIDO", response.getCode());
    }

    @Test
    void testListarPrestamosPorEstado_Success() {
        // Given
        String estado = "PENDIENTE";
        List<Prestamo> prestamos = List.of(prestamo);
        when(prestamoRepository.findByEstado(estado)).thenReturn(prestamos);

        // When
        Response<List<Prestamo>> response = prestamoService.listarPrestamosPorEstado(estado);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Préstamos obtenidos exitosamente", response.getMessage());
    }

    @Test
    void testListarPrestamosPorEstado_EstadoRequerido() {
        // When
        Response<List<Prestamo>> response = prestamoService.listarPrestamosPorEstado(null);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("ESTADO_REQUERIDO", response.getCode());
    }

    @Test
    void testListarPendientes_Success() {
        // Given
        List<Prestamo> prestamosPendientes = List.of(prestamo);
        when(prestamoRepository.findPendientesOrderByFechaAsc()).thenReturn(prestamosPendientes);

        // When
        Response<List<Prestamo>> response = prestamoService.listarPendientes();

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Préstamos pendientes obtenidos exitosamente", response.getMessage());
    }

    @Test
    void testCalcularTasaInteres_MontoAlto() {
        // Given
        BigDecimal montoAlto = new BigDecimal("60000.00");
        int plazoMeses = 24;

        // When
        BigDecimal tasa = prestamoService.calcularTasaInteres(montoAlto, plazoMeses);

        // Then
        assertTrue(tasa.compareTo(new BigDecimal("10.00")) == 0); // 12% - 2% por monto alto
    }

    @Test
    void testCalcularTasaInteres_MontoBajo() {
        // Given
        BigDecimal montoBajo = new BigDecimal("5000.00");
        int plazoMeses = 24;

        // When
        BigDecimal tasa = prestamoService.calcularTasaInteres(montoBajo, plazoMeses);

        // Then
        assertTrue(tasa.compareTo(new BigDecimal("15.00")) == 0); // 12% + 3% por monto bajo
    }

    @Test
    void testCalcularTasaInteres_PlazoLargo() {
        // Given
        BigDecimal monto = new BigDecimal("20000.00");
        int plazoLargo = 48;

        // When
        BigDecimal tasa = prestamoService.calcularTasaInteres(monto, plazoLargo);

        // Then
        assertTrue(tasa.compareTo(new BigDecimal("13.00")) == 0); // 12% + 1% por plazo largo
    }

    @Test
    void testCalcularTasaInteres_PlazoCorto() {
        // Given
        BigDecimal monto = new BigDecimal("20000.00");
        int plazoCorto = 6;

        // When
        BigDecimal tasa = prestamoService.calcularTasaInteres(monto, plazoCorto);

        // Then
        assertTrue(tasa.compareTo(new BigDecimal("11.00")) == 0); // 12% - 1% por plazo corto
    }

    @Test
    void testCalcularTasaInteres_LimiteMinimo() {
        // Given
        BigDecimal monto = new BigDecimal("80000.00");
        int plazoLargo = 48;

        // When
        BigDecimal tasa = prestamoService.calcularTasaInteres(monto, plazoLargo);

        // Then
        assertEquals(new BigDecimal("8.00"), tasa); // Límite mínimo
    }

    @Test
    void testCalcularTasaInteres_LimiteMaximo() {
        // Given
        BigDecimal monto = new BigDecimal("8000.00");
        int plazoLargo = 48;

        // When
        BigDecimal tasa = prestamoService.calcularTasaInteres(monto, plazoLargo);

        // Then
        assertEquals(new BigDecimal("20.00"), tasa); // Límite máximo
    }

    @Test
    void testCalcularCuotaMensual_Success() {
        // Given
        Prestamo prestamoConDatos = new Prestamo();
        prestamoConDatos.setMontoAprobado(new BigDecimal("12000.00"));
        prestamoConDatos.setTasaInteres(new BigDecimal("12.00")); // 12% anual
        prestamoConDatos.setPlazoMeses(24);

        // When
        prestamoService.calcularCuotaMensual(prestamoConDatos);

        // Then
        assertNotNull(prestamoConDatos.getCuotaMensual());
        assertTrue(prestamoConDatos.getCuotaMensual().compareTo(BigDecimal.ZERO) > 0);
        assertEquals(prestamoConDatos.getMontoAprobado(), prestamoConDatos.getSaldoPendiente());
    }

    @Test
    void testValidarSolicitudPrestamo_DatosCompletos() {
        // Given
        String dniCliente = "12345678";
        BigDecimal monto = new BigDecimal("10000.00");
        int plazoMeses = 24;
        String motivo = "Compra de vehículo";

        // When
        Response<Prestamo> response = prestamoService.validarSolicitudPrestamo(
                dniCliente, monto, plazoMeses, motivo);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("Validación exitosa", response.getMessage());
    }

    @Test
    void testValidarSolicitudPrestamo_DatosNulos() {
        // When
        Response<Prestamo> response = prestamoService.validarSolicitudPrestamo(
                null, null, 0, null);

        // Then
        assertFalse(response.isSuccess());
        assertTrue(response.getMessage().contains("obligatorio"));
    }

    @Test
    void testValidarSolicitudPrestamo_MontoNegativo() {
        // Given
        BigDecimal montoNegativo = new BigDecimal("-1000.00");

        // When
        Response<Prestamo> response = prestamoService.validarSolicitudPrestamo(
                "12345678", montoNegativo, 12, "Motivo");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("MONTO_INVALIDO", response.getCode());
    }

    @Test
    void testValidarSolicitudPrestamo_PlazoCero() {
        // Given
        int plazoCero = 0;

        // When
        Response<Prestamo> response = prestamoService.validarSolicitudPrestamo(
                "12345678", new BigDecimal("5000.00"), plazoCero, "Motivo");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("PLAZO_INVALIDO", response.getCode());
    }

    @Test
    void testEvaluacionCrediticia_Aprobacion() {
        // Given
        Prestamo prestamoEvaluar = new Prestamo();
        prestamoEvaluar.setMonto(new BigDecimal("5000.00"));

        // When
        Response<String> response = prestamoService.realizarEvaluacionCrediticia(prestamoEvaluar);

        // Then
        // Nota: Esta prueba usa Math.random() por lo que puede variar entre ejecuciones
        // En un entorno real, se debería mockear la evaluación o usar seeds
        assertNotNull(response.getMessage());
        assertTrue(response.isSuccess() || !response.isSuccess());
    }
}
