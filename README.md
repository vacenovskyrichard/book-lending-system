# Book Lending System

REST API for managing books and loans, built with `FastAPI`, `SQLAlchemy`, `PostgreSQL`, and `Alembic`.

This project is intended to be run with Docker.

## Architecture

The project is split into clear layers:

- `api` contains HTTP routers.
- `services` contains business logic.
- `repositories` handles database access.
- `models/db` contains SQLAlchemy models.
- `models/schemas` contains Pydantic schemas.
- `alembic` manages database migrations.

This structure makes it easy to extend the system later with entities such as `authors`, `fines`, `reservations`, or additional audit tables.

## Domain Design

- `users`: library readers.
- `books`: bibliographic book records.
- `book_copies`: concrete physical copies of each book.
- `loans`: loan and return history.

Separating `books` and `book_copies` allows the system to support multiple copies of the same title without changing the API design.

## API Endpoints

### Users

- `POST /api/users`
- `GET /api/users`
- `GET /api/users/{user_id}`

### Books

- `POST /api/books`
- `GET /api/books`
- `GET /api/books/{book_id}`

Optional query parameter:

- `available_only=true` returns only books with at least one available copy.

### Loans

- `POST /api/loans/borrow`
- `POST /api/loans/return`
- `GET /api/loans`

Required header for both borrowing and returning:

- `x-user-id: <USER_ID>`

The `user_id` is not sent in the request body, matching the assignment requirements.

## Run With Docker

Start the full stack:

```bash
docker compose up --build
```

The API will be available at [http://localhost:8000](http://localhost:8000).

Swagger UI is available at [http://localhost:8000/docs](http://localhost:8000/docs).

Stop the application:

```bash
docker compose down
```

Remove containers and database volume:

```bash
docker compose down -v
```

## Tests

Run the test suite inside Docker:

```bash
docker compose run --rm api uv run pytest
```

The tests use a separate in-memory SQLite database, so PostgreSQL does not need to be running just to verify the main API scenarios.

## Pre-commit

If you want lightweight Git checks before committing, the project includes a
[.pre-commit-config.yaml](C:/Users/richa/repos/book-lending-system/.pre-commit-config.yaml).

Install the development tools:

```bash
uv sync --dev
```

Install the Git hooks:

```bash
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

Run all configured checks manually:

```bash
uv run pre-commit run --all-files
```

The `pre-commit` hook runs fast repository hygiene checks.
The `pre-push` hook runs `pytest` through Docker to keep the main verification path consistent with the project setup.

## Example Requests

### Create User

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Jan Novak","email":"jan.novak@example.com"}'
```

### Create Book With 3 Copies

```bash
curl -X POST http://localhost:8000/api/books \
  -H "Content-Type: application/json" \
  -d '{"title":"1984","author":"George Orwell","copies_count":3}'
```

### Borrow Book

```bash
curl -X POST http://localhost:8000/api/loans/borrow \
  -H "Content-Type: application/json" \
  -H "x-user-id: 1" \
  -d '{"book_id":1}'
```

### Return Book

```bash
curl -X POST http://localhost:8000/api/loans/return \
  -H "Content-Type: application/json" \
  -H "x-user-id: 1" \
  -d '{"loan_id":1}'
```

## Extensibility Notes

- Adding a new entity means adding a DB model, schema, repository, service, router, and migration.
- Business logic stays outside routers, so the API layer remains thin.
- Loan history remains preserved even after a book is returned.
