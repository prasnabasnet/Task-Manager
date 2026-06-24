# Task-Manager Backend

A Django-based backend for the Task-Manager application, providing authentication and user management built with Django REST Framework (DRF).

---

## Prerequisites

- **Python**: `>=3.12` (as specified in `.python-version` and `pyproject.toml`)
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (recommended) or standard `pip`

---

## Getting Started

You can set up and run the project using `uv`

1. **Sync dependencies and create virtual environment**:

   ```bash
   uv sync
   ```

   This command automatically creates a virtual environment in `.venv` and installs all dependencies specified in `pyproject.toml` and `uv.lock`.

2. **Run migrations**:

   ```bash
   uv run python manage.py migrate
   ```

3. **Start the development server**:
   ```bash
   uv run python manage.py runserver
   ```

## Running Tests

You can run tests using the Django test runner or `pytest`.

### 1. Using Django Test Runner

```bash
# Using uv:
uv run python manage.py test

# Using activated virtual environment:
python manage.py test
```

### 2. Using pytest

Because Django's default test file is named `tests.py` (which pytest doesn't automatically discover by default), specify the path and the Django settings module:

```bash
# Using uv:
uv run pytest users/tests.py --ds=taskmanager.settings

# Using activated virtual environment:
pytest users/tests.py --ds=taskmanager.settings
```

---

## API Endpoints

The following authentication API endpoints are implemented under the `/api/` prefix:

- **Register**: `POST /api/auth/register/` (Request body: `email`, `password`, `role`)
- **Login**: `POST /api/auth/login/` (Request body: `email`, `password`)
- **Logout**: `POST /api/auth/logout/` (Requires Token Auth header)
- **Get Current User Info**: `GET /api/auth/me/` (Requires Token Auth header)

---

## Project Structure

- `taskmanager/`: Main configuration module (settings, URLs, WSGI/ASGI configuration).
- `users/`: Authentication, custom User model, serialization, views, and test suites.
- `projects/`, `tasks/`, `comments/`: Skeleton app directories ready for development.
- `requirements.txt`: Frozen package dependencies.
- `pyproject.toml` & `uv.lock`: Modern python packaging configurations.
