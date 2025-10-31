package com.banco.shibasito.entity;

import jakarta.persistence.*;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Entidad Cliente del sistema bancario
 * Representa los clientes del banco
 */
@Entity
@Table(name = "clientes")
public class Cliente {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;
    
    @Column(name = "dni", nullable = false, unique = true, length = 8)
    private String dni;
    
    @Column(name = "nombres", nullable = false, length = 100)
    private String nombres;
    
    @Column(name = "apellidos", nullable = false, length = 100)
    private String apellidos;
    
    @Column(name = "email", unique = true, length = 150)
    private String email;
    
    @Column(name = "telefono", length = 15)
    private String telefono;
    
    @Column(name = "direccion", length = 200)
    private String direccion;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "estado", nullable = false)
    private Estado estado = Estado.ACTIVO;
    
    @Column(name = "fecha_creacion", updatable = false)
    private LocalDateTime fechaCreacion;
    
    @Column(name = "fecha_modificacion")
    private LocalDateTime fechaModificacion;

    @Column(name = "fecha_ultima_validacion")
    private LocalDateTime fechaUltimaValidacion;

    @Column(name = "estado_validacion")
    private String estadoValidacion;

    @Column(name = "observaciones_validacion")
    private String observacionesValidacion;

    @Column(name = "fecha_nacimiento")
    private String fechaNacimiento;
    
    // Relaciones
    @OneToMany(mappedBy = "cliente", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Cuenta> cuentas = new ArrayList<>();
    
    @OneToMany(mappedBy = "cliente", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Prestamo> prestamos = new ArrayList<>();
    
    // Enum para estados
    public enum Estado {
        ACTIVO, INACTIVO, SUSPENDIDO
    }

    // Constructores
    public Cliente() {}
    
    public Cliente(String dni, String nombres, String apellidos, String email, String telefono, String direccion) {
        this.dni = dni;
        this.nombres = nombres;
        this.apellidos = apellidos;
        this.email = email;
        this.telefono = telefono;
        this.direccion = direccion;
        this.estado = Estado.ACTIVO;
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
    public void agregarCuenta(Cuenta cuenta) {
        cuentas.add(cuenta);
        cuenta.setCliente(this);
    }
    
    public void agregarPrestamo(Prestamo prestamo) {
        prestamos.add(prestamo);
        prestamo.setCliente(this);
    }

    // Getters y Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getDni() {
        return dni;
    }
    
    public void setDni(String dni) {
        this.dni = dni;
    }
    
    public String getNombres() {
        return nombres;
    }
    
    public void setNombres(String nombres) {
        this.nombres = nombres;
    }
    
    public String getApellidos() {
        return apellidos;
    }
    
    public void setApellidos(String apellidos) {
        this.apellidos = apellidos;
    }
    
    public String getEmail() {
        return email;
    }
    
    public void setEmail(String email) {
        this.email = email;
    }
    
    public String getTelefono() {
        return telefono;
    }
    
    public void setTelefono(String telefono) {
        this.telefono = telefono;
    }
    
    public String getDireccion() {
        return direccion;
    }
    
    public void setDireccion(String direccion) {
        this.direccion = direccion;
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
    
    public List<Cuenta> getCuentas() {
        return cuentas;
    }
    
    public void setCuentas(List<Cuenta> cuentas) {
        this.cuentas = cuentas;
    }
    
    public List<Prestamo> getPrestamos() {
        return prestamos;
    }
    
    public void setPrestamos(List<Prestamo> prestamos) {
        this.prestamos = prestamos;
    }

    public LocalDateTime getFechaUltimaValidacion() {
        return fechaUltimaValidacion;
    }

    public void setFechaUltimaValidacion(LocalDateTime fechaUltimaValidacion) {
        this.fechaUltimaValidacion = fechaUltimaValidacion;
    }

    public String getEstadoValidacion() {
        return estadoValidacion;
    }

    public void setEstadoValidacion(String estadoValidacion) {
        this.estadoValidacion = estadoValidacion;
    }

    public String getObservacionesValidacion() {
        return observacionesValidacion;
    }

    public void setObservacionesValidacion(String observacionesValidacion) {
        this.observacionesValidacion = observacionesValidacion;
    }

    public String getFechaNacimiento() {
        return fechaNacimiento;
    }

    public void setFechaNacimiento(String fechaNacimiento) {
        this.fechaNacimiento = fechaNacimiento;
    }

    @Override
    public String toString() {
        return "Cliente{" +
                "id=" + id +
                ", dni='" + dni + '\'' +
                ", nombres='" + nombres + '\'' +
                ", apellidos='" + apellidos + '\'' +
                ", email='" + email + '\'' +
                ", estado=" + estado +
                '}';
    }
}