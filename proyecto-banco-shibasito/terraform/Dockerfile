# Usar una imagen base ligera con un sistema operativo Alpine Linux
FROM alpine:latest

# Instalar dependencias necesarias
RUN apk --no-cache add \
    wget \
    unzip \
    bash

# Variables de entorno para la versión de Terraform
ENV TERRAFORM_VERSION=1.0.0

# Descargar e instalar Terraform
RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip -d /usr/local/bin && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

# Establecer el directorio de trabajo
WORKDIR /terraform

# Comando por defecto (no se ejecutará nada por defecto)
CMD ["/bin/bash"]
