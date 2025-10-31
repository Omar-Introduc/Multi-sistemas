package com.banco.shibasito.service;

import com.banco.shibasito.dto.Response;
import com.banco.shibasito.entity.Cliente;
import com.banco.shibasito.repository.ClienteRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Pruebas unitarias para ClienteService
 * Valida la lógica de negocio del servicio de clientes
 */
@ExtendWith(MockitoExtension.class)
class ClienteServiceTest {

    @Mock
    private ClienteRepository clienteRepository;

    @Mock
    private BancoRabbitMQService rabbitMQService;

    @InjectMocks
    private ClienteService clienteService;

    private Cliente cliente;

    @BeforeEach
    void setUp() {
        // Crear cliente mock
        cliente = new Cliente();
        cliente.setId(1L);
        cliente.setDni("12345678");
        cliente.setNombre("Juan");
        cliente.setApellido("Pérez");
        cliente.setEmail("juan.perez@test.com");
        cliente.setTelefono("999888777");
        cliente.setDireccion("Av. Principal 123, Lima");
        cliente.setFechaNacimiento(java.time.LocalDate.of(1990, 5, 15));
        cliente.setEstado(Cliente.Estado.ACTIVO);
    }

    @Test
    void testCrearCliente_Success() {
        // Given
        String dni = "87654321";
        String nombre = "María";
        String apellido = "González";
        String email = "maria.gonzalez@test.com";
        String telefono = "988777666";
        String direccion = "Av. Secundaria 456, Lima";
        java.time.LocalDate fechaNacimiento = java.time.LocalDate.of(1985, 8, 20);

        Cliente nuevoCliente = new Cliente();
        nuevoCliente.setDni(dni);
        nuevoCliente.setNombre(nombre);
        nuevoCliente.setApellido(apellido);
        nuevoCliente.setEmail(email);
        nuevoCliente.setTelefono(telefono);
        nuevoCliente.setDireccion(direccion);
        nuevoCliente.setFechaNacimiento(fechaNacimiento);
        nuevoCliente.setEstado(Cliente.Estado.ACTIVO);

        when(clienteRepository.findByDni(dni)).thenReturn(Optional.empty());
        when(clienteRepository.save(any(Cliente.class))).thenReturn(nuevoCliente);

        // When
        Response<Cliente> response = clienteService.crearCliente(dni, nombre, apellido, email, telefono, direccion, fechaNacimiento);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("Cliente creado exitosamente", response.getMessage());
        assertNotNull(response.getData());
        assertEquals(dni, response.getData().getDni());
        assertEquals(nombre, response.getData().getNombre());
        verify(rabbitMQService).enviarEventoClienteCreado(any(Cliente.class));
    }

    @Test
    void testCrearCliente_DniDuplicado() {
        // Given
        String dni = "12345678";
        String nombre = "Nuevo";
        String apellido = "Cliente";
        String email = "nuevo@test.com";
        String telefono = "999999999";
        String direccion = "Dirección test";
        java.time.LocalDate fechaNacimiento = java.time.LocalDate.of(1990, 1, 1);

        when(clienteRepository.findByDni(dni)).thenReturn(Optional.of(cliente));

        // When
        Response<Cliente> response = clienteService.crearCliente(dni, nombre, apellido, email, telefono, direccion, fechaNacimiento);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("DNI_DUPLICADO", response.getCode());
        verify(clienteRepository, never()).save(any());
        verify(rabbitMQService, never()).enviarEventoClienteCreado(any());
    }

    @Test
    void testCrearCliente_EmailDuplicado() {
        // Given
        String dni = "87654321";
        String nombre = "Nuevo";
        String apellido = "Cliente";
        String email = "juan.perez@test.com"; // Mismo email que cliente mock
        String telefono = "999999999";
        String direccion = "Dirección test";
        java.time.LocalDate fechaNacimiento = java.time.LocalDate.of(1990, 1, 1);

        when(clienteRepository.findByDni(dni)).thenReturn(Optional.empty());
        when(clienteRepository.findByEmail(email)).thenReturn(Optional.of(cliente));

        // When
        Response<Cliente> response = clienteService.crearCliente(dni, nombre, apellido, email, telefono, direccion, fechaNacimiento);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("EMAIL_DUPLICADO", response.getCode());
        verify(clienteRepository, never()).save(any());
    }

