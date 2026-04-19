"""
Тесты для аутентификации и пользователей
"""
import pytest

class TestAuth:
    """Тесты регистрации и логина"""
    
    def test_register_success(self, client):
        """Успешная регистрация нового пользователя"""
        response = client.post("/auth/register", json={
            "name": "Новый Пользователь",
            "login": "freshuser",
            "password": "securepass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["login"] == "freshuser"
        assert data["name"] == "Новый Пользователь"
        assert "user_id" in data
        assert "password" not in data  # Пароль не должен возвращаться
    
    def test_register_duplicate_login(self, client, test_user):
        """Регистрация с уже существующим логином - ошибка"""
        response = client.post("/auth/register", json={
            "name": "Другой Пользователь",
            "login": "testuser",  # Этот логин уже есть
            "password": "pass123"
        })
        assert response.status_code == 400
        assert "already registered" in response.text.lower()
    
    def test_register_short_password(self, client):
        """Регистрация с коротким паролем (<6 символов)"""
        response = client.post("/auth/register", json={
            "name": "User",
            "login": "shortpassuser",
            "password": "123"  # Слишком короткий
        })
        assert response.status_code == 422  # Validation error
    
    def test_login_success(self, client, test_user):
        """Успешный вход и получение токена"""
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """Вход с неправильным паролем"""
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "incorrect" in response.text.lower()
    
    def test_login_nonexistent_user(self, client):
        """Вход с несуществующим пользователем"""
        response = client.post("/auth/login", data={
            "username": "nouser",
            "password": "pass123"
        })
        assert response.status_code == 401
    
    def test_access_protected_endpoint_without_token(self, client):
        """Доступ к защищенному эндпоинту без токена"""
        response = client.get("/tasks/")
        assert response.status_code == 401  # Unauthorized
    
    def test_access_protected_endpoint_with_invalid_token(self, client):
        """Доступ с неверным токеном"""
        response = client.get("/tasks/", headers={"Authorization": "Bearer invalidtoken"})
        assert response.status_code == 401