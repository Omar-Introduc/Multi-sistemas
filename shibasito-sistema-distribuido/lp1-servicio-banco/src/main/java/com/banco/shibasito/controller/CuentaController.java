package com.banco.shibasito.controller;

import com.banco.shibasito.dto.*;
import com.banco.shibasito.exception.CuentaException;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Controlador REST para operaciones de cuentas bancarias
 */
@Tag(name = "Cuenta", description = "Operaciones relacionadas con cuentas bancarias")
@RestController
@RequestMapping("/api/cuentas")
@CrossOrigin(origins = "*", maxAge = 3600)
public class CuentaController {

    private static final Logger logger = LoggerFactory.getLogger(CuentaController.class);

    /**
     * Obtiene el saldo de una cuenta por DNI
     */
    @Operation(
        summary = "Consultar saldo de cuenta",
        description = "Permite consultar el saldo disponible de una cuenta bancaria mediante el DNI del titular"
    )
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Saldo consultado exitosamente")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "DNI inválido o cuenta no encontrada")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Error interno del servidor")
    @GetMapping("/{dni}/saldo")
    public ResponseEntity<ApiResponse<SaldoResponse>> consultarSaldo(
            @Parameter(description = "Documento Nacional de Identidad del titular", example = "12345678", required = true)
            @PathVariable String dni) {
        
        logger.info("Consultando saldo para DNI: {}", dni);
        
        try {
            // Validar DNI
            if (dni == null || dni.trim().isEmpty() || dni.length() != 8 || !dni.matches("\\d+")) {
                throw new CuentaException("DNI inválido. Debe contener exactamente 8 dígitos.");
            }

            // Simulación de consulta de saldo
            SaldoResponse saldoResponse = new SaldoResponse(
                "1234567890",
                dni,
                new BigDecimal("1500.50"),
                "PEN"
            );

            logger.info("Saldo consultado exitosamente para DNI: {}", dni);
            return ResponseEntity.ok(ApiResponse.success("Saldo consultado exitosamente", saldoResponse));

        } catch (CuentaException ex) {
            logger.warn("Error al consultar saldo para DNI {}: {}", dni, ex.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(400, ex.getMessage()));
        } catch (Exception ex) {
            logger.error("Error interno al consultar saldo para DNI {}: {}", dni, ex.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(500, "Error interno del servidor"));
        }
    }

    /**
     * Crea una nueva cuenta bancaria
     */
    @Operation(
        summary = "Crear nueva cuenta",
        description = "Permite crear una nueva cuenta bancaria con saldo inicial"
    )
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "201", description = "Cuenta creada exitosamente")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Datos de entrada inválidos")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Error interno del servidor")
    @PostMapping
    public ResponseEntity<ApiResponse<CuentaResponse>> crearCuenta(
            @Parameter(description = "Datos de la nueva cuenta", required = true)
            @Valid @RequestBody CuentaCreateRequest request) {
        
        logger.info("Creando nueva cuenta para DNI: {}", request.getDni());
        
        try {
            // Validar que el DNI no exista ya
            if ("12345678".equals(request.getDni())) {
                throw new CuentaException("Ya existe una cuenta con este DNI");
            }

            // Simulación de creación de cuenta
            CuentaResponse cuentaResponse = new CuentaResponse(
                "1234567890",
                request.getDni(),
                request.getNombre(),
                request.getTipoCuenta(),
                request.getSaldoInicial(),
                request.getMoneda(),
                "ACTIVA"
            );
            cuentaResponse.setFechaCreacion(LocalDateTime.now());
            cuentaResponse.setFechaActualizacion(LocalDateTime.now());

            logger.info("Cuenta creada exitosamente con número: {} para DNI: {}", 
                       cuentaResponse.getNumeroCuenta(), request.getDni());
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(ApiResponse.success("Cuenta creada exitosamente", cuentaResponse));

        } catch (CuentaException ex) {
            logger.warn("Error al crear cuenta para DNI {}: {}", request.getDni(), ex.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(400, ex.getMessage()));
        } catch (Exception ex) {
            logger.error("Error interno al crear cuenta para DNI {}: {}", request.getDni(), ex.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(500, "Error interno del servidor"));
        }
    }

    /**
     * Obtiene el historial de transacciones de una cuenta por DNI
     */
    @Operation(
        summary = "Consultar historial de transacciones",
        description = "Permite consultar el historial completo de transacciones de una cuenta bancaria mediante el DNI del titular"
    )
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Historial consultado exitosamente")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "DNI inválido o cuenta no encontrada")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Error interno del servidor")
    @GetMapping("/{dni}/historial")
    public ResponseEntity<ApiResponse<List<HistorialTransaccionResponse>>> consultarHistorial(
            @Parameter(description = "Documento Nacional de Identidad del titular", example = "12345678", required = true)
            @PathVariable String dni,
            @Parameter(description = "Página de resultados (0-based)", example = "0")
            @RequestParam(defaultValue = "0") int pagina,
            @Parameter(description = "Tamaño de página", example = "20")
            @RequestParam(defaultValue = "20") int tamaño) {
        
        logger.info("Consultando historial para DNI: {}, página: {}, tamaño: {}", dni, pagina, tamaño);
        
        try {
            // Validar DNI
            if (dni == null || dni.trim().isEmpty() || dni.length() != 8 || !dni.matches("\\d+")) {
                throw new CuentaException("DNI inválido. Debe contener exactamente 8 dígitos.");
            }

            // Validar parámetros de paginación
            if (pagina < 0) {
                throw new IllegalArgumentException("La página debe ser mayor o igual a 0");
            }
            if (tamaño < 1 || tamaño > 100) {
                throw new IllegalArgumentException("El tamaño debe estar entre 1 y 100");
            }

            // Simulación de historial de transacciones
            List<HistorialTransaccionResponse> historial = new ArrayList<>();
            
            // Agregar algunas transacciones de ejemplo
            historial.add(new HistorialTransaccionResponse(
                1L,
                LocalDateTime.now().minusDays(1),
                "DEPOSITO",
                new BigDecimal("500.00"),
                new BigDecimal("2000.50"),
                "Depósito en efectivo",
                "COMPLETADA"
            ));
            
            historial.add(new HistorialTransaccionResponse(
                2L,
                LocalDateTime.now().minusHours(2),
                "RETIRO",
                new BigDecimal("-100.00"),
                new BigDecimal("1500.50"),
                "Retiro en ATM",
                "COMPLETADA"
            ));

            logger.info("Historial consultado exitosamente para DNI: {}, total registros: {}", dni, historial.size());
            return ResponseEntity.ok(ApiResponse.success("Historial consultado exitosamente", historial));

        } catch (CuentaException | IllegalArgumentException ex) {
            logger.warn("Error al consultar historial para DNI {}: {}", dni, ex.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(400, ex.getMessage()));
        } catch (Exception ex) {
            logger.error("Error interno al consultar historial para DNI {}: {}", dni, ex.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(500, "Error interno del servidor"));
        }
    }
}