package com.banco.shibasito.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * DTO para elemento del historial de transacciones
 */
@Schema(description = "Transacción en el historial de cuenta")
public class HistorialTransaccionResponse {

    @Schema(description = "ID de la transacción", example = "1")
    private Long transaccionId;

    @Schema(description = "Fecha y hora de la transacción", example = "2025-10-30T08:44:05")
    private LocalDateTime fecha;

    @Schema(description = "Tipo de transacción", example = "RETIRO")
    private String tipoTransaccion;

    @Schema(description = "Monto de la transacción", example = "-50.00")
    private BigDecimal monto;

    @Schema(description = "Saldo después de la transacción", example = "1450.50")
    private BigDecimal saldoPosterior;

    @Schema(description = "Descripción de la transacción", example = "Retiro en ATM")
    private String descripcion;

    @Schema(description = "Estado de la transacción", example = "COMPLETADA")
    private String estado;

    @Schema(description = "Canal de la transacción", example = "ATM")
    private String canal;

    // Constructores
    public HistorialTransaccionResponse() {}

    public HistorialTransaccionResponse(Long transaccionId, LocalDateTime fecha,
                                       String tipoTransaccion, BigDecimal monto,
                                       BigDecimal saldoPosterior, String descripcion, String estado) {
        this.transaccionId = transaccionId;
        this.fecha = fecha;
        this.tipoTransaccion = tipoTransaccion;
        this.monto = monto;
        this.saldoPosterior = saldoPosterior;
        this.descripcion = descripcion;
        this.estado = estado;
    }

    // Getters y Setters
    public Long getTransaccionId() {
        return transaccionId;
    }

    public void setTransaccionId(Long transaccionId) {
        this.transaccionId = transaccionId;
    }

    public LocalDateTime getFecha() {
        return fecha;
    }

    public void setFecha(LocalDateTime fecha) {
        this.fecha = fecha;
    }

    public String getTipoTransaccion() {
        return tipoTransaccion;
    }

    public void setTipoTransaccion(String tipoTransaccion) {
        this.tipoTransaccion = tipoTransaccion;
    }

    public BigDecimal getMonto() {
        return monto;
    }

    public void setMonto(BigDecimal monto) {
        this.monto = monto;
    }

    public BigDecimal getSaldoPosterior() {
        return saldoPosterior;
    }

    public void setSaldoPosterior(BigDecimal saldoPosterior) {
        this.saldoPosterior = saldoPosterior;
    }

    public String getDescripcion() {
        return descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }

    public String getEstado() {
        return estado;
    }

    public void setEstado(String estado) {
        this.estado = estado;
    }

    public String getCanal() {
        return canal;
    }

    public void setCanal(String canal) {
        this.canal = canal;
    }
}