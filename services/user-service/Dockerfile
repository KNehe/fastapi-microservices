# Stage 1: The Builder
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_HTTP_TIMEOUT=120
WORKDIR /app

# Copy the dependency files first for docker caching
COPY pyproject.toml uv.lock ./

# Copy the specific services files
COPY services/user-service/pyproject.toml services/user-service/

# Install dependencies for the user-service
RUN uv sync --package user-service --frozen --no-dev

#  Copy the rest of the code
COPY . .

# Stage 2: The Final Image
FROM python:3.12-slim-bookworm
WORKDIR /app

# Copy the environment and code from the builder
COPY --from=builder /app /app

# Put the virtual environment on the path
ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH="/app/services/user-service:/app"

# Run the FastAPI server.
CMD ["fastapi", "run", "services/user-service/main.py", "--port", "8000", "--host", "0.0.0.0"]