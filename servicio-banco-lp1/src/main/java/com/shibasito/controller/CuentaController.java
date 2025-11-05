package com.shibasito.controller;

import com.shibasito.dto.CuentaDTO;
import com.shibasito.dto.TransaccionRequestDTO;
import com.shibasito.model.Cuenta;
import com.shibasito.service.CuentaService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/cuentas")
public class CuentaController {

    @Autowired
    private CuentaService cuentaService;

    @GetMapping
    public List<CuentaDTO> getAllCuentas() {
        return cuentaService.getAllCuentas().stream().map(this::convertToDto).collect(Collectors.toList());
    }

    @GetMapping("/{id}")
    public CuentaDTO getCuentaById(@PathVariable String id) {
        return convertToDto(cuentaService.getCuentaById(id));
    }

    @PostMapping
    public CuentaDTO createCuenta(@RequestBody CuentaDTO cuentaDTO) {
        Cuenta cuenta = convertToEntity(cuentaDTO);
        return convertToDto(cuentaService.createCuenta(cuenta));
    }

    @PostMapping("/{id}/depositar")
    public CuentaDTO depositar(@PathVariable String id, @RequestBody TransaccionRequestDTO transaccionRequestDTO) {
        return convertToDto(cuentaService.depositar(id, transaccionRequestDTO.getMonto()));
    }

    @PostMapping("/{id}/retirar")
    public CuentaDTO retirar(@PathVariable String id, @RequestBody TransaccionRequestDTO transaccionRequestDTO) {
        return convertToDto(cuentaService.retirar(id, transaccionRequestDTO.getMonto()));
    }

    @PostMapping("/transferir")
    public ResponseEntity<Void> transferir(@RequestBody TransaccionRequestDTO transaccionRequestDTO) {
        cuentaService.transferir(transaccionRequestDTO.getIdCuenta(), transaccionRequestDTO.getIdDestino(), transaccionRequestDTO.getMonto());
        return ResponseEntity.ok().build();
    }

    private CuentaDTO convertToDto(Cuenta cuenta) {
        CuentaDTO cuentaDTO = new CuentaDTO();
        cuentaDTO.setIdCuenta(cuenta.getIdCuenta());
        cuentaDTO.setIdCliente(cuenta.getIdCliente());
        cuentaDTO.setSaldo(cuenta.getSaldo());
        cuentaDTO.setFechaApertura(cuenta.getFechaApertura());
        cuentaDTO.setTipoCuenta(cuenta.getTipoCuenta());
        cuentaDTO.setEstado(cuenta.getEstado());
        return cuentaDTO;
    }

    private Cuenta convertToEntity(CuentaDTO cuentaDTO) {
        Cuenta cuenta = new Cuenta();
        cuenta.setIdCuenta(cuentaDTO.getIdCuenta());
        cuenta.setIdCliente(cuentaDTO.getIdCliente());
        cuenta.setSaldo(cuentaDTO.getSaldo());
        cuenta.setFechaApertura(cuentaDTO.getFechaApertura());
        cuenta.setTipoCuenta(cuentaDTO.getTipoCuenta());
        cuenta.setEstado(cuentaDTO.getEstado());
        return cuenta;
    }
}
