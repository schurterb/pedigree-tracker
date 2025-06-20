"""
Animal Offspring API resource for getting an animal's offspring.
"""
from flask_restx import Resource

from ..models import Animal
from ..database import get_db
from .animal import ns

@ns.route('/<int:id>/offspring')
@ns.response(404, 'Animal not found')
@ns.param('id', 'The animal identifier')
class AnimalOffspring(Resource):
    """Get the offspring of an animal."""
    
    @ns.doc('get_animal_offspring')
    def get(self, id):
        """Get the offspring (children) of an animal."""
        db = next(get_db())
        
        # Check if animal exists
        animal = db.get(Animal, id)
        if not animal:
            ns.abort(404, message=f"Animal with ID {id} not found.")
        
        # Get children where this animal is either mother or father
        children = db.query(Animal).filter(
            (Animal.mother_id == id) | (Animal.father_id == id)
        ).all()
        
        # Format output
        result = []
        for child in children:
            result.append({
                'id': child.id,
                'identifier': child.identifier,
                'name': child.name,
                'gender': child.gender,
                'date_of_birth': child.date_of_birth.isoformat() if child.date_of_birth else None,
                'relationship': 'mother' if child.mother_id == id else 'father'
            })
            
        return result
