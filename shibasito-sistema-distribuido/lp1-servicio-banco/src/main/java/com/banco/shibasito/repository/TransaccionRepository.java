package com.banco.shibasito.repository;

import com.banco.shibasito.entity.Transaccion;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Repository para la entidad Transaccion
 */
@Repository
public interface TransaccionRepository extends JpaRepository<Transaccion, Long> {

    /**
     * Busca transacciones por cuenta ordenadas por fecha descendente
     */
    List<Transaccion> findByCuentaOrderByFechaDesc(com.banco.shibasito.entity.Cuenta cuenta);

    /**
     * Busca transacciones por cuenta y rango de fechas
     */
    @Query("SELECT t FROM Transaccion t WHERE t.cuenta = :cuenta AND t.fecha BETWEEN :fechaInicio AND :fechaFin ORDER BY t.fecha DESC")
    List<Transaccion> findByCuentaAndFechaBetween(@Param("cuenta") com.banco.shibasito.entity.Cuenta cuenta,
                                                  @Param("fechaInicio") LocalDateTime fechaInicio,
                                                  @Param("fechaFin") LocalDateTime fechaFin);

    /**
     * Busca transacciones por cuenta y fecha mayor o igual
     */
    @Query("SELECT t FROM Transaccion t WHERE t.cuenta = :cuenta AND t.fecha >= :fecha ORDER BY t.fecha DESC")
    List<Transaccion> findByCuentaAndFechaGreaterThanEqual(@Param("cuenta") com.banco.shibasito.entity.Cuenta cuenta,
                                                           @Param("fecha") LocalDateTime fecha);

    /**
     * Busca transacciones por cuenta y fecha menor o igual
     */
    @Query("SELECT t FROM Transaccion t WHERE t.cuenta = :cuenta AND t.fecha <= :fecha ORDER BY t.fecha DESC")
    List<Transaccion> findByCuentaAndFechaLessThanEqual(@Param("cuenta") com.banco.shibasito.entity.Cuenta cuenta,
                                                        @Param("fecha") LocalDateTime fecha);

    /**
     * Busca transacciones por tipo ordenadas por fecha descendente
     */
    List<Transaccion> findByTipoOrderByFechaDesc(Transaccion.TipoTransaccion tipo);

    /**
     * Busca transacciones por estado ordenadas por fecha descendente
     */
    List<Transaccion> findByEstadoOrderByFechaDesc(Transaccion.Estado estado);

    /**
     * Consulta personalizada para obtener transacciones por rango de fechas
     */
    @Query("SELECT t FROM Transaccion t WHERE t.fecha BETWEEN :fechaInicio AND :fechaFin ORDER BY t.fecha DESC")
    List<Transaccion> findByFechaBetweenOrderByFechaDesc(@Param("fechaInicio") LocalDateTime fechaInicio, 
                                                        @Param("fechaFin") LocalDateTime fechaFin);
}
