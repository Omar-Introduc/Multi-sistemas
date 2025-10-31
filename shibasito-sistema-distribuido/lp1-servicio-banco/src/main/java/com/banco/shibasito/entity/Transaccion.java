package com.banco.shibasito.entity;

import javax.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entidad Transaccion del sistema bancario
 * Representa las transacciones realizadas en las cuentas
 */
@Entity
@Table(name = "transacciones")
public class Transaccion {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;
    
    @Column(name = "monto", nullable = false, precision = 15, scale = 2)
    private BigDecimal monto;
    
    @Column(name = "descripcion", length = 200)
    private String descripcion;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "tipo", nullable = false, length = 20)
    private TipoTransaccion tipo;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "estado", nullable = false)
    private Estado estado = Estado.COMPLETADA;
    
    @Column(name = "fecha", nullable = false, updatable = false)
    private LocalDateTime fecha;
    
    @Column(name = "motivo_fallo", length = 500)
    private String motivoFallo;
    
    // Relaciones
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cuenta_id", nullable = false)
    private Cuenta cuenta;
    
    // Enums
    public enum TipoTransaccion {
        DEPOSITO, RETIRO, TRANSFERENCIA, PAGO_INTERES
    }
    
    public enum Estado {
        COMPLETADA, PENDIENTE, FALLIDA, CANCELADA
    }

    // Constructores
    public Transaccion() {}
    
    public Transaccion(BigDecimal monto, TipoTransaccion tipo, String descripcion, Cuenta cuenta) {
        this.monto = monto;
        this.tipo = tipo;
        this.descripcion = descripcion;
        this.cuenta = cuenta;
        this.fecha = LocalDateTime.now();
    }
    
    // Métodos de ciclo de vida JPA
    @PrePersist
    protected void onCreate() {
        fecha = LocalDateTime.now();
    }
    
    // Métodos de negocio
    public boolean esDeposito() {
        return TipoTransaccion.DEPOSITO.equals(tipo);
    }

    public boolean esRetiro() {
        return TipoTransaccion.RETIRO.equals(tipo);
    }

    public boolean esTransferencia() {
        return TipoTransaccion.TRANSFERENCIA.equals(tipo);
    }

    public void marcarComoFallida(String motivo) {
        this.estado = Estado.FALLIDA;
        this.motivoFallo = motivo;
    }

    public void marcarComoPendiente() {
        this.estado = Estado.PENDIENTE;
    }

    public void completar() {
        this.estado = Estado.COMPLETADA;
        this.motivoFallo = null;
    }

    // Getters y Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public BigDecimal getMonto() {
        return monto;
    }
    
    public void setMonto(BigDecimal monto) {
        this.monto = monto;
    }
    
    public String getDescripcion() {
        return descripcion;
    }
    
    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }
    
    public TipoTransaccion getTipo() {
        return tipo;
    }
    
    public void setTipo(TipoTransaccion tipo) {
        this.tipo = tipo;
    }
    
    public Estado getEstado() {
        return estado;
    }
    
    public void setEstado(Estado estado) {
        this.estado = estado;
    }
    
    public LocalDateTime getFecha() {
        return fecha;
    }
    
    public void setFecha(LocalDateTime fecha) {
        this.fecha = fecha;
    }
    
    public String getMotivoFallo() {
        return motivoFallo;
    }
    
    public void setMotivoFallo(String motivoFallo) {
        this.motivoFallo = motivoFallo;
    }
    
    public Cuenta getCuenta() {
        return cuenta;
    }
    
    public void setCuenta(Cuenta cuenta) {
        this.cuenta = cuenta;
    }

    @Override
    public String toString() {
        return "Transaccion{" +
                "id=" + id +
                ", monto=" + monto +
                ", tipo=" + tipo +
                ", estado=" + estado +
                ", fecha=" + fecha +
                '}';
    }
}