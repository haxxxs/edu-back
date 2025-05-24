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
from app.api.endpoints.courses import router as new_courses_router
from app.api.endpoints.course_content import router as course_content_router
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

# Custom OpenAPI schema for proper JWT auth in Swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token obtained from /api/auth/login"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

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
app.include_router(new_courses_router, prefix="/api", tags=["Courses"])
app.include_router(course_content_router, prefix="/api", tags=["Course Content"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication & Profile"])
app.include_router(admin_router, prefix="/api/admin", tags=["Administration"])

# Initialize Tortoise ORM
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