    @Test
    void testBuscarPorDni_Success() {
        // Given
        String dni = "12345678";
        when(clienteRepository.findByDni(dni)).thenReturn(Optional.of(cliente));

        // When
        Response<Cliente> response = clienteService.buscarPorDni(dni);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(dni, response.getData().getDni());
        assertEquals("Cliente encontrado exitosamente", response.getMessage());
    }

    @Test
    void testBuscarPorDni_NotFound() {
        // Given
        String dniInexistente = "99999999";
        when(clienteRepository.findByDni(dniInexistente)).thenReturn(Optional.empty());

        // When
        Response<Cliente> response = clienteService.buscarPorDni(dniInexistente);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CLIENTE_NO_ENCONTRADO", response.getCode());
    }

    @Test
    void testBuscarPorEmail_Success() {
        // Given
        String email = "juan.perez@test.com";
        when(clienteRepository.findByEmail(email)).thenReturn(Optional.of(cliente));

        // When
        Response<Cliente> response = clienteService.buscarPorEmail(email);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(email, response.getData().getEmail());
        assertEquals("Cliente encontrado exitosamente", response.getMessage());
    }

    @Test
    void testBuscarPorEmail_NotFound() {
        // Given
        String emailInexistente = "noexiste@test.com";
        when(clienteRepository.findByEmail(emailInexistente)).thenReturn(Optional.empty());

        // When
        Response<Cliente> response = clienteService.buscarPorEmail(emailInexistente);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CLIENTE_NO_ENCONTRADO", response.getCode());
    }

    @Test
    void testActualizarCliente_Success() {
        // Given
        String dni = "12345678";
        String nuevoNombre = "Juan Carlos";
        String nuevoApellido = "Pérez López";
        String nuevoEmail = "juan.carlos@test.com";
        String nuevoTelefono = "987654321";
        String nuevaDireccion = "Av. Nueva 789, Lima";

        when(clienteRepository.findByDni(dni)).thenReturn(Optional.of(cliente));
        when(clienteRepository.findByEmail(nuevoEmail)).thenReturn(Optional.empty());
        when(clienteRepository.save(any(Cliente.class))).thenReturn(cliente);

        // When
        Response<Cliente> response = clienteService.actualizarCliente(dni, nuevoNombre, nuevoApellido, nuevoEmail, nuevoTelefono, nuevaDireccion);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("Cliente actualizado exitosamente", response.getMessage());
        assertEquals(nuevoNombre, cliente.getNombre());
        assertEquals(nuevoApellido, cliente.getApellido());
        assertEquals(nuevoEmail, cliente.getEmail());
        assertEquals(nuevoTelefono, cliente.getTelefono());
        assertEquals(nuevaDireccion, cliente.getDireccion());
        verify(rabbitMQService).enviarEventoClienteActualizado(any(Cliente.class));
    }

    @Test
    void testActualizarCliente_ClienteNotFound() {
        // Given
        String dniInexistente = "99999999";
        when(clienteRepository.findByDni(dniInexistente)).thenReturn(Optional.empty());

        // When
        Response<Cliente> response = clienteService.actualizarCliente(dniInexistente, "Nombre", "Apellido", "email@test.com", "123", "Dirección");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CLIENTE_NO_ENCONTRADO", response.getCode());
        verify(clienteRepository, never()).save(any());
        verify(rabbitMQService, never()).enviarEventoClienteActualizado(any());
    }

