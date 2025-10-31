package com.banco.shibasito.repository;

import com.banco.shibasito.entity.Cuenta;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository para la entidad Cuenta
 */
@Repository
public interface CuentaRepository extends JpaRepository<Cuenta, Long> {

    /**
     * Busca cuentas por DNI del cliente
     */
    @Query("SELECT c FROM Cuenta c WHERE c.cliente.dni = :clienteDni")
    List<Cuenta> findByClienteDni(@Param("clienteDni") String clienteDni);

    /**
     * Busca una cuenta por su número
     */
    Optional<Cuenta> findByNumero(String numero);

    /**
     * Busca cuentas por estado
     */
    List<Cuenta> findByEstado(Cuenta.Estado estado);

    /**
     * Consulta personalizada para buscar cuentas por cliente y estado
     */
    @Query("SELECT c FROM Cuenta c WHERE c.cliente.dni = :clienteDni AND c.estado = :estado")
    List<Cuenta> findByClienteDniAndEstado(@Param("clienteDni") String clienteDni, @Param("estado") Cuenta.Estado estado);

    /**
     * Consulta personalizada para obtener cuentas activas de un cliente
     */
    @Query("SELECT c FROM Cuenta c WHERE c.cliente.dni = :clienteDni AND c.estado = 'ACTIVA'")
    List<Cuenta> findActivasByClienteDni(@Param("clienteDni") String clienteDni);
}
