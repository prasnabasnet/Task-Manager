# Task-Manager Backend

A Django REST Framework backend for a multi-tenant task management platform. Supports organizations, departments, projects, tasks, and threaded comments with @mentions — all governed by role- and membership-based permissions.

---

## Tech Stack

- **Python** 3.12+
- **Django** 6.0.6
- **Django REST Framework** 3.17.1
- **django-filter** for queryset filtering
- **PostgreSQL** (via `psycopg2-binary`) — configured through `DATABASE_URL`
- **Token authentication** (`rest_framework.authtoken`)
- **uv** for dependency and virtual environment management
- **pytest / pytest-django** and Django's built-in test runner for testing
- **factory-boy** for test fixtures
- **ruff** for linting

---

## Prerequisites

- Python `>=3.12`
- [uv](https://github.com/astral-sh/uv) (recommended) or standard `pip`
- A running PostgreSQL instance

---

## Getting Started

1. **Sync dependencies and create a virtual environment**

   ```bash
   uv sync
   ```

   This creates `.venv` and installs everything from `pyproject.toml` / `uv.lock`, including the `dev` dependency group.

2. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   SECRET_KEY=change-me
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=postgres://user:password@localhost:5432/taskmanager
   ```

3. **Run migrations**

   ```bash
   uv run python manage.py migrate
   ```

4. **(Optional) Load sample data**

   ```bash
   uv run python manage.py loaddata fixtures/test_data.json
   ```

   This seeds sample users, organizations, departments, projects, tasks, and comments. Every seeded user shares the same password hash in the fixture — check `fixtures/test_data.json` for the accounts it creates.

5. **Start the development server**

   ```bash
   uv run python manage.py runserver
   ```

---

## Running Tests

### Using Django's test runner

```bash
uv run python manage.py test
```

### Using pytest

Each app's tests live in a `tests.py` file, which pytest doesn't auto-discover by default — point it at the Django settings module explicitly:

```bash
uv run pytest --ds=config.settings
```

Or target a single app:

```bash
uv run pytest apps/tasks/tests.py --ds=config.settings
```

---

## Project Structure

```
config/                Project settings, root URL conf, WSGI/ASGI entrypoints
apps/
  users/                Custom User model, auth, admin user management
  organization/          Organizations and organization membership
  department/            Departments (scoped to an organization)
  projects/               Projects and project membership
  tasks/                    Tasks belonging to a project
  comments/                 Threaded comments with @mentions, attachable to
                             organizations, projects, or tasks
fixtures/               Sample data for local development (test_data.json)
bruno/                  Bruno API collection for manually exercising every
                         endpoint (see "API Testing" below)
manage.py
main.py
pyproject.toml / uv.lock
```

Each app follows the same internal layout:

```
apps/<app>/
  models/        One file per model, re-exported via __init__.py
  serializers/    DRF serializers
  views/          DRF views/viewsets
  permissions.py   App-specific permission classes
  filters.py        django-filter FilterSets (where applicable)
  urls.py
  admin.py
  tests.py
  migrations/
```

---

## Data Model Overview

- **User** — custom, email-based auth (`USERNAME_FIELD = "email"`). Every user has a `role`: `ADMIN`, `PM` (Project Manager), or `TM` (Team Member).
- **Organization** — top-level tenant. Has an `owner` and a `slug` auto-generated from its name. Membership is tracked via **OrganizationMember**.
- **Department** — belongs to an Organization, optionally has a `head` and a set of `members`.
- **Project** — optionally belongs to a Department, has an `owner` and a set of members via **ProjectMember**.
- **Task** — belongs to a Project, has `status` (`TODO` / `IN_PROGRESS` / `DONE`), `priority` (`LOW` / `MEDIUM` / `HIGH` / `CRITICAL`), an `assignee`, and a `created_by`.
- **Comment** — polymorphic via a generic relation; can attach to an Organization, Project, or Task. Supports one level of threaded replies and `@handle` mentions that are resolved to Users.

---

## Roles & Permissions Summary

- **ADMIN** — full access across all organizations, departments, projects, and tasks.
- **PM** — can create organizations, projects, and departments (for orgs they own); manages membership for resources they own.
- **TM** — can be added as a member of projects/departments/organizations by an owner or admin; can create and act on tasks within projects they belong to.

Access to a resource generally requires the requesting user to be the resource's **owner**, a **member**, or an **ADMIN** — enforced per-app via `permissions.py`.

---

## API Endpoints

All endpoints below are prefixed with `/api/` and require a `Authorization: Token <token>` header unless noted otherwise. Note that some resource paths repeat the app's URL prefix (e.g. comment detail is under `/api/comments/comments/<id>/`, project member routes are under `/api/projects/projects/<id>/members/`) — this reflects how the app-level `urls.py` files are currently structured.

### Auth (`apps/users`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/users/auth/register/` | none | Register a new user (`email`, `password`). Role always defaults to `TM`, regardless of what's submitted. |
| POST | `/api/users/auth/login/` | none | Log in with `email` + `password`, returns a token. |
| POST | `/api/users/auth/logout/` | token | Invalidates the current user's token. |
| GET | `/api/users/auth/me/` | token | Returns the authenticated user's profile. |

### Users (`apps/users`) — Admin only

| Method | Path | Description |
|---|---|---|
| GET | `/api/users/` | List all users. |
| GET | `/api/users/<id>/` | Retrieve a user. |
| PATCH | `/api/users/<id>/` | Update a user (e.g. change role). |
| DELETE | `/api/users/<id>/` | Soft-delete: sets `is_active=False`, does not remove the row. |

`POST` and `PUT` are disabled on this resource (`405 Method Not Allowed`).

### Organizations (`apps/organization`)

| Method | Path | Description |
|---|---|---|
| GET | `/api/organizations/` | List organizations the user owns, is a member of, or all of them if ADMIN. |
| POST | `/api/organizations/` | Create an organization (creator becomes owner). |
| GET | `/api/organizations/<id>/` | Retrieve an organization. |
| PUT/PATCH | `/api/organizations/<id>/` | Update — owner or admin only. |
| DELETE | `/api/organizations/<id>/` | Delete — owner or admin only. |

### Departments (`apps/department`) — nested under an organization

| Method | Path | Description |
|---|---|---|
| GET | `/api/organizations/<oid>/departments/` | List departments in the organization. |
| POST | `/api/organizations/<oid>/departments/` | Create a department — org owner or admin only. |
| GET | `/api/organizations/<oid>/departments/<id>/` | Retrieve a department. |
| PUT/PATCH | `/api/organizations/<oid>/departments/<id>/` | Update — org owner or admin only. |
| DELETE | `/api/organizations/<oid>/departments/<id>/` | Delete — org owner or admin only. |
| GET | `/api/organizations/<oid>/departments/<id>/projects/` | List projects linked to this department. |

### Projects (`apps/projects`)

| Method | Path | Description |
|---|---|---|
| GET | `/api/projects/` | List projects the user owns, is a member of, or all if ADMIN. Supports filtering by `name`, `owner`, `created_after`, `created_before`. |
| POST | `/api/projects/` | Create a project — ADMIN or PM only. |
| GET | `/api/projects/<id>/` | Retrieve a project. |
| PUT/PATCH | `/api/projects/<id>/` | Update — owner or admin only. |
| DELETE | `/api/projects/<id>/` | Delete — owner or admin only. |
| GET | `/api/projects/projects/<id>/members/` | List a project's members. |
| POST | `/api/projects/projects/<id>/members/` | Add a member — project owner or admin only. |
| DELETE | `/api/projects/projects/<id>/members/<uid>/` | Remove a member — project owner or admin only. |

### Tasks (`apps/tasks`)

| Method | Path | Description |
|---|---|---|
| GET | `/api/tasks/` | List tasks in projects the user belongs to (all tasks if ADMIN). Supports filtering by `title`, `status`, `priority`, `assignee`, `project`, `due_date_min`, `due_date_max`. |
| POST | `/api/tasks/` | Create a task — any project member, owner, or admin. |
| GET | `/api/tasks/<id>/` | Retrieve a task. |
| PUT/PATCH | `/api/tasks/<id>/` | Update — project owner, task creator, assignee, or admin. |
| DELETE | `/api/tasks/<id>/` | Delete — task creator or admin only. |

### Comments (`apps/comments`)

| Method | Path | Description |
|---|---|---|
| GET | `/api/comments/` | List root comments. Filter with `target_type` (`organization` / `project` / `task`) + `target_id`, or `parent` to list replies to a comment. |
| POST | `/api/comments/` | Create a root comment (`target_type` + `target_id` required) or a reply (`parent` required). One level of reply nesting is supported. `@handle` mentions in the body are parsed and linked automatically. |
| GET | `/api/comments/comments/<id>/` | Retrieve a comment. |
| PUT/PATCH | `/api/comments/comments/<id>/` | Update — comment author or admin only. |
| DELETE | `/api/comments/comments/<id>/` | Delete — comment author or admin only. |

All comment access additionally requires the requester to be a member of the underlying organization/project/task the comment is attached to.

---

## API Testing

A ready-to-use [Bruno](https://www.usebruno.com/) collection is included under `./bruno`, covering auth, projects, tasks, departments, and comments. Import the `bruno/` folder into Bruno and select the `local` environment (`bruno/environments/local.bru`) to exercise the API without writing requests by hand.

---

## Configuration Reference

| Setting | Source | Notes |
|---|---|---|
| `SECRET_KEY` | `.env` | Required, no default. |
| `DEBUG` | `.env` | Defaults to `False` if unset. |
| `ALLOWED_HOSTS` | `.env` | Comma-separated list; defaults to `[]`. |
| `DATABASE_URL` | `.env` | Parsed by `django-environ`; must point at a PostgreSQL instance. |
| `AUTH_USER_MODEL` | `config/settings.py` | `users.User` |