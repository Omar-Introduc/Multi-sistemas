package com.shibasito.banco.repositories;

import com.shibasito.banco.models.Prestamo;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PrestamoRepository extends JpaRepository<Prestamo, Long> {
}
