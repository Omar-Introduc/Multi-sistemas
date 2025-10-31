package com.banco.shibasito.service;

import com.banco.shibasito.dto.Response;
import com.banco.shibasito.entity.Cliente;
import com.banco.shibasito.repository.ClienteRepository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

/**
 * Servicio de negocio para la gestión de clientes
 * Maneja la lógica de negocio relacionada con clientes del banco
 */
@Service
@Transactional
public class ClienteService {
    
    @Autowired
    private ClienteRepository clienteRepository;
    
    @Autowired
    private BancoRabbitMQService rabbitMQService;

    /**
     * Crea un nuevo cliente en el sistema
     * @param cliente Cliente a crear
     * @return Response con el cliente creado o mensaje de error
     */
    public Response<Cliente> crearCliente(Cliente cliente) {
        try {
            // Validaciones de negocio
            Response<Cliente> validacion = validarClienteParaCreacion(cliente);
            if (!validacion.isSuccess()) {
                return validacion;
            }
            
            // Verificar si ya existe un cliente con el mismo DNI
            if (clienteRepository.findByDni(cliente.getDni()).isPresent()) {
                return Response.error("Ya existe un cliente registrado con el DNI: " + cliente.getDni(), "CLIENTE_DUPLICADO");
            }
            
            // Guardar cliente
            Cliente clienteCreado = clienteRepository.save(cliente);
            
            // Enviar mensaje a RabbitMQ
            rabbitMQService.enviarEventoClienteCreado(clienteCreado);
            
            return Response.success("Cliente creado exitosamente", clienteCreado);
            
        } catch (Exception e) {
            return Response.error("Error al crear cliente: " + e.getMessage(), "ERROR_INTERNO");
        }
    }

    /**
     * Busca un cliente por su DNI
     * @param dni DNI del cliente a buscar
     * @return Response con el cliente encontrado o mensaje de error
     */
    public Response<Cliente> buscarClientePorDni(String dni) {
        try {
            if (dni == null || dni.trim().isEmpty()) {
                return Response.error("El DNI no puede estar vacío", "DNI_INVALIDO");
            }
            
            Optional<Cliente> cliente = clienteRepository.findByDni(dni);
            
            if (cliente.isPresent()) {
                return Response.success("Cliente encontrado", cliente.get());
            } else {
                return Response.error("No se encontró cliente con DNI: " + dni, "CLIENTE_NO_ENCONTRADO");
            }
            
        } catch (Exception e) {
            return Response.error("Error al buscar cliente: " + e.getMessage(), "ERROR_INTERNO");
        }
    }

    /**
     * Obtiene un cliente por su ID
     * @param id ID del cliente a buscar
     * @return Response con el cliente encontrado o mensaje de error
     */
    public Response<Cliente> obtenerClientePorId(Long id) {
        try {
            if (id == null) {
                return Response.error("El ID no puede ser nulo", "ID_INVALIDO");
            }

            Optional<Cliente> cliente = clienteRepository.findById(id);

            if (cliente.isPresent()) {
                return Response.success("Cliente encontrado", cliente.get());
            } else {
                return Response.error("No se encontró cliente con ID: " + id, "CLIENTE_NO_ENCONTRADO");
            }

        } catch (Exception e) {
            return Response.error("Error al buscar cliente: " + e.getMessage(), "ERROR_INTERNO");
        }
    }

    /**
     * Valida la existencia de un cliente por su DNI
     * @param dni DNI del cliente a validar
     * @return Response indicando si el cliente existe
     */
    public Response<Boolean> validarExistencia(String dni) {
        try {
            if (dni == null || dni.trim().isEmpty()) {
                return Response.error("El DNI no puede estar vacío", "DNI_INVALIDO");
            }
            
            boolean existe = clienteRepository.existsByDni(dni);
            String mensaje = existe ? "Cliente existe" : "Cliente no existe";
            
            return Response.success(mensaje, existe);
            
        } catch (Exception e) {
            return Response.error("Error al validar existencia: " + e.getMessage(), "ERROR_INTERNO");
        }
    }

    /**
     * Lista todos los clientes activos
     * @return Response con la lista de clientes activos
     */
    public Response<List<Cliente>> listarClientesActivos() {
        try {
            List<Cliente> clientes = clienteRepository.findActivos();
            
            return Response.success("Clientes activos obtenidos", clientes);
            
        } catch (Exception e) {
            return Response.error("Error al listar clientes: " + e.getMessage(), "ERROR_INTERNO");
        }
    }

