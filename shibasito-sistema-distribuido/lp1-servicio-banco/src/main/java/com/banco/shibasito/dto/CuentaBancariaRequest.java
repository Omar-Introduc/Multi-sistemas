package com.banco.shibasito.dto;

import com.banco.shibasito.model.CuentaBancaria;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;

/**
 * DTO para solicitudes de operaciones bancarias
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
public class CuentaBancariaRequest {

    @NotNull(message = "Número de cuenta es obligatorio")
    @Size(min = 10, max = 20, message = "Número de cuenta debe tener entre 10 y 20 caracteres")
    @Pattern(regexp = "^[0-9]+$", message = "Número de cuenta debe contener solo números")
    private String numeroCuenta;

    @NotNull(message = "ID de cliente es obligatorio")
    private Long clienteId;

    @NotNull(message = "Tipo de cuenta es obligatorio")
    private CuentaBancaria.TipoCuenta tipoCuenta;

    @NotNull(message = "Saldo inicial es obligatorio")
    @DecimalMin(value = "0.0", message = "Saldo inicial debe ser mayor o igual a 0")
    private BigDecimal saldoInicial;

    @Size(max = 500, message = "Descripción no puede exceder 500 caracteres")
    private String descripcion;

    // Constructores
    public CuentaBancariaRequest() {
    }

    public CuentaBancariaRequest(String numeroCuenta, Long clienteId, 
                                CuentaBancaria.TipoCuenta tipoCuenta, 
                                BigDecimal saldoInicial, String descripcion) {
        this.numeroCuenta = numeroCuenta;
        this.clienteId = clienteId;
        this.tipoCuenta = tipoCuenta;
        this.saldoInicial = saldoInicial;
        this.descripcion = descripcion;
    }

    // Getters y Setters
    public String getNumeroCuenta() {
        return numeroCuenta;
    }

    public void setNumeroCuenta(String numeroCuenta) {
        this.numeroCuenta = numeroCuenta;
    }

    public Long getClienteId() {
        return clienteId;
    }

    public void setClienteId(Long clienteId) {
        this.clienteId = clienteId;
    }

    public CuentaBancaria.TipoCuenta getTipoCuenta() {
        return tipoCuenta;
    }

    public void setTipoCuenta(CuentaBancaria.TipoCuenta tipoCuenta) {
        this.tipoCuenta = tipoCuenta;
    }

    public BigDecimal getSaldoInicial() {
        return saldoInicial;
    }

    public void setSaldoInicial(BigDecimal saldoInicial) {
        this.saldoInicial = saldoInicial;
    }

    public String getDescripcion() {
        return descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }

    // Convierte este DTO a entidad CuentaBancaria
    public CuentaBancaria toEntity() {
        CuentaBancaria cuenta = new CuentaBancaria();
        cuenta.setNumeroCuenta(this.numeroCuenta);
        cuenta.setClienteId(this.clienteId);
        cuenta.setTipoCuenta(this.tipoCuenta);
        cuenta.setSaldoActual(this.saldoInicial);
        cuenta.setDescripcion(this.descripcion);
        return cuenta;
    }

    @Override
    public String toString() {
        return "CuentaBancariaRequest{" +
                "numeroCuenta='" + numeroCuenta + '\'' +
                ", clienteId=" + clienteId +
                ", tipoCuenta=" + tipoCuenta +
                ", saldoInicial=" + saldoInicial +
                ", descripcion='" + descripcion + '\'' +
                '}';
    }
}
