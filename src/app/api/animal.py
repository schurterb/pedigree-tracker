"""
Animal API resource for managing animals and their genealogical data.
"""
from datetime import datetime, date
from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from ..models import Animal, AnimalType, Gender
from ..database import get_db

# Create namespace
ns = Namespace('animals', description='Animal operations')

# Request/response models
animal_model = ns.model('Animal', {
    'id': fields.Integer(readOnly=True, description='The animal unique identifier'),
    'identifier': fields.String(required=True, description='Unique identifier (e.g., tag number)'),
    'name': fields.String(description='Name of the animal'),
    'gender': fields.String(enum=Gender.values(), description='Gender of the animal'),
    'date_of_birth': fields.Date(description='Date of birth (YYYY-MM-DD)'),
    'description': fields.String(description='Description of the animal'),
    'notes': fields.String(description='Additional notes'),
    'is_active': fields.Boolean(description='Whether the animal is active'),
    'type_id': fields.Integer(required=True, description='Animal type ID'),
    'animal_type': fields.Nested(ns.model('AnimalTypeRef', {
        'id': fields.Integer,
        'name': fields.String
    }), attribute='animal_type'),
    'mother_id': fields.Integer(description='Mother animal ID'),
    'father_id': fields.Integer(description='Father animal ID'),
    'created_at': fields.DateTime(readOnly=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(readOnly=True, description='Last update timestamp')
})

# For creating/updating animals (excludes read-only fields)
animal_input_model = ns.inherit('AnimalInput', animal_model, {
    'identifier': fields.String(required=True, description='Unique identifier (e.g., tag number)'),
    'type_id': fields.Integer(required=True, description='Animal type ID'),
    'mother_id': fields.Integer(description='Mother animal ID'),
    'father_id': fields.Integer(description='Father animal ID'),
    'animal_type': None,  # Exclude from input
    'created_at': None,
    'updated_at': None
})

@ns.route('/')
class AnimalList(Resource):
    """Shows a list of all animals, and lets you POST to add new animals."""
    
    @ns.doc('list_animals')
    @ns.param('type_id', 'Filter by animal type ID')
    @ns.param('active', 'Filter by active status (true/false)')
    @ns.param('search', 'Search term for name or identifier')
    @ns.marshal_list_with(animal_model)
    def get(self):
        """List all animals with optional filtering."""
        db = next(get_db())
        query = db.query(Animal).options(joinedload(Animal.animal_type))
        
        # Apply filters
        if 'type_id' in request.args:
            query = query.filter(Animal.type_id == request.args['type_id'])
        
        if 'active' in request.args:
            is_active = request.args['active'].lower() == 'true'
            query = query.filter(Animal.is_active == is_active)
        
        if 'search' in request.args:
            search = f"%{request.args['search']}%"
            query = query.filter(
                (Animal.name.ilike(search)) | 
                (Animal.identifier.ilike(search))
            )
        
        return query.all()
    
    @ns.doc('create_animal')
    @ns.expect(animal_input_model)
    @ns.marshal_with(animal_model, code=201)
    def post(self):
        """Create a new animal."""
        data = request.get_json()
        db = next(get_db())
        
        # Validate animal type exists
        animal_type = db.get(AnimalType, data.get('type_id'))
        if not animal_type:
            ns.abort(400, message=f"Invalid animal type ID: {data.get('type_id')}")
        
        # Validate parents exist if provided
        mother_id = data.get('mother_id')
        father_id = data.get('father_id')
        
        if mother_id and not db.get(Animal, mother_id):
            ns.abort(400, message=f"Mother with ID {mother_id} not found.")
        
        if father_id and not db.get(Animal, father_id):
            ns.abort(400, message=f"Father with ID {father_id} not found.")
        
        # Process date_of_birth if provided as string
        date_of_birth = data.get('date_of_birth')
        if date_of_birth and isinstance(date_of_birth, str):
            try:
                date_of_birth = date.fromisoformat(date_of_birth)
            except ValueError:
                ns.abort(400, message=f"Invalid date format for date_of_birth: {date_of_birth}. Use YYYY-MM-DD format.")
        
        # Create animal
        animal = Animal(
            identifier=data['identifier'],
            animal_type=animal_type,
            name=data.get('name'),
            gender=data.get('gender', Gender.UNKNOWN),
            date_of_birth=date_of_birth,
            description=data.get('description'),
            notes=data.get('notes'),
            is_active=data.get('is_active', True),
            mother_id=mother_id,
            father_id=father_id
        )
        
        try:
            db.add(animal)
            db.commit()
            db.refresh(animal)
            return animal, 201
        except IntegrityError as e:
            db.rollback()
            if 'identifier' in str(e.orig).lower():
                ns.abort(409, message=f"Animal with identifier '{data['identifier']}' already exists.")
            ns.abort(400, message=str(e))
        except Exception as e:
            db.rollback()
            ns.abort(400, message=str(e))

@ns.route('/<int:id>')
@ns.response(404, 'Animal not found')
@ns.param('id', 'The animal identifier')
class AnimalResource(Resource):
    """Show a single animal and lets you delete or update it."""
    
    @ns.doc('get_animal')
    @ns.marshal_with(animal_model)
    def get(self, id):
        """Fetch a single animal by ID with its type information."""
        db = next(get_db())
        animal = db.get(Animal, id)
        if animal:
            db.refresh(animal, ['animal_type'])
        if animal is None:
            ns.abort(404, message=f"Animal with ID {id} not found.")
        return animal
    
    @ns.doc('update_animal')
    @ns.expect(animal_input_model)
    @ns.marshal_with(animal_model)
    def put(self, id):
        """Update an existing animal."""
        data = request.get_json()
        db = next(get_db())
        
        animal = db.get(Animal, id)
        if animal is None:
            ns.abort(404, message=f"Animal with ID {id} not found.")
        
        # Validate animal type if provided
        if 'type_id' in data:
            animal_type = db.get(AnimalType, data['type_id'])
            if not animal_type:
                ns.abort(400, message=f"Invalid animal type ID: {data['type_id']}")
            animal.animal_type = animal_type
        
        # Validate parents if provided
        if 'mother_id' in data and data['mother_id'] is not None:
            if not db.get(Animal, data['mother_id']):
                ns.abort(400, message=f"Mother with ID {data['mother_id']} not found.")
            animal.mother_id = data['mother_id']
        
        if 'father_id' in data and data['father_id'] is not None:
            if not db.get(Animal, data['father_id']):
                ns.abort(400, message=f"Father with ID {data['father_id']} not found.")
            animal.father_id = data['father_id']
        
        # Process date_of_birth if provided as string
        if 'date_of_birth' in data and isinstance(data['date_of_birth'], str):
            try:
                data['date_of_birth'] = date.fromisoformat(data['date_of_birth'])
            except ValueError:
                ns.abort(400, message=f"Invalid date format for date_of_birth: {data['date_of_birth']}. Use YYYY-MM-DD format.")
        
        # Update other fields
        for field in ['identifier', 'name', 'gender', 'date_of_birth', 
                     'description', 'notes', 'is_active']:
            if field in data:
                setattr(animal, field, data[field])
        
        try:
            db.commit()
            db.refresh(animal)
            return animal
        except IntegrityError as e:
            db.rollback()
            if 'identifier' in str(e.orig).lower():
                ns.abort(409, message=f"Another animal with identifier '{data.get('identifier')}' already exists.")
            ns.abort(400, message=str(e))
        except Exception as e:
            db.rollback()
            ns.abort(400, message=str(e))
    
    @ns.doc('delete_animal')
    @ns.response(204, 'Animal deleted')
    def delete(self, id):
        """Delete an animal."""
        db = next(get_db())
        animal = db.get(Animal, id)
        
        if animal is None:
            ns.abort(404, message=f"Animal with ID {id} not found.")
        
        # Check if this animal is a parent of any other animals
        children = db.query(Animal).filter(
            (Animal.mother_id == id) | (Animal.father_id == id)
        ).count()
        
        if children > 0:
            ns.abort(400, message="Cannot delete animal that is a parent of other animals.")
        
        try:
            db.delete(animal)
            db.commit()
            return '', 204
        except Exception as e:
            db.rollback()
            ns.abort(400, message=str(e))

@ns.route('/<int:id>/pedigree')
@ns.response(404, 'Animal not found')
@ns.param('id', 'The animal identifier')
class AnimalPedigree(Resource):
    """Get the pedigree of an animal."""
    
    @ns.doc('get_animal_pedigree')
    @ns.param('generations', 'Number of generations to include (default: 3, max: 5)')
    def get(self, id):
        """Get the pedigree tree of an animal."""
        try:
            generations = min(int(request.args.get('generations', 3)), 5)
        except ValueError:
            ns.abort(400, message="Generations must be an integer.")
        
        db = next(get_db())
        
        def get_pedigree(animal_id, current_gen, max_gen):
            """Recursively build pedigree tree."""
            if current_gen > max_gen or animal_id is None:
                return None
                
            animal = db.get(Animal, animal_id)
            if not animal:
                return None
                
            return {
                'id': animal.id,
                'identifier': animal.identifier,
                'name': animal.name,
                'gender': animal.gender,
                'date_of_birth': animal.date_of_birth.isoformat() if animal.date_of_birth else None,
                'animal_type': animal.animal_type.name if animal.animal_type else None,
                'mother': get_pedigree(animal.mother_id, current_gen + 1, max_gen),
                'father': get_pedigree(animal.father_id, current_gen + 1, max_gen)
            }
        
        # Check if animal exists
        animal = db.get(Animal, id)
        if not animal:
            ns.abort(404, message=f"Animal with ID {id} not found.")
        
        # Build pedigree tree directly
        pedigree = get_pedigree(id, 1, generations)
        
        # Return the pedigree directly as expected by the test
        return pedigree
