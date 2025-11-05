package com.shibasito.service;

import com.shibasito.model.Cuenta;
import com.shibasito.model.Transaccion;
import com.shibasito.repository.CuentaRepository;
import com.shibasito.repository.TransaccionRepository;
import com.shibasito.exception.ResourceNotFoundException;
import com.shibasito.exception.InsufficientFundsException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Date;
import java.util.List;
import java.util.UUID;

@Service
@Transactional
public class CuentaService {

    @Autowired
    private CuentaRepository cuentaRepository;

    @Autowired
    private TransaccionRepository transaccionRepository;

    public List<Cuenta> getAllCuentas() {
        return cuentaRepository.findAll();
    }

    public Cuenta getCuentaById(String id) {
        return cuentaRepository.findById(id).orElseThrow(() -> new ResourceNotFoundException("Cuenta not found with id " + id));
    }

    public Cuenta createCuenta(Cuenta cuenta) {
        return cuentaRepository.save(cuenta);
    }

    public Cuenta depositar(String id, BigDecimal monto) {
        Cuenta cuenta = getCuentaById(id);
        cuenta.setSaldo(cuenta.getSaldo().add(monto));
        createTransaccion(cuenta, monto, "deposito", null);
        return cuentaRepository.save(cuenta);
    }

    public Cuenta retirar(String id, BigDecimal monto) {
        Cuenta cuenta = getCuentaById(id);
        if (cuenta.getSaldo().compareTo(monto) < 0) {
            throw new InsufficientFundsException("Insufficient funds in account " + id);
        }
        cuenta.setSaldo(cuenta.getSaldo().subtract(monto));
        createTransaccion(cuenta, monto, "retiro", null);
        return cuentaRepository.save(cuenta);
    }

    public void transferir(String idOrigen, String idDestino, BigDecimal monto) {
        Cuenta cuentaOrigen = getCuentaById(idOrigen);
        Cuenta cuentaDestino = getCuentaById(idDestino);

        if (cuentaOrigen.getSaldo().compareTo(monto) < 0) {
            throw new InsufficientFundsException("Insufficient funds in account " + idOrigen);
        }

        cuentaOrigen.setSaldo(cuentaOrigen.getSaldo().subtract(monto));
        cuentaDestino.setSaldo(cuentaDestino.getSaldo().add(monto));

        createTransaccion(cuentaOrigen, monto, "transferencia", idDestino);
        createTransaccion(cuentaDestino, monto, "transferencia", idOrigen);

        cuentaRepository.save(cuentaOrigen);
        cuentaRepository.save(cuentaDestino);
    }

    private void createTransaccion(Cuenta cuenta, BigDecimal monto, String tipo, String idDestino) {
        Transaccion transaccion = new Transaccion();
        transaccion.setIdTransaccion(UUID.randomUUID().toString().substring(0, 10));
        transaccion.setIdCuenta(cuenta.getIdCuenta());
        transaccion.setMonto(monto);
        transaccion.setTipo(tipo);
        transaccion.setFecha(new Date());
        transaccion.setIdDestino(idDestino);
        transaccion.setEstado("completada");
        transaccionRepository.save(transaccion);
    }
}
