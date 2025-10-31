package com.banco.shibasito.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "prestamos")
public class Prestamo {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cliente_id", nullable = false)
    private Cliente cliente;
    
    @Column(name = "monto", nullable = false, precision = 15, scale = 2)
    private BigDecimal monto;
    
    @Column(name = "monto_aprobado", precision = 15, scale = 2)
    private BigDecimal montoAprobado;
    
    @Column(name = "tasa_interes", precision = 5, scale = 2)
    private BigDecimal tasaInteres;
    
    @Column(name = "plazo_meses", nullable = false)
    private int plazoMeses;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "estado", nullable = false)
    private Estado estado = Estado.PENDIENTE;
    
    @Column(name = "motivo", length = 500)
    private String motivo;
    
    @Column(name = "motivo_rechazo", length = 500)
    private String motivoRechazo;
    
    @Column(name = "fecha", updatable = false)
    private LocalDate fecha;
    
    @Column(name = "fecha_aprobacion")
    private LocalDate fechaAprobacion;
    
    @Column(name = "fecha_vencimiento")
    private LocalDate fechaVencimiento;
    
    @Column(name = "cuota_mensual", precision = 15, scale = 2)
    private BigDecimal cuotaMensual;
    
    @Column(name = "cuotas_pagadas")
    private int cuotasPagadas;
    
    @Column(name = "saldo_pendiente", precision = 15, scale = 2)
    private BigDecimal saldoPendiente;
    
    public enum Estado {
        PENDIENTE, EVALUANDO, APROBADO, RECHAZADO, PAGADO
    }

    public Prestamo() {
        this.fecha = LocalDate.now();
        this.cuotasPagadas = 0;
    }
    
    @PrePersist
    protected void onCreate() {
        fecha = LocalDate.now();
    }

    // Métodos de negocio
    public boolean puedeSerAprobado() {
        return Estado.PENDIENTE.equals(estado) || Estado.EVALUANDO.equals(estado);
    }

    public void aprobar(BigDecimal montoAprobado, LocalDate fechaVencimiento) {
        this.estado = Estado.APROBADO;
        this.montoAprobado = montoAprobado;
        this.fechaAprobacion = LocalDate.now();
        this.fechaVencimiento = fechaVencimiento;
        this.saldoPendiente = montoAprobado;
        calcularCuotaMensual();
    }

    public void rechazar(String motivo) {
        this.estado = Estado.RECHAZADO;
        this.motivoRechazo = motivo;
    }

    public void evaluar() {
        this.estado = Estado.EVALUANDO;
    }

    public void marcarComoPagado() {
        this.estado = Estado.PAGADO;
        this.saldoPendiente = BigDecimal.ZERO;
    }

    private void calcularCuotaMensual() {
        if (this.montoAprobado != null && this.tasaInteres != null && this.plazoMeses > 0) {
            // Cálculo simple de cuota mensual (sin considerar amortización)
            BigDecimal interesTotal = this.montoAprobado.multiply(this.tasaInteres)
                    .divide(BigDecimal.valueOf(100), 2, BigDecimal.ROUND_HALF_UP);
            BigDecimal totalAPagar = this.montoAprobado.add(interesTotal);
            this.cuotaMensual = totalAPagar.divide(BigDecimal.valueOf(this.plazoMeses), 2, BigDecimal.ROUND_HALF_UP);
        }
    }

    // Getters y Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Cliente getCliente() { return cliente; }
    public void setCliente(Cliente cliente) { this.cliente = cliente; }

    public BigDecimal getMonto() { return monto; }
    public void setMonto(BigDecimal monto) { this.monto = monto; }

    public BigDecimal getMontoAprobado() { return montoAprobado; }
    public void setMontoAprobado(BigDecimal montoAprobado) { this.montoAprobado = montoAprobado; }

    public BigDecimal getTasaInteres() { return tasaInteres; }
    public void setTasaInteres(BigDecimal tasaInteres) { this.tasaInteres = tasaInteres; }

    public int getPlazoMeses() { return plazoMeses; }
    public void setPlazoMeses(int plazoMeses) { this.plazoMeses = plazoMeses; }

    public Estado getEstado() { return estado; }
    public void setEstado(Estado estado) { this.estado = estado; }

    public String getMotivo() { return motivo; }
    public void setMotivo(String motivo) { this.motivo = motivo; }

    public String getMotivoRechazo() { return motivoRechazo; }
    public void setMotivoRechazo(String motivoRechazo) { this.motivoRechazo = motivoRechazo; }

    public LocalDate getFecha() { return fecha; }
    public void setFecha(LocalDate fecha) { this.fecha = fecha; }

    public LocalDate getFechaAprobacion() { return fechaAprobacion; }
    public void setFechaAprobacion(LocalDate fechaAprobacion) { this.fechaAprobacion = fechaAprobacion; }

    public LocalDate getFechaVencimiento() { return fechaVencimiento; }
    public void setFechaVencimiento(LocalDate fechaVencimiento) { this.fechaVencimiento = fechaVencimiento; }

    public BigDecimal getCuotaMensual() { return cuotaMensual; }
    public void setCuotaMensual(BigDecimal cuotaMensual) { this.cuotaMensual = cuotaMensual; }

    public int getCuotasPagadas() { return cuotasPagadas; }
    public void setCuotasPagadas(int cuotasPagadas) { this.cuotasPagadas = cuotasPagadas; }

    public BigDecimal getSaldoPendiente() { return saldoPendiente; }
    public void setSaldoPendiente(BigDecimal saldoPendiente) { this.saldoPendiente = saldoPendiente; }

    @Override
    public String toString() {
        return "Prestamo{" +
                "id=" + id +
                ", monto=" + monto +
                ", montoAprobado=" + montoAprobado +
                ", estado=" + estado +
                ", fecha=" + fecha +
                '}';
    }
}