from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, tasks, analytics
from app.database import engine, Base, SessionLocal
from app.models import Role, Status
from app.config import settings

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Функция для добавления начальных данных
def init_db():
    db = SessionLocal()
    try:
        # Добавляем роли, если их нет
        if db.query(Role).count() == 0:
            roles = [
                Role(role_id=1, descr="admin"),
                Role(role_id=2, descr="user")
            ]
            db.add_all(roles)
            db.commit()
            print("Добавлены роли: admin, user")
        
        # Добавляем статусы, если их нет
        if db.query(Status).count() == 0:
            statuses = [
                Status(status_id=1, title="Новая"),
                Status(status_id=2, title="В работе"),
                Status(status_id=3, title="Сделано")
            ]
            db.add_all(statuses)
            db.commit()
            print("Добавлены статусы: Новая, В работе, Сделано")
    
    finally:
        db.close()

# Вызываем инициализацию БД
init_db()

app = FastAPI(
    title="Task Tracker API",
    description="A powerful task tracking system with analytics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)
# app.include_router(analytics.router)  # раскомментируй, когда добавишь analytics

@app.get("/")
def root():
    return {
        "message": "Welcome to Task Tracker API",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/auth/register, /auth/login",
            "tasks": "/tasks (GET, POST, PUT, DELETE)",
            # "analytics": "/analytics/status-distribution, /analytics/summary, /analytics/visualizations"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}