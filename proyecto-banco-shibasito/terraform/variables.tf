# variables.tf

variable "postgres_image" {
  description = "The Docker image for the PostgreSQL database"
  default     = "postgres:15-alpine"
}

variable "mysql_image" {
  description = "The Docker image for the MySQL database"
  default     = "mysql:8.0"
}

variable "rabbitmq_image" {
  description = "The Docker image for RabbitMQ"
  default     = "rabbitmq:3.13-management"
}