    /**
     * Actualiza los datos de un cliente
     * @param clienteActualizado Datos actualizados del cliente
     * @return Response con el cliente actualizado
     */
    public Response<Cliente> actualizarCliente(Cliente clienteActualizado) {
        try {
            if (clienteActualizado == null || clienteActualizado.getId() == null) {
                return Response.error("Los datos del cliente y su ID no pueden ser nulos", "CLIENTE_INVALIDO");
            }
            
            Optional<Cliente> clienteExistente = clienteRepository.findById(clienteActualizado.getId());
            
            if (!clienteExistente.isPresent()) {
                return Response.error("No se encontró cliente con ID: " + clienteActualizado.getId(), "CLIENTE_NO_ENCONTRADO");
            }
            
            // Actualizar datos
            Cliente cliente = clienteExistente.get();
            cliente.setNombres(clienteActualizado.getNombres());
            cliente.setApellidos(clienteActualizado.getApellidos());
            cliente.setTelefono(clienteActualizado.getTelefono());
            cliente.setEmail(clienteActualizado.getEmail());
            cliente.setDireccion(clienteActualizado.getDireccion());
            
            Cliente clienteGuardado = clienteRepository.save(cliente);
            
            // Enviar mensaje a RabbitMQ
            rabbitMQService.enviarEventoClienteActualizado(clienteGuardado);
            
            return Response.success("Cliente actualizado exitosamente", clienteGuardado);
            
        } catch (Exception e) {
            return Response.error("Error al actualizar cliente: " + e.getMessage(), "ERROR_INTERNO");
        }
    }

    /**
     * Desactiva un cliente (no lo elimina, solo lo marca como inactivo)
     * @param dni DNI del cliente a desactivar
     * @return Response indicando el resultado de la operación
     */
    public Response<String> desactivarCliente(String dni) {
        try {
            if (dni == null || dni.trim().isEmpty()) {
                return Response.error("El DNI no puede estar vacío", "DNI_INVALIDO");
            }
            
            Optional<Cliente> cliente = clienteRepository.findByDni(dni);
            
            if (!cliente.isPresent()) {
                return Response.error("No se encontró cliente con DNI: " + dni, "CLIENTE_NO_ENCONTRADO");
            }
            
            cliente.get().setEstado(Cliente.Estado.INACTIVO);
            clienteRepository.save(cliente.get());
            
            // Enviar mensaje a RabbitMQ
            rabbitMQService.enviarEventoClienteDesactivado(cliente.get());
            
            return Response.success("Cliente desactivado exitosamente");
            
        } catch (Exception e) {
            return Response.error("Error al desactivar cliente: " + e.getMessage(), "ERROR_INTERNO");
        }
    }

    /**
     * Valida los datos de un cliente para creación
     * @param cliente Cliente a validar
     * @return Response indicando si la validación es exitosa
     */
    private Response<Cliente> validarClienteParaCreacion(Cliente cliente) {
        if (cliente == null) {
            return Response.error("Los datos del cliente no pueden estar vacíos", "CLIENTE_NULO");
        }
        
        if (cliente.getDni() == null || cliente.getDni().trim().isEmpty()) {
            return Response.error("El DNI es obligatorio", "DNI_REQUERIDO");
        }
        
        if (cliente.getNombres() == null || cliente.getNombres().trim().isEmpty()) {
            return Response.error("El nombre es obligatorio", "NOMBRE_REQUERIDO");
        }
        
        if (cliente.getApellidos() == null || cliente.getApellidos().trim().isEmpty()) {
            return Response.error("El apellido es obligatorio", "APELLIDO_REQUERIDO");
        }
        
        if (cliente.getEmail() != null && !cliente.getEmail().contains("@")) {
            return Response.error("El email debe tener un formato válido", "EMAIL_INVALIDO");
        }
        
        // Validar que el DNI tenga un formato básico (8 dígitos)
        if (!cliente.getDni().matches("\\d{8}")) {
            return Response.error("El DNI debe tener 8 dígitos", "DNI_FORMATO_INVALIDO");
        }
        
        return Response.success("Validación exitosa");
    }
}