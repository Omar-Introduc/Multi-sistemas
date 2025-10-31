package com.banco.shibasito.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * DTO para respuesta de transacción
 */
@Schema(description = "Información de transacción bancaria")
public class TransaccionResponse {

    @Schema(description = "ID único de la transacción", example = "1")
    private Long id;

    @Schema(description = "ID único de la transacción", example = "TXN-2025-0001")
    private String transaccionId;

    @Schema(description = "Número de cuenta origen", example = "1234567890")
    private String cuentaOrigen;

    @Schema(description = "Número de cuenta destino", example = "0987654321")
    private String cuentaDestino;

    @Schema(description = "Monto de la transacción", example = "100.50")
    private BigDecimal monto;

    @Schema(description = "Tipo de transacción", example = "RETIRO")
    private String tipoTransaccion;

    @Schema(description = "Descripción de la transacción", example = "Retiro de efectivo en ATM")
    private String descripcion;

    @Schema(description = "Estado de la transacción", example = "COMPLETADA")
    private String estado;

    @Schema(description = "Moneda de la transacción", example = "PEN")
    private String moneda;

    @Schema(description = "Fecha y hora de la transacción", example = "2025-10-30T08:44:05")
    private LocalDateTime fechaTransaccion;

    @Schema(description = "Saldo anterior de la cuenta", example = "1600.50")
    private BigDecimal saldoAnterior;

    @Schema(description = "Saldo posterior de la cuenta", example = "1500.00")
    private BigDecimal saldoPosterior;

    @Schema(description = "Código de autorización", example = "AUTH-123456")
    private String codigoAutorizacion;

    @Schema(description = "Canal de la transacción", example = "ATM")
    private String canal;

    // Constructores
    public TransaccionResponse() {}

    public TransaccionResponse(String transaccionId, String cuentaOrigen, BigDecimal monto, 
                              String tipoTransaccion, String estado, String moneda) {
        this.transaccionId = transaccionId;
        this.cuentaOrigen = cuentaOrigen;
        this.monto = monto;
        this.tipoTransaccion = tipoTransaccion;
        this.estado = estado;
        this.moneda = moneda;
        this.fechaTransaccion = LocalDateTime.now();
    }

    // Getters y Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTransaccionId() {
        return transaccionId;
    }

    public void setTransaccionId(String transaccionId) {
        this.transaccionId = transaccionId;
    }

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

    public String getEstado() {
        return estado;
    }

    public void setEstado(String estado) {
        this.estado = estado;
    }

    public String getMoneda() {
        return moneda;
    }

    public void setMoneda(String moneda) {
        this.moneda = moneda;
    }

    public LocalDateTime getFechaTransaccion() {
        return fechaTransaccion;
    }

    public void setFechaTransaccion(LocalDateTime fechaTransaccion) {
        this.fechaTransaccion = fechaTransaccion;
    }

    public BigDecimal getSaldoAnterior() {
        return saldoAnterior;
    }

    public void setSaldoAnterior(BigDecimal saldoAnterior) {
        this.saldoAnterior = saldoAnterior;
    }

    public BigDecimal getSaldoPosterior() {
        return saldoPosterior;
    }

    public void setSaldoPosterior(BigDecimal saldoPosterior) {
        this.saldoPosterior = saldoPosterior;
    }

    public String getCodigoAutorizacion() {
        return codigoAutorizacion;
    }

    public void setCodigoAutorizacion(String codigoAutorizacion) {
        this.codigoAutorizacion = codigoAutorizacion;
    }

    public String getCanal() {
        return canal;
    }

    public void setCanal(String canal) {
        this.canal = canal;
    }
}