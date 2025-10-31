package com.banco.shibasito.exception;

import com.banco.shibasito.dto.ApiResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;

import java.util.HashMap;
import java.util.Map;

/**
 * Controlador global para manejo de excepciones
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /**
     * Maneja errores de validación de argumentos
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Map<String, String>>> handleValidationExceptions(
            MethodArgumentNotValidException ex) {
        logger.warn("Error de validación: {}", ex.getMessage());
        
        Map<String, String> errores = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach((error) -> {
            String fieldName = ((FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            errores.put(fieldName, errorMessage);
        });

        ApiResponse<Map<String, String>> response = ApiResponse.error(400, "Errores de validación");
        response.setData(errores);
        
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Maneja errores de cuenta
     */
    @ExceptionHandler(CuentaException.class)
    public ResponseEntity<ApiResponse<Void>> handleCuentaException(CuentaException ex, WebRequest request) {
        logger.error("Error de cuenta: {}", ex.getMessage(), ex);
        
        ApiResponse<Void> response = ApiResponse.error(400, ex.getMessage());
        
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Maneja errores de transacción
     */
    @ExceptionHandler(TransaccionException.class)
    public ResponseEntity<ApiResponse<Void>> handleTransaccionException(TransaccionException ex, WebRequest request) {
        logger.error("Error de transacción: {}", ex.getMessage(), ex);
        
        ApiResponse<Void> response = ApiResponse.error(400, ex.getMessage());
        
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Maneja errores de préstamo
     */
    @ExceptionHandler(PrestamoException.class)
    public ResponseEntity<ApiResponse<Void>> handlePrestamoException(PrestamoException ex, WebRequest request) {
        logger.error("Error de préstamo: {}", ex.getMessage(), ex);
        
        ApiResponse<Void> response = ApiResponse.error(400, ex.getMessage());
        
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Maneja errores de argumentos ilegales
     */
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ApiResponse<Void>> handleIllegalArgumentException(IllegalArgumentException ex) {
        logger.warn("Argumento ilegal: {}", ex.getMessage());
        
        ApiResponse<Void> response = ApiResponse.error(400, ex.getMessage());
        
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * Maneja cualquier otra excepción no controlada
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGenericException(Exception ex, WebRequest request) {
        logger.error("Error interno del servidor: {}", ex.getMessage(), ex);
        
        ApiResponse<Void> response = ApiResponse.error(500, "Error interno del servidor");
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
    }
}