package com.shibasito.service;

import com.shibasito.model.Prestamo;
import com.shibasito.repository.PrestamoRepository;
import com.shibasito.exception.ResourceNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
public class PrestamoService {

    @Autowired
    private PrestamoRepository prestamoRepository;

    @Autowired
    private RabbitMQSenderService rabbitMQSenderService;

    public List<Prestamo> getAllPrestamos() {
        return prestamoRepository.findAll();
    }

    public Prestamo getPrestamoById(String id) {
        return prestamoRepository.findById(id).orElseThrow(() -> new ResourceNotFoundException("Prestamo not found with id " + id));
    }

    public Prestamo createPrestamo(Prestamo prestamo) {
        String message = "{\"dni\": \"" + prestamo.getIdCliente() + "\"}";
        rabbitMQSenderService.send(message);
        return prestamoRepository.save(prestamo);
    }
}
