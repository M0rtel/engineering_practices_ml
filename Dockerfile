FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.6.1

# Configure Poetry: Don't create virtual environment, install dependencies to system
RUN poetry config virtualenvs.create false

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy project files
COPY . .

# Install the project
RUN poetry install --no-interaction --no-ansi

# Set Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Default command
CMD ["python", "main.py"]
