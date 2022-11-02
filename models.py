from sqlalchemy import Column, Integer, VARCHAR, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

eng = create_engine("sqlite:///taskmanager.db", echo=True)

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key = True, index = True)
    name = Column(VARCHAR)
    user_name = Column(VARCHAR)
    email = Column(VARCHAR)
    password = Column(VARCHAR)
    created_at = Column(DateTime)
    
    task_user = relationship("Task", back_populates = "user_task")

#task table stores the task detail of a user
class Task(Base):
    __tablename__="task"
    task_id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer ,ForeignKey("user.user_id") )
    task_name = Column(VARCHAR)
    is_deleted = Column(Integer)
    created_at = Column(DateTime)

    user_task = relationship("User", back_populates = "task_user")

session = sessionmaker(bind=eng)

Base.metadata.create_all(eng)

