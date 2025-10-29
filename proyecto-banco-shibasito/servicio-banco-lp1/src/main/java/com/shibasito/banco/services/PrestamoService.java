package com.shibasito.banco.services;

import com.shibasito.banco.models.Prestamo;
import com.shibasito.banco.repositories.PrestamoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class PrestamoService {

    @Autowired
    private PrestamoRepository prestamoRepository;

    public List<Prestamo> getAllPrestamos() {
        return prestamoRepository.findAll();
    }
}
