package com.banco.shibasito.controller;

import com.banco.shibasito.dto.*;
import com.banco.shibasito.exception.TransaccionException;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Controlador REST para operaciones de transacciones bancarias
 */
@Tag(name = "Transacción", description = "Operaciones relacionadas con transacciones bancarias")
@RestController
@RequestMapping("/api/transacciones")
@CrossOrigin(origins = "*", maxAge = 3600)
public class TransaccionController {

    private static final Logger logger = LoggerFactory.getLogger(TransaccionController.class);

    /**
     * Procesa una nueva transacción bancaria
     */
    @Operation(
        summary = "Procesar transacción",
        description = "Permite procesar una nueva transacción bancaria (retiro, depósito, transferencia, etc.)"
    )
    @ApiResponse(responseCode = "201", description = "Transacción procesada exitosamente")
    @ApiResponse(responseCode = "400", description = "Datos de entrada inválidos o fondos insuficientes")
    @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    @PostMapping
    public ResponseEntity<ApiResponse<TransaccionResponse>> procesarTransaccion(
            @Parameter(description = "Datos de la transacción a procesar", required = true)
            @Valid @RequestBody TransaccionRequest request) {
        
        logger.info("Procesando transacción - Cuenta origen: {}, Tipo: {}, Monto: {}", 
                   request.getCuentaOrigen(), request.getTipoTransaccion(), request.getMonto());
        
        try {
            // Validaciones básicas
            validarTransaccionRequest(request);

            // Simular procesamiento de transacción
            String transaccionId = generarIdTransaccion();
            BigDecimal saldoAnterior = new BigDecimal("1600.50");
            BigDecimal saldoPosterior = saldoAnterior.subtract(request.getMonto());
            
            // Simulación de lógica de negocio
            if ("RETIRO".equals(request.getTipoTransaccion()) && 
                request.getMonto().compareTo(saldoAnterior) > 0) {
                throw new TransaccionException("Fondos insuficientes para realizar el retiro");
            }

            // Crear respuesta
            TransaccionResponse response = new TransaccionResponse(
                transaccionId,
                request.getCuentaOrigen(),
                request.getMonto(),
                request.getTipoTransaccion(),
                "COMPLETADA",
                "PEN"
            );
            response.setDescripcion(request.getDescripcion());
            response.setCuentaDestino(request.getCuentaDestino());
            response.setFechaTransaccion(LocalDateTime.now());
            response.setSaldoAnterior(saldoAnterior);
            response.setSaldoPosterior(saldoPosterior);
            response.setCodigoAutorizacion(generarCodigoAutorizacion());

            logger.info("Transacción procesada exitosamente - ID: {}, Saldo posterior: {}", 
                       transaccionId, saldoPosterior);
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(ApiResponse.success("Transacción procesada exitosamente", response));

        } catch (TransaccionException | IllegalArgumentException ex) {
            logger.warn("Error al procesar transacción: {}", ex.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(400, ex.getMessage()));
        } catch (Exception ex) {
            logger.error("Error interno al procesar transacción: {}", ex.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(500, "Error interno del servidor"));
        }
    }

    /**
     * Consulta una transacción por su ID
     */
    @Operation(
        summary = "Consultar transacción",
        description = "Permite consultar los detalles de una transacción específica mediante su ID"
    )
    @ApiResponse(responseCode = "200", description = "Transacción consultada exitosamente")
    @ApiResponse(responseCode = "400", description = "ID de transacción inválido")
    @ApiResponse(responseCode = "404", description = "Transacción no encontrada")
    @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<TransaccionResponse>> consultarTransaccion(
            @Parameter(description = "ID único de la transacción", example = "TXN-2025-0001", required = true)
            @PathVariable String id) {
        
        logger.info("Consultando transacción con ID: {}", id);
        
        try {
            // Validar ID de transacción
            if (id == null || id.trim().isEmpty()) {
                throw new IllegalArgumentException("El ID de transacción es obligatorio");
            }

            if (!id.startsWith("TXN-")) {
                throw new IllegalArgumentException("Formato de ID de transacción inválido");
            }

            // Simulación de consulta de transacción
            if (!"TXN-2025-0001".equals(id)) {
                throw new TransaccionException("Transacción no encontrada", "TRANSACCION_NOT_FOUND");
            }

            TransaccionResponse response = new TransaccionResponse(
                id,
                "1234567890",
                new BigDecimal("100.00"),
                "RETIRO",
                "COMPLETADA",
                "PEN"
            );
            response.setDescripcion("Retiro en ATM");
            response.setFechaTransaccion(LocalDateTime.now().minusMinutes(30));
            response.setSaldoAnterior(new BigDecimal("1600.50"));
            response.setSaldoPosterior(new BigDecimal("1500.50"));
            response.setCodigoAutorizacion("AUTH-789123");
            response.setCanal("ATM");

            logger.info("Transacción consultada exitosamente - ID: {}", id);
            return ResponseEntity.ok(ApiResponse.success("Transacción consultada exitosamente", response));

        } catch (TransaccionException ex) {
            if ("TRANSACCION_NOT_FOUND".equals(ex.getCodigoError())) {
                logger.warn("Transacción no encontrada: {}", id);
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(ApiResponse.error(404, ex.getMessage()));
            } else {
                logger.warn("Error al consultar transacción: {}", ex.getMessage());
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body(ApiResponse.error(400, ex.getMessage()));
            }
        } catch (IllegalArgumentException ex) {
            logger.warn("Error de validación al consultar transacción: {}", ex.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(400, ex.getMessage()));
        } catch (Exception ex) {
            logger.error("Error interno al consultar transacción: {}", ex.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(500, "Error interno del servidor"));
        }
    }

    /**
     * Valida los datos de entrada de una transacción
     */
    private void validarTransaccionRequest(TransaccionRequest request) {
        if (request.getMonto().compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("El monto debe ser mayor a cero");
        }

        if (request.getMonto().compareTo(new BigDecimal("10000")) > 0) {
            throw new IllegalArgumentException("El monto no puede exceder 10,000.00");
        }

        if ("TRANSFERENCIA".equals(request.getTipoTransaccion())) {
            if (request.getCuentaDestino() == null || request.getCuentaDestino().trim().isEmpty()) {
                throw new IllegalArgumentException("La cuenta destino es requerida para transferencias");
            }
            if (request.getCuentaDestino().equals(request.getCuentaOrigen())) {
                throw new IllegalArgumentException("La cuenta origen y destino deben ser diferentes");
            }
        }
    }

    /**
     * Genera un ID único para la transacción
     */
    private String generarIdTransaccion() {
        return "TXN-" + LocalDateTime.now().getYear() + "-" + 
               String.format("%04d", (int)(Math.random() * 10000));
    }

    /**
     * Genera un código de autorización
     */
    private String generarCodigoAutorizacion() {
        return "AUTH-" + String.format("%06d", (int)(Math.random() * 1000000));
    }
}