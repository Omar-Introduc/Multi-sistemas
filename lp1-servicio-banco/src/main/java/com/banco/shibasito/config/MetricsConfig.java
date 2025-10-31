package com.banco.shibasito.config;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tag;
import io.micrometer.core.instrument.binder.MeterBinder;
import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import io.micrometer.core.instrument.binder.jvm.JvmMemoryMetrics;
import io.micrometer.core.instrument.binder.logging.LogbackMetrics;
import io.micrometer.core.instrument.binder.system.ProcessorMetrics;
import io.micrometer.core.instrument.binder.web.servlet.WebMvcMetrics;
import io.micrometer.core.instrument.config.MeterFilter;
import io.micrometer.prometheus.PrometheusConfig;
import io.micrometer.prometheus.PrometheusMeterRegistry;
import io.prometheus.client.CollectorRegistry;
import io.prometheus.client.Gauge;
import io.prometheus.client.Histogram;
import io.prometheus.client.Summary;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.actuate.autoconfigure.metrics.MeterRegistryCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.servlet.http.HttpServletRequest;
import java.util.Arrays;

/**
 * Configuración de métricas Prometheus para el servicio bancario
 */
@Configuration
public class MetricsConfig {

    @Value("${spring.application.name:banco-shibasito}")
    private String applicationName;

    @Value("${server.port:8080}")
    private String serverPort;

    /**
     * Configuración personalizada del PrometheusMeterRegistry
     */
    @Bean
    public PrometheusMeterRegistry prometheusMeterRegistry(PrometheusConfig prometheusConfig) {
        PrometheusMeterRegistry registry = new PrometheusMeterRegistry(prometheusConfig);
        
        // Configurar filtros para las métricas
        registry.config()
                .meterFilter(MeterFilter.denyNameStartsWith("jvm.threads.states"))
                .meterFilter(MeterFilter.denyNameStartsWith("logback.events"))
                .meterFilter(MeterFilter.denyNameStartsWith("process.files"));
        
        return registry;
    }

    /**
     * Configuración personalizada del MeterRegistry
     */
    @Bean
    public MeterRegistryCustomizer<MeterRegistry> meterRegistryCustomizer() {
        return registry -> registry.config()
                .commonTags(Arrays.asList(
                    Tag.of("application", applicationName),
                    Tag.of("port", serverPort),
                    Tag.of("service", "banco"),
                    Tag.of("version", "1.0.0")
                ))
                .namingConvention(io.micrometer.core.instrument.config.NamingConvention.dot);
    }

    /**
     * Métricas personalizadas para el banco
     */
    @Bean
    public BankMetrics bankMetrics(PrometheusMeterRegistry registry) {
        return new BankMetrics(registry);
    }

    /**
     * Web MVC metrics
     */
    @Bean
    public WebMvcMetrics webMvcMetrics() {
        return new WebMvcMetrics();
    }

    /**
     * Métricas JVM
     */
    @Bean
    public MeterBinder jvmMemoryMetrics() {
        return new JvmMemoryMetrics();
    }

    /**
     * Métricas de GC
     */
    @Bean
    public MeterBinder jvmGcMetrics() {
        return new JvmGcMetrics();
    }

    /**
     * Métricas del sistema
     */
    @Bean
    public MeterBinder processorMetrics() {
        return new ProcessorMetrics();
    }

    /**
     * Métricas de logging
     */
    @Bean
    public MeterBinder logbackMetrics() {
        return new LogbackMetrics();
    }

    /**
     * Clase para métricas personalizadas del banco
     */
    public static class BankMetrics {
        
        private final Histogram transaccionesHistogram;
        private final Gauge cuentasActivasGauge;
        private final Gauge saldoTotalGauge;
        private final Summary requestLatencySummary;
        private final Gauge erroresPorEndpointGauge;

        public BankMetrics(PrometheusMeterRegistry registry) {
            this.transaccionesHistogram = Histogram.build()
                    .name("banco_transacciones_duracion_segundos")
                    .help("Duración de transacciones bancarias en segundos")
                    .labelNames("tipo_transaccion", "status")
                    .buckets(0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
                    .register(registry);

            this.cuentasActivasGauge = Gauge.build()
                    .name("banco_cuentas_activas_total")
                    .help("Número total de cuentas activas")
                    .labelNames("tipo_cuenta", "moneda")
                    .register(registry);

            this.saldoTotalGauge = Gauge.build()
                    .name("banco_saldo_total")
                    .help("Saldo total en el sistema")
                    .labelNames("moneda", "tipo_cuenta")
                    .register(registry);

            this.requestLatencySummary = Summary.build()
                    .name("banco_request_latency_seconds")
                    .help("Latencia de requests HTTP")
                    .labelNames("endpoint", "metodo", "status")
                    .quantiles(0.5, 0.9, 0.95, 0.99)
                    .register(registry);

            this.erroresPorEndpointGauge = Gauge.build()
                    .name("banco_errores_por_endpoint")
                    .help("Número de errores por endpoint")
                    .labelNames("endpoint", "metodo", "status_code")
                    .register(registry);
        }

        public void recordTransactionDuration(String tipoTransaccion, String status, double duration) {
            transaccionesHistogram.labels(tipoTransaccion, status).observe(duration);
        }

        public void updateCuentasActivas(String tipoCuenta, String moneda, double count) {
            cuentasActivasGauge.labels(tipoCuenta, moneda).set(count);
        }

        public void updateSaldoTotal(String moneda, String tipoCuenta, double saldo) {
            saldoTotalGauge.labels(moneda, tipoCuenta).set(saldo);
        }

        public void recordRequestLatency(String endpoint, String metodo, String status, double latency) {
            requestLatencySummary.labels(endpoint, metodo, status).observe(latency);
        }

        public void incrementErrores(String endpoint, String metodo, String statusCode) {
            erroresPorEndpointGauge.labels(endpoint, metodo, statusCode).inc();
        }
    }

    /**
     * Configuración adicional para métricas de seguridad
     */
    @Bean
    public SecurityMetrics securityMetrics(PrometheusMeterRegistry registry) {
        return new SecurityMetrics(registry);
    }

    /**
     * Clase para métricas de seguridad
     */
    public static class SecurityMetrics {
        
        private final Gauge intentosLoginFallidos;
        private final Gauge sesionesActivas;
        private final Histogram timeoutsSessionHistogram;

        public SecurityMetrics(PrometheusMeterRegistry registry) {
            this.intentosLoginFallidos = Gauge.build()
                    .name("banco_intentos_login_fallidos")
                    .help("Intentos de login fallidos")
                    .labelNames("ip", "usuario")
                    .register(registry);

            this.sesionesActivas = Gauge.build()
                    .name("banco_sesiones_activas")
                    .help("Número de sesiones activas")
                    .register(registry);

            this.timeoutsSessionHistogram = Histogram.build()
                    .name("banco_session_timeout_segundos")
                    .help("Tiempo hasta timeout de sesión")
                    .buckets(300, 600, 900, 1800, 3600)
                    .register(registry);
        }

        public void recordLoginFailure(String ip, String usuario) {
            intentosLoginFallidos.labels(ip, usuario).inc();
        }

        public void updateSesionesActivas(double count) {
            sesionesActivas.set(count);
        }

        public void recordSessionTimeout(double timeoutSeconds) {
            timeoutsSessionHistogram.observe(timeoutSeconds);
        }
    }

    /**
     * Configuración para CollectorRegistry personalizado
     */
    @Bean
    public CollectorRegistry collectorRegistry() {
        return CollectorRegistry.defaultRegistry;
    }
}
