# outputs.tf

output "bd1_container_id" {
  description = "The ID of the PostgreSQL container"
  value       = docker_container.bd1.id
}

output "bd2_container_id" {
  description = "The ID of the MySQL container"
  value       = docker_container.bd2.id
}

output "rabbitmq_container_id" {
  description = "The ID of the RabbitMQ container"
  value       = docker_container.rabbitmq.id
}
