# Pedigree Tracker Project Plan
Date: 2025-05-06

## 1. Project Overview
Creating a pedigree tracking tool for farm animals with the following features:
- Support for customizable animal types (cattle, sheep, horses, etc.)
- Database to retain lists of all animals by type
- Generation of pedigree plots/trees
- Export of plots to PNG for printing

## 2. Detailed Requirements

### 2.1 Animal Type Management
- Create, edit, and delete animal types (e.g., cattle, sheep, horses)
- Each animal type should have:
  - Unique name
  - Optional description
  - Type-specific attributes (optional future enhancement)

### 2.2 Animal Management
- Create, edit, and delete individual animals
- Each animal should have:
  - Unique identifier (e.g., tag number, registration number)
  - Name (optional)
  - Animal type
  - Gender
  - Date of birth
  - Optional description/notes
  - Parent references (mother and father)
  - Active/inactive status

### 2.3 Pedigree Visualization
- Generate pedigree trees for any animal in the database
- Configure the number of generations to display (1-5)
- Display pedigree in an easy-to-read format
- Highlight genetic relationships
- Handle missing parent information gracefully
- Export pedigree as PNG for printing

### 2.4 Data Management
- Import/export animals via CSV (optional future enhancement)
- Backup and restore database functionality (optional future enhancement)
- Data validation to prevent errors

## 3. Data Model

### 3.1 AnimalType
- id: Integer, primary key
- name: String, unique, required
- description: String
- created_at: DateTime

### 3.2 Animal
- id: Integer, primary key
- identifier: String, required (unique within animal type)
- name: String, optional
- type_id: Integer, foreign key to AnimalType
- gender: String (male/female)
- date_of_birth: Date
- description: Text
- notes: Text, optional (for detailed observations or comments)
- mother_id: Integer, self-referential foreign key
- father_id: Integer, self-referential foreign key
- is_active: Boolean
- created_at: DateTime
- updated_at: DateTime

**Constraints:**
- Composite uniqueness constraint on (type_id, identifier) - ensures no two animals of the same type can have the same identifier

## 4. Technical Stack

### 4.1 Backend
- **API**: Nodejs with Express.js for lightweight REST API
- **Database**: SQLite for simplicity and portability
- **Server**: Simple Nodejs server to host static files and provide API endpoints

### 4.2 Frontend
- **Core**: HTML5, CSS3, JavaScript (ES6+)
- **Framework**: Modern client-side JavaScript (Vue.js or React)
- **Styling**: Bootstrap 5 for responsive design
- **Data Visualization**: Client-side libraries (D3.js or Plotly.js) for pedigree visualization
- **Chart Export**: HTML-to-Canvas conversion for PNG export
- **API Communication**: Fetch API or Axios for REST calls

## 5. Project Structure
```
pedigree-tracker/
├── config/            # Configuration files
│   └── config.json    # Application configuration
├── data/              # SQLite database and any data files
│   └── pedigree.db    # Main database file
├── logs/              # Application logs
├── scripts/           # Utility scripts
│   ├── backup.sh      # Database backup script
│   └── setup.sh       # Initial setup script
├── src/               # Server-side Nodejs code
│   ├── models.js      # Database models
│   ├── api.js         # REST API endpoints only
│   └── utils.js       # Helper functions
├── www/               # Web files / client-side code
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   │   ├── components/  # UI components
│   │   ├── services/    # API communication
│   │   ├── utils/       # Client-side utilities 
│   │   └── pedigree/    # Pedigree visualization logic
│   ├── img/           # Images
│   └── index.html     # Main HTML file
├── tests/             # Test files
└── README.md
```
## 6. User Interface Design

### 6.1 Application Structure
- **Single Page Application (SPA)**: Client-side routing with modern JavaScript framework
- **RESTful API**: Backend provides data through JSON-based REST endpoints
- **Tab-Based Layout**: Based on user's sketch at `/docs/img/PedigreeTrackerWebpageSketch.jpg`
- **Two-Panel Design**: Animal list sidebar + main content area

