# Stage 1: Build
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Run
FROM python:3.11-slim
WORKDIR /app
# AÑADIR ESTA LÍNEA para copiar los ejecutables (como uvicorn)
COPY --from=builder /usr/local/bin/ /usr/local/bin/
# La línea siguiente ya existía y copia las librerías
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
RUN chmod +x start.sh
ENTRYPOINT ["./start.sh"]
