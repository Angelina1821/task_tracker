from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    login = Column(String(30), unique=True, nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"))
    password = Column(String(255), nullable=False)
    last_active = Column(DateTime(timezone= True), server_default=func.now())

    tasks = relationship("Task", back_populates="user")
    role = relationship("Role", back_populates="users")

class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True)
    descr = Column(String(20), nullable=False, unique=True)

    users = relationship("User", back_populates="role")

class Category(Base):
    __tablename__ = "categories"

    categ_id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False, unique=True)

    tasks = relationship("Task", back_populates="category")

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    categ_id = Column(Integer, ForeignKey("categories.categ_id"))
    created = Column(DateTime(timezone=True), server_default=func.now())
    deadline = Column(DateTime(timezone=True))
    status_id = Column(Integer, ForeignKey("status.status_id"), default=1)
    title = Column(String(100), nullable=False)
    descr = Column(Text)

    user = relationship("User", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
    status = relationship("Status", back_populates="tasks")
    history = relationship("History", back_populates="task")

class Status(Base):
    __tablename__ = "status"

    status_id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False, unique=True)

    tasks = relationship("Task", back_populates="status")

class History(Base):
    __tablename__ = "history"

    history_id = Column(Integer, primary_key=True)
    from_status = Column(Integer, ForeignKey("status.status_id"))
    to_status = Column(Integer, ForeignKey("status.status_id"))
    transformed = Column(DateTime(timezone=True), server_default=func.now())
    task_id = Column(Integer, ForeignKey("tasks.task_id"))

    task = relationship("Task", back_populates="history")
    from_status_obj = relationship("Status", foreign_keys=[from_status])
    to_status_obj = relationship("Status", foreign_keys=[to_status])