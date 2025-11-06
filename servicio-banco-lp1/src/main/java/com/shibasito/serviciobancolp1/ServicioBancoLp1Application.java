package com.shibasito.serviciobancolp1;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
// AÑADE ESTAS LÍNEAS
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication
// AÑADE ESTAS TRES LÍNEAS
@ComponentScan(basePackages = "com.shibasito")
@EntityScan(basePackages = "com.shibasito.model")
@EnableJpaRepositories(basePackages = "com.shibasito.repository")
public class ServicioBancoLp1Application {

	public static void main(String[] args) {
		SpringApplication.run(ServicioBancoLp1Application.class, args);
	}

}