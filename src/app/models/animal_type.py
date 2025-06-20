"""
AnimalType model for managing different types of animals.
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel

class AnimalType(BaseModel):
    """
    Represents a type of animal (e.g., Cattle, Sheep, Horses).
    """
    __tablename__ = 'animal_type'
    
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    animals = relationship('Animal', back_populates='animal_type')
    
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
    
    def __repr__(self):
        return f"<AnimalType {self.name}>"
    
    def to_dict(self, include_relationships=False):
        """Convert to dictionary representation.
        
        Args:
            include_relationships: Whether to include related animals
            
        Returns:
            Dictionary representation of the animal type
        """
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relationships:
            result['animals'] = [animal.to_dict(include_relationships=False) for animal in self.animals]
            
        return result
