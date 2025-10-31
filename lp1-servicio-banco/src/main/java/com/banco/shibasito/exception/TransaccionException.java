package com.banco.shibasito.exception;

/**
 * Excepción personalizada para errores de transacción bancaria
 */
public class TransaccionException extends RuntimeException {

    private final String codigoError;

    public TransaccionException(String mensaje) {
        super(mensaje);
        this.codigoError = "TRANSACCION_ERROR";
    }

    public TransaccionException(String mensaje, String codigoError) {
        super(mensaje);
        this.codigoError = codigoError;
    }

    public TransaccionException(String mensaje, Throwable causa) {
        super(mensaje, causa);
        this.codigoError = "TRANSACCION_ERROR";
    }

    public String getCodigoError() {
        return codigoError;
    }
}