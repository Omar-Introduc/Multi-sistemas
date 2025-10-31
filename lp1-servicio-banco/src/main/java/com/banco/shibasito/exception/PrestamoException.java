package com.banco.shibasito.exception;

/**
 * Excepción personalizada para errores de préstamo bancario
 */
public class PrestamoException extends RuntimeException {

    private final String codigoError;

    public PrestamoException(String mensaje) {
        super(mensaje);
        this.codigoError = "PRESTAMO_ERROR";
    }

    public PrestamoException(String mensaje, String codigoError) {
        super(mensaje);
        this.codigoError = codigoError;
    }

    public PrestamoException(String mensaje, Throwable causa) {
        super(mensaje, causa);
        this.codigoError = "PRESTAMO_ERROR";
    }

    public String getCodigoError() {
        return codigoError;
    }
}