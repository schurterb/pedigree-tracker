"""
Tests for animal relationships and genealogy.
"""
import pytest
from datetime import date

from app.models.animal import Animal, Gender

def test_animal_parent_relationships(db_session, sample_animal_type):
    """Test parent-child relationships between animals."""
    # Create parent animals
    mother = Animal(
        identifier='MOTHER001',
        name='Mother',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2018, 1, 1)
    )
    
    father = Animal(
        identifier='FATHER001',
        name='Father',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2017, 1, 1)
    )
    
    # Create child animal
    child = Animal(
        identifier='CHILD001',
        name='Child',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2020, 5, 15),
        mother=mother,
        father=father
    )
    
    db_session.add_all([mother, father, child])
    db_session.commit()
    
    # Test relationships
    assert child.mother_id == mother.id
    assert child.father_id == father.id
    assert child.mother == mother
    assert child.father == father
    
    # Test backrefs
    assert child in mother.children_mother.all()
    assert child in father.children_father.all()
    
    # Test that parents are older than children
    assert mother.date_of_birth < child.date_of_birth
    assert father.date_of_birth < child.date_of_birth

def test_animal_grandparent_relationships(db_session, sample_animal_type):
    """Test multi-generational family relationships."""
    # Create grandparents
    grand_mother = Animal(
        identifier='GRANDMA001',
        name='Grandma',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2010, 1, 1)
    )
    
    grand_father = Animal(
        identifier='GRANDPA001',
        name='Grandpa',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2009, 1, 1)
    )
    
    # Create parents
    mother = Animal(
        identifier='MOTHER002',
        name='Mother',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2015, 1, 1),
        mother=grand_mother,
        father=grand_father
    )
    
    father = Animal(
        identifier='FATHER002',
        name='Father',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2014, 1, 1)
    )
    
    # Create child
    child = Animal(
        identifier='CHILD002',
        name='Grandchild',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2020, 6, 1),
        mother=mother,
        father=father
    )
    
    db_session.add_all([grand_mother, grand_father, mother, father, child])
    db_session.commit()
    
    # Test direct relationships
    assert child.mother == mother
    assert child.father == father
    assert mother.mother == grand_mother
    assert mother.father == grand_father
    
    # Test grandparent relationships through mother
    assert child.mother.mother == grand_mother
    assert child.mother.father == grand_father
    
    # Test that all dates are in the correct order
    assert grand_mother.date_of_birth < mother.date_of_birth
    assert grand_father.date_of_birth < mother.date_of_birth
    assert mother.date_of_birth < child.date_of_birth
    assert father.date_of_birth < child.date_of_birth

def test_animal_siblings_relationship(db_session, sample_animal_type):
    """Test sibling relationships between animals."""
    # Create parents
    mother = Animal(
        identifier='MOTHER003',
        name='Mother',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2015, 1, 1)
    )
    
    father = Animal(
        identifier='FATHER003',
        name='Father',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2014, 1, 1)
    )
    
    # Create siblings
    sibling1 = Animal(
        identifier='SIBLING001',
        name='First Born',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2020, 1, 1),
        mother=mother,
        father=father
    )
    
    sibling2 = Animal(
        identifier='SIBLING002',
        name='Second Born',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2020, 6, 1),
        mother=mother,
        father=father
    )
    
    db_session.add_all([mother, father, sibling1, sibling2])
    db_session.commit()
    
    # Test that siblings share the same parents
    assert sibling1.mother == sibling2.mother
    assert sibling1.father == sibling2.father
    
    # Test that mother's children includes both siblings
    mother_children = mother.children_mother.all()
    assert sibling1 in mother_children
    assert sibling2 in mother_children
    assert len(mother_children) == 2
    
    # Test that father's children includes both siblings
    father_children = father.children_father.all()
    assert sibling1 in father_children
    assert sibling2 in father_children
    assert len(father_children) == 2

def test_animal_half_siblings_relationship(db_session, sample_animal_type):
    """Test half-sibling relationships between animals."""
    # Create shared parent
    shared_mother = Animal(
        identifier='SHARED_MOTHER',
        name='Shared Mother',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2015, 1, 1)
    )
    
    # Create different fathers
    father1 = Animal(
        identifier='FATHER1',
        name='Father One',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2014, 1, 1)
    )
    
    father2 = Animal(
        identifier='FATHER2',
        name='Father Two',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2013, 1, 1)
    )
    
    # Create half-siblings (same mother, different fathers)
    child1 = Animal(
        identifier='CHILD1',
        name='First Child',
        gender=Gender.FEMALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2020, 1, 1),
        mother=shared_mother,
        father=father1
    )
    
    child2 = Animal(
        identifier='CHILD2',
        name='Second Child',
        gender=Gender.MALE,
        animal_type=sample_animal_type,
        date_of_birth=date(2020, 6, 1),
        mother=shared_mother,
        father=father2
    )
    
    db_session.add_all([shared_mother, father1, father2, child1, child2])
    db_session.commit()
    
    # Test that they share the same mother
    assert child1.mother == child2.mother
    
    # Test that they have different fathers
    assert child1.father != child2.father
    
    # Test that mother's children includes both children
    mother_children = shared_mother.children_mother.all()
    assert child1 in mother_children
    assert child2 in mother_children
    assert len(mother_children) == 2
    
    # Test that each father only has one child
    father1_children = father1.children_father.all()
    assert child1 in father1_children
    assert len(father1_children) == 1
    
    father2_children = father2.children_father.all()
    assert child2 in father2_children
    assert len(father2_children) == 1
