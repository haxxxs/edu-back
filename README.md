# Edu Events Platform Backend

## Project Structure
```
app/
├── main.py               # FastAPI application entry point
├── core/                 # Core utilities and configurations
├── models/               # Database models using Tortoise ORM
│   ├── event.py
│   ├── user.py
│   └── task.py
├── schemas/              # Pydantic schemas for request/response validation
│   ├── event.py
│   ├── user.py
│   └── task.py
└── services/             # Microservices with individual routers
    ├── events/
    ├── users/
    └── tasks/
```

## Setup and Running
1. Create a virtual environment
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
uvicorn app.main:app --reload
```

## API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
  - Interactive API documentation
  - Try out endpoints directly in the browser
- **ReDoc**: `http://localhost:8000/redoc`
  - Alternative, more readable documentation

## API Endpoints
- `/events/`: Event management
- `/users/`: User management
- `/tasks/`: Task management
- `/health`: Health check endpoint

## Development Notes
- Uses FastAPI for API development
- Tortoise ORM for database interactions
- Async programming paradigm
- Modular microservices architecture
