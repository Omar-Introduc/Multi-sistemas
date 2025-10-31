package com.banco.shibasito.controller;

import com.banco.shibasito.dto.*;
import com.banco.shibasito.exception.PrestamoException;
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
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Controlador REST para operaciones de préstamos bancarios
 */
@Tag(name = "Préstamo", description = "Operaciones relacionadas con préstamos bancarios")
@RestController
@RequestMapping("/api/prestamos")
@CrossOrigin(origins = "*", maxAge = 3600)
public class PrestamoController {

    private static final Logger logger = LoggerFactory.getLogger(PrestamoController.class);

    /**
     * Solicita un nuevo préstamo bancario
     */
    @Operation(
        summary = "Solicitar préstamo",
        description = "Permite solicitar un nuevo préstamo bancario con los datos proporcionados"
    )
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "201", description = "Préstamo solicitado exitosamente")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Datos de entrada inválidos o solicitud no aprobada")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Error interno del servidor")
    @PostMapping("/solicitar")
    public ResponseEntity<ApiResponse<PrestamoResponse>> solicitarPrestamo(
            @Parameter(description = "Datos de la solicitud de préstamo", required = true)
            @Valid @RequestBody PrestamoRequest request) {
        
        logger.info("Solicitando préstamo - DNI: {}, Monto: {}, Tipo: {}", 
                   request.getDni(), request.getMonto(), request.getTipoPrestamo());
        
        try {
            // Validar solicitud
            validarSolicitudPrestamo(request);

            // Simular evaluación de crédito
            boolean aprobado = evaluarCredito(request);
            
            if (!aprobado) {
                throw new PrestamoException("Solicitud de préstamo no aprobada. Verifique sus datos e intente nuevamente.");
            }

            // Calcular parámetros del préstamo
            BigDecimal tasaInteres = calcularTasaInteres(request.getTipoPrestamo());
            BigDecimal cuotaMensual = calcularCuotaMensual(request.getMonto(), tasaInteres, request.getPlazoMeses());
            BigDecimal montoTotal = cuotaMensual.multiply(new BigDecimal(request.getPlazoMeses()));
            
            // Crear respuesta
            PrestamoResponse response = new PrestamoResponse(
                generarIdPrestamo(),
                request.getDni(),
                request.getMonto(),
                request.getPlazoMeses(),
                request.getTipoPrestamo(),
                "APROBADO"
            );
            response.setTasaInteres(tasaInteres);
            response.setCuotaMensual(cuotaMensual);
            response.setFechaAprobacion(LocalDate.now());
            response.setFechaVencimiento(LocalDate.now().plusMonths(request.getPlazoMeses()));
            response.setCapitalPendiente(request.getMonto());
            response.setInteresesPendientes(montoTotal.subtract(request.getMonto()));
            response.setMontoTotal(montoTotal);
            response.setProposito(request.getProposito());

            logger.info("Préstamo aprobado exitosamente - ID: {}, Cuota mensual: {}", 
                       response.getPrestamoId(), response.getCuotaMensual());
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(ApiResponse.success("Préstamo aprobado exitosamente", response));

        } catch (PrestamoException | IllegalArgumentException ex) {
            logger.warn("Error al solicitar préstamo: {}", ex.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(400, ex.getMessage()));
        } catch (Exception ex) {
            logger.error("Error interno al solicitar préstamo: {}", ex.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(500, "Error interno del servidor"));
        }
    }

    /**
     * Consulta los préstamos de un cliente por DNI
     */
    @Operation(
        summary = "Consultar préstamos",
        description = "Permite consultar todos los préstamos asociados a un cliente mediante su DNI"
    )
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Préstamos consultados exitosamente")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "DNI inválido")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "No se encontraron préstamos para el DNI proporcionado")
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Error interno del servidor")
    @GetMapping("/{dni}")
    public ResponseEntity<ApiResponse<List<PrestamoResponse>>> consultarPrestamos(
            @Parameter(description = "Documento Nacional de Identidad del cliente", example = "12345678", required = true)
            @PathVariable String dni) {
        
        logger.info("Consultando préstamos para DNI: {}", dni);
        
        try {
            // Validar DNI
            if (dni == null || dni.trim().isEmpty() || dni.length() != 8 || !dni.matches("\\d+")) {
                throw new IllegalArgumentException("DNI inválido. Debe contener exactamente 8 dígitos.");
            }

            // Simulación de consulta de préstamos
            List<PrestamoResponse> prestamos = new ArrayList<>();
            
            // Agregar préstamo de ejemplo si es el DNI esperado
            if ("12345678".equals(dni)) {
                prestamos.add(crearPrestamoEjemplo("PRST-2025-0001", dni));
                prestamos.add(crearPrestamoEjemplo("PRST-2025-0002", dni));
            }

            if (prestamos.isEmpty()) {
                throw new PrestamoException("No se encontraron préstamos para el DNI proporcionado", "PRESTAMOS_NOT_FOUND");
            }

            logger.info("Préstamos consultados exitosamente para DNI: {}, total: {}", dni, prestamos.size());
            return ResponseEntity.ok(ApiResponse.success("Préstamos consultados exitosamente", prestamos));

        } catch (PrestamoException ex) {
            if ("PRESTAMOS_NOT_FOUND".equals(ex.getCodigoError())) {
                logger.warn("No se encontraron préstamos para DNI: {}", dni);
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(ApiResponse.error(404, ex.getMessage()));
            } else {
                logger.warn("Error al consultar préstamos: {}", ex.getMessage());
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body(ApiResponse.error(400, ex.getMessage()));
            }
        } catch (IllegalArgumentException ex) {
            logger.warn("Error de validación al consultar préstamos: {}", ex.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(400, ex.getMessage()));
        } catch (Exception ex) {
            logger.error("Error interno al consultar préstamos: {}", ex.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error(500, "Error interno del servidor"));
        }
    }

    /**
     * Valida los datos de la solicitud de préstamo
     */
    private void validarSolicitudPrestamo(PrestamoRequest request) {
        if (request.getMonto().compareTo(new BigDecimal("50000")) > 0) {
            throw new IllegalArgumentException("El monto máximo permitido es 50,000.00");
        }

        if (request.getPlazoMeses() > 360) {
            throw new IllegalArgumentException("El plazo máximo permitido es 360 meses (30 años)");
        }

        if (request.getPlazoMeses() < 6) {
            throw new IllegalArgumentException("El plazo mínimo permitido es 6 meses");
        }
    }

    /**
     * Simula una evaluación de crédito básica
     */
    private boolean evaluarCredito(PrestamoRequest request) {
        // Lógica básica de evaluación
        if (request.getIngresosMensuales() == null) {
            return false; // Requiere información de ingresos
        }

        BigDecimal cuotaEstimada = calcularCuotaMensual(request.getMonto(), 
                                                       calcularTasaInteres(request.getTipoPrestamo()), 
                                                       request.getPlazoMeses());
        
        // El monto de la cuota no debe exceder el 30% de los ingresos
        BigDecimal porcentajeCuota = cuotaEstimada.multiply(new BigDecimal("100"))
                                                  .divide(request.getIngresosMensuales(), 2, BigDecimal.ROUND_HALF_UP);
        
        return porcentajeCuota.compareTo(new BigDecimal("30")) <= 0;
    }

    /**
     * Calcula la tasa de interés según el tipo de préstamo
     */
    private BigDecimal calcularTasaInteres(String tipoPrestamo) {
        return switch (tipoPrestamo.toUpperCase()) {
            case "PERSONAL" -> new BigDecimal("18.5");
            case "VEHICULAR" -> new BigDecimal("16.0");
            case "HIPOTECARIO" -> new BigDecimal("12.5");
            case "EMPRESARIAL" -> new BigDecimal("20.0");
            case "EDUCATIVO" -> new BigDecimal("15.0");
            default -> new BigDecimal("19.0");
        };
    }

    /**
     * Calcula la cuota mensual del préstamo
     */
    private BigDecimal calcularCuotaMensual(BigDecimal monto, BigDecimal tasaInteres, Integer plazoMeses) {
        BigDecimal tasaMensual = tasaInteres.divide(new BigDecimal("100"), 6, BigDecimal.ROUND_HALF_UP)
                                          .divide(new BigDecimal("12"), 6, BigDecimal.ROUND_HALF_UP);
        
        if (tasaMensual.compareTo(BigDecimal.ZERO) == 0) {
            return monto.divide(new BigDecimal(plazoMeses), 2, BigDecimal.ROUND_HALF_UP);
        }
        
        BigDecimal factor = BigDecimal.ONE.add(tasaMensual).pow(plazoMeses);
        BigDecimal cuota = monto.multiply(tasaMensual).multiply(factor)
                               .divide(factor.subtract(BigDecimal.ONE), 2, BigDecimal.ROUND_HALF_UP);
        
        return cuota;
    }

    /**
     * Genera un ID único para el préstamo
     */
    private String generarIdPrestamo() {
        return "PRST-" + LocalDateTime.now().getYear() + "-" + 
               String.format("%04d", (int)(Math.random() * 10000));
    }

    /**
     * Crea un préstamo de ejemplo
     */
    private PrestamoResponse crearPrestamoEjemplo(String id, String dni) {
        PrestamoResponse prestamo = new PrestamoResponse(id, dni, new BigDecimal("15000.00"), 
                                                        24, "PERSONAL", "ACTIVO");
        prestamo.setTasaInteres(new BigDecimal("18.5"));
        prestamo.setCuotaMensual(new BigDecimal("750.25"));
        prestamo.setFechaAprobacion(LocalDate.now().minusMonths(6));
        prestamo.setFechaVencimiento(LocalDate.now().plusMonths(18));
        prestamo.setCapitalPendiente(new BigDecimal("9000.00"));
        prestamo.setInteresesPendientes(new BigDecimal("450.00"));
        prestamo.setMontoTotal(new BigDecimal("18006.00"));
        prestamo.setProposito("Consolidación de deudas");
        
        return prestamo;
    }
}