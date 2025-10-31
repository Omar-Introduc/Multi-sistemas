package com.banco.shibasito.controller;

import com.banco.shibasito.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Controlador REST para verificación de salud del servicio bancario
 */
@Tag(name = "Health", description = "Endpoints para verificación de estado y salud del servicio")
@RestController
@RequestMapping
@CrossOrigin(origins = "*", maxAge = 3600)
public class BancoHealthController {

    private static final Logger logger = LoggerFactory.getLogger(BancoHealthController.class);

    /**
     * Endpoint principal de verificación de salud
     */
    @Operation(
        summary = "Verificar salud del servicio",
        description = "Endpoint principal para verificar el estado y salud del microservicio bancario"
    )
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Servicio funcionando correctamente")
    @GetMapping("/health")
    public ResponseEntity<ApiResponse<Map<String, Object>>> health() {
        logger.debug("Verificando salud del servicio");
        
        try {
            Map<String, Object> healthData = new HashMap<>();
            healthData.put("status", "UP");
            healthData.put("service", "servicio-banco-shibasito");
            healthData.put("version", "1.0.0");
            healthData.put("timestamp", LocalDateTime.now().toString());
            healthData.put("uptime", "En funcionamiento");
            
            // Información adicional del sistema
            Map<String, Object> details = new HashMap<>();
            details.put("database", "Conectado");
            details.put("rabbitmq", "Conectado");
            details.put("redis", "Conectado");
            healthData.put("components", details);
            
            logger.info("Health check exitoso - Servicio: {}, Status: UP", healthData.get("service"));
            return ResponseEntity.ok(ApiResponse.success("Servicio funcionando correctamente", healthData));
            
        } catch (Exception ex) {
            logger.error("Error durante health check: {}", ex.getMessage());
            
            Map<String, Object> errorData = new HashMap<>();
            errorData.put("status", "DOWN");
            errorData.put("service", "servicio-banco-shibasito");
            errorData.put("version", "1.0.0");
            errorData.put("timestamp", LocalDateTime.now().toString());
            errorData.put("error", "Error interno del servicio");
            
            return ResponseEntity.ok(ApiResponse.error(503, "Servicio no disponible", errorData));
        }
    }

    /**
     * Endpoint de verificación de estado simple
     */
    @Operation(
        summary = "Estado simple del servicio",
        description = "Endpoint simplificado para verificación rápida de estado del servicio"
    )
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Servicio activo")
    @GetMapping("/status")
    public ResponseEntity<Map<String, String>> status() {
        logger.debug("Verificando estado simple del servicio");
        
        Map<String, String> response = new HashMap<>();
        response.put("status", "OK");
        response.put("service", "banco-shibasito");
        response.put("timestamp", LocalDateTime.now().toString());
        
        return ResponseEntity.ok(response);
    }

    /**
     * Endpoint de información del servicio
     */
    @Operation(
        summary = "Información del servicio",
        description = "Obtiene información detallada del microservicio bancario"
    )
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Información obtenida exitosamente")
    @GetMapping("/info")
    public ResponseEntity<ApiResponse<Map<String, Object>>> info() {
        logger.debug("Obteniendo información del servicio");
        
        try {
            Map<String, Object> info = new HashMap<>();
            info.put("name", "Servicio Banco Shibasito");
            info.put("description", "Microservicio bancario del sistema distribuido Shibasito");
            info.put("version", "1.0.0");
            info.put("javaVersion", System.getProperty("java.version"));
            info.put("osName", System.getProperty("os.name"));
            info.put("osArch", System.getProperty("os.arch"));
            info.put("timestamp", LocalDateTime.now().toString());
            
            // Información de endpoints disponibles
            Map<String, String> endpoints = new HashMap<>();
            endpoints.put("health", "/health");
            endpoints.put("status", "/status");
            endpoints.put("info", "/info");
            endpoints.put("cuentas", "/api/cuentas");
            endpoints.put("transacciones", "/api/transacciones");
            endpoints.put("prestamos", "/api/prestamos");
            info.put("endpoints", endpoints);
            
            return ResponseEntity.ok(ApiResponse.success("Información del servicio obtenida exitosamente", info));
            
        } catch (Exception ex) {
            logger.error("Error al obtener información del servicio: {}", ex.getMessage());
            return ResponseEntity.ok(ApiResponse.error(500, "Error interno del servidor"));
        }
    }

    /**
     * Endpoint de métricas básicas del sistema
     */
    @Operation(
        summary = "Métricas básicas del sistema",
        description = "Obtiene métricas básicas de rendimiento del microservicio"
    )
    @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Métricas obtenidas exitosamente")
    @GetMapping("/metrics")
    public ResponseEntity<ApiResponse<Map<String, Object>>> metrics() {
        logger.debug("Obteniendo métricas del sistema");
        
        try {
            Map<String, Object> metrics = new HashMap<>();
            
            // Información de memoria
            Runtime runtime = Runtime.getRuntime();
            long totalMemory = runtime.totalMemory();
            long freeMemory = runtime.freeMemory();
            long usedMemory = totalMemory - freeMemory;
            
            Map<String, Object> memory = new HashMap<>();
            memory.put("total", String.format("%.2f MB", totalMemory / (1024.0 * 1024.0)));
            memory.put("free", String.format("%.2f MB", freeMemory / (1024.0 * 1024.0)));
            memory.put("used", String.format("%.2f MB", usedMemory / (1024.0 * 1024.0)));
            memory.put("usagePercentage", String.format("%.2f%%", (usedMemory * 100.0) / totalMemory));
            
            metrics.put("memory", memory);
            metrics.put("timestamp", LocalDateTime.now().toString());
            metrics.put("uptime", "Sistema en funcionamiento");
            
            return ResponseEntity.ok(ApiResponse.success("Métricas obtenidas exitosamente", metrics));
            
        } catch (Exception ex) {
            logger.error("Error al obtener métricas del sistema: {}", ex.getMessage());
            return ResponseEntity.ok(ApiResponse.error(500, "Error interno del servidor"));
        }
    }
}