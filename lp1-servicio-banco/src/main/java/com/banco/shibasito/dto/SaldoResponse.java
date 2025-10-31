package com.banco.shibasito.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.math.BigDecimal;

/**
 * DTO para respuesta de saldo de cuenta
 */
@Schema(description = "Saldo de cuenta bancaria")
public class SaldoResponse {

    @Schema(description = "Número de cuenta", example = "1234567890")
    private String numeroCuenta;

    @Schema(description = "DNI del titular", example = "12345678")
    private String dni;

    @Schema(description = "Saldo disponible", example = "1500.50")
    private BigDecimal saldo;

    @Schema(description = "Saldo disponible para retiros", example = "1500.50")
    private BigDecimal saldoDisponible;

    @Schema(description = "Moneda de la cuenta", example = "PEN")
    private String moneda;

    @Schema(description = "Fecha y hora de consulta", example = "2025-10-30T08:44:05")
    private String fechaConsulta;

    // Constructores
    public SaldoResponse() {}

    public SaldoResponse(String numeroCuenta, String dni, BigDecimal saldo, String moneda) {
        this.numeroCuenta = numeroCuenta;
        this.dni = dni;
        this.saldo = saldo;
        this.saldoDisponible = saldo; // Por ahora igual al saldo
        this.moneda = moneda;
        this.fechaConsulta = java.time.LocalDateTime.now().toString();
    }

    // Getters y Setters
    public String getNumeroCuenta() {
        return numeroCuenta;
    }

    public void setNumeroCuenta(String numeroCuenta) {
        this.numeroCuenta = numeroCuenta;
    }

    public String getDni() {
        return dni;
    }

    public void setDni(String dni) {
        this.dni = dni;
    }

    public BigDecimal getSaldo() {
        return saldo;
    }

    public void setSaldo(BigDecimal saldo) {
        this.saldo = saldo;
    }

    public BigDecimal getSaldoDisponible() {
        return saldoDisponible;
    }

    public void setSaldoDisponible(BigDecimal saldoDisponible) {
        this.saldoDisponible = saldoDisponible;
    }

    public String getMoneda() {
        return moneda;
    }

    public void setMoneda(String moneda) {
        this.moneda = moneda;
    }

    public String getFechaConsulta() {
        return fechaConsulta;
    }

    public void setFechaConsulta(String fechaConsulta) {
        this.fechaConsulta = fechaConsulta;
    }
}