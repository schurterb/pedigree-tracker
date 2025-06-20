# Pedigree Tracker REST API Specification
Date: 2025-05-06

## API Overview

This document defines the REST API endpoints for the Pedigree Tracker application. The API is designed to provide data to the client-side application while maintaining proper separation of concerns.

## Base URL

All API endpoints are relative to `/api/v1/`

## Authentication

Authentication is not implemented in the initial version. This will be a potential future enhancement.

## Response Format

All responses are returned in JSON format. Successful responses will include an appropriate HTTP status code.

Standard response structure:
```json
{
  "data": { /* Response data */ },
  "meta": { /* Pagination or other metadata */ },
  "errors": [ /* Error details if applicable */ ]
}
```

## Error Handling

Errors will be returned with appropriate HTTP status codes and detailed error messages:

```json
{
  "errors": [
    {
      "code": "ERROR_CODE",
      "message": "Human-readable error message",
      "detail": "Additional details about the error"
    }
  ]
}
```

## Endpoints

### Animal Types

#### GET /api/v1/animal-types
List all animal types.

**Query Parameters:**
- `sort`: Field to sort by (default: name)
- `direction`: Sort direction (asc/desc, default: asc)

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Cattle",
      "description": "Farm cattle",
      "animal_count": 24,
      "created_at": "2025-04-01T10:00:00Z"
    },
    ...
  ],
  "meta": {
    "total": 5
  }
}
```

#### GET /api/v1/animal-types/:id
Get details for a specific animal type.

**Response:**
```json
{
  "data": {
    "id": 1,
    "name": "Cattle",
    "description": "Farm cattle",
    "animal_count": 24,
    "created_at": "2025-04-01T10:00:00Z"
  }
}
```

#### POST /api/v1/animal-types
Create a new animal type.

**Request Body:**
```json
{
  "name": "Goats",
  "description": "Farm goats"
}
```

**Response:**
```json
{
  "data": {
    "id": 6,
    "name": "Goats",
    "description": "Farm goats",
    "animal_count": 0,
    "created_at": "2025-05-06T15:45:00Z"
  }
}
```

#### PUT /api/v1/animal-types/:id
Update an existing animal type.

**Request Body:**
```json
{
  "name": "Dairy Cattle",
  "description": "Dairy producing cattle"
}
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "name": "Dairy Cattle",
    "description": "Dairy producing cattle",
    "animal_count": 24,
    "created_at": "2025-04-01T10:00:00Z"
  }
}
```

#### DELETE /api/v1/animal-types/:id
Delete an animal type. Will return 400 error if animals exist for this type.

**Response:**
```
HTTP/1.1 204 No Content
```

### Animals

#### GET /api/v1/animals
List all animals with optional filtering.

**Query Parameters:**
- `type_id`: Filter by animal type
- `search`: Search term for identifier or name
- `sort`: Field to sort by (default: identifier)
- `direction`: Sort direction (asc/desc, default: asc)
- `page`: Page number for pagination
- `limit`: Number of items per page

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "identifier": "C001",
      "name": "Bessie",
      "type_id": 1,
      "type_name": "Cattle",
      "gender": "female",
      "date_of_birth": "2023-03-15",
      "status": "active",
      "has_parents": true
    },
    ...
  ],
  "meta": {
    "total": 145,
    "page": 1,
    "limit": 20,
    "pages": 8
  }
}
```

#### GET /api/v1/animals/:id
Get detailed information about a specific animal.

**Response:**
```json
{
  "data": {
    "id": 1,
    "identifier": "C001",
    "name": "Bessie",
    "type_id": 1,
    "type_name": "Cattle",
    "gender": "female",
    "date_of_birth": "2023-03-15",
    "description": "Holstein dairy cow",
    "notes": "High milk production, calm temperament",
    "mother_id": 15,
    "father_id": 22,
    "mother_identifier": "C015",
    "father_identifier": "C022",
    "status": "breedable",
    "created_at": "2025-04-01T12:30:45Z",
    "updated_at": "2025-04-15T09:12:30Z"
  }
}
```

#### POST /api/v1/animals
Create a new animal.

**Request Body:**
```json
{
  "identifier": "C045",
  "name": "Daisy",
  "type_id": 1,
  "gender": "female",
  "date_of_birth": "2024-02-20",
  "description": "Jersey dairy cow",
  "notes": "Purchased from neighbor farm",
  "mother_id": 12,
  "father_id": 8,
  "status": "active"
}
```

