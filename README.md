# Pedigree Tracker

A simple tool for farmers and breeders to track and visualize animal pedigrees.

> If you want this as a Progressive Web App (PWA), please reach out to me [here](https://godsartificer.com/contact).

## Features

- **Animal Type Management**: Create, rename, and delete animal categories (cattle, sheep, horses, etc.)
- **Animal Records**: Maintain detailed records of individual animals with parentage tracking
- **Pedigree Visualization**: Generate multi-generational pedigree trees (up to 5 generations)
- **Data Export**: Export pedigree charts as PNG, PDF, or JSON for printing or sharing
- **RESTful API**: Full-featured API with consistent, field-keyed validation errors
- **Responsive Design**: Works on desktop and mobile devices, keyboard navigable

## Tech Stack

- **Backend**: Python 3.11+, Flask, Flask-RESTX, SQLAlchemy
- **Database**: SQLite (with support for other SQL databases)
- **API**: RESTful JSON API with Swagger documentation
- **Frontend**: HTML, CSS, JavaScript (vanilla; Treant.js for trees)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/pedigree-tracker.git
   cd pedigree-tracker
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration if needed
   ```

5. **Initialize the database**:
   The database will be automatically initialized when you first run the application.

### Running the Application

#### Standard Method

Start the unified server (serves both the API and the web UI):

```bash
python -m src.app
```

The application will be available at `http://localhost:8000` (override with the `PORT` environment variable).

#### Using Docker

The application can be run in a Docker container, which is especially useful for deployment on a Raspberry Pi:

1. **Start the application**:
   ```bash
   ./scripts/docker_start.sh
   ```
   This builds and starts the Docker container in detached mode.

2. **Stop the application**:
   ```bash
   ./scripts/docker_stop.sh
   ```
   To stop and remove volumes (will delete all data):
   ```bash
   ./scripts/docker_stop.sh --volumes
   ```

3. **Reset Docker completely** (removes all containers, images, and volumes):
   ```bash
   ./scripts/docker_reset.sh
   ```

When running with Docker, the application will be available at `http://localhost:8000`

### API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI (OpenAPI 3.0): `http://localhost:8000/docs/index.html`
- OpenAPI 3.0.3 spec: `http://localhost:8000/docs/openapi.json`

## Project Structure

```
pedigree-tracker/
├── data/                  # Database files
├── docs/                  # Project documentation
├── logs/                  # Application logs
├── scripts/               # Utility scripts
├── src/                   # Source code
│   ├── app/               # Application package
│   │   ├── api/           # API endpoints
│   │   ├── models/        # Database models
│   │   ├── config.py      # Application configuration
│   │   ├── database.py    # Database connection and initialization
│   │   └── __main__.py    # Application entry point
│   └── tests/             # Test files
├── tests/e2e/             # Playwright end-to-end tests
├── www/                   # Web frontend (served by the app)
│   ├── docs/              # OpenAPI 3.0.3 spec + Swagger UI (served at /docs/)
├── .env.example           # Example environment variables
├── .gitignore
├── README.md
└── requirements.txt       # Python dependencies
```

## Usage

1. Create animal categories relevant to your farm (the **+** tab; the ✎ button
   next to it renames or deletes the current category)
2. Add animals with their details and parent information
3. View pedigree charts for any animal (click its row)
4. Export charts as PNG, PDF, or JSON for record-keeping

## Data Rules

The API enforces these invariants on both create and update:

- `identifier` is required and unique **within its category** (the same tag
  may be reused in a different category)
- `date_of_birth` is optional but may not be in the future
- The mother must be `female`, the father must be `male`, and both must
  belong to the same category as the animal
- An animal cannot be its own ancestor (no self-parenting or cycles)
- A child's known birth date must be after each parent's known birth date
- Gender, category, or birth date edits that would invalidate recorded
  offspring are rejected

Validation errors return HTTP 400 with `{"message", "errors": {field: msg}}`.
Error responses never contain SQL or exception details. See
`www/docs/openapi.json` for the full API contract.

## Development

### Setting Up for Development

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run the backend tests (uses an isolated temporary database):
   ```bash
   ./scripts/run_tests.sh
   ```

3. Run the end-to-end tests (requires Node.js; starts the app on port 8001):
   ```bash
   npm install
   npx playwright install chromium
   ./scripts/run_e2e_tests.sh
   ```

4. Run with auto-reload:
   ```bash
   FLASK_DEBUG=1 python -m src.app
   ```

### Code Style

We use:
- **Black** for code formatting
- **Flake8** for linting
- **Mypy** for static type checking

Run all three checks before committing with the lint script (reports a
pass/fail result per tool):
```bash
./scripts/lint.sh
```

Or run each tool manually:
```bash
black src
flake8 src
mypy src
```

Flake8 and mypy configuration lives in `setup.cfg`.

## API Endpoints

### Animal Types (Categories)

- `GET /api/v1/animal-types/` - List all animal types
- `POST /api/v1/animal-types/` - Create a new animal type
- `GET /api/v1/animal-types/<id>` - Get an animal type by ID
- `PUT /api/v1/animal-types/<id>` - Update an animal type
- `DELETE /api/v1/animal-types/<id>` - Delete an animal type (only when it has no animals)
- `GET /api/v1/animal-types/<id>/potential-parents` - List eligible parents (optionally `?gender=male|female`)

### Animals

- `GET /api/v1/animals/` - List all animals (with optional filtering)
- `POST /api/v1/animals/` - Create a new animal
- `GET /api/v1/animals/<id>` - Get an animal by ID
- `PUT /api/v1/animals/<id>` - Update an animal (partial; `null` on `mother_id`/`father_id` clears the parent)
- `DELETE /api/v1/animals/<id>` - Delete an animal (only when it has no offspring)
- `GET /api/v1/animals/<id>/pedigree` - Get an animal's pedigree tree (`?generations=1..5`)
- `GET /api/v1/animals/<id>/offspring` - List an animal's offspring

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Flask-RESTX](https://flask-restx.readthedocs.io/)
- And all other open-source projects that made this possible.
