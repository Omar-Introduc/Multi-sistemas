package com.shibasito.repository;

import com.shibasito.model.Prestamo;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface PrestamoRepository extends JpaRepository<Prestamo, String> {
    Optional<Prestamo> findFirstByClienteDniOrderByIdDesc(String dni);
}
