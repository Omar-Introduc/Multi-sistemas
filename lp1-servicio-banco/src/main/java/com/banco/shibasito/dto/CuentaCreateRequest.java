package com.banco.shibasito.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;

/**
 * DTO para solicitud de creación de cuenta
 */
@Schema(description = "Solicitud para crear una nueva cuenta bancaria")
public class CuentaCreateRequest {

    @NotBlank(message = "El DNI es obligatorio")
    @Size(min = 8, max = 8, message = "El DNI debe tener exactamente 8 dígitos")
    @Schema(description = "Documento Nacional de Identidad del titular", example = "12345678", required = true)
    private String dni;

    @NotBlank(message = "El nombre es obligatorio")
    @Size(min = 2, max = 100, message = "El nombre debe tener entre 2 y 100 caracteres")
    @Schema(description = "Nombre completo del titular", example = "Juan Pérez García", required = true)
    private String nombre;

    @NotBlank(message = "El tipo de cuenta es obligatorio")
    @Schema(description = "Tipo de cuenta", example = "AHORRO", allowableValues = {"AHORRO", "CORRIENTE", "PLAZO_FIJO"}, required = true)
    private String tipoCuenta;

    @NotNull(message = "El saldo inicial es obligatorio")
    @DecimalMin(value = "0.0", inclusive = true, message = "El saldo inicial no puede ser negativo")
    @Schema(description = "Saldo inicial de la cuenta", example = "1000.00", required = true)
    private BigDecimal saldoInicial;

    @Schema(description = "Moneda de la cuenta", example = "PEN", allowableValues = {"PEN", "USD", "EUR"})
    private String moneda = "PEN";

    // Constructores
    public CuentaCreateRequest() {}

    public CuentaCreateRequest(String dni, String nombre, String tipoCuenta, BigDecimal saldoInicial) {
        this.dni = dni;
        this.nombre = nombre;
        this.tipoCuenta = tipoCuenta;
        this.saldoInicial = saldoInicial;
        this.moneda = "PEN";
    }

    public CuentaCreateRequest(String dni, String nombre, String tipoCuenta, BigDecimal saldoInicial, String moneda) {
        this.dni = dni;
        this.nombre = nombre;
        this.tipoCuenta = tipoCuenta;
        this.saldoInicial = saldoInicial;
        this.moneda = moneda;
    }

    // Getters y Setters
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

    public BigDecimal getSaldoInicial() {
        return saldoInicial;
    }

    public void setSaldoInicial(BigDecimal saldoInicial) {
        this.saldoInicial = saldoInicial;
    }

    public String getMoneda() {
        return moneda;
    }

    public void setMoneda(String moneda) {
        this.moneda = moneda;
    }
}