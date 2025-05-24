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

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database settings
DATABASE_URL=sqlite://db.sqlite3

# JWT settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram settings
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_BOT_USERNAME=your-bot-username
```

## API Documentation

### Authentication

#### Register User

- **Endpoint**: `/api/auth/register`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe",
    "telegram_id": "@username" // or numeric ID
  }
  ```
- **Response**:
  ```json
  {
    "message": "User registered successfully"
  }
  ```

#### Login

- **Endpoint**: `/api/auth/login`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
    "token": "jwt_token_here",
    "token_type": "bearer",
    "is_admin": false,
    "user_id": 1,
    "email": "user@example.com",
    "telegram_id": "@username"
  }
  ```

#### Get User Profile

- **Endpoint**: `/api/users/profile`
- **Method**: GET
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "student",
    "avatarUrl": "https://example.com/avatar.jpg",
    "about": "About me",
    "location": "New York",
    "telegram_id": "@username",
    "joinedAt": "2024-03-20T12:00:00Z"
  }
  ```

## Telegram Integration

The platform supports Telegram integration for notifications and updates. Users can register with their Telegram ID or username, which must follow these rules:

1. Username format: Must start with @ and be 5-32 characters long, containing only letters, numbers, and underscores
2. Numeric ID: Must be a positive number

## Development

1. Create and activate a virtual environment:

   ```bash
   python -m venv myenv
   source myenv/bin/activate  # Linux/Mac
   myenv\Scripts\activate     # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:

   ```bash
   python -m app.scripts.run_migrations
   ```

4. Start the server:
   ```bash
   python -m app.main
   ```

## Testing

Run tests with:

```bash
pytest
```
