package com.banco.shibasito.repository;

import com.banco.shibasito.model.CuentaBancaria;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import jakarta.persistence.LockModeType;
import java.util.List;
import java.util.Optional;

/**
 * Repositorio para la entidad CuentaBancaria
 * 
 * Proporciona operaciones CRUD y consultas específicas para cuentas bancarias
 * con soporte para paginación y especificaciones.
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
@Repository
public interface CuentaBancariaRepository extends 
        JpaRepository<CuentaBancaria, Long>,
        JpaSpecificationExecutor<CuentaBancaria> {

    /**
     * Busca una cuenta por número de cuenta
     */
    Optional<CuentaBancaria> findByNumeroCuenta(String numeroCuenta);

    /**
     * Busca cuentas por ID de cliente
     */
    List<CuentaBancaria> findByClienteId(Long clienteId);

    /**
     * Busca cuentas por cliente con paginación
     */
    Page<CuentaBancaria> findByClienteId(Long clienteId, Pageable pageable);

    /**
     * Busca cuentas por tipo y estado
     */
    List<CuentaBancaria> findByTipoCuentaAndEstado(
            CuentaBancaria.TipoCuenta tipoCuenta, 
            CuentaBancaria.EstadoCuenta estado);

    /**
     * Busca cuentas activas por cliente
     */
    @Query("SELECT c FROM CuentaBancaria c WHERE c.clienteId = :clienteId AND c.estado = 'ACTIVA'")
    List<CuentaBancaria> findCuentasActivasByCliente(@Param("clienteId") Long clienteId);

    /**
     * Obtiene el saldo total del cliente
     */
    @Query("SELECT COALESCE(SUM(c.saldoActual), 0) FROM CuentaBancaria c WHERE c.clienteId = :clienteId AND c.estado = 'ACTIVA'")
    Double getSaldoTotalByCliente(@Param("clienteId") Long clienteId);

    /**
     * Busca cuentas con saldo mayor al especificado
     */
    @Query("SELECT c FROM CuentaBancaria c WHERE c.saldoActual > :saldo AND c.estado = 'ACTIVA'")
    List<CuentaBancaria> findBySaldoGreaterThan(@Param("saldo") Double saldo);

    /**
     * Cuenta el número de cuentas por cliente
     */
    @Query("SELECT COUNT(c) FROM CuentaBancaria c WHERE c.clienteId = :clienteId")
    Long countByClienteId(@Param("clienteId") Long clienteId);

    /**
     * Busca cuentas por múltiples criterios
     */
    @Query("SELECT c FROM CuentaBancaria c WHERE " +
           "(:clienteId IS NULL OR c.clienteId = :clienteId) AND " +
           "(:tipoCuenta IS NULL OR c.tipoCuenta = :tipoCuenta) AND " +
           "(:estado IS NULL OR c.estado = :estado) AND " +
           "(:numeroCuenta IS NULL OR c.numeroCuenta LIKE %:numeroCuenta%)")
    Page<CuentaBancaria> findByFiltros(
            @Param("clienteId") Long clienteId,
            @Param("tipoCuenta") CuentaBancaria.TipoCuenta tipoCuenta,
            @Param("estado") CuentaBancaria.EstadoCuenta estado,
            @Param("numeroCuenta") String numeroCuenta,
            Pageable pageable);

    /**
     * Actualiza el saldo de una cuenta con bloqueo pesimista
     */
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT c FROM CuentaBancaria c WHERE c.id = :id")
    Optional<CuentaBancaria> findByIdWithLock(@Param("id") Long id);

    /**
     * Verifica si existe una cuenta por número
     */
    boolean existsByNumeroCuenta(String numeroCuenta);

    /**
     * Busca cuentas con mayor saldo
     */
    @Query("SELECT c FROM CuentaBancaria c WHERE c.estado = 'ACTIVA' ORDER BY c.saldoActual DESC")
    List<CuentaBancaria> findTopCuentasBySaldo(Pageable pageable);

    /**
     * Obtiene estadísticas de cuentas por tipo
     */
    @Query("SELECT c.tipoCuenta, COUNT(c), AVG(c.saldoActual) FROM CuentaBancaria c " +
           "WHERE c.estado = 'ACTIVA' GROUP BY c.tipoCuenta")
    List<Object[]> getEstadisticasPorTipo();

    /**
     * Busca cuentas con saldo negativo
     */
    @Query("SELECT c FROM CuentaBancaria c WHERE c.saldoActual < 0 AND c.estado = 'ACTIVA'")
    List<CuentaBancaria> findCuentasConSaldoNegativo();
}