    @Test
    void testActualizarCliente_EmailDuplicado() {
        // Given
        String dni = "12345678";
        String nuevoEmail = "otro@test.com"; // Email de otro cliente
        
        Cliente otroCliente = new Cliente();
        otroCliente.setId(2L);
        otroCliente.setEmail("otro@test.com");

        when(clienteRepository.findByDni(dni)).thenReturn(Optional.of(cliente));
        when(clienteRepository.findByEmail(nuevoEmail)).thenReturn(Optional.of(otroCliente));

        // When
        Response<Cliente> response = clienteService.actualizarCliente(dni, "Nombre", "Apellido", nuevoEmail, "123", "Dirección");

        // Then
        assertFalse(response.isSuccess());
        assertEquals("EMAIL_DUPLICADO", response.getCode());
        verify(clienteRepository, never()).save(any());
    }

    @Test
    void testDesactivarCliente_Success() {
        // Given
        String dni = "12345678";
        String motivo = "Solicitud del cliente";

        when(clienteRepository.findByDni(dni)).thenReturn(Optional.of(cliente));
        when(clienteRepository.save(any(Cliente.class))).thenReturn(cliente);

        // When
        Response<String> response = clienteService.desactivarCliente(dni, motivo);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(Cliente.Estado.INACTIVO, cliente.getEstado());
        assertEquals("Cliente desactivado exitosamente", response.getMessage());
        verify(rabbitMQService).enviarAlerta(eq("CLIENTE_DESACTIVADO"), anyString(), any());
    }

    @Test
    void testDesactivarCliente_ClienteNotFound() {
        // Given
        String dniInexistente = "99999999";
        String motivo = "Motivo";

        when(clienteRepository.findByDni(dniInexistente)).thenReturn(Optional.empty());

        // When
        Response<String> response = clienteService.desactivarCliente(dniInexistente, motivo);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CLIENTE_NO_ENCONTRADO", response.getCode());
    }

    @Test
    void testActivarCliente_Success() {
        // Given
        cliente.setEstado(Cliente.Estado.INACTIVO);
        String dni = "12345678";

        when(clienteRepository.findByDni(dni)).thenReturn(Optional.of(cliente));
        when(clienteRepository.save(any(Cliente.class))).thenReturn(cliente);

        // When
        Response<String> response = clienteService.activarCliente(dni);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(Cliente.Estado.ACTIVO, cliente.getEstado());
        assertEquals("Cliente activado exitosamente", response.getMessage());
    }

    @Test
    void testActivarCliente_ClienteNotFound() {
        // Given
        String dniInexistente = "99999999";
        when(clienteRepository.findByDni(dniInexistente)).thenReturn(Optional.empty());

        // When
        Response<String> response = clienteService.activarCliente(dniInexistente);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CLIENTE_NO_ENCONTRADO", response.getCode());
    }

    @Test
    void testListarClientes_Success() {
        // Given
        List<Cliente> clientes = List.of(cliente);
        when(clienteRepository.findAll()).thenReturn(clientes);

        // When
        Response<List<Cliente>> response = clienteService.listarClientes();

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Clientes obtenidos exitosamente", response.getMessage());
    }

    @Test
    void testListarClientesActivos_Success() {
        // Given
        List<Cliente> clientesActivos = List.of(cliente);
        when(clienteRepository.findByEstado(Cliente.Estado.ACTIVO)).thenReturn(clientesActivos);

        // When
        Response<List<Cliente>> response = clienteService.listarClientesActivos();

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertTrue(response.getData().stream().allMatch(c -> c.getEstado() == Cliente.Estado.ACTIVO));
        assertEquals("Clientes activos obtenidos exitosamente", response.getMessage());
    }

    @Test
    void testListarClientesInactivos_Success() {
        // Given
        cliente.setEstado(Cliente.Estado.INACTIVO);
        List<Cliente> clientesInactivos = List.of(cliente);
        when(clienteRepository.findByEstado(Cliente.Estado.INACTIVO)).thenReturn(clientesInactivos);

        // When
        Response<List<Cliente>> response = clienteService.listarClientesInactivos();

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertTrue(response.getData().stream().allMatch(c -> c.getEstado() == Cliente.Estado.INACTIVO));
        assertEquals("Clientes inactivos obtenidos exitosamente", response.getMessage());
    }

