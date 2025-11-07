FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg libsm6 libxext6 && rm -rf /var/lib/apt/lists/*

# Copy backend files (including model)
COPY . /app

# Upgrade pip and install dependencies (CPU-only torch)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "app.py"]
