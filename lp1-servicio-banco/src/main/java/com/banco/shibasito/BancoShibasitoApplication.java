package com.banco.shibasito;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.transaction.annotation.EnableTransactionManagement;

/**
 * Aplicación principal del Servicio Banco Shibasito
 * 
 * Esta clase configura y lanza la aplicación Spring Boot
 * con todas las funcionalidades del microservicio bancario.
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
@SpringBootApplication
@EnableTransactionManagement
@EnableCaching
@EnableAsync
@EnableScheduling
public class BancoShibasitoApplication {

    public static void main(String[] args) {
        SpringApplication.run(BancoShibasitoApplication.class, args);
    }
}
