package com.banco.shibasito.repository;

import com.banco.shibasito.entity.Cuenta;
import com.banco.shibasito.entity.Cliente;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;
import org.springframework.test.context.ActiveProfiles;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Pruebas JPA para CuentaRepository
 * Valida las operaciones de base de datos para la entidad Cuenta
 */
@DataJpaTest
@ActiveProfiles("test")
class CuentaRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private CuentaRepository cuentaRepository;

    @Autowired
    private ClienteRepository clienteRepository;

    private Cliente cliente;
    private Cuenta cuentaAhorros;
    private Cuenta cuentaCorriente;

    @BeforeEach
    void setUp() {
        // Crear cliente de prueba
        cliente = new Cliente();
        cliente.setDni("12345678");
        cliente.setNombre("Juan");
        cliente.setApellido("Pérez");
        cliente.setEmail("juan.perez@test.com");
        cliente.setTelefono("999888777");
        cliente.setEstado(Cliente.Estado.ACTIVO);
        clienteRepository.save(cliente);

        // Crear cuenta de ahorros
        cuentaAhorros = new Cuenta();
        cuentaAhorros.setNumero("2001234567890");
        cuentaAhorros.setSaldo(new BigDecimal("1500.00"));
        cuentaAhorros.setTipo(Cuenta.TipoCuenta.AHORROS);
        cuentaAhorros.setEstado(Cuenta.Estado.ACTIVA);
        cuentaAhorros.setCliente(cliente);
        entityManager.persistAndFlush(cuentaAhorros);

        // Crear cuenta corriente
        cuentaCorriente = new Cuenta();
        cuentaCorriente.setNumero("1001234567890");
        cuentaCorriente.setSaldo(new BigDecimal("2000.00"));
        cuentaCorriente.setTipo(Cuenta.TipoCuenta.CORRIENTE);
        cuentaCorriente.setEstado(Cuenta.Estado.ACTIVA);
        cuentaCorriente.setCliente(cliente);
        entityManager.persistAndFlush(cuentaCorriente);
    }

    @Test
    void testFindByNumero_Success() {
        // Given
        String numeroCuenta = "2001234567890";

        // When
        Optional<Cuenta> result = cuentaRepository.findByNumero(numeroCuenta);

        // Then
        assertTrue(result.isPresent());
        assertEquals(numeroCuenta, result.get().getNumero());
        assertEquals(Cuenta.TipoCuenta.AHORROS, result.get().getTipo());
    }

    @Test
    void testFindByNumero_NotFound() {
        // Given
        String numeroInexistente = "9999999999999";

        // When
        Optional<Cuenta> result = cuentaRepository.findByNumero(numeroInexistente);

        // Then
        assertFalse(result.isPresent());
    }

    @Test
    void testFindByClienteDni_Success() {
        // Given
        String dniCliente = "12345678";

        // When
        List<Cuenta> result = cuentaRepository.findByClienteDni(dniCliente);

        // Then
        assertEquals(2, result.size());
        assertTrue(result.stream().anyMatch(c -> c.getNumero().equals("2001234567890")));
        assertTrue(result.stream().anyMatch(c -> c.getNumero().equals("1001234567890")));
    }

    @Test
    void testFindByClienteDni_NoAccounts() {
        // Given
        String dniInexistente = "99999999";

        // When
        List<Cuenta> result = cuentaRepository.findByClienteDni(dniInexistente);

        // Then
        assertTrue(result.isEmpty());
    }

    @Test
    void testFindByEstado_Success() {
        // Given
        Cuenta.Estado estado = Cuenta.Estado.ACTIVA;

        // When
        List<Cuenta> result = cuentaRepository.findByEstado(estado);

        // Then
        assertEquals(2, result.size());
        assertTrue(result.stream().allMatch(c -> c.getEstado() == Cuenta.Estado.ACTIVA));
    }

    @Test
    void testFindByClienteDniAndEstado_Success() {
        // Given
        String dniCliente = "12345678";
        Cuenta.Estado estado = Cuenta.Estado.ACTIVA;

        // When
        List<Cuenta> result = cuentaRepository.findByClienteDniAndEstado(dniCliente, estado);

        // Then
        assertEquals(2, result.size());
        assertTrue(result.stream().allMatch(c -> c.getCliente().getDni().equals(dniCliente)));
        assertTrue(result.stream().allMatch(c -> c.getEstado() == Cuenta.Estado.ACTIVA));
    }

    @Test
    void testFindActivasByClienteDni_Success() {
        // Given
        String dniCliente = "12345678";

        // When
        List<Cuenta> result = cuentaRepository.findActivasByClienteDni(dniCliente);

        // Then
        assertEquals(2, result.size());
        assertTrue(result.stream().allMatch(c -> c.getEstado() == Cuenta.Estado.ACTIVA));
    }

    @Test
    void testSaveCuenta_Success() {
        // Given
        Cuenta nuevaCuenta = new Cuenta();
        nuevaCuenta.setNumero("3001234567890");
        nuevaCuenta.setSaldo(new BigDecimal("3000.00"));
        nuevaCuenta.setTipo(Cuenta.TipoCuenta.PLAZO_FIJO);
        nuevaCuenta.setEstado(Cuenta.Estado.ACTIVA);
        nuevaCuenta.setCliente(cliente);

        // When
        Cuenta cuentaGuardada = cuentaRepository.save(nuevaCuenta);

        // Then
        assertNotNull(cuentaGuardada.getId());
        assertEquals("3001234567890", cuentaGuardada.getNumero());
        assertEquals(Cuenta.TipoCuenta.PLAZO_FIJO, cuentaGuardada.getTipo());
        assertNotNull(cuentaGuardada.getFechaCreacion());
    }

    @Test
    void testUpdateCuenta_Success() {
        // Given
        Long cuentaId = cuentaAhorros.getId();
        Optional<Cuenta> cuentaOriginal = cuentaRepository.findById(cuentaId);
        assertTrue(cuentaOriginal.isPresent());

        // When
        cuentaOriginal.get().setSaldo(new BigDecimal("5000.00"));
        cuentaRepository.save(cuentaOriginal.get());

        // Then
        Optional<Cuenta> cuentaActualizada = cuentaRepository.findById(cuentaId);
        assertTrue(cuentaActualizada.isPresent());
        assertEquals(new BigDecimal("5000.00"), cuentaActualizada.get().getSaldo());
    }

    @Test
    void testDeleteCuenta_Success() {
        // Given
        Long cuentaId = cuentaAhorros.getId();

        // When
        cuentaRepository.delete(cuentaAhorros);

        // Then
        Optional<Cuenta> result = cuentaRepository.findById(cuentaId);
        assertFalse(result.isPresent());
    }

    @Test
    void testFindAll_Success() {
        // When
        List<Cuenta> todasLasCuentas = cuentaRepository.findAll();

        // Then
        assertTrue(todasLasCuentas.size() >= 2);
    }

    @Test
    void testFindById_Success() {
        // Given
        Long cuentaId = cuentaAhorros.getId();

        // When
        Optional<Cuenta> result = cuentaRepository.findById(cuentaId);

        // Then
        assertTrue(result.isPresent());
        assertEquals(cuentaId, result.get().getId());
    }

    @Test
    void testFindById_NotFound() {
        // Given
        Long idInexistente = 999999L;

        // When
        Optional<Cuenta> result = cuentaRepository.findById(idInexistente);

        // Then
        assertFalse(result.isPresent());
    }

    @Test
    void testCuentaUniqueConstraint() {
        // Given - Intentar crear una cuenta con el mismo número
        Cuenta cuentaDuplicada = new Cuenta();
        cuentaDuplicada.setNumero("2001234567890"); // Mismo número que cuentaAhorros
        cuentaDuplicada.setSaldo(new BigDecimal("1000.00"));
        cuentaDuplicada.setTipo(Cuenta.TipoCuenta.AHORROS);
        cuentaDuplicada.setEstado(Cuenta.Estado.ACTIVA);
        cuentaDuplicada.setCliente(cliente);

        // When & Then - Debería lanzar una excepción por violación de restricción unique
        assertThrows(Exception.class, () -> {
            cuentaRepository.save(cuentaDuplicada);
            entityManager.flush(); // Forzar flush para触发 la restricción
        });
    }

    @Test
    void testCuentaBusinessMethods() {
        // Given
        Cuenta cuenta = cuentaRepository.findByNumero("2001234567890").get();
        BigDecimal saldoInicial = cuenta.getSaldo();
        BigDecimal montoDeposito = new BigDecimal("500.00");

        // Test puedeRetirar con saldo suficiente
        assertTrue(cuenta.puedeRetirar(new BigDecimal("1000.00")));

        // Test depositar
        cuenta.depositar(montoDeposito);
        assertEquals(saldoInicial.add(montoDeposito), cuenta.getSaldo());

        // Test retirar exitoso
        BigDecimal montoRetiro = new BigDecimal("200.00");
        boolean retiroExitoso = cuenta.retirar(montoRetiro);
        assertTrue(retiroExitoso);
        assertEquals(saldoInicial.add(montoDeposito).subtract(montoRetiro), cuenta.getSaldo());

        // Test retirar con saldo insuficiente
        boolean retiroFallido = cuenta.retirar(new BigDecimal("1000000.00"));
        assertFalse(retiroFallido);
    }

    @Test
    void testCuentaStateManagement() {
        // Given
        Cuenta cuenta = cuentaRepository.findByNumero("2001234567890").get();
        
        // Test estado inicial
        assertEquals(Cuenta.Estado.ACTIVA, cuenta.getEstado());

        // Cambiar estado a bloqueada
        cuenta.setEstado(Cuenta.Estado.BLOQUEADA);
        cuentaRepository.save(cuenta);

        // Verificar que no se puede retirar de cuenta bloqueada
        assertFalse(cuenta.puedeRetirar(new BigDecimal("100.00")));

        // Cambiar estado a cerrada
        cuenta.setEstado(Cuenta.Estado.CERRADA);
        cuentaRepository.save(cuenta);

        // Verificar que la cuenta está cerrada
        assertEquals(Cuenta.Estado.CERRADA, cuenta.getEstado());
    }
}