### 6.2 Main Interface Components
- **Animal Type Tabs**: Horizontal tabs for switching between different animal types (Horses, Cattle, Sheep, Rabbits)
- **Animal List Sidebar**: Shows animals of the selected type with gender indicators (♀/♂)
- **Pedigree Visualization Area**: Main display showing animal relationships
- **Add Animal Button**: Prominent button in the header area
- **Settings Bar**: Control panel at the bottom of the sidebar

### 6.3 Key Interaction Patterns
- **Type Selection**: Users first select animal type via tabs
- **Animal Selection**: Users select an animal from the sidebar list
- **Pedigree View**: Animal pedigree displays automatically in the main area
- **Inline Editing**: Animal information can be viewed and directly edited in the main area
- **Add Animal**: Clicking 'Add Animal' shows an empty Animal Details form in the main area for direct entry
- **Toggle Views**: Users can switch between Pedigree View and Details View for the selected animal

### 6.4 Design Principles
- **Simplicity First**: Focus on the most common tasks and workflows
- **Visual Clarity**: Clear visual indicators like gender symbols (♀/♂)
- **Task-Based Organization**: UI organized around primary user workflows
- **Minimal Modal Use**: Only forms use modal overlays
- **Client-Side Logic**: Most application logic happens in the browser
- **Responsive Design**: Adapts to different screen sizes while maintaining usability

## 7. Development Phases

### 7.1 Phase 1: Project Setup & Backend API (1 week)
- Set up project structure following standard layout
- Create database schema with SQLite
- Implement database models for AnimalType and Animal
- Set up basic Nodejs RESTful API structure
- Create initial configuration files
- Implement API endpoints for CRUD operations on animal types and animals
- Add proper error handling and validation at the API level

### 7.2 Phase 2: Front-end Foundation (1 week)
- Set up client-side framework (React)
- Create basic HTML structure and styling with Bootstrap
- Implement site navigation and responsive layout
- Set up API communication service layer
- Create reusable UI components for forms and lists

### 7.3 Phase 3: Core Feature Implementation (2 weeks)
- Implement animal type management screens
- Create animal management interface with parent selection
- Add filtering and search functionality
- Implement client-side validation
- Develop dashboard components
- Add error handling and user feedback

### 7.4 Phase 4: Pedigree Visualization (1-2 weeks)
- Research and select appropriate client-side visualization library (D3.js or Plotly.js)
- Implement pedigree data processing in JavaScript
- Create interactive pedigree chart component
- Implement dynamic generation based on selected animal
- Add configuration options (generations, display options)
- Create PNG export functionality using HTML5 Canvas

### 7.5 Phase 5: Testing & Refinement (1 week)
- Conduct cross-browser testing
- Perform usability testing with sample data
- Fix bugs and UI/UX issues
- Optimize API performance and client-side rendering
- Add offline capabilities (if time permits)
- Create user documentation

## 8. Risk Assessment and Mitigation

### 8.1 Technical Risks
- **Complex pedigree visualization**: Research multiple libraries; create prototype early
- **Data integrity**: Implement robust validation; test edge cases thoroughly
- **Performance with large datasets**: Consider pagination and lazy loading

### 8.2 Project Risks
- **Scope creep**: Maintain strict feature boundaries; defer enhancements to future versions
- **Time constraints**: Prioritize core functionality; maintain flexible timelines

## 9. Future Enhancements
- Mobile app version
- Advanced search and filtering
- Genetic trait tracking
- Breeding recommendations
- Statistical reports and analytics
- Multi-user support with permissions
- Cloud synchronization

## 10. Immediate Next Steps
1. Finalize this project plan and get approval
2. Set up the basic project structure
3. Create detailed database schema design
4. Design API endpoints specification
5. Create wireframes for UI components
