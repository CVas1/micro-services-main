# Payment Service

## Description
A microservice for payment operations built with FastAPI and SQLAlchemy.

## Tech Stack
- FastAPI - High-performance web framework
- SQLAlchemy - SQL toolkit and ORM
- MySQL - Database
- Docker - Containerization
- Pydantic - Data validation
- Uvicorn - ASGI server

## Prerequisites
- Python 3.8+
- Docker
- pip

## Database Setup
Start the MySQL database using Docker:

```bash
docker run --name mysql-dev \
  --network app-network \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=payments_db \
  -e MYSQL_USER=myuser \
  -e MYSQL_PASSWORD=mypassword \
  -p 3306:3306 \
  -d mysql:8.0
```
## To Connect To Your Docker Mysql Image
```bash
docker exec -it mysql-dev mysql -u root -p
```


## Add Access To The DB
```
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;
```

## Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Mac/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```
## To Run The App
```bash
. venv/bin/activate
fastapi dev app/main.py --port 9001
```
## Project Structure
```
project/
├── app/
│   ├── main.py                # Application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       └── payments.py    # Contains routes for payments
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Configuration settings (DB, broker URLs, etc.)
│   ├── models/
│   │   ├── __init__.py
│   │   └── payment.py         # Pydantic models and/or ORM models for payments
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── payment_schema.py  # Pydantic models for payments
│   ├── db/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── base.py            # Database connection and session handling
│   └── services/
│       ├── __init__.py
│       ├── payment_service.py # Business logic for payments
│       ├── auth_service.py  
│       └── rabbitmq_publisher.py
├── tests/                     # Test suite for your application
│   ├── __init__.py
│   └── test_payments.py
├── requirements.txt           # Python dependencies
├── pyproject.toml 
├── Dockerfile                 # (Optional) Containerization file
└── README.md                  # Project documentation

```

## API Endpoints

### Payments


## Development

## Build Docker Image And Run it
First build the docker image of the app
```bash
sudo docker build \
--build-arg DATABASE_HOST=mysql-dev:3306 \
--build-arg DATABASE_PASSWORD=root \
--build-arg DATABASE_NAME=payments_db \
--build-arg DATABASE_USER=root \
--build-arg RABBITMQ_HOST=rabbitmq \
--build-arg RABBITMQ_PORT=5672 \
--build-arg RABBITMQ_USER=guest \
--build-arg RABBITMQ_PASSWORD=guest \
-t payment-service:latest .
```
Than connect db and service to the same network(all the services and the database must be in the same network):
For more information $ docker network
```bash
sudo docker run --name payment-container --network app-network -d -p 9001:9001 payment-service:latest

```

## Connect Rabbitmq To Network
docker network connect app-network rabbitmq

Run tests:
```bash
pytest
```