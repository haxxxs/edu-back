from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.services.events.router import router as events_router
from app.services.users.router import router as users_router
from app.services.tasks.router import router as tasks_router
from app.services.calendar.router import router as calendar_router
from app.services.courses.router import router as courses_router
from app.services.auth.router import router as auth_router
from app.services.admin.router import router as admin_router
from app.core.config import DATABASE_URL, TORTOISE_ORM

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
app.include_router(calendar_router, prefix="/calendar", tags=["Calendar"])
app.include_router(courses_router, prefix="/api/education/courses", tags=["Education Courses"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication & Profile"])
app.include_router(admin_router, prefix="/api/admin", tags=["Administration"])

print(TORTOISE_ORM)

register_tortoise(app, generate_schemas=True, add_exception_handlers=True, config=TORTOISE_ORM)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
