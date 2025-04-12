# RevoBank API Documentation

## Table of Contents

- [RevoBank API Documentation](#revobank-api-documentation)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Local Setup Instructions](#local-setup-instructions)
  - [API Documentation](#api-documentation)
  - [Docker Component](#docker-component)
  - [Important Notes](#important-notes)
  - [Deployed Endpoint and Image](#deployed-endpoint-and-image)
  - [Services](#services)
  - [Dependencies](#dependencies)

## Introduction

RevoBank API is a banking system API built using Flask, designed to manage users, accounts, and transactions. This documentation provides setup instructions, API details, and deployment information.

## Prerequisites

Before setting up the project, ensure you have the following installed:

- [Python](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/)
- [Insomnia](https://insomnia.rest/download) (optional, for API testing)

## Local Setup Instructions

1. Navigate to the project directory.
2. Copy the `.env.example` as `.env` and set the provided values for Postgres' database URL, JWT secret key, and mail server provider you like.

3. Build and run the Docker containers for the first time (detached from the command prompt):

```bash
docker compose up --build -d
```

4. To stop the running containers:

```bash
docker compose down
```

5. To restart the containers:

```bash
docker compose up
```

## API Documentation

- Full API documentation is available via [Postman Collection](https://documenter.getpostman.com/view/39087709/2sAYkBrgBB).
- Base URL: Replace `{{Prefix}}` with `https://banking-system-r349.onrender.com`.
- Alternatively, import the `Insomnia_revobank_request_list.json` file into the Insomnia application.

## Docker Component

- **Flask Application**: Accessible at `http://localhost:8080`.

## Important Notes

- Ensure the Docker image is running before accessing the application.

- Example endpoints for testing:
  - Check the database connection health: `http://127.0.0.1:8080/api/health`
  - View all accounts (requires access token obtained from `POST http://127.0.0.1:8080/api/login`): `http://127.0.0.1:8080/api/accounts`

## Deployed Endpoint and Image

- **Render**: [https://banking-system-r349.onrender.com](https://banking-system-r349.onrender.com)
- **Docker**: [DockerHub](https://hub.docker.com/r/alfifrr/bankingsystem)

## Services

- **Database**: Supabase
- **Mail Server**: Mailtrap

## Dependencies

The following Python dependencies are used in this project:

- **Flask** (3.1.0): The framework
- **Flask-Bcrypt** (1.0.1): Password hasher for database
- **Flask-JWT-Extended** (4.7.1): JWT authentication
- **Flask-Limiter** (3.12): Request limiter
- **Flask-Mail** (0.10.0): Mail sender
- **Flask-Migrate** (4.1.0): Database migration management
- **Flask-SQLAlchemy** (3.1.1): SQL ORM
- **Flask-Swagger-UI** (4.11.1): Documentation (access using `/api/docs`)
- **Password-Strength** (0.0.3.post2): Password validation
- **Psycopg2-Binary** (2.9.10): PostgreSQL adapter
- **Python-Dotenv** (1.0.1): Environment variable management
- **Requests** (2.32.3): HTTP requests
- **SQLAlchemy** (2.0.39): SQL ORM
