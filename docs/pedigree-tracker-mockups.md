# Pedigree Tracker UI Mockups
Date: 2025-05-09

## Overview

This document tracks the creation of HTML/CSS/JS mockups for the Pedigree Tracker application. The mockups are designed to represent what the final application will look like, allowing for feature placement and UX review before full implementation.

## Mockup Structure

The mockups have been created with the following structure:

```
www/
├── index.html       # Main application HTML structure
├── css/
│   ├── normalize.css # CSS reset for browser consistency
│   └── styles.css    # Application-specific styles
└── js/
    └── main.js       # Interactive functionality
```

## Features Implemented

The mockup demonstrates the following features and views:

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

5. **Responsive Design**
   - Layout adjusts for different screen sizes
   - Mobile-friendly interface

## Testing Instructions

To view the mockups:

1. Open the application in a browser
2. Explore the different tabs and views
3. Test the interactive elements:
   - Click on animal names in the sidebar
   - Click "Add Animal" buttons
   - Navigate between pedigree and details views

## Next Steps

1. Review the mockups with stakeholders
2. Gather feedback on layout, features, and usability
3. Make adjustments based on feedback
4. Begin implementing the actual application with backend integration

## Notes

- These mockups use static data for demonstration purposes
- The JavaScript provides simulated interactions but doesn't connect to any backend
- The design follows the wireframe specifications from the earlier document and user sketch
