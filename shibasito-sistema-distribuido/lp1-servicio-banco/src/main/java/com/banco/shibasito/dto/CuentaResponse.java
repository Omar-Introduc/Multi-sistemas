package com.banco.shibasito.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * DTO para respuesta de información de cuenta
 */
@Schema(description = "Información de cuenta bancaria")
public class CuentaResponse {

    @Schema(description = "Número único de cuenta", example = "1234567890")
    private String numeroCuenta;

    @Schema(description = "DNI del titular", example = "12345678")
    private String dni;

    @Schema(description = "Nombre del titular", example = "Juan Pérez García")
    private String nombre;

    @Schema(description = "Tipo de cuenta", example = "AHORRO")
    private String tipoCuenta;

    @Schema(description = "Saldo actual de la cuenta", example = "1500.50")
    private BigDecimal saldo;

    @Schema(description = "Moneda de la cuenta", example = "PEN")
    private String moneda;

    @Schema(description = "Estado de la cuenta", example = "ACTIVA")
    private String estado;

    @Schema(description = "Fecha y hora de creación", example = "2025-10-30T08:44:05")
    private LocalDateTime fechaCreacion;

    @Schema(description = "Última actualización de saldo", example = "2025-10-30T08:44:05")
    private LocalDateTime fechaActualizacion;

    // Constructores
    public CuentaResponse() {}

    public CuentaResponse(String numeroCuenta, String dni, String nombre, String tipoCuenta, 
                         BigDecimal saldo, String moneda, String estado) {
        this.numeroCuenta = numeroCuenta;
        this.dni = dni;
        this.nombre = nombre;
        this.tipoCuenta = tipoCuenta;
        this.saldo = saldo;
        this.moneda = moneda;
        this.estado = estado;
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

    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public String getTipoCuenta() {
        return tipoCuenta;
    }

    public void setTipoCuenta(String tipoCuenta) {
        this.tipoCuenta = tipoCuenta;
    }

    public BigDecimal getSaldo() {
        return saldo;
    }

    public void setSaldo(BigDecimal saldo) {
        this.saldo = saldo;
    }

    public String getMoneda() {
        return moneda;
    }

    public void setMoneda(String moneda) {
        this.moneda = moneda;
    }

    public String getEstado() {
        return estado;
    }

    public void setEstado(String estado) {
        this.estado = estado;
    }

    public LocalDateTime getFechaCreacion() {
        return fechaCreacion;
    }

    public void setFechaCreacion(LocalDateTime fechaCreacion) {
        this.fechaCreacion = fechaCreacion;
    }

    public LocalDateTime getFechaActualizacion() {
        return fechaActualizacion;
    }

    public void setFechaActualizacion(LocalDateTime fechaActualizacion) {
        this.fechaActualizacion = fechaActualizacion;
    }
}