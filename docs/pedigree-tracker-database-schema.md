# Pedigree Tracker Database Schema
Date: 2025-05-06

## Overview

This document outlines the database schema for the Pedigree Tracker application. We're using SQLite for simplicity and portability, with a focus on capturing animal genealogy data efficiently.

## Entity Relationship Diagram

```
+------------------+       +----------------------------+
| AnimalType       |       | Animal                     |
+------------------+       +----------------------------+
| PK: id           |<---+  | PK: id                     |
| name             |    |  | identifier                 |
| description      |    |  | FK: type_id                |
| created_at       |    |  | name                       |
+------------------+    |  | gender                     |
                        |  | date_of_birth              |
                        |  | description                |
                        |  | notes                      |
                        |  | FK: mother_id (self-ref)   |<--+
                        |  | FK: father_id (self-ref)   |<--+
                        |  | is_active                  |   |
                        |  | created_at                 |   |
                        |  | updated_at                 |   |
                        |  +----------------------------+   |
                        |       ^                   ^       |
                        |       |                   |       |
                        +-------+                   +-------+
```

## Tables and Fields

### AnimalType

Stores the different types of animals on the farm.

| Column       | Type           | Constraints                 | Description                     |
|--------------|----------------|-----------------------------|---------------------------------|
| id           | INTEGER        | PRIMARY KEY, AUTOINCREMENT  | Unique identifier               |
| name         | VARCHAR(50)    | UNIQUE, NOT NULL            | Type name (e.g., "Cattle")      |
| description  | VARCHAR(200)   |                             | Optional description            |
| created_at   | DATETIME       | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp      |

### Animal

Stores individual animals with their genealogical relationships.

| Column       | Type           | Constraints                 | Description                     |
|--------------|----------------|-----------------------------|---------------------------------|
| id           | INTEGER        | PRIMARY KEY, AUTOINCREMENT  | Unique identifier               |
| identifier   | VARCHAR(50)    | NOT NULL                    | Animal's tag/identifier         |
| type_id      | INTEGER        | NOT NULL, FOREIGN KEY       | Reference to animal type        |
| name         | VARCHAR(100)   |                             | Optional animal name            |
| gender       | VARCHAR(10)    |                             | Male/Female                     |
| date_of_birth| DATE           |                             | Birth date                      |
| description  | TEXT           |                             | General description             |
| notes        | TEXT           |                             | Detailed observations/comments  |
| mother_id    | INTEGER        | FOREIGN KEY (self)          | Reference to mother animal      |
| father_id    | INTEGER        | FOREIGN KEY (self)          | Reference to father animal      |
| status       | VARCHAR(20)    | NOT NULL, DEFAULT 'active'  | Animal status (active, breedable, retired, deceased, etc.) |
| created_at   | DATETIME       | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp      |
| updated_at   | DATETIME       | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp   |

## Constraints

### Primary Keys
- `AnimalType.id` - Primary key for animal types
- `Animal.id` - Primary key for animals

### Foreign Keys
- `Animal.type_id` → `AnimalType.id` - Associates an animal with its type
- `Animal.mother_id` → `Animal.id` - Self-referential relationship to mother
- `Animal.father_id` → `Animal.id` - Self-referential relationship to father

### Unique Constraints
- `AnimalType.name` - Each animal type must have a unique name
- Composite constraint on `(Animal.type_id, Animal.identifier)` - Identifiers must be unique within an animal type

### Indexes
For performance optimization, we'll create the following indexes:

1. Index on `Animal.type_id` for faster filtering by animal type
2. Index on `Animal.mother_id` for faster pedigree lookups
3. Index on `Animal.father_id` for faster pedigree lookups
4. Composite index on `(Animal.type_id, Animal.identifier)` for enforcing unique constraints and faster lookups

## Database Schema Creation SQL

```sql
-- Create AnimalType table
CREATE TABLE animal_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(200),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create Animal table
CREATE TABLE animal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier VARCHAR(50) NOT NULL,
    type_id INTEGER NOT NULL,
    name VARCHAR(100),
    gender VARCHAR(10),
    date_of_birth DATE,
    description TEXT,
    notes TEXT,
    mother_id INTEGER,
    father_id INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (type_id) REFERENCES animal_type(id),
    FOREIGN KEY (mother_id) REFERENCES animal(id),
    FOREIGN KEY (father_id) REFERENCES animal(id),
    UNIQUE (type_id, identifier)
);

-- Create indexes for performance
CREATE INDEX idx_animal_type_id ON animal(type_id);
CREATE INDEX idx_animal_mother_id ON animal(mother_id);
CREATE INDEX idx_animal_father_id ON animal(father_id);
```

## Data Migration Considerations

For the initial setup, we'll need to:

1. Create the database file in the data directory
2. Run the schema creation script
3. Add initial animal types relevant to the farm
4. Import existing animals, if any (possibly from CSV files)

In future versions, we might consider:

1. Adding support for more complex migration patterns
2. Including version control for the database schema
3. Implementing backup and restore functionality

## Performance Considerations

The schema is designed to be efficient for:

1. Retrieving animals by type
2. Finding an animal's immediate parents
3. Building multi-generation pedigree trees
4. Ensuring data integrity with appropriate constraints

For large farms with thousands of animals, we might need to implement:

1. Query optimization techniques
2. Pagination for large result sets
3. Potentially more sophisticated caching strategies
