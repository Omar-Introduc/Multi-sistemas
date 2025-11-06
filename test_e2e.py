import docker
import requests
import time
import subprocess

def test_e2e():
    try:
        # Build and start services
        subprocess.run(["sudo", "docker", "compose", "-f", "docker-compose.main.yml", "build"], check=True)
        subprocess.run(["sudo", "docker", "compose", "-f", "docker-compose.main.yml", "up", "-d"], check=True)

        # Wait for services to be healthy
        for _ in range(60):
            try:
                response = requests.get("http://localhost:8080/api/cuentas/health")
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)
        else:
            raise Exception("Services did not become healthy in time")

        # Create a loan
        response = requests.post(
            "http://localhost:8080/api/prestamos",
            json={"dniCliente": "12345678", "monto": 1000.0},
        )
        assert response.status_code == 200

        # Check consumer logs
        client = docker.from_env()
        consumer_container = client.containers.get("servicio-reniec-lp2")
        logs = consumer_container.logs().decode("utf-8")
        assert "DNI 12345678 is valid" in logs

    finally:
        # Stop services
        subprocess.run(["sudo", "docker", "compose", "-f", "docker-compose.main.yml", "down"], check=True)
