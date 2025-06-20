# Pedigree Tracker Wireframe Specifications
Date: 2025-05-06 (Updated based on user sketch)

## Overview

This document provides wireframe specifications for the Pedigree Tracker single-page application (SPA). The design follows the user's sketch with a simple, tab-based interface focused on efficiency and clarity.

## Reference

The design is based on the user's sketch located at:
`/home/schurterb/workspace/pedigree-tracker/docs/img/PedigreeTrackerWebpageSketch.jpg`

## Global Layout

The application follows a single-screen layout with these key components:

```
+-----------------------------------------------------------------------------+
| [Animal Type Tabs: Horses | Cattle | Sheep | Rabbits] | [Add Animal Button] |
+-----------------------------------------------------------------------------+
|                   |                                                         |
|                   |                                                         |
|  Animals List     |      Main Display Area                                  |
|  with gender      |      (Pedigree Visualization                            |
|  indicators       |       or Animal Details)                                |
|                   |                                                         |
|                   |                                                         |
|                   |                                                         |
|                   |                                                         |
|  [+ Add Animal]   |                                                         |
|                   |                                                         |
| [Settings Bar]    |                                                         |
+-----------------------------------------------------------------------------+
```

## Main Application View

Based on your sketch, the main application has a clean, tab-based interface with a sidebar for animal listings:

```
+-----------------------------------------------------------------------------+
| [Horses | Cattle | Sheep | Rabbits | +]                                     |
+-----------------------------------------------------------------------------+
|                   |                                                         |
| ♀ [Choco Chip]    |                                                         |
|                   |                                                         |
| ♂ [Trevor Crop]   |                                                         |
|                   |                                                         |
| .....             |      Pedigree Visualization                             |
|                   |                                                         |
| .....             |      (Connected boxes showing animal relationships)     |
|                   |                                                         |
| .....             |                                                         |
|                   |                                                         |
| .....             |                                                         |
|                   |                                                         |
| [+ Add Animal]    |                                                         |
|                   |                                                         |
| [Settings Bar]    |                                                         |
+-----------------------------------------------------------------------------+
```

### Key Features of Main View

1. **Animal Type Tabs**: Horizontal tabs at the top allow switching between different animal types (Horses, Cattle, Sheep, Rabbits)
   - Each tab shows only animals of that type
   - Plus icon allows adding new animal types

2. **Animal List Sidebar**: 
   - Shows all animals within the selected type
   - Gender indicators (♀/♂) before each animal name
   - Each entry shows the animal's name/identifier
   - Entry can be selected to show details or pedigree
   - "Add Animal" button at bottom of list opens form

3. **Main Display Area**:
   - Shows pedigree visualization as a default view
   - Can also display detailed animal information when an animal is selected
   - Pedigree shows relationship connections between animals

4. **Add Animal Button**:
   - Prominent button in the top-right corner
   - Opens a popup form for adding new animals

5. **Settings Bar**:
   - Located at the bottom of the sidebar
   - Contains configuration options for the application

## Add Animal Flow

When the "Add Animal" button is clicked, the main area switches to an empty Animal Details form for direct entry:

```
+-------------------------------------------------------+
| New Animal                           [Save] [Cancel]  |
+-------------------------------------------------------+
|                                                       |
| Basic Information:                                    |
| ID/Tag*: [__________]           Type: [Current Tab]   |
| Name: [______________]         Gender: ○ ♀ ○ ♂        |
| Date of Birth: [MM/DD/YYYY]                           |
|                                                       |
| Lineage:                                              |
| Mother: [Select female animal▼]                       |
| Father: [Select male animal▼]                         |
|                                                       |
| Notes:                                                |
| [                                                   ] |
| [                                                   ] |
| [                                                   ] |
|                                                       |
+-------------------------------------------------------+
```

All fields are directly editable on this screen. The user can either save the new animal or cancel the operation.

## Pedigree Visualization

The pedigree visualization in the main area shows a family tree structure:

```
+-------------------------------------------------------+
|                                                       |
|                  [Great Grandparent]                  |
|                          |                            |
|                          |                            |
|             [Grandparent]      [Grandparent]          |
|                   |                |                  |
|                   |                |                  |
|             [Mother]          [Father]                |
|                    \              /                   |
|                     \            /                    |
|                     [Selected Animal]                 |
|                     /            \                    |
|                    /              \                   |
|            [Offspring]       [Offspring]              |
|                                                       |
+-------------------------------------------------------+
```

## Animal Detail View

When an animal is selected, its details can be viewed and edited directly in the main area:

```
+-------------------------------------------------------+
| Animal Details: Choco Chip        [Save] [Pedigree]   |
+-------------------------------------------------------+
|                                                       |
| Basic Information:                                    |
| ID/Tag: [H001]                Type: [Horse]           |
| Name: [Choco Chip]            Gender: [♀ Female ▼]    |
| Date of Birth: [03/15/2022]                           |
|                                                       |
| Lineage:                                              |
| Mother: [Sugar Cube (H023) ▼]                         |
| Father: [Dark Thunder (H017) ▼]                       |
|                                                       |
| Notes:                                                |
| [Brown mare with white star marking on forehead.     ]|
| [Good temperament, trained for basic riding.         ]|
| [Purchased from Highland Farm in March 2023.         ]|
|                                                       |
| Offspring:                                            |
| - Cocoa Bean (H045) - born 04/12/2024                 |
| - Mocha Swirl (H052) - born 05/20/2025                |
|                                                       |
+-------------------------------------------------------+
```

All fields appear as editable inputs or selects, allowing the user to make changes directly in this view. The user can save changes or switch to the Pedigree view. Offspring are displayed but not directly editable from this screen - they must be edited from their own details view.

## Settings and Controls

The settings bar at the bottom of the sidebar includes:

```
+-------------------+
| ⚙️ | 📄 | ? | ... |
+-------------------+
```

- ⚙️ - General settings
- 📄 - Export/import data
- ? - Help/documentation
- ... - Additional options

## Mobile Layout Adaptation

On mobile devices, the layout adapts:

1. Animal type tabs remain at top, but scroll horizontally if needed
2. Animal list becomes a slide-out panel from the left
3. Main area takes full width when list is hidden
4. Add button remains fixed in top-right position
5. Bottom settings bar remains accessible

## Design Notes

1. **Simplicity First**: The layout prioritizes the most common tasks (viewing animals by type and seeing pedigrees)
2. **Consistent Visual Language**: Gender symbols and color-coding make scanning the list easier
3. **Task-Based Organization**: UI is organized around the primary workflows (selecting types, viewing/adding animals)
4. **Minimal Modal Use**: Only forms that require focus (like adding animals) use modal dialogs
5. **Visual Pedigrees**: The pedigree display is central to the application's purpose and takes the largest screen area
