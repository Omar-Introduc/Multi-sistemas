package com.banco.shibasito.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.connection.RedisStandaloneConfiguration;
import org.springframework.data.redis.connection.jedis.JedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

/**
 * Configuración de Redis para caching del servicio bancario
 */
@Configuration
@EnableCaching
public class CacheConfig {

    @Value("${spring.redis.host:localhost}")
    private String redisHost;

    @Value("${spring.redis.port:6379}")
    private int redisPort;

    @Value("${spring.redis.password:}")
    private String redisPassword;

    @Value("${spring.redis.timeout:2000}")
    private int redisTimeout;

    // Nombres de cache
    public static final String CACHE_USUARIOS = "usuarios";
    public static final String CACHE_CUENTAS = "cuentas";
    public static final String CACHE_TRANSACCIONES = "transacciones";
    public static final String CACHE_TIPOS_CAMBIO = "tiposCambio";
    public static final String CACHE_TASA_INTERES = "tasaInteres";
    public static final String CACHE_SALDOS = "saldos";
    public static final String CACHE_HISTORIAL_TRANSACCIONES = "historialTransacciones";

    // TTL por defecto (en minutos)
    public static final int DEFAULT_TTL_MINUTES = 30;
    public static final int TIPO_CAMBIO_TTL_MINUTES = 5;
    public static final int SALDO_TTL_MINUTES = 10;
    public static final int HISTORIAL_TTL_MINUTES = 60;

    /**
     * Configuración de la conexión a Redis
     */
    @Bean
    public RedisConnectionFactory redisConnectionFactory() {
        RedisStandaloneConfiguration config = new RedisStandaloneConfiguration();
        config.setHostName(redisHost);
        config.setPort(redisPort);
        
        if (redisPassword != null && !redisPassword.isEmpty()) {
            config.setPassword(redisPassword);
        }
        
        return new JedisConnectionFactory(config);
    }

    /**
     * Configuración del CacheManager con Redis
     */
    @Bean
    public CacheManager cacheManager(RedisConnectionFactory redisConnectionFactory) {
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofMinutes(DEFAULT_TTL_MINUTES))
                .disableCachingNullValues()
                .serializeKeysWith(org.springframework.data.redis.serializer.RedisSerializationContext.SerializationPair
                        .fromSerializer(new StringRedisSerializer()))
                .serializeValuesWith(org.springframework.data.redis.serializer.RedisSerializationContext.SerializationPair
                        .fromSerializer(new GenericJackson2JsonRedisSerializer()));

        // Configuración específica por cache
        Map<String, RedisCacheConfiguration> cacheConfigurations = new HashMap<>();
        
        cacheConfigurations.put(CACHE_USUARIOS, defaultConfig
                .entryTtl(Duration.ofMinutes(DEFAULT_TTL_MINUTES)));
        
        cacheConfigurations.put(CACHE_CUENTAS, defaultConfig
                .entryTtl(Duration.ofMinutes(DEFAULT_TTL_MINUTES)));
        
        cacheConfigurations.put(CACHE_TRANSACCIONES, defaultConfig
                .entryTtl(Duration.ofMinutes(DEFAULT_TTL_MINUTES)));
        
        cacheConfigurations.put(CACHE_TIPOS_CAMBIO, defaultConfig
                .entryTtl(Duration.ofMinutes(TIPO_CAMBIO_TTL_MINUTES)));
        
        cacheConfigurations.put(CACHE_TASA_INTERES, defaultConfig
                .entryTtl(Duration.ofMinutes(15)));
        
        cacheConfigurations.put(CACHE_SALDOS, defaultConfig
                .entryTtl(Duration.ofMinutes(SALDO_TTL_MINUTES)));
        
        cacheConfigurations.put(CACHE_HISTORIAL_TRANSACCIONES, defaultConfig
                .entryTtl(Duration.ofMinutes(HISTORIAL_TTL_MINUTES)));

        return RedisCacheManager.builder(redisConnectionFactory)
                .cacheDefaults(defaultConfig)
                .withInitialCacheConfigurations(cacheConfigurations)
                .build();
    }

    /**
     * Configuración del RedisTemplate para operaciones manuales
     */
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);

        // Serializadores
        StringRedisSerializer stringSerializer = new StringRedisSerializer();
        GenericJackson2JsonRedisSerializer jsonSerializer = new GenericJackson2JsonRedisSerializer();

        // Configurar serialización
        template.setKeySerializer(stringSerializer);
        template.setHashKeySerializer(stringSerializer);
        template.setValueSerializer(jsonSerializer);
        template.setHashValueSerializer(jsonSerializer);

        template.afterPropertiesSet();
        return template;
    }

    /**
     * Configuración específica para cache de usuarios
     */
    @Bean(name = "usuariosCacheConfig")
    public RedisCacheConfiguration usuariosCacheConfig() {
        return RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofMinutes(DEFAULT_TTL_MINUTES))
                .serializeKeysWith(org.springframework.data.redis.serializer.RedisSerializationContext.SerializationPair
                        .fromSerializer(new StringRedisSerializer()))
                .serializeValuesWith(org.springframework.data.redis.serializer.RedisSerializationContext.SerializationPair
                        .fromSerializer(new GenericJackson2JsonRedisSerializer()));
    }

    /**
     * Configuración específica para cache de tipos de cambio
     */
    @Bean(name = "tiposCambioCacheConfig")
    public RedisCacheConfiguration tiposCambioCacheConfig() {
        return RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofMinutes(TIPO_CAMBIO_TTL_MINUTES))
                .serializeKeysWith(org.springframework.data.redis.serializer.RedisSerializationContext.SerializationPair
                        .fromSerializer(new StringRedisSerializer()))
                .serializeValuesWith(org.springframework.data.redis.serializer.RedisSerializationContext.SerializationPair
                        .fromSerializer(new GenericJackson2JsonRedisSerializer()));
    }

    /**
     * Configuración específica para cache de saldos
     */
    @Bean(name = "saldosCacheConfig")
    public RedisCacheConfiguration saldosCacheConfig() {
        return RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofMinutes(SALDO_TTL_MINUTES))
                .serializeKeysWith(org.springframework.data.redis.serializer.RedisSerializationContext.SerializationPair
                        .fromSerializer(new StringRedisSerializer()))
                .serializeValuesWith(org.springframework.data.redis.serializer.RedisSerializationContext.SerializationPair
                        .fromSerializer(new GenericJackson2JsonRedisSerializer()));
    }
}
