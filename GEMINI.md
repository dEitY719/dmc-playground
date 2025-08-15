# Gemini Code Assistant Context

This document provides context for the Gemini Code Assistant to understand the project structure, conventions, and tasks.

## Project Overview

This project contains a frontend application built with Dash Mantine Components (DMC) and a backend service built with FastAPI. It's a Python-based monorepo set up to explore different UI/UX patterns and serve data. The project emphasizes code quality, using `black`, `isort`, `mypy`, and `pylint` managed via `tox`.

The project is divided into two main parts:

- `src/frontend`: A Dash application for the user interface. The entry point is `src/frontend/app.py`.
- `src/backend`: A FastAPI application for serving data.

## Building and Running

### Installation

1. Create and activate a Python virtual environment:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

2. Install the base dependencies and the optional dependencies for the component you want to work on.

    To install all dependencies for both frontend and backend development:

    ```bash
    pip install -e ".[all,dev]"
    ```

    To install only frontend dependencies:

    ```bash
    pip install -e ".[frontend,dev]"
    ```

    To install only backend dependencies:

    ```bash
    pip install -e ".[backend,dev]"
    ```

    The `-e` flag installs the project in "editable" mode. The `[all,dev]` part tells pip to install the `all` and `dev` optional dependencies.

### Running the Application

To run the development server:

```bash
python src/frontend/app.py
```

### Code Quality and Formatting

This project uses `tox` to manage code quality checks.

- **Run all checks (formatting, linting, type-checking):**

    ```bash
    tox
    ```

- **Automatically fix formatting issues:**

    ```bash
    tox -e fix
    ```

- **Run individual checks:**
  - `tox -e black` (formatter)
  - `tox -e isort` (import sorter)
  - `tox -e mypy` (type checker)
  - `tox -e pylint` (linter)

## Development Conventions

- **Code Style:** The project uses `black` for code formatting and `isort` for import sorting. The configurations are in `pyproject.toml`.
- **Type Hinting:** The project uses `mypy` for static type checking. Type hints are expected for all new code.
- **Linting:** `pylint` is used for code linting. The configuration is in `pyproject.toml`.
- **Modularity:** The application is structured in a modular way, with different functionalities separated into directories like `components`, `pages`, and `services`. New features should follow this structure.
- **Dependencies:** Project dependencies are managed in `pyproject.toml` and a `requirements.txt` file is also present.
