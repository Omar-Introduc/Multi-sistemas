package com.banco.shibasito.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Entidad Cuenta del sistema bancario
 * Representa las cuentas bancarias de los clientes
 */
@Entity
@Table(name = "cuentas")
public class Cuenta {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;
    
    @Column(name = "numero", nullable = false, unique = true, length = 20)
    private String numero;
    
    @Column(name = "saldo", nullable = false, precision = 15, scale = 2)
    private BigDecimal saldo;
    
    @Column(name = "saldo_minimo", precision = 15, scale = 2)
    private BigDecimal saldoMinimo = BigDecimal.ZERO;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "tipo", nullable = false, length = 20)
    private TipoCuenta tipo;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "estado", nullable = false)
    private Estado estado = Estado.ACTIVA;
    
    @Column(name = "fecha_creacion", updatable = false)
    private LocalDateTime fechaCreacion;
    
    @Column(name = "fecha_modificacion")
    private LocalDateTime fechaModificacion;
    
    // Relaciones
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cliente_id", nullable = false)
    private Cliente cliente;
    
    @OneToMany(mappedBy = "cuenta", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Transaccion> transacciones = new ArrayList<>();
    
    // Enums
    public enum TipoCuenta {
        AHORROS, CORRIENTE, PLAZO_FIJO
    }
    
    public enum Estado {
        ACTIVA, INACTIVA, BLOQUEADA, CERRADA
    }

    // Constructores
    public Cuenta() {}
    
    public Cuenta(String numero, BigDecimal saldo, TipoCuenta tipo, Cliente cliente) {
        this.numero = numero;
        this.saldo = saldo != null ? saldo : BigDecimal.ZERO;
        this.tipo = tipo;
        this.cliente = cliente;
        this.fechaCreacion = LocalDateTime.now();
    }
    
    // Métodos de ciclo de vida JPA
    @PrePersist
    protected void onCreate() {
        fechaCreacion = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        fechaModificacion = LocalDateTime.now();
    }
    
    // Métodos de negocio
    public boolean puedeRetirar(BigDecimal monto) {
        return this.estado == Estado.ACTIVA && 
               this.saldo.compareTo(monto) >= 0 && 
               this.saldo.subtract(monto).compareTo(this.saldoMinimo) >= 0;
    }

    public void depositar(BigDecimal monto) {
        if (this.estado == Estado.ACTIVA && monto != null && monto.compareTo(BigDecimal.ZERO) > 0) {
            this.saldo = this.saldo.add(monto);
        }
    }

    public boolean retirar(BigDecimal monto) {
        if (puedeRetirar(monto)) {
            this.saldo = this.saldo.subtract(monto);
            return true;
        }
        return false;
    }
    
    public void agregarTransaccion(Transaccion transaccion) {
        transacciones.add(transaccion);
        transaccion.setCuenta(this);
    }

    // Getters y Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getNumero() {
        return numero;
    }
    
    public void setNumero(String numero) {
        this.numero = numero;
    }
    
    public BigDecimal getSaldo() {
        return saldo;
    }
    
    public void setSaldo(BigDecimal saldo) {
        this.saldo = saldo;
    }
    
    public BigDecimal getSaldoMinimo() {
        return saldoMinimo;
    }
    
    public void setSaldoMinimo(BigDecimal saldoMinimo) {
        this.saldoMinimo = saldoMinimo;
    }
    
    public TipoCuenta getTipo() {
        return tipo;
    }
    
    public void setTipo(TipoCuenta tipo) {
        this.tipo = tipo;
    }
    
    public Estado getEstado() {
        return estado;
    }
    
    public void setEstado(Estado estado) {
        this.estado = estado;
    }
    
    public LocalDateTime getFechaCreacion() {
        return fechaCreacion;
    }
    
    public void setFechaCreacion(LocalDateTime fechaCreacion) {
        this.fechaCreacion = fechaCreacion;
    }
    
    public LocalDateTime getFechaModificacion() {
        return fechaModificacion;
    }
    
    public void setFechaModificacion(LocalDateTime fechaModificacion) {
        this.fechaModificacion = fechaModificacion;
    }
    
    public Cliente getCliente() {
        return cliente;
    }
    
    public void setCliente(Cliente cliente) {
        this.cliente = cliente;
    }
    
    public List<Transaccion> getTransacciones() {
        return transacciones;
    }
    
    public void setTransacciones(List<Transaccion> transacciones) {
        this.transacciones = transacciones;
    }

    @Override
    public String toString() {
        return "Cuenta{" +
                "id=" + id +
                ", numero='" + numero + '\'' +
                ", saldo=" + saldo +
                ", tipo=" + tipo +
                ", estado=" + estado +
                '}';
    }
}