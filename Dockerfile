# Dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential cmake

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# (opcional) Crear carpetas dentro del contenedor
RUN mkdir -p storage uploads

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
