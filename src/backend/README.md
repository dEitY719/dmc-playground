# Seraph Default Backend Server

A reusable FastAPI backend server template with SQLModel and PostgreSQL support.

## Features

- FastAPI for API development
- SQLModel for database interactions (ORM)
- PostgreSQL support
- Basic CRUD operations for Stock model
- Type hinting and code quality checks (ruff, mypy)

## Installation

There are two primary ways to install and use this backend server:

### 1. From PyPI (Recommended for Users)

This is the easiest way to install the pre-built package.

```bash
pip install seraph-default-backend-server
```

### 2. From GitHub Source (For Developers/Contributors)

If you want to contribute to the project, modify the source code, or run tests, you should clone the repository and install it.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dEitY719/seraph-backend-template.git
    cd seraph-backend-template/src/backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the package in editable mode:**
    This allows you to make changes to the source code directly and have them reflected without re-installation.
    ```bash
    pip install -e .
    ```

    To run tests or development tools, you may need to install additional dependencies:
    ```bash
    pip install pytest httpx sqlmodel # Example development dependencies
    ```

## Usage

(Detailed usage instructions will be added here)
