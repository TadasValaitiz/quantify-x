FROM python:3.13.2-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    python3-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Set environment variables for better pip behavior
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install -r requirements.txt


# Copy the rest of the application
COPY . .

# Expose port (use PORT env var or default to 8080 for Cloud Run)
ENV PORT=8080
EXPOSE ${PORT}

# Command to run the application with the port from the environment variable
CMD streamlit run frontend/app.py --server.port=${PORT} --server.address=0.0.0.0
