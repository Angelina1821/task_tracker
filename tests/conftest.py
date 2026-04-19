# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User, Role, Status
from app.api.auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/task_tracker_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Создаём таблицы и начальные данные один раз
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        # Роли
        if db.query(Role).count() == 0:
            db.add_all([Role(role_id=1, descr="admin"), Role(role_id=2, descr="user")])
        
        # Статусы
        if db.query(Status).count() == 0:
            db.add_all([
                Status(status_id=1, title="Новая"),
                Status(status_id=2, title="В работе"),
                Status(status_id=3, title="Сделано")
            ])
        db.commit()
    finally:
        db.close()
    
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="function")
def test_user(db):
    """Создаёт тестового пользователя (не удаляет)"""
    user = db.query(User).filter(User.login == "testuser").first()
    if not user:
        user = User(
            name="Test User",
            login="testuser",
            password=get_password_hash("testpass123"),
            role_id=2
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
    