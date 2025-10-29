# Configuración del proveedor de Docker
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 2.15.0"
    }
  }
}

provider "docker" {}

# Definición de la red de Docker
resource "docker_network" "shibasito_network" {
  name = "shibasito_network"
}

# Definición de los volúmenes de Docker
resource "docker_volume" "postgres_data" {
  name = "postgres_data"
}

resource "docker_volume" "mysql_data" {
  name = "mysql_data"
}

# Definición de los contenedores de Docker
resource "docker_container" "bd1" {
  name  = "bd1"
  image = "postgres:15-alpine"
  networks_advanced {
    name = docker_network.shibasito_network.name
  }
  ports {
    internal = 5432
    external = 5432
  }
  volumes {
    volume_name = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }
}

resource "docker_container" "bd2" {
  name  = "bd2"
  image = "mysql:8.0"
  networks_advanced {
    name = docker_network.shibasito_network.name
  }
  ports {
    internal = 3306
    external = 3306
  }
  volumes {
    volume_name = docker_volume.mysql_data.name
    container_path = "/var/lib/mysql"
  }
}

resource "docker_container" "rabbitmq" {
  name  = "rabbitmq"
  image = "rabbitmq:3.13-management"
  networks_advanced {
    name = docker_network.shibasito_network.name
  }
  ports {
    internal = 5672
    external = 5672
  }
  ports {
    internal = 15672
    external = 15672
  }
}
