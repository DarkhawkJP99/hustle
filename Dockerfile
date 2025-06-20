# Hustle. v2.2 Dockerfile
FROM python:3.10-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ai_hustle_automator.py .
COPY render.yaml .

CMD ["uvicorn", "ai_hustle_automator:app", "--host", "0.0.0.0", "--port", "8000"]
