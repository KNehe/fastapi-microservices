# FastAPI Microservices

A hands-on tutorial series on building microservices with **FastAPI**, **SQLModel**, **Docker**, and **PostgreSQL**.

📺 **YouTube Playlist:** [Building Microservices with FastAPI](https://www.youtube.com/playlist?list=PLdtwawCR2QjlCvbu2WJ-8EiJNHmJuprvT)

## What You'll Learn

- Setting up a Python monorepo with **uv workspaces**
- Building REST APIs with **FastAPI**
- Database modeling with **SQLModel** (SQLAlchemy + Pydantic)
- Containerizing services with **Docker** (multi-stage builds)
- Orchestrating multiple services with **Docker Compose**
- Connecting to **PostgreSQL** in production with SQLite fallback for local dev

## Tech Stack

- **Python 3.12**
- **FastAPI** — Web framework
- **SQLModel** — ORM & data validation
- **PostgreSQL** — Database
- **Docker & Docker Compose** — Containerization
- **uv** — Package & project management

## Project Structure

```
fastapi-microservices/
├── compose.yaml                 # Docker Compose (services + database)
├── pyproject.toml               # Workspace root
└── services/
    └── user-service/            # User management microservice
        ├── Dockerfile
        ├── main.py
        ├── models.py
        └── db.py
```

## Getting Started

### Prerequisites

- [Python 3.12+](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/)
- [Docker](https://www.docker.com/) (for running with PostgreSQL)

### Run Locally (SQLite)

```bash
uv sync --package user-service
fastapi dev services/user-service/main.py
```

The API will be available at `http://localhost:8000`.

### Run with Docker (PostgreSQL)

```bash
docker compose up --build
```

The API will be available at `http://localhost:8001`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/` | Create a new user |
| `GET`  | `/users/` | List all users |

## Tutorial Progress

| Day | Topic | Status |
|-----|-------|--------|
| Day 2 | Project setup & FastAPI scaffolding | ✅ |
| Day 3 | SQLModel, database & CRUD endpoints | ✅ |
| Day 4 | Docker, Compose & PostgreSQL | ✅ |

## License

This project is for educational purposes. Feel free to use it as a reference for your own projects.
