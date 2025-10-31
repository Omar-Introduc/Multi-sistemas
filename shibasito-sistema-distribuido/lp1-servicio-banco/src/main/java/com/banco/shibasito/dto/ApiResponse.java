package com.banco.shibasito.dto;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * DTO para respuesta genérica de API
 */
@Schema(description = "Respuesta estándar de API")
public class ApiResponse<T> {

    @Schema(description = "Código de respuesta", example = "200")
    private int codigo;

    @Schema(description = "Mensaje de respuesta", example = "Operación exitosa")
    private String mensaje;

    @Schema(description = "Datos de respuesta")
    private T data;

    @Schema(description = "Indica si la operación fue exitosa", example = "true")
    private boolean exito;

    @Schema(description = "Timestamp de la respuesta", example = "2025-10-30T08:44:05")
    private String timestamp;

    // Constructores
    public ApiResponse() {
        this.timestamp = java.time.LocalDateTime.now().toString();
    }

    public ApiResponse(int codigo, String mensaje, boolean exito) {
        this.codigo = codigo;
        this.mensaje = mensaje;
        this.exito = exito;
        this.timestamp = java.time.LocalDateTime.now().toString();
    }

    public ApiResponse(int codigo, String mensaje, T data, boolean exito) {
        this.codigo = codigo;
        this.mensaje = mensaje;
        this.data = data;
        this.exito = exito;
        this.timestamp = java.time.LocalDateTime.now().toString();
    }

    // Métodos estáticos para respuestas comunes
    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(200, "Operación exitosa", data, true);
    }

    public static <T> ApiResponse<T> success(String mensaje, T data) {
        return new ApiResponse<>(200, mensaje, data, true);
    }

    public static <T> ApiResponse<T> error(int codigo, String mensaje) {
        return new ApiResponse<>(codigo, mensaje, null, false);
    }

    public static <T> ApiResponse<T> error(int codigo, String mensaje, T data) {
        return new ApiResponse<>(codigo, mensaje, data, false);
    }

    public static <T> ApiResponse<T> error(String mensaje) {
        return new ApiResponse<>(500, mensaje, false);
    }

    // Getters y Setters
    public int getCodigo() {
        return codigo;
    }

    public void setCodigo(int codigo) {
        this.codigo = codigo;
    }

    public String getMensaje() {
        return mensaje;
    }

    public void setMensaje(String mensaje) {
        this.mensaje = mensaje;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }

    public boolean isExito() {
        return exito;
    }

    public void setExito(boolean exito) {
        this.exito = exito;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
}