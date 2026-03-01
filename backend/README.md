# OptiMeal Backend

Backend service for OptiMeal meal planning optimization application.

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Optimization**: OR-Tools (CP-SAT Solver)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Package Manager**: uv
- **Testing**: pytest, pytest-cov
- **Type Checking**: mypy (strict mode)
- **Linting**: ruff

## Project Structure

```
backend/
├── src/
│   ├── api/              # API endpoints
│   ├── core/             # Core configuration, security
│   ├── database/         # Database connection, session management
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic and optimization
│   └── main.py           # FastAPI application entry point
├── tests/                # Unit and integration tests
├── data/                 # Seed data (recipes, products)
├── alembic/              # Database migrations
├── pyproject.toml        # Project configuration
├── .python-version       # Python version specification
└── Dockerfile            # Docker build configuration
```

## Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 16+
- uv package manager (`pip install uv`)

### Installation

1. **Install dependencies**:
   ```bash
   cd backend
   uv sync
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start PostgreSQL** (using Docker Compose from project root):
   ```bash
   cd ..
   docker-compose up -d db
   ```

4. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Seed the database** (optional but recommended):
   ```bash
   python -m src.database.seed
   ```

6. **Run the development server**:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000` and API docs at `http://localhost:8000/docs`.

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_optimization.py

# Run with verbose output
pytest -v
```

### Type Checking

```bash
mypy src/
```

### Linting

```bash
# Check code
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Code Quality Gates

Before committing, ensure:
- [x] All tests pass (`pytest`)
- [x] Test coverage ≥80% for optimization code
- [x] No type errors (`mypy src/`)
- [x] No linting errors (`ruff check .`)
- [x] Code is formatted (`ruff format .`)

## Docker

### Build Image

```bash
docker build -t optimealy-backend .
```

### Run Container

```bash
docker-compose up backend
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Key Endpoints

- **Authentication**: `/api/v1/auth/*`
- **Meal Plans**: `/api/v1/plans/*`
- **Grocery Lists**: `/api/v1/grocery/*`
- **Health Check**: `/health`

## Database

### Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Seeding Data

The `backend/data/` directory contains:
- `recipes/sample-recipes.json`: Recipe database
- `products/sample-products.json`: Product/ingredient database

Run seeding script:
```bash
python -m src.database.seed
```

## Optimization Algorithm

The core optimization algorithm uses OR-Tools CP-SAT solver to:
1. Minimize food waste (primary objective)
2. Meet nutritional constraints (±5% calories, ±10% macros)
3. Respect user preferences (exclude allergens, use available ingredients)
4. Ensure recipe variety (no repeats within 3 days)
5. Complete within 60 seconds

See `src/services/optimization/` for implementation details.

## Contributing

1. Create a feature branch
2. Make changes
3. Run quality checks (tests, mypy, ruff)
4. Submit pull request

For detailed guidelines, see the project constitution: `../.specify/memory/constitution.md`

## License

Private project - All rights reserved.
