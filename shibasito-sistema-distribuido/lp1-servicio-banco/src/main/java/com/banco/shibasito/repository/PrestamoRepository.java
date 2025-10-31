package com.banco.shibasito.repository;

import com.banco.shibasito.entity.Prestamo;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

/**
 * Repository para la entidad Prestamo
 */
@Repository
public interface PrestamoRepository extends JpaRepository<Prestamo, Long> {

    /**
     * Busca préstamos por DNI del cliente
     */
    @Query("SELECT p FROM Prestamo p WHERE p.cliente.dni = :clienteDni")
    List<Prestamo> findByClienteDni(@Param("clienteDni") String clienteDni);

    /**
     * Busca préstamos por estado
     */
    List<Prestamo> findByEstado(Prestamo.Estado estado);

    /**
     * Busca préstamos por cliente y estado
     */
    @Query("SELECT p FROM Prestamo p WHERE p.cliente.dni = :clienteDni AND p.estado = :estado")
    List<Prestamo> findByClienteDniAndEstado(@Param("clienteDni") String clienteDni, @Param("estado") Prestamo.Estado estado);

    /**
     * Consulta personalizada para obtener préstamos aprobados
     */
    @Query("SELECT p FROM Prestamo p WHERE p.estado = 'APROBADO'")
    List<Prestamo> findAprobados();

    /**
     * Consulta personalizada para obtener préstamos por monto mayor a
     */
    @Query("SELECT p FROM Prestamo p WHERE p.monto > :monto ORDER BY p.monto DESC")
    List<Prestamo> findByMontoGreaterThan(@Param("monto") BigDecimal monto);

    /**
     * Consulta personalizada para obtener préstamos por rango de monto
     */
    @Query("SELECT p FROM Prestamo p WHERE p.monto BETWEEN :montoMin AND :montoMax ORDER BY p.monto")
    List<Prestamo> findByMontoBetween(@Param("montoMin") BigDecimal montoMin, @Param("montoMax") BigDecimal montoMax);

    /**
     * Consulta personalizada para obtener préstamos de un cliente ordenados por fecha
     */
    @Query("SELECT p FROM Prestamo p WHERE p.cliente.dni = :clienteDni ORDER BY p.fecha DESC")
    List<Prestamo> findByClienteDniOrderByFechaDesc(@Param("clienteDni") String clienteDni);

    /**
     * Consulta personalizada para contar préstamos por estado
     */
    @Query("SELECT COUNT(p) FROM Prestamo p WHERE p.estado = :estado")
    Long countByEstado(@Param("estado") Prestamo.Estado estado);

    /**
     * Consulta personalizada para obtener préstamos pendientes de aprobación
     */
    @Query("SELECT p FROM Prestamo p WHERE p.estado = 'PENDIENTE' ORDER BY p.fecha ASC")
    List<Prestamo> findPendientesOrderByFechaAsc();

    List<Prestamo> findByClienteId(Long id);
}
