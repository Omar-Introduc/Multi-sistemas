package com.banco.shibasito.exception;

/**
 * Excepción personalizada para errores de cuenta bancaria
 */
public class CuentaException extends RuntimeException {

    private final String codigoError;

    public CuentaException(String mensaje) {
        super(mensaje);
        this.codigoError = "CUENTA_ERROR";
    }

    public CuentaException(String mensaje, String codigoError) {
        super(mensaje);
        this.codigoError = codigoError;
    }

    public CuentaException(String mensaje, Throwable causa) {
        super(mensaje, causa);
        this.codigoError = "CUENTA_ERROR";
    }

    public String getCodigoError() {
        return codigoError;
    }
}