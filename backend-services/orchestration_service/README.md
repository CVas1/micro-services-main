# Order Orchestration Service

This service implements the Saga pattern to coordinate distributed transactions across multiple microservices (Orders, Products, Payments) using event-driven architecture.

## Architecture

### Components
- **Saga Orchestrator**: Coordinates the distributed transaction workflow
- **Event Consumer**: Listens for events from other services
- **Message Publisher**: Publishes commands to RabbitMQ
- **Redis Saga Store**: Maintains saga state during transactions
- **Auth Client**: Verifies user authentication

### Event Flow
1. Create Order Request → Verify Auth
2. Reduce Stock Command → Stock Service
3. Take Payment Command → Payment Service
4. Create Order Command → Order Service
5. Update Related Services

## Folder Structure
```
orchestration_service/
│
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── routers/              # API route handlers
│   ├── services/             # Business logic & external services
│   ├── models/               # Data models & schemas
│   └── events/               # Event definitions
│
├── tests/                    # Test files
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
└── README.md                # Documentation
```

## Prerequisites
- Python 3.11+
- RabbitMQ
- Redis
- Docker & Docker Compose

## Configuration

Environment variables required:
```bash

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Auth Server
AUTHERIZATION_SERVER_HOST=http://auth-service
AUTHERIZATION_SERVER_PORT=5206
```

## Setup & Running

### 1. Build Docker Image
```bash
docker build \
--build-arg RABBITMQ_HOST=rabbitmq \
--build-arg RABBITMQ_PORT=5672 \
--build-arg RABBITMQ_USER=guest \
--build-arg RABBITMQ_PASSWORD=guest \
--build-arg REDIS_HOST=redis \
--build-arg REDIS_PORT=6379 \
--build-arg REDIS_DB=0 \
--build-arg AUTHERIZATION_SERVER_HOST=http://auth-service \
--build-arg AUTHERIZATION_SERVER_PORT=8086 \
-t orchestration-service:latest .
```

### 2. Setup Network
```bash
# Create network if not exists
docker network create app-network

# Connect services to network
docker network connect app-network rabbitmq
docker network connect app-network redis
```

### 3. Run Services
```bash
# Run Redis
docker run --name redis-instance --network app-network -d -p 6379:6379 redis

# Run Orchestration Service
docker run --name orchestration-service \
  --network app-network \
  -d -p 7001:7001 \
  orchestration-service:latest
```

## API Endpoints

- `POST /orders/create_order` - Create a new order (starts saga)
- `GET /` - Health check endpoint

## Development

1. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run locally:
```bash
uvicorn app.main:app --reload --port 7001
```