    @Test
    void testBuscarClientesPorNombre_Success() {
        // Given
        String nombre = "Juan";
        List<Cliente> clientesEncontrados = List.of(cliente);
        when(clienteRepository.findByNombreContainingIgnoreCase(nombre)).thenReturn(clientesEncontrados);

        // When
        Response<List<Cliente>> response = clienteService.buscarClientesPorNombre(nombre);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Clientes encontrados exitosamente", response.getMessage());
    }

    @Test
    void testBuscarClientesPorApellido_Success() {
        // Given
        String apellido = "Pérez";
        List<Cliente> clientesEncontrados = List.of(cliente);
        when(clienteRepository.findByApellidoContainingIgnoreCase(apellido)).thenReturn(clientesEncontrados);

        // When
        Response<List<Cliente>> response = clienteService.buscarClientesPorApellido(apellido);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Clientes encontrados exitosamente", response.getMessage());
    }

    @Test
    void testEliminarCliente_Success() {
        // Given
        String dni = "12345678";
        when(clienteRepository.findByDni(dni)).thenReturn(Optional.of(cliente));

        // When
        Response<String> response = clienteService.eliminarCliente(dni);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("Cliente eliminado exitosamente", response.getMessage());
        verify(clienteRepository).delete(cliente);
    }

    @Test
    void testEliminarCliente_ClienteNotFound() {
        // Given
        String dniInexistente = "99999999";
        when(clienteRepository.findByDni(dniInexistente)).thenReturn(Optional.empty());

        // When
        Response<String> response = clienteService.eliminarCliente(dniInexistente);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("CLIENTE_NO_ENCONTRADO", response.getCode());
        verify(clienteRepository, never()).delete(any());
    }

    @Test
    void testValidarEdad_ClienteMayorEdad() {
        // Given
        java.time.LocalDate fechaNacimientoMayor = java.time.LocalDate.of(2000, 1, 1); // Mayor de edad

        // When
        boolean esMayor = clienteService.validarEdad(fechaNacimientoMayor);

        // Then
        assertTrue(esMayor);
    }

    @Test
    void testValidarEdad_ClienteMenorEdad() {
        // Given
        java.time.LocalDate fechaNacimientoMenor = java.time.LocalDate.of(2010, 1, 1); // Menor de edad

        // When
        boolean esMayor = clienteService.validarEdad(fechaNacimientoMenor);

        // Then
        assertFalse(esMayor);
    }

    @Test
    void testValidarEmail_EmailValido() {
        // Given
        String emailValido = "usuario@dominio.com";

        // When
        boolean esValido = clienteService.validarEmail(emailValido);

        // Then
        assertTrue(esValido);
    }

    @Test
    void testValidarEmail_EmailInvalido() {
        // Given
        String emailInvalido = "email-invalido";

        // When
        boolean esValido = clienteService.validarEmail(emailInvalido);

        // Then
        assertFalse(esValido);
    }

    @Test
    void testValidarTelefono_TelefonoValido() {
        // Given
        String telefonoValido = "999888777";

        // When
        boolean esValido = clienteService.validarTelefono(telefonoValido);

        // Then
        assertTrue(esValido);
    }

    @Test
    void testValidarTelefono_TelefonoInvalido() {
        // Given
        String telefonoInvalido = "123"; // Muy corto

        // When
        boolean esValido = clienteService.validarTelefono(telefonoInvalido);

        // Then
        assertFalse(esValido);
    }

    @Test
    void testValidarDni_DniValido() {
        // Given
        String dniValido = "12345678";

        // When
        boolean esValido = clienteService.validarDni(dniValido);

        // Then
        assertTrue(esValido);
    }

    @Test
    void testValidarDni_DniInvalido() {
        // Given
        String dniInvalido = "12345"; // Muy corto

        // When
        boolean esValido = clienteService.validarDni(dniInvalido);

        // Then
        assertFalse(esValido);
    }

    @Test
    void testCalcularEdad_Success() {
        // Given
        java.time.LocalDate fechaNacimiento = java.time.LocalDate.of(1990, 5, 15);

        // When
        int edad = clienteService.calcularEdad(fechaNacimiento);

        // Then
        assertTrue(edad > 0);
        assertTrue(edad <= 100);
    }

