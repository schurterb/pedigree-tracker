# Pedigree Tracker

A comprehensive tool for farmers and breeders to track and visualize animal pedigrees, enabling better breeding decisions and genetic management.

## Features

- **Animal Type Management**: Create and manage different types of animals (cattle, sheep, horses, etc.)
- **Animal Records**: Maintain detailed records of individual animals with parentage tracking
- **Pedigree Visualization**: Generate multi-generational pedigree trees (up to 5 generations)
- **Data Export**: Export pedigree charts as PNG images for printing or sharing
- **RESTful API**: Full-featured API for integration with other systems
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Backend**: Python 3.8+, Flask, SQLAlchemy
- **Database**: SQLite (with support for other SQL databases)
- **API**: RESTful JSON API with Swagger documentation
- **Frontend**: HTML, CSS, JavaScript (with plans for React/Vue.js frontend)

## Getting Started

### Prerequisites

- Python 3.8 or higher
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

Start the development server:
```bash
python -m src.app
```

The application will be available at `http://localhost:5000`

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

Once the application is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:5000/api/v1/docs/`
- ReDoc: `http://localhost:5000/api/v1/docs/#/`

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
├── .env.example           # Example environment variables
├── .gitignore
├── README.md
└── requirements.txt       # Python dependencies
```

## Development

### Setting Up for Development

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Run with auto-reload:
   ```bash
   FLASK_DEBUG=1 python -m src.app
   ```

### Code Style

We use:
- **Black** for code formatting
- **Flake8** for linting
- **Mypy** for static type checking

Run the following commands before committing:
```bash
black .
flake8 .
mypy .
```

## API Endpoints

### Animal Types

- `GET /api/v1/animal-types` - List all animal types
- `POST /api/v1/animal-types` - Create a new animal type
- `GET /api/v1/animal-types/<id>` - Get an animal type by ID
- `PUT /api/v1/animal-types/<id>` - Update an animal type
- `DELETE /api/v1/animal-types/<id>` - Delete an animal type

### Animals

- `GET /api/v1/animals` - List all animals (with optional filtering)
- `POST /api/v1/animals` - Create a new animal
- `GET /api/v1/animals/<id>` - Get an animal by ID
- `PUT /api/v1/animals/<id>` - Update an animal
- `DELETE /api/v1/animals/<id>` - Delete an animal
- `GET /api/v1/animals/<id>/pedigree` - Get an animal's pedigree tree

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Flask-RESTX](https://flask-restx.readthedocs.io/)
- And all other open-source projects that made this possible.
```

3. Start the application:
```
python src/app.py
```

4. Open your browser and navigate to http://localhost:5000

## Usage

1. First, create animal types relevant to your farm
2. Add animals with their details and parent information
3. View pedigree charts for any animal
4. Export charts as PNG for record-keeping

## Technologies Used

- Python
- Flask
- SQLite
- Plotly/NetworkX
- HTML/CSS/JavaScript
- Bootstrap

## License

MIT License
