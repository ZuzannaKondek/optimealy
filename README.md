# OptiMeal - Meal Planning Optimization

A full-stack meal planning application that uses mathematical optimization to create personalized meal plans based on nutritional targets, dietary preferences, and pantry inventory.

## Tech Stack

### Frontend (app/)
- **Framework**: React Native with Expo SDK 54
- **Language**: TypeScript
- **Navigation**: React Navigation 6
- **State**: Zustand + React Context
- **HTTP**: Axios

### Backend (backend/)
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy async
- **Optimization**: OR-Tools CP-SAT Solver
- **Auth**: JWT + bcrypt

### Shared
- TypeScript API contracts

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend local development)

### Setup

1. **Clone the repository**
   ```bash
   cd optimealy
   ```

2. **Start the database and backend**
   ```bash
   docker compose up -d
   ```

3. **Seed the database with sample data**
   ```bash
   # Option A: Using the convenience script (from project root)
   cd backend && chmod +x scripts/setup_db.sh && ./scripts/setup_db.sh
   
   # Option B: Run seed manually inside container
   docker compose exec backend python scripts/run_seed.py
   
   # Option C: Run seed locally (with Python virtualenv)
   cd backend
   uv sync
   python scripts/run_seed.py
   ```

4. **Start the backend** (already running via Docker)
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Start the frontend**
   ```bash
   cd app
   npm install
   npx expo start
   ```

## Project Structure

```
optimealy/
├── app/                    # React Native mobile app
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── screens/        # Screen components
│   │   ├── services/      # API layer
│   │   ├── hooks/         # Custom hooks
│   │   ├── context/       # React Context
│   │   └── navigation/    # Navigation config
│   └── App.tsx
│
├── backend/                # FastAPI backend
│   ├── src/
│   │   ├── api/           # REST endpoints
│   │   ├── services/      # Business logic
│   │   ├── models/        # Database models
│   │   ├── core/          # Config, security
│   │   └── database/      # DB connection
│   ├── data/              # Seed data
│   ├── scripts/           # Utility scripts
│   └── pyproject.toml
│
├── shared/                 # Shared types
│   └── types/
│       └── api-contracts.ts
│
└── docker-compose.yml      # Docker services
```

## Development

### Backend

```bash
cd backend

# Run with hot reload
uvicorn src.main:app --reload

# Run tests
pytest

# Run linter
ruff check .
```

### Frontend

```bash
cd app

# Start Expo
npx expo start

# Run on iOS
npx expo start --ios

# Run on Android
npx expo start --android

# Run tests
npm test
```

## Database

### Running Migrations

```bash
# Inside Docker
docker compose exec backend alembic upgrade head

# Locally
cd backend
alembic upgrade head
```

### Seeding Data

The seed script populates the database with:
- **Products**: ~50 common ingredients with nutritional data
- **Recipes**: ~30 recipes with ingredients and instructions

```bash
# Run seed
python scripts/run_seed.py
```

### Database Scripts

- `scripts/run_seed.py` - Seed database with sample data
- `scripts/setup_db.sh` - Full database setup (migrations + seed)

## API Documentation

Once the backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Features

- **Meal Plan Optimization**: Create personalized meal plans using OR-Tools CP-SAT solver
- **Nutritional Targets**: Set daily calories, protein, carbs, and fat goals
- **Pantry Management**: Track available ingredients
- **Grocery Lists**: Auto-generate shopping lists from meal plans
- **Dietary Preferences**: Filter by cuisine, dietary tags (vegan, gluten-free, etc.)

## License

Private project - All rights reserved.
