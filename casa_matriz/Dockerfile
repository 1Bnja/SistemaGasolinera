FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY casa_matriz/ .

RUN mkdir -p /data

EXPOSE 5000 5001

CMD ["python", "app.py"]
