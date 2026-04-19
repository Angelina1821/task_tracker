from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.models import Task, User, History, Category
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, CategoryCreate, CategoryResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_task = Task(
        **task.model_dump(),
        user_id=current_user.user_id,
        status_id=1  # new
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_id: Optional[int] = Query(None, ge=1, le=3),
    categ_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task).filter(Task.user_id == current_user.user_id)
    
    if status_id:
        query = query.filter(Task.status_id == status_id)
    if categ_id:
        query = query.filter(Task.category_id == category_id)
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.task_id == task_id,
        Task.user_id == current_user.user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.task_id == task_id,
        Task.user_id == current_user.user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    old_status = task.status_id
    
    for field, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    
    # Log status change to history
    if task_update.status_id is not None and old_status != task_update.status_id:
        history = History(
            task_id=task_id,
            from_status=old_status,
            to_status=task_update.status_id
        )
        db.add(history)
    
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.task_id == task_id,
        Task.user_id == current_user.user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}

@router.patch("/{task_id}/status")
def update_task_status(
    task_id: int,
    status_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.task_id == task_id,
        Task.user_id == current_user.user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    old_status = task.status_id
    task.status_id = status_id
    
    history = History(
        task_id=task_id,
        from_status=old_status,
        to_status=status_id
    )
    db.add(history)
    db.commit()
    
    return {"message": "Status updated successfully"}

# Category endpoints
@router.post("/categories", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()