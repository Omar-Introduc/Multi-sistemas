package com.banco.shibasito.service;

import com.banco.shibasito.dto.Response;
import com.banco.shibasito.entity.Cliente;
import com.banco.shibasito.entity.Cuenta;
import com.banco.shibasito.entity.Transaccion;
import com.banco.shibasito.repository.CuentaRepository;
import com.banco.shibasito.repository.ClienteRepository;
import com.banco.shibasito.repository.TransaccionRepository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Servicio de negocio para la gestión de cuentas bancarias
 * Maneja la lógica de negocio relacionada con cuentas del banco
 */
@Service
@Transactional
public class CuentaService {
    
    @Autowired
    private CuentaRepository cuentaRepository;
    
    @Autowired
    private ClienteRepository clienteRepository;
    
    @Autowired
    private TransaccionRepository transaccionRepository;
    
    @Autowired
    private BancoRabbitMQService rabbitMQService;
    
    /**
     * Crea una nueva cuenta bancaria
     * @param numero Numero de la cuenta
     * @param dniCliente DNI del cliente propietario
     * @param tipo Tipo de cuenta (AHORROS, CORRIENTE)
     * @param saldoInicial Saldo inicial de la cuenta
     * @return Response con la cuenta creada o mensaje de error
     */
    public Response<Cuenta> crearCuenta(String numero, String dniCliente, Cuenta.TipoCuenta tipo, BigDecimal saldoInicial) {
        try {
            // Validaciones
            Response<Cuenta> validacion = validarCreacionCuenta(numero, dniCliente, tipo, saldoInicial);
            if (!validacion.isSuccess()) {
                return validacion;
            }
            
            // Verificar que el cliente existe
            Optional<Cliente> clienteOpt = clienteRepository.findByDni(dniCliente);
            if (!clienteOpt.isPresent()) {
                return Response.error("No se encontró cliente con DNI: " + dniCliente, "CLIENTE_NO_ENCONTRADO");
            }
            
            // Verificar que no existe una cuenta con el mismo número
            if (cuentaRepository.findByNumero(numero).isPresent()) {
                return Response.error("Ya existe una cuenta con el número: " + numero, "CUENTA_DUPLICADA");
            }
            
            // Crear la cuenta
            Cuenta cuenta = new Cuenta(numero, saldoInicial, tipo, clienteOpt.get());
            cuenta.setSaldoMinimo(calcularSaldoMinimo(tipo));
            
            // Guardar la cuenta
            Cuenta cuentaCreada = cuentaRepository.save(cuenta);
            
            // Enviar mensaje a RabbitMQ
            rabbitMQService.enviarEventoCuentaCreada(cuentaCreada);
            
            return Response.success("Cuenta creada exitosamente", cuentaCreada);
            
        } catch (Exception e) {
            return Response.error("Error al crear cuenta: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Consulta el saldo de una cuenta
     * @param numero Numero de la cuenta
     * @return Response con el saldo de la cuenta o mensaje de error
     */
    public Response<BigDecimal> consultarSaldo(String numero) {
        try {
            if (numero == null || numero.trim().isEmpty()) {
                return Response.error("El número de cuenta no puede estar vacío", "NUMERO_CUENTA_INVALIDO");
            }
            
            Optional<Cuenta> cuenta = cuentaRepository.findByNumero(numero);
            
            if (!cuenta.isPresent()) {
                return Response.error("No se encontró cuenta con número: " + numero, "CUENTA_NO_ENCONTRADA");
            }
            
            // Verificar que la cuenta está activa
            if (cuenta.get().getEstado() != Cuenta.Estado.ACTIVA) {
                return Response.error("La cuenta no está activa. Estado actual: " + cuenta.get().getEstado(), "CUENTA_INACTIVA");
            }
            
            return Response.success("Saldo consultado exitosamente", cuenta.get().getSaldo());
            
        } catch (Exception e) {
            return Response.error("Error al consultar saldo: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Realiza un depósito en una cuenta
     * @param numero Numero de la cuenta
     * @param monto Monto a depositar
     * @param descripcion Descripción del depósito
     * @return Response con el resultado de la operación
     */
    public Response<String> depositar(String numero, BigDecimal monto, String descripcion) {
        try {
            if (monto == null || monto.compareTo(BigDecimal.ZERO) <= 0) {
                return Response.error("El monto debe ser mayor a cero", "MONTO_INVALIDO");
            }
            
            Optional<Cuenta> cuentaOpt = cuentaRepository.findByNumero(numero);
            if (!cuentaOpt.isPresent()) {
                return Response.error("No se encontró cuenta con número: " + numero, "CUENTA_NO_ENCONTRADA");
            }
            
            Cuenta cuenta = cuentaOpt.get();
            
            // Verificar que la cuenta está activa
            if (cuenta.getEstado() != Cuenta.Estado.ACTIVA) {
                return Response.error("No se puede depositar en una cuenta no activa", "CUENTA_INACTIVA");
            }
            
            // Realizar el depósito
            cuenta.depositar(monto);
            cuentaRepository.save(cuenta);
            
            // Crear registro de transacción
            Transaccion transaccion = new Transaccion();
            transaccion.setCuenta(cuenta);
            transaccion.setTipo(Transaccion.Tipo.DEPOSITO);
            transaccion.setMonto(monto);
            transaccion.setDescripcion(descripcion != null ? descripcion : "Depósito en cuenta");
            transaccion.setFecha(LocalDateTime.now());
            transaccion.setEstado(Transaccion.Estado.COMPLETADA);
            
            transaccionRepository.save(transaccion);
            
            // Enviar mensaje a RabbitMQ
            rabbitMQService.enviarEventoTransaccionProcesada(transaccion);
            
            return Response.success("Depósito realizado exitosamente. Nuevo saldo: " + cuenta.getSaldo());
            
        } catch (Exception e) {
            return Response.error("Error al realizar depósito: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Realiza un retiro de una cuenta
     * @param numero Numero de la cuenta
     * @param monto Monto a retirar
     * @param descripcion Descripción del retiro
     * @return Response con el resultado de la operación
     */
    public Response<String> retirar(String numero, BigDecimal monto, String descripcion) {
        try {
            if (monto == null || monto.compareTo(BigDecimal.ZERO) <= 0) {
                return Response.error("El monto debe ser mayor a cero", "MONTO_INVALIDO");
            }
            
            Optional<Cuenta> cuentaOpt = cuentaRepository.findByNumero(numero);
            if (!cuentaOpt.isPresent()) {
                return Response.error("No se encontró cuenta con número: " + numero, "CUENTA_NO_ENCONTRADA");
            }
            
            Cuenta cuenta = cuentaOpt.get();
            
            // Verificar que la cuenta está activa
            if (cuenta.getEstado() != Cuenta.Estado.ACTIVA) {
                return Response.error("No se puede retirar de una cuenta no activa", "CUENTA_INACTIVA");
            }
            
            // Verificar si se puede realizar el retiro
            if (!cuenta.puedeRetirar(monto)) {
                return Response.error("No se puede realizar el retiro. Saldo insuficiente o límite mínimo no alcanzado", "RETIRO_NO_PERMITIDO");
            }
            
            // Realizar el retiro
            cuenta.retirar(monto);
            cuentaRepository.save(cuenta);
            
            // Crear registro de transacción
            Transaccion transaccion = new Transaccion();
            transaccion.setCuenta(cuenta);
            transaccion.setTipo(Transaccion.Tipo.RETIRO);
            transaccion.setMonto(monto);
            transaccion.setDescripcion(descripcion != null ? descripcion : "Retiro de cuenta");
            transaccion.setFecha(LocalDateTime.now());
            transaccion.setEstado(Transaccion.Estado.COMPLETADA);
            
            transaccionRepository.save(transaccion);
            
            // Enviar mensaje a RabbitMQ
            rabbitMQService.enviarEventoTransaccionProcesada(transaccion);
            
            return Response.success("Retiro realizado exitosamente. Nuevo saldo: " + cuenta.getSaldo());
            
        } catch (Exception e) {
            return Response.error("Error al realizar retiro: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Consulta el historial de transacciones de una cuenta
     * @param numero Numero de la cuenta
     * @param fechaInicio Fecha de inicio del período (opcional)
     * @param fechaFin Fecha de fin del período (opcional)
     * @return Response con la lista de transacciones o mensaje de error
     */
    public Response<List<Transaccion>> consultarHistorial(String numero, LocalDate fechaInicio, LocalDate fechaFin) {
        try {
            if (numero == null || numero.trim().isEmpty()) {
                return Response.error("El número de cuenta no puede estar vacío", "NUMERO_CUENTA_INVALIDO");
            }
            
            Optional<Cuenta> cuenta = cuentaRepository.findByNumero(numero);
            if (!cuenta.isPresent()) {
                return Response.error("No se encontró cuenta con número: " + numero, "CUENTA_NO_ENCONTRADA");
            }
            
            List<Transaccion> transacciones;
            
            // Si se especifican fechas, filtrar por período
            if (fechaInicio != null && fechaFin != null) {
                transacciones = transaccionRepository.findByCuentaAndFechaBetween(
                        cuenta.get(), 
                        fechaInicio.atStartOfDay(), 
                        fechaFin.atTime(23, 59, 59)
                );
            } else if (fechaInicio != null) {
                transacciones = transaccionRepository.findByCuentaAndFechaGreaterThanEqual(
                        cuenta.get(), 
                        fechaInicio.atStartOfDay()
                );
            } else if (fechaFin != null) {
                transacciones = transaccionRepository.findByCuentaAndFechaLessThanEqual(
                        cuenta.get(), 
                        fechaFin.atTime(23, 59, 59)
                );
            } else {
                // Sin filtros de fecha
                transacciones = transaccionRepository.findByCuentaOrderByFechaDesc(cuenta.get());
            }
            
            return Response.success("Historial de transacciones obtenido exitosamente", transacciones);
            
        } catch (Exception e) {
            return Response.error("Error al consultar historial: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Bloquea una cuenta
     * @param numero Numero de la cuenta
     * @param motivo Motivo del bloqueo
     * @return Response con el resultado de la operación
     */
    public Response<String> bloquearCuenta(String numero, String motivo) {
        try {
            Optional<Cuenta> cuentaOpt = cuentaRepository.findByNumero(numero);
            if (!cuentaOpt.isPresent()) {
                return Response.error("No se encontró cuenta con número: " + numero, "CUENTA_NO_ENCONTRADA");
            }
            
            Cuenta cuenta = cuentaOpt.get();
            cuenta.setEstado(Cuenta.Estado.BLOQUEADA);
            cuentaRepository.save(cuenta);
            
            // Enviar alerta
            rabbitMQService.enviarAlerta("CUENTA_BLOQUEADA", 
                    "Cuenta " + numero + " bloqueada. Motivo: " + motivo, null);
            
            return Response.success("Cuenta bloqueada exitosamente");
            
        } catch (Exception e) {
            return Response.error("Error al bloquear cuenta: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Desbloquea una cuenta
     * @param numero Numero de la cuenta
     * @return Response con el resultado de la operación
     */
    public Response<String> desbloquearCuenta(String numero) {
        try {
            Optional<Cuenta> cuentaOpt = cuentaRepository.findByNumero(numero);
            if (!cuentaOpt.isPresent()) {
                return Response.error("No se encontró cuenta con número: " + numero, "CUENTA_NO_ENCONTRADA");
            }
            
            Cuenta cuenta = cuentaOpt.get();
            cuenta.setEstado(Cuenta.Estado.ACTIVA);
            cuentaRepository.save(cuenta);
            
            return Response.success("Cuenta desbloqueada exitosamente");
            
        } catch (Exception e) {
            return Response.error("Error al desbloquear cuenta: " + e.getMessage(), "ERROR_INTERNO");
        }
    }
    
    /**
     * Genera un número de cuenta único
     * @param tipo Tipo de cuenta
     * @return Número de cuenta generado
     */
    public String generarNumeroCuenta(Cuenta.TipoCuenta tipo) {
        String prefix = "";
        switch (tipo) {
            case AHORROS: prefix = "20"; break;
            case CORRIENTE: prefix = "10"; break;
            case PLAZO_FIJO: prefix = "30"; break;
        }
        
        String numero = prefix + String.format("%013d", System.currentTimeMillis() % 1000000000000L);
        return numero;
    }
    
    /**
     * Calcula el saldo mínimo según el tipo de cuenta
     * @param tipo Tipo de cuenta
     * @return Saldo mínimo
     */
    private BigDecimal calcularSaldoMinimo(Cuenta.TipoCuenta tipo) {
        switch (tipo) {
            case AHORROS: return new BigDecimal("100.00");
            case CORRIENTE: return new BigDecimal("500.00");
            case PLAZO_FIJO: return new BigDecimal("1000.00");
            default: return BigDecimal.ZERO;
        }
    }
    
    /**
     * Valida los datos para creación de cuenta
     * @param numero Numero de cuenta
     * @param dniCliente DNI del cliente
     * @param tipo Tipo de cuenta
     * @param saldoInicial Saldo inicial
     * @return Response con resultado de validación
     */
    private Response<Cuenta> validarCreacionCuenta(String numero, String dniCliente, Cuenta.TipoCuenta tipo, BigDecimal saldoInicial) {
        if (numero == null || numero.trim().isEmpty()) {
            return Response.error("El número de cuenta es obligatorio", "NUMERO_CUENTA_REQUERIDO");
        }
        
        if (dniCliente == null || dniCliente.trim().isEmpty()) {
            return Response.error("El DNI del cliente es obligatorio", "DNI_CLIENTE_REQUERIDO");
        }
        
        if (tipo == null) {
            return Response.error("El tipo de cuenta es obligatorio", "TIPO_CUENTA_REQUERIDO");
        }
        
        if (saldoInicial == null || saldoInicial.compareTo(BigDecimal.ZERO) < 0) {
            return Response.error("El saldo inicial no puede ser negativo", "SALDO_INICIAL_INVALIDO");
        }
        
        return Response.success("Validación exitosa");
    }
}