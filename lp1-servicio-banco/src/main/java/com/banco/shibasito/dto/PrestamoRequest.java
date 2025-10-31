package com.banco.shibasito.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;

/**
 * DTO para solicitud de préstamo
 */
@Schema(description = "Solicitud para solicitar un préstamo")
public class PrestamoRequest {

    @NotBlank(message = "El DNI es obligatorio")
    @Size(min = 8, max = 8, message = "El DNI debe tener exactamente 8 dígitos")
    @Schema(description = "Documento Nacional de Identidad del solicitante", example = "12345678", required = true)
    private String dni;

    @NotNull(message = "El monto solicitado es obligatorio")
    @DecimalMin(value = "1000.0", message = "El monto mínimo es 1000.0")
    @Schema(description = "Monto del préstamo solicitado", example = "10000.00", required = true)
    private BigDecimal monto;

    @NotNull(message = "El plazo en meses es obligatorio")
    @Schema(description = "Plazo del préstamo en meses", example = "12", minimum = "1", maximum = "360", required = true)
    private Integer plazoMeses;

    @NotBlank(message = "El tipo de préstamo es obligatorio")
    @Schema(description = "Tipo de préstamo", example = "PERSONAL", 
             allowableValues = {"PERSONAL", "HIPOTECARIO", "VEHICULAR", "EMPRESARIAL", "EDUCATIVO"}, required = true)
    private String tipoPrestamo;

    @Schema(description = "Propósito del préstamo", example = "Compra de electrodomésticos")
    private String proposito;

    @Schema(description = "Ingresos mensuales del solicitante", example = "3500.00")
    private BigDecimal ingresosMensuales;

    @Schema(description = "Lugar de trabajo del solicitante", example = "Empresa ABC S.A.C.")
    private String lugarTrabajo;

    @Schema(description = "ID del cliente", example = "1")
    private Long clienteId;

    @Schema(description = "Tasa de interés", example = "12.5")
    private Double tasaInteres;

    // Constructores
    public PrestamoRequest() {}

    public PrestamoRequest(String dni, BigDecimal monto, Integer plazoMeses, String tipoPrestamo) {
        this.dni = dni;
        this.monto = monto;
        this.plazoMeses = plazoMeses;
        this.tipoPrestamo = tipoPrestamo;
    }

    // Getters y Setters
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

    public String getProposito() {
        return proposito;
    }

    public void setProposito(String proposito) {
        this.proposito = proposito;
    }

    public BigDecimal getIngresosMensuales() {
        return ingresosMensuales;
    }

    public void setIngresosMensuales(BigDecimal ingresosMensuales) {
        this.ingresosMensuales = ingresosMensuales;
    }

    public String getLugarTrabajo() {
        return lugarTrabajo;
    }

    public void setLugarTrabajo(String lugarTrabajo) {
        this.lugarTrabajo = lugarTrabajo;
    }

    public Long getClienteId() {
        return clienteId;
    }

    public void setClienteId(Long clienteId) {
        this.clienteId = clienteId;
    }

    public Double getTasaInteres() {
        return tasaInteres;
    }

    public void setTasaInteres(Double tasaInteres) {
        this.tasaInteres = tasaInteres;
    }
}