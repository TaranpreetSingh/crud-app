FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY python/app.py .
COPY python/templates/ ./templates/

# Expose ports for API and Prometheus metrics
EXPOSE 8080
EXPOSE 8000



CMD ["python", "app.py"]