    @Test
    void testObtenerClientesPorEstado_Success() {
        // Given
        Cliente.Estado estado = Cliente.Estado.ACTIVO;
        List<Cliente> clientes = List.of(cliente);
        when(clienteRepository.findByEstado(estado)).thenReturn(clientes);

        // When
        Response<List<Cliente>> response = clienteService.obtenerClientesPorEstado(estado);

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Clientes obtenidos exitosamente", response.getMessage());
    }

    @Test
    void testValidarCreacionCliente_DatosCompletos() {
        // Given
        String dni = "87654321";
        String nombre = "María";
        String apellido = "González";
        String email = "maria@test.com";
        String telefono = "999888777";
        java.time.LocalDate fechaNacimiento = java.time.LocalDate.of(1990, 1, 1);

        when(clienteRepository.findByDni(dni)).thenReturn(Optional.empty());
        when(clienteRepository.findByEmail(email)).thenReturn(Optional.empty());

        // When
        Response<Cliente> response = clienteService.validarCreacionCliente(dni, nombre, apellido, email, telefono, fechaNacimiento);

        // Then
        assertTrue(response.isSuccess());
        assertEquals("Validación exitosa", response.getMessage());
    }

    @Test
    void testValidarCreacionCliente_DatosNulos() {
        // When
        Response<Cliente> response = clienteService.validarCreacionCliente(null, null, null, null, null, null);

        // Then
        assertFalse(response.isSuccess());
        assertTrue(response.getMessage().contains("obligatorio"));
    }

    @Test
    void testValidarCreacionCliente_FechaFutura() {
        // Given
        java.time.LocalDate fechaFutura = java.time.LocalDate.of(2030, 1, 1);

        // When
        Response<Cliente> response = clienteService.validarCreacionCliente(
                "12345678", "Juan", "Pérez", "juan@test.com", "999888777", fechaFutura);

        // Then
        assertFalse(response.isSuccess());
        assertEquals("FECHA_NACIMIENTO_INVALIDA", response.getCode());
    }

    @Test
    void testObtenerEstadisticasClientes_Success() {
        // Given
        List<Object[]> estadisticas = new ArrayList<>();
        estadisticas.add(new Object[]{Cliente.Estado.ACTIVO, 50L});
        estadisticas.add(new Object[]{Cliente.Estado.INACTIVO, 10L});

        when(clienteRepository.getEstadisticasPorEstado()).thenReturn(estadisticas);

        // When
        Response<List<Object[]>> response = clienteService.obtenerEstadisticasClientes();

        // Then
        assertTrue(response.isSuccess());
        assertEquals(2, response.getData().size());
        assertEquals("Estadísticas obtenidas exitosamente", response.getMessage());
    }

    @Test
    void testBuscarClientesConCuentas_Success() {
        // Given
        List<Cliente> clientesConCuentas = List.of(cliente);
        when(clienteRepository.findClientesConCuentas()).thenReturn(clientesConCuentas);

        // When
        Response<List<Cliente>> response = clienteService.buscarClientesConCuentas();

        // Then
        assertTrue(response.isSuccess());
        assertEquals(1, response.getData().size());
        assertEquals("Clientes con cuentas obtenidos exitosamente", response.getMessage());
    }

    @Test
    void testBuscarClientesSinCuentas_Success() {
        // Given
        List<Cliente> clientesSinCuentas = new ArrayList<>();
        when(clienteRepository.findClientesSinCuentas()).thenReturn(clientesSinCuentas);

        // When
        Response<List<Cliente>> response = clienteService.buscarClientesSinCuentas();

        // Then
        assertTrue(response.isSuccess());
        assertEquals(0, response.getData().size());
        assertEquals("Clientes sin cuentas obtenidos exitosamente", response.getMessage());
    }

    @Test
    void testGenerarNumeroCliente_Success() {
        // When
        String numeroCliente = clienteService.generarNumeroCliente();

        // Then
        assertNotNull(numeroCliente);
        assertEquals(10, numeroCliente.length());
        assertTrue(numeroCliente.startsWith("CLI"));
    }
}
