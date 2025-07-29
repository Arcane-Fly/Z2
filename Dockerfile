# ---------------------------------------------
# Stage 1: Install dependencies via Poetry
# ---------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install Poetry CLI (no cache to reduce image size)
RUN pip install --no-cache-dir poetry

# Copy only lockfiles and configure Poetry
COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-interaction --no-ansi --no-root

# ---------------------------------------------
# Stage 2: Build runtime image
# ---------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/poetry /usr/local/bin/poetry

# Copy source
COPY backend/ .

# Expose dynamic PORT (Railway sets $PORT), fallback to 8000
ARG PORT
EXPOSE ${PORT:-8000}

# Entrypoint: start Uvicorn on 0.0.0.0:$PORT
ENTRYPOINT ["sh", "-c"]
CMD ["python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]