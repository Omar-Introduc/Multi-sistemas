package com.banco.shibasito.controller;

import com.banco.shibasito.model.CuentaBancaria;
import com.banco.shibasito.service.CuentaBancariaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Controlador REST para la gestión de cuentas bancarias
 * 
 * Expone los endpoints de la API para operaciones relacionadas
 * con cuentas bancarias.
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
@RestController
@RequestMapping("/api/cuentas")
@Tag(name = "Cuentas Bancarias", description = "API para gestión de cuentas bancarias")
@CrossOrigin(origins = "*", maxAge = 3600)
public class CuentaBancariaController {

    private final CuentaBancariaService cuentaService;

    @Autowired
    public CuentaBancariaController(CuentaBancariaService cuentaService) {
        this.cuentaService = cuentaService;
    }

    @PostMapping
    @Operation(summary = "Crear nueva cuenta", description = "Crea una nueva cuenta bancaria")
    public ResponseEntity<?> crearCuenta(
            @Valid @RequestBody CuentaBancaria cuenta) {
        try {
            CuentaBancaria nuevaCuenta = cuentaService.crearCuenta(cuenta);
            return ResponseEntity.status(HttpStatus.CREATED).body(nuevaCuenta);
        } catch (IllegalArgumentException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener cuenta por ID", description = "Obtiene una cuenta bancaria por su ID")
    public ResponseEntity<?> obtenerCuentaPorId(
            @Parameter(description = "ID de la cuenta") @PathVariable Long id) {
        Optional<CuentaBancaria> cuenta = cuentaService.obtenerCuentaPorId(id);
        
        if (cuenta.isPresent()) {
            return ResponseEntity.ok(cuenta.get());
        } else {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Cuenta no encontrada con ID: " + id);
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/numero/{numeroCuenta}")
    @Operation(summary = "Obtener cuenta por número", description = "Obtiene una cuenta bancaria por su número")
    public ResponseEntity<?> obtenerCuentaPorNumero(
            @Parameter(description = "Número de cuenta") @PathVariable String numeroCuenta) {
        Optional<CuentaBancaria> cuenta = cuentaService.obtenerCuentaPorNumero(numeroCuenta);
        
        if (cuenta.isPresent()) {
            return ResponseEntity.ok(cuenta.get());
        } else {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Cuenta no encontrada: " + numeroCuenta);
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/cliente/{clienteId}")
    @Operation(summary = "Obtener cuentas por cliente", description = "Obtiene todas las cuentas de un cliente")
    public ResponseEntity<?> obtenerCuentasPorCliente(
            @Parameter(description = "ID del cliente") @PathVariable Long clienteId) {
        List<CuentaBancaria> cuentas = cuentaService.obtenerCuentasPorCliente(clienteId);
        return ResponseEntity.ok(cuentas);
    }

    @GetMapping("/cliente/{clienteId}/activas")
    @Operation(summary = "Obtener cuentas activas por cliente", description = "Obtiene las cuentas activas de un cliente")
    public ResponseEntity<?> obtenerCuentasActivasPorCliente(
            @Parameter(description = "ID del cliente") @PathVariable Long clienteId) {
        List<CuentaBancaria> cuentas = cuentaService.obtenerCuentasActivasPorCliente(clienteId);
        return ResponseEntity.ok(cuentas);
    }

    @GetMapping("/buscar")
    @Operation(summary = "Buscar cuentas con filtros", description = "Busca cuentas con filtros y paginación")
    public ResponseEntity<?> buscarCuentas(
            @Parameter(description = "ID del cliente (opcional)") @RequestParam(required = false) Long clienteId,
            @Parameter(description = "Tipo de cuenta (opcional)") @RequestParam(required = false) CuentaBancaria.TipoCuenta tipoCuenta,
            @Parameter(description = "Estado de cuenta (opcional)") @RequestParam(required = false) CuentaBancaria.EstadoCuenta estado,
            @Parameter(description = "Número de cuenta (opcional)") @RequestParam(required = false) String numeroCuenta,
            Pageable pageable) {
        
        Page<CuentaBancaria> cuentas = cuentaService.buscarCuentasConFiltros(
            clienteId, tipoCuenta, estado, numeroCuenta, pageable);
        
        return ResponseEntity.ok(cuentas);
    }

    @PostMapping("/{id}/deposito")
    @Operation(summary = "Realizar depósito", description = "Realiza un depósito en una cuenta")
    public ResponseEntity<?> realizarDeposito(
            @Parameter(description = "ID de la cuenta") @PathVariable Long id,
            @Parameter(description = "Monto del depósito") @RequestParam BigDecimal monto) {
        
        boolean exitoso = cuentaService.realizarDeposito(id, monto);
        
        if (exitoso) {
            Map<String, String> response = new HashMap<>();
            response.put("mensaje", "Depósito realizado exitosamente");
            response.put("monto", monto.toString());
            return ResponseEntity.ok(response);
        } else {
            Map<String, String> error = new HashMap<>();
            error.put("error", "No se pudo realizar el depósito");
            return ResponseEntity.badRequest().body(error);
        }
    }

    @PostMapping("/{id}/retiro")
    @Operation(summary = "Realizar retiro", description = "Realiza un retiro de una cuenta")
    public ResponseEntity<?> realizarRetiro(
            @Parameter(description = "ID de la cuenta") @PathVariable Long id,
            @Parameter(description = "Monto del retiro") @RequestParam BigDecimal monto) {
        
        boolean exitoso = cuentaService.realizarRetiro(id, monto);
        
        if (exitoso) {
            Map<String, String> response = new HashMap<>();
            response.put("mensaje", "Retiro realizado exitosamente");
            response.put("monto", monto.toString());
            return ResponseEntity.ok(response);
        } else {
            Map<String, String> error = new HashMap<>();
            error.put("error", "No se pudo realizar el retiro. Verifique saldo disponible y estado de la cuenta");
            return ResponseEntity.badRequest().body(error);
        }
    }

    @PostMapping("/transferencia")
    @Operation(summary = "Realizar transferencia", description = "Transfiere dinero entre dos cuentas")
    public ResponseEntity<?> realizarTransferencia(
            @Parameter(description = "ID de la cuenta origen") @RequestParam Long cuentaOrigenId,
            @Parameter(description = "ID de la cuenta destino") @RequestParam Long cuentaDestinoId,
            @Parameter(description = "Monto a transferir") @RequestParam BigDecimal monto) {
        
        boolean exitoso = cuentaService.realizarTransferencia(cuentaOrigenId, cuentaDestinoId, monto);
        
        if (exitoso) {
            Map<String, String> response = new HashMap<>();
            response.put("mensaje", "Transferencia realizada exitosamente");
            response.put("cuentaOrigen", cuentaOrigenId.toString());
            response.put("cuentaDestino", cuentaDestinoId.toString());
            response.put("monto", monto.toString());
            return ResponseEntity.ok(response);
        } else {
            Map<String, String> error = new HashMap<>();
            error.put("error", "No se pudo realizar la transferencia");
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/cliente/{clienteId}/saldo-total")
    @Operation(summary = "Obtener saldo total del cliente", description = "Calcula el saldo total de todas las cuentas activas de un cliente")
    public ResponseEntity<?> obtenerSaldoTotalCliente(
            @Parameter(description = "ID del cliente") @PathVariable Long clienteId) {
        
        Double saldoTotal = cuentaService.obtenerSaldoTotalCliente(clienteId);
        
        Map<String, Object> response = new HashMap<>();
        response.put("clienteId", clienteId);
        response.put("saldoTotal", saldoTotal);
        response.put("fechaConsulta", LocalDateTime.now());
        
        return ResponseEntity.ok(response);
    }

    @GetMapping("/cliente/{clienteId}/cantidad")
    @Operation(summary = "Contar cuentas del cliente", description = "Obtiene la cantidad de cuentas de un cliente")
    public ResponseEntity<?> contarCuentasCliente(
            @Parameter(description = "ID del cliente") @PathVariable Long clienteId) {
        
        Long cantidad = cuentaService.contarCuentasCliente(clienteId);
        
        Map<String, Object> response = new HashMap<>();
        response.put("clienteId", clienteId);
        response.put("cantidadCuentas", cantidad);
        
        return ResponseEntity.ok(response);
    }

    @PatchMapping("/{id}/estado")
    @Operation(summary = "Cambiar estado de cuenta", description = "Cambia el estado de una cuenta bancaria")
    public ResponseEntity<?> cambiarEstadoCuenta(
            @Parameter(description = "ID de la cuenta") @PathVariable Long id,
            @Parameter(description = "Nuevo estado") @RequestParam CuentaBancaria.EstadoCuenta estado) {
        
        boolean exitoso = cuentaService.cambiarEstadoCuenta(id, estado);
        
        if (exitoso) {
            Map<String, String> response = new HashMap<>();
            response.put("mensaje", "Estado de cuenta cambiado exitosamente");
            response.put("nuevoEstado", estado.name());
            return ResponseEntity.ok(response);
        } else {
            Map<String, String> error = new HashMap<>();
            error.put("error", "No se pudo cambiar el estado de la cuenta");
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/saldo-mayor/{saldo}")
    @Operation(summary = "Cuentas con saldo mayor", description = "Obtiene cuentas con saldo mayor al especificado")
    public ResponseEntity<?> obtenerCuentasConSaldoMayor(
            @Parameter(description = "Saldo mínimo") @PathVariable Double saldo) {
        
        List<CuentaBancaria> cuentas = cuentaService.obtenerCuentasConSaldoMayor(saldo);
        return ResponseEntity.ok(cuentas);
    }

    @GetMapping("/top-saldo")
    @Operation(summary = "Top cuentas por saldo", description = "Obtiene las cuentas con mayor saldo")
    public ResponseEntity<?> obtenerTopCuentasPorSaldo(Pageable pageable) {
        List<CuentaBancaria> cuentas = cuentaService.obtenerTopCuentasPorSaldo(pageable);
        return ResponseEntity.ok(cuentas);
    }

    @GetMapping("/estadisticas/tipo")
    @Operation(summary = "Estadísticas por tipo", description = "Obtiene estadísticas de cuentas agrupadas por tipo")
    public ResponseEntity<?> obtenerEstadisticasPorTipo() {
        List<Object[]> estadisticas = cuentaService.obtenerEstadisticasPorTipo();
        
        Map<String, Object> response = new HashMap<>();
        response.put("estadisticas", estadisticas);
        response.put("fechaConsulta", LocalDateTime.now());
        
        return ResponseEntity.ok(response);
    }

    @GetMapping("/saldo-negativo")
    @Operation(summary = "Cuentas con saldo negativo", description = "Obtiene cuentas que tienen saldo negativo")
    public ResponseEntity<?> obtenerCuentasConSaldoNegativo() {
        List<CuentaBancaria> cuentas = cuentaService.obtenerCuentasConSaldoNegativo();
        return ResponseEntity.ok(cuentas);
    }

    @GetMapping("/validar-creacion/{clienteId}")
    @Operation(summary = "Validar creación de cuenta", description = "Valida si un cliente puede crear una nueva cuenta")
    public ResponseEntity<?> validarCreacionCuenta(
            @Parameter(description = "ID del cliente") @PathVariable Long clienteId,
            @Parameter(description = "Tipo de cuenta") @RequestParam CuentaBancaria.TipoCuenta tipoCuenta) {
        
        boolean puedeCrear = cuentaService.validarCreacionCuenta(clienteId, tipoCuenta);
        
        Map<String, Object> response = new HashMap<>();
        response.put("clienteId", clienteId);
        response.put("tipoCuenta", tipoCuenta.name());
        response.put("puedeCrear", puedeCrear);
        
        return ResponseEntity.ok(response);
    }
}
