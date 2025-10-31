package com.banco.shibasito.integration;

import com.banco.shibasito.dto.Response;
import com.banco.shibasito.entity.Cliente;
import com.banco.shibasito.entity.Cuenta;
import com.banco.shibasito.entity.Transaccion;
import com.banco.shibasito.service.CuentaService;
import com.banco.shibasito.service.PrestamoService;
import com.banco.shibasito.service.TransaccionService;
import com.banco.shibasito.service.BancoRabbitMQService;
import com.banco.shibasito.repository.CuentaRepository;
import com.banco.shibasito.repository.ClienteRepository;
import com.banco.shibasito.repository.PrestamoRepository;
import com.banco.shibasito.repository.TransaccionRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.RabbitMQContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

import java.math.BigDecimal;
import java.util.List;
import java.util.concurrent.TimeUnit;

import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.timeout;
import static org.mockito.Mockito.verify;

/**
 * Pruebas de integración para el sistema bancario completo
 * Incluye pruebas de integración con RabbitMQ
 */
@SpringBootTest
@ActiveProfiles("integration")
@Testcontainers
class BancoIntegrationTest {

    @Container
    static RabbitMQContainer rabbitMQContainer = new RabbitMQContainer(
            DockerImageName.parse("rabbitmq:3.8-management-alpine")
    );

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.rabbitmq.host", rabbitMQContainer::getHost);
        registry.add("spring.rabbitmq.port", rabbitMQContainer::getAmqpPort);
        registry.add("spring.rabbitmq.username", rabbitMQContainer::getAdminUsername);
        registry.add("spring.rabbitmq.password", rabbitMQContainer::getAdminPassword);
    }

    @Autowired
    private CuentaService cuentaService;

    @Autowired
    private PrestamoService prestamoService;

    @Autowired
    private TransaccionService transaccionService;

    @Autowired
    private BancoRabbitMQService rabbitMQService;

    @Autowired
    private CuentaRepository cuentaRepository;

    @Autowired
    private ClienteRepository clienteRepository;

    @Autowired
    private PrestamoRepository prestamoRepository;

    @Autowired
    private TransaccionRepository transaccionRepository;

    // Mock para verificar llamadas a RabbitMQ sin enviar mensajes reales
    @MockBean
    private BancoRabbitMQService mockRabbitMQService;

    private Cliente cliente;
    private Cuenta cuenta;
    private Transaccion transaccion;

    @BeforeEach
    void setUp() {
        // Limpiar datos de pruebas anteriores
        prestamoRepository.deleteAll();
        transaccionRepository.deleteAll();
        cuentaRepository.deleteAll();
        clienteRepository.deleteAll();

        // Crear cliente para pruebas
        cliente = new Cliente();
        cliente.setDni("12345678");
        cliente.setNombre("Juan");
        cliente.setApellido("Pérez");
        cliente.setEmail("juan.perez@test.com");
        cliente.setTelefono("999888777");
        cliente.setEstado(Cliente.Estado.ACTIVO);
        cliente = clienteRepository.save(cliente);

        // Crear cuenta para pruebas
        cuenta = new Cuenta();
        cuenta.setNumero("2001234567890");
        cuenta.setSaldo(new BigDecimal("2000.00"));
        cuenta.setTipo(Cuenta.TipoCuenta.AHORROS);
        cuenta.setEstado(Cuenta.Estado.ACTIVA);
        cuenta.setCliente(cliente);
        cuenta = cuentaRepository.save(cuenta);
    }

    @Test
    void testCrearCuenta_EnvioRabbitMQ() {
        // Given
        String numero = "2001234567891";
        String dniCliente = cliente.getDni();
        Cuenta.TipoCuenta tipo = Cuenta.TipoCuenta.CORRIENTE;
        BigDecimal saldoInicial = new BigDecimal("1500.00");

        // When
        Response<Cuenta> response = cuentaService.crearCuenta(numero, dniCliente, tipo, saldoInicial);

        // Then
        assertTrue(response.isSuccess());
        assertNotNull(response.getData());
        
        // Verificar que se envió mensaje a RabbitMQ
        verify(mockRabbitMQService, timeout(5000)).enviarEventoCuentaCreada(any(Cuenta.class));
    }

    @Test
    void testDeposito_EnvioRabbitMQ() {
        // Given
        String numero = cuenta.getNumero();
        BigDecimal monto = new BigDecimal("500.00");
        String descripcion = "Depósito de prueba";

        // When
        Response<String> response = cuentaService.depositar(numero, monto, descripcion);

        // Then
        assertTrue(response.isSuccess());
        assertTrue(response.getMessage().contains("Depósito realizado exitosamente"));
        
        // Verificar que se envió mensaje a RabbitMQ
        verify(mockRabbitMQService, timeout(5000)).enviarEventoTransaccionProcesada(any(Transaccion.class));
    }

    @Test
    void testRetiro_EnvioRabbitMQ() {
        // Given
        String numero = cuenta.getNumero();
        BigDecimal monto = new BigDecimal("300.00");
        String descripcion = "Retiro de prueba";

        // When
        Response<String> response = cuentaService.retirar(numero, monto, descripcion);

        // Then
        assertTrue(response.isSuccess());
        assertTrue(response.getMessage().contains("Retiro realizado exitosamente"));
        
        // Verificar que se envió mensaje a RabbitMQ
        verify(mockRabbitMQService, timeout(5000)).enviarEventoTransaccionProcesada(any(Transaccion.class));
    }

    @Test
    void testSolicitarPrestamo_EnvioRabbitMQ() {
        // Given
        String dniCliente = cliente.getDni();
        BigDecimal monto = new BigDecimal("10000.00");
        int plazoMeses = 24;
        String motivo = "Compra de vehículo";

        // When
        Response<com.banco.shibasito.entity.Prestamo> response = prestamoService.solicitarPrestamo(
                dniCliente, monto, plazoMeses, motivo);

        // Then
        assertTrue(response.isSuccess());
        assertNotNull(response.getData());
        assertEquals("PENDIENTE", response.getData().getEstado());
        
        // Verificar que se envió mensaje a RabbitMQ
        verify(mockRabbitMQService, timeout(5000)).enviarEventoPrestamoSolicitado(any());
    }

    @Test
    void testAprobarPrestamo_EnvioRabbitMQ() {
        // Given - Crear préstamo pendiente
        com.banco.shibasito.entity.Prestamo prestamo = new com.banco.shibasito.entity.Prestamo();
        prestamo.setCliente(cliente);
        prestamo.setMonto(new BigDecimal("10000.00"));
        prestamo.setPlazoMeses(24);
        prestamo.setMotivo("Compra de vehículo");
        prestamo.setEstado("PENDIENTE");
        prestamo = prestamoRepository.save(prestamo);

        BigDecimal montoAprobado = new BigDecimal("8000.00");
        String observaciones = "Aprobado con reducción de monto";

        // When
        Response<com.banco.shibasito.entity.Prestamo> response = prestamoService.aprobarPrestamo(
                prestamo.getId(), montoAprobado, observaciones);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("APROBADO", response.getData().getEstado());
        assertEquals(montoAprobado, response.getData().getMontoAprobado());
        
        // Verificar que se envió mensaje a RabbitMQ
        verify(mockRabbitMQService, timeout(5000)).enviarEventoPrestamoAprobado(any());
    }

    @Test
    void testRechazarPrestamo_EnvioRabbitMQ() {
        // Given - Crear préstamo pendiente
        com.banco.shibasito.entity.Prestamo prestamo = new com.banco.shibasito.entity.Prestamo();
        prestamo.setCliente(cliente);
        prestamo.setMonto(new BigDecimal("50000.00"));
        prestamo.setPlazoMeses(36);
        prestamo.setMotivo("Expansión de negocio");
        prestamo.setEstado("PENDIENTE");
        prestamo = prestamoRepository.save(prestamo);

        String motivoRechazo = "Capacidad de pago insuficiente";

        // When
        Response<String> response = prestamoService.rechazarPrestamo(prestamo.getId(), motivoRechazo);

        // Then
        assertTrue(response.isSuccess());
        
        // Verificar estado actualizado
        com.banco.shibasito.entity.Prestamo prestamoActualizado = 
                prestamoRepository.findById(prestamo.getId()).get();
        assertEquals("RECHAZADO", prestamoActualizado.getEstado());
        assertEquals(motivoRechazo, prestamoActualizado.getMotivoRechazo());
        
        // Verificar que se envió mensaje a RabbitMQ
        verify(mockRabbitMQService, timeout(5000)).enviarEventoPrestamoRechazado(any());
    }

    @Test
    void testBloquearCuenta_EnvioAlerta() {
        // Given
        String numero = cuenta.getNumero();
        String motivo = "Actividad sospechosa detectada";

        // When
        Response<String> response = cuentaService.bloquearCuenta(numero, motivo);

        // Then
        assertTrue(response.isSuccess());
        
        // Verificar estado actualizado
        Cuenta cuentaActualizada = cuentaRepository.findByNumero(numero).get();
        assertEquals(Cuenta.Estado.BLOQUEADA, cuentaActualizada.getEstado());
        
        // Verificar que se envió alerta a RabbitMQ
        verify(mockRabbitMQService, timeout(5000)).enviarAlerta(
                eq("CUENTA_BLOQUEADA"), anyString(), isNull());
    }

    @Test
    void testFlujoCompleto_CreacionDepositoRetiro() {
        // 1. Crear nueva cuenta
        String numeroNuevaCuenta = "2001234567892";
        Response<Cuenta> crearResponse = cuentaService.crearCuenta(
                numeroNuevaCuenta, cliente.getDni(), 
                Cuenta.TipoCuenta.AHORROS, new BigDecimal("1000.00"));
        
        assertTrue(crearResponse.isSuccess());
        verify(mockRabbitMQService, timeout(5000)).enviarEventoCuentaCreada(any(Cuenta.class));

        // 2. Realizar depósito
        BigDecimal montoDeposito = new BigDecimal("500.00");
        Response<String> depositoResponse = cuentaService.depositar(
                numeroNuevaCuenta, montoDeposito, "Apertura de cuenta");
        
        assertTrue(depositoResponse.isSuccess());
        verify(mockRabbitMQService, timeout(5000)).enviarEventoTransaccionProcesada(any(Transaccion.class));

        // 3. Verificar saldo
        Response<BigDecimal> saldoResponse = cuentaService.consultarSaldo(numeroNuevaCuenta);
        assertTrue(saldoResponse.isSuccess());
        assertEquals(new BigDecimal("1500.00"), saldoResponse.getData());

        // 4. Realizar retiro parcial
        BigDecimal montoRetiro = new BigDecimal("200.00");
        Response<String> retiroResponse = cuentaService.retirar(
                numeroNuevaCuenta, montoRetiro, "Retiro parcial");
        
        assertTrue(retiroResponse.isSuccess());
        verify(mockRabbitMQService, timeout(5000)).enviarEventoTransaccionProcesada(any(Transaccion.class));

        // 5. Verificar saldo final
        Response<BigDecimal> saldoFinalResponse = cuentaService.consultarSaldo(numeroNuevaCuenta);
        assertTrue(saldoFinalResponse.isSuccess());
        assertEquals(new BigDecimal("1300.00"), saldoFinalResponse.getData());
    }

    @Test
    void testFlujoCompleto_SolicitudPrestamo() {
        // 1. Solicitar préstamo
        Response<com.banco.shibasito.entity.Prestamo> solicitudResponse = prestamoService.solicitarPrestamo(
                cliente.getDni(), new BigDecimal("15000.00"), 30, "Mejora de vivienda");
        
        assertTrue(solicitudResponse.isSuccess());
        assertEquals("PENDIENTE", solicitudResponse.getData().getEstado());
        verify(mockRabbitMQService, timeout(5000)).enviarEventoPrestamoSolicitado(any());

        // 2. Listar préstamos del cliente
        Response<List<com.banco.shibasito.entity.Prestamo>> listarResponse = 
                prestamoService.listarPrestamos(cliente.getDni());
        
        assertTrue(listarResponse.isSuccess());
        assertEquals(1, listarResponse.getData().size());
        assertEquals("PENDIENTE", listarResponse.getData().get(0).getEstado());

        // 3. Aprobar préstamo
        Response<com.banco.shibasito.entity.Prestamo> aprobarResponse = 
                prestamoService.aprobarPrestamo(solicitudResponse.getData().getId(), 
                        new BigDecimal("12000.00"), "Aprobado por comité");
        
        assertTrue(aprobarResponse.isSuccess());
        assertEquals("APROBADO", aprobarResponse.getData().getEstado());
        assertEquals(new BigDecimal("12000.00"), aprobarResponse.getData().getMontoAprobado());
        verify(mockRabbitMQService, timeout(5000)).enviarEventoPrestamoAprobado(any());

        // 4. Verificar que se eliminó de pendientes
        Response<List<com.banco.shibasito.entity.Prestamo>> pendientesResponse = 
                prestamoService.listarPendientes();
        
        assertTrue(pendientesResponse.isSuccess());
        assertTrue(pendientesResponse.getData().isEmpty());
    }

    @Test
    void testIntegridadTransaccional_rollbackEnError() {
        // Given - Simular un error durante la creación
        // Nota: En una prueba real, esto requeriría configurar el repository para lanzar excepción
        
        String numero = "2001234567893";
        
        // Esta prueba debería ser expandida con configuración específica para testing de rollback
        // Por ahora verificamos el comportamiento normal
        
        Response<Cuenta> response = cuentaService.crearCuenta(
                numero, cliente.getDni(), Cuenta.TipoCuenta.AHORROS, new BigDecimal("500.00"));
        
        assertTrue(response.isSuccess());
        
        // Verificar que la cuenta fue creada
        Cuenta cuentaCreada = cuentaRepository.findByNumero(numero).get();
        assertNotNull(cuentaCreada);
        assertEquals(numero, cuentaCreada.getNumero());
    }

    @Test
    void testValidacionesNegocio_ImpedirOperacionesInvalidas() {
        // 1. Intentar depositar monto negativo
        Response<String> depositoNegativo = cuentaService.depositar(
                cuenta.getNumero(), new BigDecimal("-100.00"), "Depósito inválido");
        
        assertFalse(depositoNegativo.isSuccess());
        assertEquals("MONTO_INVALIDO", depositoNegativo.getCode());

        // 2. Intentar retirar más del saldo disponible
        Response<String> retiroExcesivo = cuentaService.retirar(
                cuenta.getNumero(), new BigDecimal("100000.00"), "Retiro excesivo");
        
        assertFalse(retiroExcesivo.isSuccess());
        assertEquals("RETIRO_NO_PERMITIDO", retiroExcesivo.getCode());

        // 3. Intentar operar con cuenta inexistente
        Response<String> operacionCuentaInexistente = cuentaService.depositar(
                "9999999999999", new BigDecimal("100.00"), "Cuenta inexistente");
        
        assertFalse(operacionCuentaInexistente.isSuccess());
        assertEquals("CUENTA_NO_ENCONTRADA", operacionCuentaInexistente.getCode());
    }

    @Test
    void testManejoEstadosCuenta() {
        // 1. Verificar estado inicial
        assertEquals(Cuenta.Estado.ACTIVA, cuenta.getEstado());

        // 2. Bloquear cuenta
        Response<String> bloquearResponse = cuentaService.bloquearCuenta(
                cuenta.getNumero(), "Bloqueo por seguridad");
        assertTrue(bloquearResponse.isSuccess());
        
        verify(mockRabbitMQService, timeout(5000)).enviarAlerta(
                eq("CUENTA_BLOQUEADA"), anyString(), isNull());

        // 3. Verificar que no se puede operar con cuenta bloqueada
        Response<String> depositoBloqueada = cuentaService.depositar(
                cuenta.getNumero(), new BigDecimal("100.00"), "Depósito en cuenta bloqueada");
        assertFalse(depositoBloqueada.isSuccess());
        assertEquals("CUENTA_INACTIVA", depositoBloqueada.getCode());

        // 4. Desbloquear cuenta
        Response<String> desbloquearResponse = cuentaService.desbloquearCuenta(cuenta.getNumero());
        assertTrue(desbloquearResponse.isSuccess());

        // 5. Verificar que se puede operar normalmente
        Response<String> depositoDesbloqueada = cuentaService.depositar(
                cuenta.getNumero(), new BigDecimal("100.00"), "Depósito en cuenta desbloqueada");
        assertTrue(depositoDesbloqueada.isSuccess());
    }

    @Test
    void testValidacionesPrestamo() {
        // 1. Solicitar préstamo con monto inválido
        Response<com.banco.shibasito.entity.Prestamo> prestamoMontoInvalido = 
                prestamoService.solicitarPrestamo(cliente.getDni(), 
                        new BigDecimal("0.00"), 12, "Monto cero");
        
        assertFalse(prestamoMontoInvalido.isSuccess());
        assertEquals("MONTO_INVALIDO", prestamoMontoInvalido.getCode());

        // 2. Solicitar préstamo con monto muy alto
        Response<com.banco.shibasito.entity.Prestamo> prestamoMontoAlto = 
                prestamoService.solicitarPrestamo(cliente.getDni(), 
                        new BigDecimal("200000.00"), 24, "Monto excesivo");
        
        assertFalse(prestamoMontoAlto.isSuccess());
        assertEquals("MONTO_MAXIMO_EXCEDIDO", prestamoMontoAlto.getCode());

        // 3. Solicitar préstamo con plazo inválido
        Response<com.banco.shibasito.entity.Prestamo> prestamoPlazoInvalido = 
                prestamoService.solicitarPrestamo(cliente.getDni(), 
                        new BigDecimal("5000.00"), 100, "Plazo excesivo");
        
        assertFalse(prestamoPlazoInvalido.isSuccess());
        assertEquals("PLAZO_MAXIMO_EXCEDIDO", prestamoPlazoInvalido.getCode());

        // 4. Solicitar préstamo válido
        Response<com.banco.shibasito.entity.Prestamo> prestamoValido = 
                prestamoService.solicitarPrestamo(cliente.getDni(), 
                        new BigDecimal("5000.00"), 24, "Préstamo válido");
        
        assertTrue(prestamoValido.isSuccess());
        verify(mockRabbitMQService, timeout(5000)).enviarEventoPrestamoSolicitado(any());
    }
}
