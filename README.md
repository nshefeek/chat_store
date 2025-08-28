# RAG Chat Storage Microservice

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A scalable and resilient backend microservice for managing chat sessions and messages in a Retrieval-Augmented Generation (RAG) chatbot system, specifically designed for a CLI-based coding assistant.

This service provides robust session management, handles interruptions gracefully, and allows for the resumption of conversations, optimizing resource usage and ensuring a seamless user experience.

## Key Features

- **Full Session Management**: Create, retrieve, rename, favorite, and delete chat sessions.
- **Persistent Message Storage**: Securely stores user prompts, AI responses, and the RAG context for each message.
- **Interruption & Resumption**: Handles client disconnects and LLM timeouts by tracking message status (`pending`, `in_progress`, `complete`, `failed`). Allows for resuming failed or pending messages without re-running the entire generation process.
- **Optimized LLM Usage**: Saves partial AI responses, allowing resumption from the point of failure, which significantly reduces redundant LLM calls and saves costs.
- **Scalable by Design**: Built with an asynchronous framework (FastAPI), async database drivers (`asyncpg`), connection pooling, and caching to handle high concurrency.
- **Secure**: Protects endpoints with API key authentication, rate limiting, and CORS policies.
- **Containerized**: Fully containerized with Docker Compose for easy setup, deployment, and portability across environments. Includes the main application, PostgreSQL, Redis, and pgAdmin.

## Tech Stack

- **Backend**: **FastAPI** for high-performance, asynchronous API development with automatic OpenAPI/Swagger documentation.
- **Database**: **PostgreSQL** for reliable and structured data storage, managed with the **SQLAlchemy** ORM.
- **Database Migrations**: **Alembic** for seamless schema versioning and updates.
- **Caching**: **Redis** for caching session data, RAG context, and partial responses to improve performance.
- **Testing**: **pytest** with `pytest-asyncio` for comprehensive unit and integration testing.
- **Packaging**: **uv** for fast and efficient Python package management.

## System Architecture

The service is designed as a synchronous API but is architected for a seamless transition to an Event-Driven Architecture (EDA).

1.  **Prompt Ingestion**: When a user sends a prompt, it's immediately stored in the database with a `pending` status, along with any RAG context. This ensures no data is lost.
2.  **Streaming & Status Updates**: As the LLM generates a response, the service stores partial content and updates the message status to `in_progress`. Upon completion, the status becomes `complete`. If an error occurs, it's marked as `failed` with an error message.
3.  **Resumption Flow**: The `/resume` endpoint checks the last message for a session. If its status is `pending` or `failed`, it re-triggers the generation process using the saved context and partial content, avoiding costly re-computation.

This design ensures data integrity and operational resilience, which is critical for a stateful application like a chatbot.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ and `uv` (for local development)

### Docker Setup (Recommended)

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd chat_store
    ```

2.  **Create Environment File**:
    Copy the example `.env.example` to `.env`.
    ```bash
    cp .env.example .env
    ```

3.  **Configure `.env`**:
    Update the `.env` file with your credentials.
    ```ini
    # PostgreSQL Settings
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=your-super-secure-password
    POSTGRES_DB=chat_store

    # Database URL for the application
    DATABASE_URL=postgresql+asyncpg://postgres:your-super-secure-password@db:5432/chat_store

    # Redis URL
    REDIS_URL=redis://redis:6379/0

    # API Security
    API_KEY=your-secret-api-key

    # pgAdmin Settings
    PGADMIN_DEFAULT_EMAIL=admin@example.com
    PGADMIN_DEFAULT_PASSWORD=admin
    ```

4.  **Launch Services**:
    ```bash
    docker-compose up -d --build
    ```

5.  **Access Services**:
    - **API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
    - **pgAdmin**: [http://localhost:8080](http://localhost:8080)

### Local Development Setup

1.  **Install Dependencies**:
    ```bash
    uv pip sync
    ```

2.  **Run PostgreSQL and Redis**:
    Ensure you have local instances of PostgreSQL and Redis running.

3.  **Configure `.env`**:
    Update `DATABASE_URL` and `REDIS_URL` to point to your local services.

4.  **Run Database Migrations**:
    The application entrypoint handles this, but you can run them manually if needed:
    ```bash
    alembic upgrade head
    ```

5.  **Start the Server**:
    ```bash
    uvicorn src.main:app --reload
    ```

## API Documentation

All endpoints are prefixed with `/api/v1` and require an API key for authentication.

### Authentication

Provide your API key in the `Authorization` header.

```
Authorization: Bearer your-secret-api-key
```

### Endpoints

#### Sessions
- `POST /sessions`: Create a new chat session.
- `GET /sessions`: List all sessions for a user (paginated).
- `PUT /sessions/{session_id}`: Rename a session.
- `PATCH /sessions/{session_id}/favorite`: Toggle the favorite status of a session.
- `DELETE /sessions/{session_id}`: Delete a session and all its messages.

#### Messages
- `POST /sessions/{session_id}/messages`: Add a new message to a session.
- `GET /sessions/{session_id}/messages`: Get all messages for a session (paginated).
- `POST /sessions/{session_id}/resume`: Resume a failed or pending message generation.

#### Health Check
- `GET /health`: Check the health of the service.

## Database Schema

### `sessions` Table
| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary Key |
| `user_id` | String | User identifier (indexed) |
| `name` | String | Session name |
| `is_favorite` | Boolean | Favorite status |
| `created_at` | Timestamp | |
| `updated_at` | Timestamp | |

### `messages` Table
| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary Key |
| `session_id` | UUID | Foreign key to `sessions` |
| `sender` | Enum | 'user' or 'ai' |
| `content` | Text | The message content |
| `context` | JSONB | Stores RAG context data |
| `status` | Enum | 'pending', 'in_progress', 'complete', 'failed' |
| `partial_content` | Text | For resuming incomplete AI responses |
| `error_message` | Text | Details on generation failure |
| `timestamp` | Timestamp | |

## Development

### Project Structure

```
chat_store/
├── alembic/              # Database migrations
├── docker/               # Docker helper scripts
├── scripts/              # Utility scripts
├── src/                  # Source code
│   ├── api/              # API endpoints and routers
│   ├── core/             # Configuration, logging, security
│   ├── db/               # Database session management
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Business logic
├── tests/                # Unit and integration tests
├── alembic.ini           # Alembic configuration
├── compose.yml           # Docker Compose definition
├── Dockerfile            # Application container definition
├── pyproject.toml        # Project metadata and dependencies
└── README.md
```

### Running Tests

Execute the full test suite with:
```bash
pytest
```
You can also run unit or integration tests separately:
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/
```

### Database Migrations

When you change a SQLAlchemy model:
1.  **Generate a new migration script**:
    ```bash
    alembic revision --autogenerate -m "Short description of model changes"
    ```
2.  **Apply the migration**:
    ```bash
    alembic upgrade head
    ```
The Docker entrypoint script automatically applies migrations on startup.

## Future Enhancements

- **Event-Driven Architecture**: Transition to a message broker (e.g., RabbitMQ, Kafka) for even greater scalability and decoupling of services.
- **WebSockets**: Implement WebSocket support for real-time updates to clients.
- **Advanced Caching**: Introduce more sophisticated caching strategies for frequently accessed data.
- **Message Search**: Add full-text search capabilities for message history.
- **Import/Export**: Allow users to export and import their chat sessions.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
