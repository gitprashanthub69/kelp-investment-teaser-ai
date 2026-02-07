FROM python:3.11-slim

# Install system dependencies for Camelot and OpenCV
RUN apt-get update && apt-get install -y \
    ghostscript \
    python3-tk \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Default command (will be overridden in docker-compose for worker)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
