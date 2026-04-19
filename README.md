
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
SECRET_KEY=63f4945d921d599f27ae4fdf5bada3f1
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
# 4. Запустить
uvicorn app.main:app --reload

Открыть: http://localhost:8000/docs