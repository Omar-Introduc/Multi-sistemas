package com.banco.shibasito.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Objects;

/**
 * Entidad que representa una Cuenta Bancaria en el sistema
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
@Entity
@Table(name = "cuentas_bancarias", indexes = {
    @Index(name = "idx_cuenta_numero", columnList = "numero_cuenta"),
    @Index(name = "idx_cuenta_cliente", columnList = "cliente_id"),
    @Index(name = "idx_cuenta_estado", columnList = "estado")
})
@EntityListeners(AuditingEntityListener.class)
public class CuentaBancaria {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @Size(min = 10, max = 20)
    @Column(name = "numero_cuenta", unique = true, nullable = false)
    private String numeroCuenta;

    @NotNull
    @Column(name = "cliente_id", nullable = false)
    private Long clienteId;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(name = "tipo_cuenta", nullable = false)
    private TipoCuenta tipoCuenta;

    @NotNull
    @Column(name = "saldo_actual", precision = 15, scale = 2, nullable = false)
    private BigDecimal saldoActual;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(name = "estado", nullable = false)
    private EstadoCuenta estado;

    @Size(max = 500)
    @Column(name = "descripcion")
    private String descripcion;

    @CreatedDate
    @Column(name = "fecha_creacion", nullable = false, updatable = false)
    private LocalDateTime fechaCreacion;

    @LastModifiedDate
    @Column(name = "fecha_modificacion")
    private LocalDateTime fechaModificacion;

    // Constructor por defecto
    public CuentaBancaria() {
    }

    // Constructor con parámetros
    public CuentaBancaria(String numeroCuenta, Long clienteId, TipoCuenta tipoCuenta, 
                         BigDecimal saldoInicial, EstadoCuenta estado) {
        this.numeroCuenta = numeroCuenta;
        this.clienteId = clienteId;
        this.tipoCuenta = tipoCuenta;
        this.saldoActual = saldoInicial;
        this.estado = estado;
    }

    // Getters y Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

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

    public TipoCuenta getTipoCuenta() {
        return tipoCuenta;
    }

    public void setTipoCuenta(TipoCuenta tipoCuenta) {
        this.tipoCuenta = tipoCuenta;
    }

    public BigDecimal getSaldoActual() {
        return saldoActual;
    }

    public void setSaldoActual(BigDecimal saldoActual) {
        this.saldoActual = saldoActual;
    }

    public EstadoCuenta getEstado() {
        return estado;
    }

    public void setEstado(EstadoCuenta estado) {
        this.estado = estado;
    }

    public String getDescripcion() {
        return descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
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

    // Métodos utilitarios
    /**
     * Deposita dinero en la cuenta
     */
    public void depositar(BigDecimal monto) {
        if (monto != null && monto.compareTo(BigDecimal.ZERO) > 0) {
            this.saldoActual = this.saldoActual.add(monto);
        }
    }

    /**
     * Retira dinero de la cuenta
     */
    public boolean retirar(BigDecimal monto) {
        if (monto != null && monto.compareTo(BigDecimal.ZERO) > 0 
            && this.saldoActual.compareTo(monto) >= 0) {
            this.saldoActual = this.saldoActual.subtract(monto);
            return true;
        }
        return false;
    }

    /**
     * Verifica si la cuenta está activa
     */
    public boolean isActiva() {
        return this.estado == EstadoCuenta.ACTIVA;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        CuentaBancaria that = (CuentaBancaria) o;
        return Objects.equals(id, that.id) && Objects.equals(numeroCuenta, that.numeroCuenta);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, numeroCuenta);
    }

    @Override
    public String toString() {
        return "CuentaBancaria{" +
                "id=" + id +
                ", numeroCuenta='" + numeroCuenta + '\'' +
                ", clienteId=" + clienteId +
                ", tipoCuenta=" + tipoCuenta +
                ", saldoActual=" + saldoActual +
                ", estado=" + estado +
                ", fechaCreacion=" + fechaCreacion +
                '}';
    }

    // Enums
    public enum TipoCuenta {
        AHORROS("A"),
        CORRIENTE("C"),
        PLAZO_FIJO("P"),
        MINIMA("M");

        private final String codigo;

        TipoCuenta(String codigo) {
            this.codigo = codigo;
        }

        public String getCodigo() {
            return codigo;
        }
    }

    public enum EstadoCuenta {
        ACTIVA,
        INACTIVA,
        BLOQUEADA,
        CERRADA
    }
}
