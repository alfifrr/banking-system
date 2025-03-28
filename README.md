# RevoBank API

## Table of Contents

- [RevoBank API](#revobank-api)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Initial Setup](#initial-setup)
    - [1. Database Setup](#1-database-setup)
    - [2. Python Environment](#2-python-environment)
    - [3. Dependencies](#3-dependencies)
    - [4. Environment Configuration](#4-environment-configuration)
    - [5. Database Initialization](#5-database-initialization)
    - [6. Running the Application](#6-running-the-application)
  - [API Documentation](#api-documentation)
  - [Important Notes](#important-notes)
  - [Dependencies Used](#dependencies-used)

## Prerequisites

- Python 3.11+
- PostgreSQL
- UV package installer

## Initial Setup

### 1. Database Setup

```bash
# Create database as postgres user
psql -U postgres -c "CREATE DATABASE revobank"
```

### 2. Python Environment

```bash
# Install UV
pip install uv

# Create and activate virtual environment
uv venv

# Activate virtual environment
# Windows CMD:
.venv\Scripts\activate.bat
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/MacOS:
source .venv/Scripts/activate
```

### 3. Dependencies

```bash
uv pip install -r pyproject.toml
```

### 4. Environment Configuration

1. Create `.env` file (see `.env.example`)
2. Configure database: `POSTGRESQL_URL=postgresql://postgres:your_password@localhost/revobank`
3. Generate JWT secret:

```python
import uuid
uuid.uuid4().hex  # Copy output to JWT_SECRET_KEY in .env
```

### 5. Database Initialization

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Running the Application

```bash
uv run flask run
```

## API Documentation

- Full API documentation: [Postman Collection](https://documenter.getpostman.com/view/39087709/2sAYkBrgBB)
- Base URL: Replace `{{Prefix}}` with `https://banking-system-r349.onrender.com`
- Deployment: Hosted on Render

## Important Notes

- Ensure PostgreSQL service is running
- Verify database connection using pgAdmin or psql
- Default postgres password was set during installation

## Dependencies Used

- **Flask (>=3.1.0)**: Web framework for building the API
- **Flask-JWT-Extended (>=4.7.1)**: JWT token authentication and authorization
- **Flask-Migrate (>=4.1.0)**: Database migration management
- **Flask-SQLAlchemy (>=3.1.1)**: SQL ORM for database operations
- **Gunicorn (>=23.0.0)**: WSGI HTTP Server for deployment on Render
- **password-strength (>=0.0.3.post2)**: Password validation and security checks
- **psycopg2 (>=2.9.10)**: PostgreSQL database adapter
- **python-dotenv (>=1.0.1)**: Environment (`.env`) variable management
- **requests (>=2.32.3)**: HTTP requests handling
- **sqlalchemy-utils (>=0.41.2)**: SQLAlchemy utility functions
- **uuid (>=1.30)**: Unique identifier generation for `JWT_SECRET_KEY` variable
