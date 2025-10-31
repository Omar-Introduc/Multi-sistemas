package com.banco.shibasito.dto;

public class Response<T> {
    private boolean success;
    private String message;
    private T data;
    private String errorCode;

    public Response() {
    }

    public Response(boolean success, String message) {
        this.success = success;
        this.message = message;
    }

    public Response(boolean success, String message, T data) {
        this.success = success;
        this.message = message;
        this.data = data;
    }

    public Response(boolean success, String message, String errorCode) {
        this.success = success;
        this.message = message;
        this.errorCode = errorCode;
    }

    // Métodos utilitarios
    public static <T> Response<T> success(T data) {
        return new Response<>(true, "Operación exitosa", data);
    }

    public static <T> Response<T> success(String message, T data) {
        return new Response<>(true, message, data);
    }

    public static <T> Response<T> success(String message) {
        return new Response<>(true, message);
    }

    public static <T> Response<T> error(String message) {
        return new Response<>(false, message);
    }

    public static <T> Response<T> error(String message, String errorCode) {
        return new Response<>(false, message, errorCode);
    }

    // Getters y Setters
    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public T getData() { return data; }
    public void setData(T data) { this.data = data; }

    public String getErrorCode() { return errorCode; }
    public void setErrorCode(String errorCode) { this.errorCode = errorCode; }
}