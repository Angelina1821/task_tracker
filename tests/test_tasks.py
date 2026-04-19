"""
Тесты для CRUD операций с задачами
"""
import pytest

class TestTasks:
    """Тесты для эндпоинтов задач"""
    
    def test_create_task_success(self, client, auth_headers):
        """Создание задачи - успех"""
        response = client.post("/tasks/", headers=auth_headers, json={
            "title": "Моя новая задача",
            "descr": "Подробное описание",
            "deadline": "2024-12-31T23:59:59"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Моя новая задача"
        assert data["descr"] == "Подробное описание"
        assert data["status_id"] == 1  # Статус "Новая"
        assert "task_id" in data
    
    def test_create_task_without_title(self, client, auth_headers):
        """Создание задачи без заголовка - ошибка"""
        response = client.post("/tasks/", headers=auth_headers, json={
            "descr": "Описание без заголовка"
        })
        assert response.status_code == 422  # Validation error
    
    def test_create_task_title_too_long(self, client, auth_headers):
        """Создание задачи с заголовком >100 символов"""
        response = client.post("/tasks/", headers=auth_headers, json={
            "title": "A" * 101,
            "descr": "Описание"
        })
        assert response.status_code == 422
    
    def test_get_tasks_list(self, client, auth_headers):
        """Получение списка всех задач"""
        # Создаем несколько задач
        client.post("/tasks/", headers=auth_headers, json={"title": "Задача 1"})
        client.post("/tasks/", headers=auth_headers, json={"title": "Задача 2"})
        
        response = client.get("/tasks/", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 2
        assert isinstance(tasks, list)
    
    def test_get_single_task(self, client, auth_headers):
        """Получение конкретной задачи по ID"""
        # Создаем задачу
        create_resp = client.post("/tasks/", headers=auth_headers, json={
            "title": "Задача для поиска",
            "descr": "Найти меня"
        })
        task_id = create_resp.json()["task_id"]
        
        # Получаем её
        response = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["title"] == "Задача для поиска"
    
    def test_get_nonexistent_task(self, client, auth_headers):
        """Получение несуществующей задачи"""
        response = client.get("/tasks/99999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_update_task(self, client, auth_headers):
        """Обновление задачи"""
        # Создаем
        create_resp = client.post("/tasks/", headers=auth_headers, json={
            "title": "Старый заголовок",
            "descr": "Старое описание"
        })
        task_id = create_resp.json()["task_id"]
        
        # Обновляем
        response = client.put(f"/tasks/{task_id}", headers=auth_headers, json={
            "title": "Новый заголовок",
            "descr": "Новое описание"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Новый заголовок"
        assert data["descr"] == "Новое описание"
    
    def test_update_task_status(self, client, auth_headers):
        """Изменение статуса задачи"""
        # Создаем
        create_resp = client.post("/tasks/", headers=auth_headers, json={
            "title": "Задача для смены статуса"
        })
        task_id = create_resp.json()["task_id"]
        
        # Меняем статус на "В работе" (2)
        response = client.patch(f"/tasks/{task_id}/status?status_id=2", headers=auth_headers)
        assert response.status_code == 200
        
        # Проверяем
        task_resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert task_resp.json()["status_id"] == 2
    
    def test_update_task_invalid_status(self, client, auth_headers):
        """Установка несуществующего статуса"""
        create_resp = client.post("/tasks/", headers=auth_headers, json={
            "title": "Тестовая задача"
        })
        task_id = create_resp.json()["task_id"]
        
        response = client.patch(f"/tasks/{task_id}/status?status_id=99", headers=auth_headers)
        assert response.status_code == 422  # Validation error
    
    def test_delete_task(self, client, auth_headers):
        """Удаление задачи"""
        # Создаем
        create_resp = client.post("/tasks/", headers=auth_headers, json={
            "title": "Задача на удаление"
        })
        task_id = create_resp.json()["task_id"]
        
        # Удаляем
        response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Проверяем, что задачи нет
        get_resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert get_resp.status_code == 404
    
    def test_delete_nonexistent_task(self, client, auth_headers):
        """Удаление несуществующей задачи"""
        response = client.delete("/tasks/99999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_get_tasks_with_filter(self, client, auth_headers):
        """Получение задач с фильтрацией по статусу"""
        # Создаем задачи с разными статусами
        task1 = client.post("/tasks/", headers=auth_headers, json={"title": "Новая задача"})
        task_id = task1.json()["task_id"]
        
        # Меняем статус на "Сделано" (3)
        client.patch(f"/tasks/{task_id}/status?status_id=3", headers=auth_headers)
        
        # Фильтруем по статусу "Сделано"
        response = client.get("/tasks/?status_id=3", headers=auth_headers)
        tasks = response.json()
        
        for task in tasks:
            assert task["status_id"] == 3
    
    def test_get_tasks_with_search(self, client, auth_headers):
        """Поиск задач по названию"""
        client.post("/tasks/", headers=auth_headers, json={"title": "Купить молоко"})
        client.post("/tasks/", headers=auth_headers, json={"title": "Сделать домашку"})
        
        response = client.get("/tasks/?search=молоко", headers=auth_headers)
        tasks = response.json()
        
        assert len(tasks) == 1
        assert "молоко" in tasks[0]["title"].lower()