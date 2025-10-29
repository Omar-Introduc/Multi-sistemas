# 1. Define la versión explícita del lenguaje
FROM python:3.11-slim

# 2. Copia el código
WORKDIR /app
COPY . .

# 3. Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 4. Define cómo correr el servicio
COPY ./start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
