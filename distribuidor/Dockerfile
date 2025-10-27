FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY distribuidor/ .

# Crear directorio para datos
RUN mkdir -p /data

EXPOSE 8000 6000

CMD ["python", "app.py"]
