FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy project files
COPY . .

# Install the project
RUN uv sync --frozen || uv sync

# Set Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Initialize DVC (if not already initialized)
# Note: DVC remote storage should be configured separately
RUN dvc init --no-scm || true

# Default command
CMD ["python", "main.py"]
