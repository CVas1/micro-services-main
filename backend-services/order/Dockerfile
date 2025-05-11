## ------------------------------- Builder Stage ------------------------------ ## 
FROM python:3.13-bookworm AS builder

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Download the latest installer, install it and then remove it
ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod -R 655 /install.sh && /install.sh && rm /install.sh

# Set up the UV environment path correctly
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY ./pyproject.toml .

RUN uv sync

## ------------------------------- Production Stage ------------------------------ ##
FROM python:3.13-slim-bookworm AS production

ARG DATABASE_PASSWORD
ARG DATABASE_USER
ARG DATABASE_NAME
ARG DATABASE_HOST
ARG RABBITMQ_HOST
ARG RABBITMQ_PORT
ARG RABBITMQ_USER
ARG RABBITMQ_PASSWORD
# Set environment variables for DB and access token
ENV DATABASE_PASSWORD=${DATABASE_PASSWORD}
ENV DATABASE_USER=${DATABASE_USER}
ENV DATABASE_NAME=${DATABASE_NAME}
ENV DATABASE_HOST=${DATABASE_HOST}
ENV RABBITMQ_HOST=${RABBITMQ_HOST}
ENV RABBITMQ_PORT=${RABBITMQ_PORT}
ENV RABBITMQ_USER=${RABBITMQ_USER}
ENV RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD}
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .
COPY --from=builder /app/.venv .venv

# Set up environment variables for production
ENV PATH="/app/.venv/bin:$PATH"

# Expose the specified port for FastAPI
EXPOSE $PORT

# Start the application with Uvicorn in production mode, using environment variable references
CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8080"]