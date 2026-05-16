# Football AI Platform

AI-powered football analysis and prediction system.

## Project Structure

```
football-ai/
├── backend/              # FastAPI backend application
│   ├── api/              # API routes and WebSocket endpoints
│   ├── core/             # Core utilities (config, constants, exceptions)
│   ├── models/           # Pydantic data models
│   ├── repositories/     # Data access layer
│   ├── services/         # Business logic (AI, cache, notifications, recommendations)
│   ├── cli/              # CLI commands
│   └── utils/            # Utilities (logger, HTTP client)
├── frontend/             # Vue 3 + TypeScript frontend
│   └── src/
│       ├── components/   # Reusable Vue components
│       ├── views/        # Page components
│       ├── services/     # API service layer
│       ├── stores/       # Pinia state management
│       ├── router/       # Vue Router config
│       └── i18n/          # Internationalization
├── collector_service/    # Data collection service
│   └── src/collectors/   # News, match, transfer collectors
├── notification_service/ # Real-time notification service
├── admin_panel/          # Admin dashboard Vue app
├── data/                 # Data files and SQLite database
└── docker-compose.yml    # Container orchestration
```

## Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python cli/commands.py seed  # Initialize database with mock data
python cli/commands.py server  # Start API server
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # Start dev server on port 3000
```

### Docker
```bash
docker-compose up
```

## Configuration

Backend uses `config.yaml` (not .env). Key settings:
- `app.debug` - Enable debug mode
- `redis.*` - Redis connection settings
- `llm.provider` - "gemini" or "openai"
- `cache.enable` - Enable/disable Redis caching

## Key Technologies

- **Backend**: FastAPI, Pydantic, SQLite, Redis
- **Frontend**: Vue 3, TypeScript, Element Plus, ECharts, vue-i18n
- **AI**: Gemini/OpenAI for predictions
- **Data Collection**: httpx, BeautifulSoup, APScheduler

## Notes

- Original `config.py` and `models/` were in root; migrated to `backend/`
- Database uses SQLite at `data/football.db`
- WebSocket endpoint at `/ws/notifications`
- All services share Redis for caching and pub/sub