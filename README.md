
```markdown
## Запуск

```bash
# 1. Запустить PostgreSQL
docker-compose up -d

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Создать .env и заполнить
cp .env.example .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/task_tracker
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
# 4. Запустить
uvicorn app.main:app --reload

Открыть: http://localhost:8000/docs

__________
#Тестирование

## 1. Установка

```bash
pip install pytest pytest-cov httpx

##2. Создание тестовой бд
```bash
docker exec -it task_tracker_db psql -U postgres -c "CREATE DATABASE task_tracker_test;"

## 3. Запуск тестов
```bash
pytest -v



