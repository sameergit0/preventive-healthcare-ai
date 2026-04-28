# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for psycopg2 + builds)
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project
COPY . .

# Install dependencies using uv
RUN uv sync 

# Expose port
EXPOSE 8000

# Run app
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]