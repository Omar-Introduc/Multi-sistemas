package com.banco.shibasito.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.domain.AuditorAware;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.transaction.annotation.EnableTransactionManagement;

/**
 * Configuración de JPA Auditing para el sistema
 * 
 * Habilita el seguimiento automático de fechas de creación
 * y modificación de entidades.
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
@Configuration
@EnableJpaRepositories(basePackages = "com.banco.shibasito.repository")
@EnableJpaAuditing(auditorAwareRef = "auditorProvider")
@EnableTransactionManagement
public class JpaAuditingConfig {

    /**
     * Proveedor de información del auditor
     */
    @Bean
    public AuditorAware<String> auditorProvider() {
        return new AuditorAwareImpl();
    }

    /**
     * Implementación de AuditorAware para obtener información del usuario actual
     */
    public static class AuditorAwareImpl implements AuditorAware<String> {

        @Override
        public String getCurrentAuditor() {
            // En una aplicación real, aquí se obtendría el usuario autenticado
            // desde el SecurityContext o otro mecanismo de autenticación
            return "system"; // Usuario por defecto para auditorías
        }
    }
}
