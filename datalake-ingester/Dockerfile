# Dockerfile para el contenedor de ingesta
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script de ingesta
COPY ingester.py .

# Comando por defecto
CMD ["python", "ingester.py"]