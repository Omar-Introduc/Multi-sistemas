package com.shibasito.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.util.Date;

@Entity
@Table(name = "transacciones")
public class Transaccion {

    @Id
    @Column(name = "id_transaccion", length = 10)
    private String idTransaccion;

    @Column(name = "id_cuenta", length = 10, nullable = false)
    private String idCuenta;

    @Column(length = 15, nullable = false)
    private String tipo;

    @Column(nullable = false)
    private BigDecimal monto;

    @Temporal(TemporalType.TIMESTAMP)
    private Date fecha;

    private String descripcion;

    @Column(name = "id_destino", length = 10)
    private String idDestino;

    @Column(length = 10)
    private String estado;

    // Getters and Setters

    public String getIdTransaccion() {
        return idTransaccion;
    }

    public void setIdTransaccion(String idTransaccion) {
        this.idTransaccion = idTransaccion;
    }

    public String getIdCuenta() {
        return idCuenta;
    }

    public void setIdCuenta(String idCuenta) {
        this.idCuenta = idCuenta;
    }

    public String getTipo() {
        return tipo;
    }

    public void setTipo(String tipo) {
        this.tipo = tipo;
    }

    public BigDecimal getMonto() {
        return monto;
    }

    public void setMonto(BigDecimal monto) {
        this.monto = monto;
    }

    public Date getFecha() {
        return fecha;
    }

    public void setFecha(Date fecha) {
        this.fecha = fecha;
    }

    public String getDescripcion() {
        return descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }

    public String getIdDestino() {
        return idDestino;
    }

    public void setIdDestino(String idDestino) {
        this.idDestino = idDestino;
    }

    public String getEstado() {
        return estado;
    }

    public void setEstado(String estado) {
        this.estado = estado;
    }
}
