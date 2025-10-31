package com.banco.shibasito.service;

import com.banco.shibasito.model.CuentaBancaria;
import com.banco.shibasito.repository.CuentaBancariaRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

/**
 * Servicio para la gestión de cuentas bancarias
 * 
 * Maneja toda la lógica de negocio relacionada con cuentas bancarias
 * incluyendo operaciones de depósito, retiro, consultas y validaciones.
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
@Service
@Transactional
public class CuentaBancariaService {

    private static final Logger logger = LoggerFactory.getLogger(CuentaBancariaService.class);

    private final CuentaBancariaRepository cuentaRepository;

    @Autowired
    public CuentaBancariaService(CuentaBancariaRepository cuentaRepository) {
        this.cuentaRepository = cuentaRepository;
    }

    /**
     * Crea una nueva cuenta bancaria
     */
    public CuentaBancaria crearCuenta(CuentaBancaria cuenta) {
        logger.info("Creando nueva cuenta: {}", cuenta.getNumeroCuenta());
        
        // Validaciones
        if (cuentaRepository.existsByNumeroCuenta(cuenta.getNumeroCuenta())) {
            throw new IllegalArgumentException("El número de cuenta ya existe: " + cuenta.getNumeroCuenta());
        }

        cuenta.setEstado(CuentaBancaria.EstadoCuenta.ACTIVA);
        CuentaBancaria nuevaCuenta = cuentaRepository.save(cuenta);
        
        logger.info("Cuenta creada exitosamente: ID {}", nuevaCuenta.getId());
        return nuevaCuenta;
    }

    /**
     * Obtiene una cuenta por ID
     */
    @Transactional(readOnly = true)
    public Optional<CuentaBancaria> obtenerCuentaPorId(Long id) {
        return cuentaRepository.findById(id);
    }

    /**
     * Obtiene una cuenta por número
     */
    @Transactional(readOnly = true)
    public Optional<CuentaBancaria> obtenerCuentaPorNumero(String numeroCuenta) {
        return cuentaRepository.findByNumeroCuenta(numeroCuenta);
    }

    /**
     * Obtiene todas las cuentas de un cliente
     */
    @Transactional(readOnly = true)
    public List<CuentaBancaria> obtenerCuentasPorCliente(Long clienteId) {
        return cuentaRepository.findByClienteId(clienteId);
    }

    /**
     * Obtiene cuentas activas de un cliente
     */
    @Transactional(readOnly = true)
    public List<CuentaBancaria> obtenerCuentasActivasPorCliente(Long clienteId) {
        return cuentaRepository.findCuentasActivasByCliente(clienteId);
    }

    /**
     * Busca cuentas con filtros y paginación
     */
    @Transactional(readOnly = true)
    public Page<CuentaBancaria> buscarCuentasConFiltros(
            Long clienteId,
            CuentaBancaria.TipoCuenta tipoCuenta,
            CuentaBancaria.EstadoCuenta estado,
            String numeroCuenta,
            Pageable pageable) {
        
        return cuentaRepository.findByFiltros(clienteId, tipoCuenta, estado, numeroCuenta, pageable);
    }

    /**
     * Realiza un depósito en una cuenta
     */
    public boolean realizarDeposito(Long cuentaId, BigDecimal monto) {
        logger.info("Realizando depósito: Cuenta ID {}, Monto {}", cuentaId, monto);
        
        Optional<CuentaBancaria> cuentaOpt = cuentaRepository.findByIdWithLock(cuentaId);
        
        if (cuentaOpt.isEmpty()) {
            logger.warn("Cuenta no encontrada: ID {}", cuentaId);
            return false;
        }

        CuentaBancaria cuenta = cuentaOpt.get();
        
        if (cuenta.getEstado() != CuentaBancaria.EstadoCuenta.ACTIVA) {
            logger.warn("Cuenta no está activa: ID {}", cuentaId);
            return false;
        }

        if (monto == null || monto.compareTo(BigDecimal.ZERO) <= 0) {
            logger.warn("Monto inválido para depósito: {}", monto);
            return false;
        }

        cuenta.depositar(monto);
        cuentaRepository.save(cuenta);
        
        logger.info("Depósito realizado exitosamente. Nuevo saldo: {}", cuenta.getSaldoActual());
        return true;
    }

    /**
     * Realiza un retiro de una cuenta
     */
    public boolean realizarRetiro(Long cuentaId, BigDecimal monto) {
        logger.info("Realizando retiro: Cuenta ID {}, Monto {}", cuentaId, monto);
        
        Optional<CuentaBancaria> cuentaOpt = cuentaRepository.findByIdWithLock(cuentaId);
        
        if (cuentaOpt.isEmpty()) {
            logger.warn("Cuenta no encontrada: ID {}", cuentaId);
            return false;
        }

        CuentaBancaria cuenta = cuentaOpt.get();
        
        if (cuenta.getEstado() != CuentaBancaria.EstadoCuenta.ACTIVA) {
            logger.warn("Cuenta no está activa: ID {}", cuentaId);
            return false;
        }

        if (monto == null || monto.compareTo(BigDecimal.ZERO) <= 0) {
            logger.warn("Monto inválido para retiro: {}", monto);
            return false;
        }

        boolean retiroExitoso = cuenta.retirar(monto);
        
        if (retiroExitoso) {
            cuentaRepository.save(cuenta);
            logger.info("Retiro realizado exitosamente. Nuevo saldo: {}", cuenta.getSaldoActual());
        } else {
            logger.warn("Saldo insuficiente para retiro. Saldo actual: {}", cuenta.getSaldoActual());
        }
        
        return retiroExitoso;
    }

    /**
     * Transfiere dinero entre cuentas
     */
    public boolean realizarTransferencia(Long cuentaOrigenId, Long cuentaDestinoId, BigDecimal monto) {
        logger.info("Iniciando transferencia: Origen {}, Destino {}, Monto {}", 
                   cuentaOrigenId, cuentaDestinoId, monto);
        
        if (cuentaOrigenId.equals(cuentaDestinoId)) {
            logger.warn("No se puede transferir a la misma cuenta");
            return false;
        }

        Optional<CuentaBancaria> origenOpt = cuentaRepository.findByIdWithLock(cuentaOrigenId);
        Optional<CuentaBancaria> destinoOpt = cuentaRepository.findByIdWithLock(cuentaDestinoId);
        
        if (origenOpt.isEmpty() || destinoOpt.isEmpty()) {
            logger.warn("Una de las cuentas no fue encontrada");
            return false;
        }

        CuentaBancaria origen = origenOpt.get();
        CuentaBancaria destino = destinoOpt.get();

        // Validar que ambas cuentas estén activas
        if (origen.getEstado() != CuentaBancaria.EstadoCuenta.ACTIVA ||
            destino.getEstado() != CuentaBancaria.EstadoCuenta.ACTIVA) {
            logger.warn("Una de las cuentas no está activa");
            return false;
        }

        // Realizar retiro del origen
        boolean retiroExitoso = origen.retirar(monto);
        if (!retiroExitoso) {
            logger.warn("Saldo insuficiente en cuenta origen");
            return false;
        }

        // Realizar depósito en destino
        destino.depositar(monto);

        // Guardar cambios
        cuentaRepository.save(origen);
        cuentaRepository.save(destino);
        
        logger.info("Transferencia completada exitosamente");
        return true;
    }

    /**
     * Obtiene el saldo total del cliente
     */
    @Transactional(readOnly = true)
    public Double obtenerSaldoTotalCliente(Long clienteId) {
        return cuentaRepository.getSaldoTotalByCliente(clienteId);
    }

    /**
     * Cuenta el número de cuentas de un cliente
     */
    @Transactional(readOnly = true)
    public Long contarCuentasCliente(Long clienteId) {
        return cuentaRepository.countByClienteId(clienteId);
    }

    /**
     * Cambia el estado de una cuenta
     */
    public boolean cambiarEstadoCuenta(Long cuentaId, CuentaBancaria.EstadoCuenta nuevoEstado) {
        logger.info("Cambiando estado de cuenta: ID {}, Nuevo estado {}", cuentaId, nuevoEstado);
        
        Optional<CuentaBancaria> cuentaOpt = cuentaRepository.findById(cuentaId);
        
        if (cuentaOpt.isEmpty()) {
            return false;
        }

        CuentaBancaria cuenta = cuentaOpt.get();
        cuenta.setEstado(nuevoEstado);
        cuentaRepository.save(cuenta);
        
        logger.info("Estado de cuenta cambiado exitosamente");
        return true;
    }

    /**
     * Obtiene cuentas con saldo mayor al especificado
     */
    @Transactional(readOnly = true)
    public List<CuentaBancaria> obtenerCuentasConSaldoMayor(Double saldo) {
        return cuentaRepository.findBySaldoGreaterThan(saldo);
    }

    /**
     * Obtiene las cuentas con mayor saldo
     */
    @Transactional(readOnly = true)
    public List<CuentaBancaria> obtenerTopCuentasPorSaldo(Pageable pageable) {
        return cuentaRepository.findTopCuentasBySaldo(pageable);
    }

    /**
     * Obtiene estadísticas de cuentas por tipo
     */
    @Transactional(readOnly = true)
    public List<Object[]> obtenerEstadisticasPorTipo() {
        return cuentaRepository.getEstadisticasPorTipo();
    }

    /**
     * Busca cuentas con saldo negativo
     */
    @Transactional(readOnly = true)
    public List<CuentaBancaria> obtenerCuentasConSaldoNegativo() {
        return cuentaRepository.findCuentasConSaldoNegativo();
    }

    /**
     * Valida si un cliente puede crear una nueva cuenta
     */
    @Transactional(readOnly = true)
    public boolean validarCreacionCuenta(Long clienteId, CuentaBancaria.TipoCuenta tipoCuenta) {
        Long cantidadCuentas = contarCuentasCliente(clienteId);
        
        // Reglas de negocio simplificadas:
        // - Máximo 5 cuentas por cliente
        // - Solo 1 cuenta de plazo fijo por cliente
        if (cantidadCuentas >= 5) {
            return false;
        }

        if (tipoCuenta == CuentaBancaria.TipoCuenta.PLAZO_FIJO) {
            List<CuentaBancaria> cuentasPlazoFijo = cuentaRepository
                .findByTipoCuentaAndEstado(tipoCuenta, CuentaBancaria.EstadoCuenta.ACTIVA);
            return cuentasPlazoFijo.isEmpty();
        }

        return true;
    }
}
