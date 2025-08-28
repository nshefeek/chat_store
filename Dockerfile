FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create virtual environment
RUN uv venv
ENV PATH="/app/.venv/bin:$PATH"

# Install Python dependencies
RUN uv pip install --no-cache-dir -e .

# Copy application code
COPY src ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY scripts/ ./scripts/

# Ensure the package is installed
RUN uv pip install --no-cache-dir -e .

# Make entrypoint script executable
RUN chmod +x scripts/entrypoint.sh

EXPOSE 8000

CMD ["./scripts/entrypoint.sh"]
