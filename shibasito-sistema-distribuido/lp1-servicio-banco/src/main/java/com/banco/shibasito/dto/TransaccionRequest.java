package com.banco.shibasito.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;

/**
 * DTO para solicitud de transacción
 */
@Schema(description = "Solicitud para realizar una transacción")
public class TransaccionRequest {

    @NotBlank(message = "El número de cuenta origen es obligatorio")
    @Schema(description = "Número de cuenta origen", example = "1234567890", required = true)
    private String cuentaOrigen;

    @Schema(description = "Número de cuenta destino (para transferencias)", example = "0987654321")
    private String cuentaDestino;

    @NotNull(message = "El monto es obligatorio")
    @DecimalMin(value = "0.01", message = "El monto debe ser mayor a 0")
    @Schema(description = "Monto de la transacción", example = "100.50", required = true)
    private BigDecimal monto;

    @NotBlank(message = "El tipo de transacción es obligatorio")
    @Schema(description = "Tipo de transacción", example = "RETIRO", 
             allowableValues = {"RETIRO", "DEPOSITO", "TRANSFERENCIA", "PAGO"}, required = true)
    private String tipoTransaccion;

    @Schema(description = "Descripción de la transacción", example = "Retiro de efectivo en ATM")
    private String descripcion;

    @Schema(description = "Canal por donde se realiza la transacción", 
             example = "WEB", allowableValues = {"WEB", "MOBILE", "ATM", "SUCURSAL", "API"})
    private String canal = "WEB";

    // Constructores
    public TransaccionRequest() {}

    public TransaccionRequest(String cuentaOrigen, BigDecimal monto, String tipoTransaccion) {
        this.cuentaOrigen = cuentaOrigen;
        this.monto = monto;
        this.tipoTransaccion = tipoTransaccion;
    }

    public TransaccionRequest(String cuentaOrigen, String cuentaDestino, BigDecimal monto, 
                             String tipoTransaccion, String descripcion) {
        this.cuentaOrigen = cuentaOrigen;
        this.cuentaDestino = cuentaDestino;
        this.monto = monto;
        this.tipoTransaccion = tipoTransaccion;
        this.descripcion = descripcion;
    }

    // Getters y Setters
    public String getCuentaOrigen() {
        return cuentaOrigen;
    }

    public void setCuentaOrigen(String cuentaOrigen) {
        this.cuentaOrigen = cuentaOrigen;
    }

    public String getCuentaDestino() {
        return cuentaDestino;
    }

    public void setCuentaDestino(String cuentaDestino) {
        this.cuentaDestino = cuentaDestino;
    }

    public BigDecimal getMonto() {
        return monto;
    }

    public void setMonto(BigDecimal monto) {
        this.monto = monto;
    }

    public String getTipoTransaccion() {
        return tipoTransaccion;
    }

    public void setTipoTransaccion(String tipoTransaccion) {
        this.tipoTransaccion = tipoTransaccion;
    }

    public String getDescripcion() {
        return descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }

    public String getCanal() {
        return canal;
    }

    public void setCanal(String canal) {
        this.canal = canal;
    }
}