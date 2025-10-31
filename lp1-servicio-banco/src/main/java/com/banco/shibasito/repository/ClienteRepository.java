package com.banco.shibasito.repository;

import com.banco.shibasito.entity.Cliente;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository para la entidad Cliente
 */
@Repository
public interface ClienteRepository extends JpaRepository<Cliente, Long> {

    /**
     * Busca un cliente por DNI
     */
    Optional<Cliente> findByDni(String dni);

    /**
     * Verifica si existe un cliente por DNI
     */
    boolean existsByDni(String dni);

    /**
     * Busca clientes por nombre que contenga el texto especificado
     */
    List<Cliente> findByNombreContainingIgnoreCase(String nombre);

    /**
     * Busca clientes por apellido que contenga el texto especificado
     */
    List<Cliente> findByApellidoContainingIgnoreCase(String apellido);

    /**
     * Busca clientes por nombre y apellido
     */
    List<Cliente> findByNombreContainingIgnoreCaseAndApellidoContainingIgnoreCase(String nombre, String apellido);

    /**
     * Consulta personalizada para buscar clientes activos
     */
    @Query("SELECT c FROM Cliente c WHERE c.estado = 'ACTIVO'")
    List<Cliente> findActivos();

    /**
     * Consulta personalizada para buscar clientes por estado
     */
    @Query("SELECT c FROM Cliente c WHERE c.estado = :estado")
    List<Cliente> findByEstado(@Param("estado") String estado);

    /**
     * Consulta personalizada para buscar clientes que empiecen con un nombre
     */
    @Query("SELECT c FROM Cliente c WHERE LOWER(c.nombre) LIKE LOWER(CONCAT(:prefijo, '%'))")
    List<Cliente> findByNombreStartingWithIgnoreCase(@Param("prefijo") String prefijo);

    /**
     * Consulta personalizada para buscar clientes por email
     */
    @Query("SELECT c FROM Cliente c WHERE c.email = :email")
    Optional<Cliente> findByEmail(@Param("email") String email);

    /**
     * Consulta personalizada para contar clientes por estado
     */
    @Query("SELECT COUNT(c) FROM Cliente c WHERE c.estado = :estado")
    Long countByEstado(@Param("estado") String estado);

    /**
     * Consulta personalizada para obtener todos los clientes ordenados por apellido y nombre
     */
    @Query("SELECT c FROM Cliente c ORDER BY c.apellido, c.nombre")
    List<Cliente> findAllOrderByApellidoAndNombre();

    /**
     * Consulta personalizada para verificar si existe email
     */
    boolean existsByEmail(String email);
}
