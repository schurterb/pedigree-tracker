# Pedigree Tracker UI Updates
Date: 2025-05-10

## Overview

This document tracks the UI design iterations for the Pedigree Tracker application, particularly focusing on the pedigree visualization component.

## Pedigree Chart Evolution

### Initial Design (2025-05-09)
- Top-to-bottom flow (ancestors at top, selected animal in middle, offspring at bottom)
- Basic styling with gender indicators
- Limited to showing only maternal lineage

### Current Design (2025-05-10)
- Left-to-right flow (selected animal on left, ancestors expanding to right)
- Removed offspring section from pedigree view (still present in details view)
- Added complete paternal lineage along with maternal lineage
- Enhanced visual distinction between maternal and paternal lines
- Color-coded borders to help identify lineage types
- Improved connection lines to better represent relationships

## Visual Cues

The updated design incorporates several visual elements to improve usability:

1. **Direction**: Animal → Parents → Grandparents → Great-Grandparents (left to right)
2. **Color Coding**:
   - Female/maternal elements: Pink/rose accents
   - Male/paternal elements: Blue accents
3. **Connection Lines**: Clear visual connections showing relationship hierarchy

## Next Steps

Potential further improvements to consider:

1. Add hover effects to show brief details about ancestors
2. Implement collapsible sections for complex pedigrees
3. Add zoom/pan controls for very large family trees
4. Consider options for printing or exporting pedigree charts

## Screenshots

No screenshots included in this document, but the mockups can be viewed directly by running:
```
./scripts/serve_mockups.sh
```

And navigating to http://localhost:8080/docs/mockups/
