"""
Base model class with common functionality for all models.
"""
from datetime import datetime, UTC
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, DateTime

Base = declarative_base()

class BaseModel(Base):
    """
    Abstract base model with common fields and methods.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), 
                       onupdate=lambda: datetime.now(UTC), nullable=False)
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"
