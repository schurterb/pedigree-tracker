# Pedigree Tracker UI Mockups

## Overview

This folder contains static HTML/CSS/JS mockups of the Pedigree Tracker application UI. These mockups demonstrate the intended look and feel of the final application and can be used for design review and feature placement discussions.

## Structure

```
mockups/
├── index.html       # Main application HTML structure
├── css/
│   ├── normalize.css # CSS reset for browser consistency
│   └── styles.css    # Application-specific styles
├── js/
│   └── main.js       # Interactive functionality
└── README.md        # This file
```

## Features Demonstrated

1. **Main Layout**
   - Tab navigation for different animal types (Horses, Cattle, Sheep, Rabbits)
   - Sidebar with animal list including gender indicators
   - Main display area for pedigree visualization or animal details
   - Settings bar at the bottom of sidebar

2. **Pedigree View**
   - Displays family tree with ancestors, the selected animal, and offspring
   - Interactive animal cards that can be clicked to see details
   - Visual connections between related animals

3. **Animal Details View**
   - Form for viewing and editing animal information
   - Basic information section (ID, Type, Name, Gender, Date of Birth)
   - Lineage section (Mother, Father)
   - Notes section
   - Offspring list

4. **Add Animal View**
   - Form for creating new animals
   - Similar fields to the details view
   - Save and Cancel buttons

## Viewing the Mockups

To view these mockups:

1. Start a local web server in the project root:
   ```
   cd /path/to/pedigree-tracker
   python3 -m http.server 8000
   ```

2. Navigate to:
   ```
   http://localhost:8000/docs/mockups/index.html
   ```

3. Interact with the UI to explore different views and features

## Notes

- These mockups use static HTML/CSS/JS with no backend connectivity
- The final application will implement these designs with actual functionality
- Design is based on wireframes at `/docs/cascade-notes/2025-05-06-pedigree-tracker-wireframes.md`
