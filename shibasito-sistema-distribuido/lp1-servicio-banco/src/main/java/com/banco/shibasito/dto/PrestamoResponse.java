package com.banco.shibasito.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * DTO para respuesta de préstamo
 */
@Schema(description = "Información de préstamo bancario")
public class PrestamoResponse {

    @Schema(description = "ID único del préstamo", example = "PRST-2025-0001")
    private String prestamoId;

    @Schema(description = "DNI del solicitante", example = "12345678")
    private String dni;

    @Schema(description = "Monto aprobado del préstamo", example = "10000.00")
    private BigDecimal monto;

    @Schema(description = "Plazo del préstamo en meses", example = "12")
    private Integer plazoMeses;

    @Schema(description = "Tipo de préstamo", example = "PERSONAL")
    private String tipoPrestamo;

    @Schema(description = "Tasa de interés anual", example = "18.5")
    private BigDecimal tasaInteres;

    @Schema(description = "Estado del préstamo", example = "APROBADO")
    private String estado;

    @Schema(description = "Cuota mensual", example = "920.33")
    private BigDecimal cuotaMensual;

    @Schema(description = "Fecha de aprobación", example = "2025-10-30")
    private LocalDate fechaAprobacion;

    @Schema(description = "Fecha de vencimiento", example = "2026-10-30")
    private LocalDate fechaVencimiento;

    @Schema(description = "Capital pendiente", example = "9500.00")
    private BigDecimal capitalPendiente;

    @Schema(description = "Intereses pendientes", example = "150.00")
    private BigDecimal interesesPendientes;

    @Schema(description = "Monto total a pagar", example = "11040.00")
    private BigDecimal montoTotal;

    @Schema(description = "Propósito del préstamo", example = "Compra de electrodomésticos")
    private String proposito;

    // Constructores
    public PrestamoResponse() {}

    public PrestamoResponse(String prestamoId, String dni, BigDecimal monto, Integer plazoMeses, 
                           String tipoPrestamo, String estado) {
        this.prestamoId = prestamoId;
        this.dni = dni;
        this.monto = monto;
        this.plazoMeses = plazoMeses;
        this.tipoPrestamo = tipoPrestamo;
        this.estado = estado;
        this.fechaAprobacion = LocalDate.now();
    }

    // Getters y Setters
    public String getPrestamoId() {
        return prestamoId;
    }

    public void setPrestamoId(String prestamoId) {
        this.prestamoId = prestamoId;
    }

    public String getDni() {
        return dni;
    }

    public void setDni(String dni) {
        this.dni = dni;
    }

    public BigDecimal getMonto() {
        return monto;
    }

    public void setMonto(BigDecimal monto) {
        this.monto = monto;
    }

    public Integer getPlazoMeses() {
        return plazoMeses;
    }

    public void setPlazoMeses(Integer plazoMeses) {
        this.plazoMeses = plazoMeses;
    }

    public String getTipoPrestamo() {
        return tipoPrestamo;
    }

    public void setTipoPrestamo(String tipoPrestamo) {
        this.tipoPrestamo = tipoPrestamo;
    }

    public BigDecimal getTasaInteres() {
        return tasaInteres;
    }

    public void setTasaInteres(BigDecimal tasaInteres) {
        this.tasaInteres = tasaInteres;
    }

    public String getEstado() {
        return estado;
    }

    public void setEstado(String estado) {
        this.estado = estado;
    }

    public BigDecimal getCuotaMensual() {
        return cuotaMensual;
    }

    public void setCuotaMensual(BigDecimal cuotaMensual) {
        this.cuotaMensual = cuotaMensual;
    }

    public LocalDate getFechaAprobacion() {
        return fechaAprobacion;
    }

    public void setFechaAprobacion(LocalDate fechaAprobacion) {
        this.fechaAprobacion = fechaAprobacion;
    }

    public LocalDate getFechaVencimiento() {
        return fechaVencimiento;
    }

    public void setFechaVencimiento(LocalDate fechaVencimiento) {
        this.fechaVencimiento = fechaVencimiento;
    }

    public BigDecimal getCapitalPendiente() {
        return capitalPendiente;
    }

    public void setCapitalPendiente(BigDecimal capitalPendiente) {
        this.capitalPendiente = capitalPendiente;
    }

    public BigDecimal getInteresesPendientes() {
        return interesesPendientes;
    }

    public void setInteresesPendientes(BigDecimal interesesPendientes) {
        this.interesesPendientes = interesesPendientes;
    }

    public BigDecimal getMontoTotal() {
        return montoTotal;
    }

    public void setMontoTotal(BigDecimal montoTotal) {
        this.montoTotal = montoTotal;
    }

    public String getProposito() {
        return proposito;
    }

    public void setProposito(String proposito) {
        this.proposito = proposito;
    }
}