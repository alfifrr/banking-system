# RevoBank API Documentation

## Table of Contents

- [RevoBank API Documentation](#revobank-api-documentation)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Local Setup Instructions](#local-setup-instructions)
  - [API Documentation](#api-documentation)
  - [Docker Components](#docker-components)
  - [Important Notes](#important-notes)
  - [Deployed Endpoint and Image](#deployed-endpoint-and-image)
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

2. Build and run the Docker containers for the first time (detached from the command prompt):

```bash
docker compose up --build -d
```

3. To stop the running containers:

```bash
docker compose down
```

4. To restart the containers:

```bash
docker compose up
```

## API Documentation

- Full API documentation is available via [Postman Collection](https://documenter.getpostman.com/view/39087709/2sAYkBrgBB).
- Base URL: Replace `{{Prefix}}` with `https://banking-system-r349.onrender.com`.
- Alternatively, import the `Insomnia_revobank_request_list.json` file into the Insomnia application.

## Docker Components

The Docker setup includes the following services:

- **Flask Application**: Accessible at `http://localhost:8080`.

## Important Notes

- Ensure all Docker containers are running before accessing the application.

- Example endpoints for testing:
  - View all users: `http://127.0.0.1:8080/api/users`
  - View all accounts: `http://127.0.0.1:8080/api/accounts`

## Deployed Endpoint and Image

- **Render**: [https://banking-system-r349.onrender.com](https://banking-system-r349.onrender.com)
- **Docker**: [DockerHub](https://hub.docker.com/r/alfifrr/bankingsystem)

## Dependencies

The following Python dependencies are used in this project:

- **Alembic** (1.15.1): Database migrations for SQLAlchemy
- **Blinker** (1.9.0): Signal support for Flask
- **Certifi** (2025.1.31): SSL certificate validation
- **Charset-Normalizer** (3.4.1): Encoding detection
- **Click** (8.1.8): CLI creation for Flask
- **Flask** (3.1.0): Web framework
- **Flask-JWT-Extended** (4.7.1): JWT authentication
- **Flask-Migrate** (4.1.0): Database migration management
- **Flask-SQLAlchemy** (3.1.1): SQL ORM
- **Greenlet** (3.1.1): Concurrent programming
- **IDNA** (3.10): Domain name handling
- **Itsdangerous** (2.2.0): Cryptographic utilities
- **Jinja2** (3.1.6): Templating engine
- **Mako** (1.3.9): Templating engine for Alembic
- **MarkupSafe** (3.0.2): String escaping
- **Password-Strength** (0.0.3.post2): Password validation
- **Psycopg2-Binary** (2.9.10): PostgreSQL adapter
- **PyJWT** (2.10.1): JWT implementation
- **Python-Dotenv** (1.0.1): Environment variable management
- **Requests** (2.32.3): HTTP requests
- **Six** (1.17.0): Python compatibility utilities
- **SQLAlchemy** (2.0.39): SQL ORM
- **SQLAlchemy-Utils** (0.41.2): SQLAlchemy utilities
- **Typing-Extensions** (4.12.2): Typing features backport
- **Urllib3** (2.3.0): HTTP client
- **UUID** (1.30): Unique identifier generation
- **Werkzeug** (3.1.3): WSGI utility library
