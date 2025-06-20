"""
Animal model for managing individual animals and their genealogy.
"""
from datetime import date, datetime
from sqlalchemy import (
    Column, String, Date, Boolean, Text, ForeignKey, Integer, Enum, event
)
from sqlalchemy.orm import relationship, backref, validates
from sqlalchemy.ext.associationproxy import association_proxy
import json
import inspect

from .base import BaseModel

class Gender:
    """Gender enumeration for animals."""
    MALE = 'male'
    FEMALE = 'female'
    UNKNOWN = 'unknown'
    
    @classmethod
    def values(cls):
        """Return all valid gender values."""
        return [cls.MALE, cls.FEMALE, cls.UNKNOWN]

class Animal(BaseModel):
    """
    Represents an individual animal with genealogical information.
    """
    __tablename__ = 'animal'
    
    # Basic information
    identifier = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=True)
    gender = Column(
        Enum(Gender.MALE, Gender.FEMALE, Gender.UNKNOWN, 
             name='gender_enum'),
        default=Gender.UNKNOWN,
        nullable=False
    )
    date_of_birth = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    external_id = Column(String(50), nullable=True)
    metadata_json = Column(String(1000), nullable=True)  # Store JSON as string
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    type_id = Column(Integer, ForeignKey('animal_type.id'), nullable=False)
    animal_type = relationship('AnimalType', back_populates='animals')
    
    # Self-referential relationships for genealogy
    mother_id = Column(Integer, ForeignKey('animal.id'), nullable=True)
    father_id = Column(Integer, ForeignKey('animal.id'), nullable=True)
    
    # Relationships for parents/children
    mother = relationship(
        'Animal', 
        foreign_keys=[mother_id],
        remote_side='Animal.id',
        backref=backref('children_mother', lazy='dynamic'),
    )
    
    father = relationship(
        'Animal',
        foreign_keys=[father_id],
        remote_side='Animal.id',
        backref=backref('children_father', lazy='dynamic'),
    )
    
    # Convenience properties
    children = association_proxy('children_mother', 'children_father')
    
    @property
    def offspring(self):
        """Return a list of all child animals."""
        result = list(self.children_mother)
        result.extend([c for c in self.children_father if c not in result])
        return result
        
    @property
    def age(self):
        """Calculate the age in years."""
        if not self.date_of_birth:
            return 0
        today = date.today()
        # For test cases with future dates, return 0
        if self.date_of_birth > today:
            return 0
        # Calculate age, handling birthdays that haven't occurred yet this year
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def is_adult(self):
        """Determine if the animal is an adult (> 2 years old)."""
        return self.age >= 2
        
    @property
    def ancestors(self):
        """Return a list of all ancestor animals."""
        result = set()
        if self.mother:
            result.add(self.mother)
            result.update(self.mother.ancestors)
        if self.father:
            result.add(self.father)
            result.update(self.father.ancestors)
        return list(result)
        
    @property
    def descendants(self):
        """Return a list of all descendant animals."""
        result = set(self.offspring)
        for child in self.offspring:
            result.update(child.descendants)
        return list(result)
    
    def __init__(self, identifier, animal_type, **kwargs):
        self.identifier = identifier
        self.animal_type = animal_type
        
        # Validate gender (it's required)
        if 'gender' not in kwargs:
            raise ValueError(f"Gender is required. Must be one of {Gender.values()}")
        elif kwargs['gender'] not in Gender.values():
            raise ValueError(f"Invalid gender value. Must be one of {Gender.values()}")
        
        # Set other attributes from kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
        # Validate self-referential constraints
        if hasattr(self, 'id') and self.id is not None:
            if self.mother_id == self.id:
                raise ValueError("An animal cannot be its own mother.")
            if self.father_id == self.id:
                raise ValueError("An animal cannot be its own father.")
    
    # Add validation for circular references
    @validates('mother_id', 'father_id')
    def validate_parent(self, key, value):
        """Validate parent-child relationships to prevent circular references."""
        if value is None:
            return value
            
        # Prevent self-reference
        if hasattr(self, 'id') and value == self.id:
            raise ValueError(f"An animal cannot be its own {key.split('_')[0]}.")
        
        # Check for circular references (where an animal is set as a parent of one of its ancestors)
        # This validation needs to use the database session to check existing relationships
        from sqlalchemy.orm import object_session
        session = object_session(self)
        
        if session and hasattr(self, 'id') and self.id is not None:
            # Get the potential parent animal
            potential_parent = session.get(Animal, value)
            if potential_parent:
                # Check if this would create a circular reference
                # Method 1: Check if we're already a parent of this animal directly
                if potential_parent.mother_id == self.id or potential_parent.father_id == self.id:
                    raise ValueError("Circular parentage reference detected.")
                    
                # Method 2: Check through the ancestry chain
                # Here we're checking if the potential parent is already a descendant of this animal
                ancestors_to_check = [value]  # Start with the direct parent
                checked_ids = set()  # Track checked IDs to avoid infinite loops
                
                while ancestors_to_check:
                    current_id = ancestors_to_check.pop(0)
                    if current_id in checked_ids:
                        continue  # Skip already checked IDs
                        
                    checked_ids.add(current_id)
                    current = session.get(Animal, current_id)
                    
                    if not current:
                        continue
                    
                    # Check if any descendants include this animal (creating a cycle)
                    for descendant in session.query(Animal).filter(
                        (Animal.mother_id == current.id) | (Animal.father_id == current.id)
                    ).all():
                        if descendant.id == self.id:
                            raise ValueError("Circular parentage reference detected.")
                        ancestors_to_check.append(descendant.id)
            
        return value
        
    def __repr__(self):
        return f"<Animal {self.identifier}>"
    
    def to_dict(self, include_relationships=False, fields=None):
        """Convert to dictionary representation.
        
        Args:
            include_relationships: Whether to include related objects
            fields: List of specific fields to include
            
        Returns:
            Dictionary representation of the animal
        """
        # Base dictionary with all fields
        base_dict = {
            'id': self.id,
            'identifier': self.identifier,
            'name': self.name,
            'gender': self.gender.upper() if hasattr(self.gender, 'upper') else self.gender,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'description': self.description,
            'notes': self.notes,
            'is_active': self.is_active,
            'animal_type_id': self.type_id,
            'mother_id': self.mother_id,
            'father_id': self.father_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'age': self.age,
            'external_id': getattr(self, 'external_id', None),
            'metadata_json': json.loads(self.metadata_json) if self.metadata_json and isinstance(self.metadata_json, str) else self.metadata_json
        }
        
        # Include relationships if requested
        if include_relationships:
            base_dict['mother'] = self.mother.to_dict(include_relationships=False) if self.mother else None
            base_dict['father'] = self.father.to_dict(include_relationships=False) if self.father else None
            base_dict['animal_type'] = self.animal_type.to_dict() if self.animal_type else None
        
        # Filter by specific fields if provided
        if fields:
            return {k: v for k, v in base_dict.items() if k in fields}
        
        return base_dict
    
    def get_parents(self):
        """Return a list of parent animals."""
        parents = []
        if self.mother:
            parents.append(('mother', self.mother))
        if self.father:
            parents.append(('father', self.father))
        return parents
    
    def get_children(self):
        """Return a list of child animals."""
        # This will return a union of children from both mother and father relationships
        children = []
        for child in self.children_mother:
            children.append(('mother', child))
        for child in self.children_father:
            children.append(('father', child))
        return children
