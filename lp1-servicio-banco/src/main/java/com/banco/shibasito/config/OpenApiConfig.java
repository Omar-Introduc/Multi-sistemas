package com.banco.shibasito.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import io.swagger.v3.oas.models.servers.Server;
import io.swagger.v3.oas.models.tags.Tag;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

/**
 * Configuración de Swagger/OpenAPI para documentación de la API
 * 
 * @author Sistema Shibasito
 * @version 1.0.0
 */
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(apiInfo())
                .servers(List.of(
                        new Server().url("http://localhost:8080/banco").description("Servidor de desarrollo"),
                        new Server().url("https://api-banco.shibasito.com").description("Servidor de producción")
                ))
                .tags(List.of(
                        new Tag().name("Cuentas Bancarias").description("API para gestión de cuentas bancarias"),
                        new Tag().name("Transacciones").description("API para operaciones de transacciones"),
                        new Tag().name("Reportes").description("API para generación de reportes"),
                        new Tag().name("Sistema").description("APIs de sistema y monitoreo")
                ))
                .components(new Components()
                        .addSecuritySchemes("bearer-key", 
                                new SecurityScheme()
                                        .type(SecurityScheme.Type.HTTP)
                                        .scheme("bearer")
                                        .bearerFormat("JWT")
                                        .description("Token JWT para autenticación"))
                )
                .security(List.of(new SecurityRequirement().addList("bearer-key")));
    }

    private Info apiInfo() {
        return new Info()
                .title("Servicio Banco Shibasito API")
                .description("""
                    API REST para la gestión del microservicio bancario del sistema distribuido Shibasito.
                    
                    ## Funcionalidades
                    
                    - **Gestión de Cuentas**: Crear, consultar y administrar cuentas bancarias
                    - **Operaciones Bancarias**: Depósitos, retiros y transferencias
                    - **Consultas**: Búsquedas avanzadas y reportes
                    - **Integración**: Comunicación con otros servicios del sistema
                    
                    ## Autenticación
                    
                    Esta API utiliza JWT (JSON Web Tokens) para autenticación.
                    Incluya el token en el header: `Authorization: Bearer <token>`
                    
                    ## Códigos de Estado
                    
                    - `200`: Operación exitosa
                    - `201`: Recurso creado exitosamente
                    - `400`: Solicitud incorrecta
                    - `401`: No autorizado
                    - `403`: Prohibido
                    - `404`: Recurso no encontrado
                    - `500`: Error interno del servidor
                    
                    ## Versión
                    
                    **Versión actual**: 1.0.0
                    
                    **Última actualización**: Octubre 2025
                    """)
                .version("1.0.0")
                .contact(new Contact()
                        .name("Equipo Shibasito")
                        .email("desarrollo@shibasito.com")
                        .url("https://shibasito.com"))
                .license(new License()
                        .name("Licencia MIT")
                        .url("https://opensource.org/licenses/MIT"));
    }
}