**Response:**
```json
{
  "data": {
    "id": 46,
    "identifier": "C045",
    "name": "Daisy",
    "type_id": 1,
    "type_name": "Cattle",
    "gender": "female",
    "date_of_birth": "2024-02-20",
    "description": "Jersey dairy cow",
    "notes": "Purchased from neighbor farm",
    "mother_id": 12,
    "father_id": 8,
    "mother_identifier": "C012",
    "father_identifier": "C008",
    "is_active": true,
    "created_at": "2025-05-06T15:48:12Z",
    "updated_at": "2025-05-06T15:48:12Z"
  }
}
```

#### PUT /api/v1/animals/:id
Update an existing animal.

**Request Body:**
```json
{
  "name": "Daisy Belle",
  "notes": "Purchased from neighbor farm, showing excellent milk production"
}
```

**Response:**
```json
{
  "data": {
    "id": 46,
    "identifier": "C045",
    "name": "Daisy Belle",
    "type_id": 1,
    "type_name": "Cattle",
    "gender": "female",
    "date_of_birth": "2024-02-20",
    "description": "Jersey dairy cow",
    "notes": "Purchased from neighbor farm, showing excellent milk production",
    "mother_id": 12,
    "father_id": 8,
    "mother_identifier": "C012",
    "father_identifier": "C008",
    "status": "breedable",
    "created_at": "2025-05-06T15:48:12Z",
    "updated_at": "2025-05-06T15:49:30Z"
  }
}
```

#### DELETE /api/v1/animals/:id
Delete an animal. Will return 400 error if the animal is a parent to other animals.

**Response:**
```
HTTP/1.1 204 No Content
```

### Pedigree

#### GET /api/v1/animals/:id/pedigree
Get the pedigree data for a specific animal.

**Query Parameters:**
- `generations`: Number of generations to include (default: 3, max: 5)

**Response:**
```json
{
  "data": {
    "id": 46,
    "identifier": "C045",
    "name": "Daisy Belle",
    "gender": "female",
    "type": "Cattle",
    "mother": {
      "id": 12,
      "identifier": "C012",
      "name": "Molly",
      "gender": "female",
      "type": "Cattle",
      "mother": { ... },
      "father": { ... }
    },
    "father": {
      "id": 8,
      "identifier": "C008",
      "name": "Ferdinand",
      "gender": "male",
      "type": "Cattle",
      "mother": { ... },
      "father": { ... }
    }
  }
}
```

#### GET /api/v1/animal-types/:type_id/potential-parents
Get a list of potential parents for a new animal of the given type.

**Query Parameters:**
- `gender`: Filter for "male" or "female" parents

**Response:**
```json
{
  "data": [
    {
      "id": 8,
      "identifier": "C008",
      "name": "Ferdinand",
      "gender": "male"
    },
    ...
  ],
  "meta": {
    "total": 12
  }
}
```

#### GET /api/v1/animals/:id/offspring
Get a list of offspring for a specific animal.

**Query Parameters:**
- `sort`: Field to sort by (default: date_of_birth)
- `direction`: Sort direction (asc/desc, default: desc)

**Response:**
```json
{
  "data": [
    {
      "id": 52,
      "identifier": "H052",
      "name": "Mocha Swirl",
      "type_id": 2,
      "type_name": "Horse",
      "gender": "female",
      "date_of_birth": "2025-05-20",
      "other_parent": {
        "id": 17,
        "identifier": "H017",
        "name": "Dark Thunder",
        "gender": "male"
      }
    },
    {
      "id": 45,
      "identifier": "H045",
      "name": "Cocoa Bean",
      "type_id": 2,
      "type_name": "Horse",
      "gender": "male",
      "date_of_birth": "2024-04-12",
      "other_parent": {
        "id": 23,
        "identifier": "H023",
        "name": "Sugar Cube",
        "gender": "female"
      }
    },
    ...
  ],
  "meta": {
    "total": 7
  }
}
```

## Status Codes

- 200: OK - Request succeeded
- 201: Created - Resource was successfully created
- 204: No Content - Request succeeded but no content to return
- 400: Bad Request - Invalid request parameters
- 404: Not Found - Resource not found
- 422: Unprocessable Entity - Validation error
- 500: Internal Server Error - Server-side error
