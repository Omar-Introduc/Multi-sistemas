package com.shibasito.controller;

import com.shibasito.dto.PrestamoDTO;
import com.shibasito.model.Prestamo;
import com.shibasito.service.PrestamoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/prestamos")
public class PrestamoController {

    @Autowired
    private PrestamoService prestamoService;

    @GetMapping
    public List<PrestamoDTO> getAllPrestamos() {
        return prestamoService.getAllPrestamos().stream().map(this::convertToDto).collect(Collectors.toList());
    }

    @GetMapping("/{id}")
    public PrestamoDTO getPrestamoById(@PathVariable String id) {
        return convertToDto(prestamoService.getPrestamoById(id));
    }

    @PostMapping
    public PrestamoDTO createPrestamo(@RequestBody PrestamoDTO prestamoDTO) {
        Prestamo prestamo = convertToEntity(prestamoDTO);
        return convertToDto(prestamoService.createPrestamo(prestamo));
    }

    private PrestamoDTO convertToDto(Prestamo prestamo) {
        PrestamoDTO prestamoDTO = new PrestamoDTO();
        prestamoDTO.setIdPrestamo(prestamo.getIdPrestamo());
        prestamoDTO.setIdCliente(prestamo.getIdCliente());
        prestamoDTO.setMonto(prestamo.getMonto());
        prestamoDTO.setMontoPendiente(prestamo.getMontoPendiente());
        prestamoDTO.setTasaInteres(prestamo.getTasaInteres());
        prestamoDTO.setEstado(prestamo.getEstado());
        prestamoDTO.setFechaSolicitud(prestamo.getFechaSolicitud());
        prestamoDTO.setFechaVencimiento(prestamo.getFechaVencimiento());
        return prestamoDTO;
    }

    private Prestamo convertToEntity(PrestamoDTO prestamoDTO) {
        Prestamo prestamo = new Prestamo();
        prestamo.setIdPrestamo(prestamoDTO.getIdPrestamo());
        prestamo.setIdCliente(prestamoDTO.getIdCliente());
        prestamo.setMonto(prestamoDTO.getMonto());
        prestamo.setMontoPendiente(prestamoDTO.getMontoPendiente());
        prestamo.setTasaInteres(prestamoDTO.getTasaInteres());
        prestamo.setEstado(prestamoDTO.getEstado());
        prestamo.setFechaSolicitud(prestamoDTO.getFechaSolicitud());
        prestamo.setFechaVencimiento(prestamoDTO.getFechaVencimiento());
        return prestamo;
    }
}
