from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.services.events.router import router as events_router
from app.services.users.router import router as users_router
from app.services.tasks.router import router as tasks_router

app = FastAPI(
    title="Edu Events Platform API",
    description="API for managing educational events, users, and tasks",
    version="1.0.0",
    docs_url="/docs",  
    redoc_url="/redoc",  
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  
        "docExpansion": "none"  
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

app.include_router(events_router, prefix="/events", tags=["Events"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])

register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={
        "models": [
            "app.models.event",
            "app.models.user", 
            "app.models.task"
        ]
    },
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
