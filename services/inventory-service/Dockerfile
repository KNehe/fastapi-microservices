FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY services/inventory-service/pyproject.toml services/inventory-service/
RUN uv sync --package inventory-service --frozen --no-dev
COPY . .

FROM python:3.12-slim-bookworm
WORKDIR /app
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONUNBUFFERED=1

CMD ["fastapi", "run", "services/inventory-service/main.py", "--port", "8000", "--host", "0.0.0.0"]
