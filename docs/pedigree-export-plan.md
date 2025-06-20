# Pedigree Tree Export Plan (2025-05-12)

## Overview

This document outlines a plan to implement client-side PDF and PNG export functionality for the pedigree tree visualization in the Pedigree Tracker application. The implementation will use pure JavaScript libraries without requiring any server-side processing.

## Technical Approach

After researching available options, I recommend the following two JavaScript libraries for implementing export functionality:

1. **html2canvas** - For capturing the tree visualization as a PNG image
   - Renders HTML elements to a canvas
   - Preserves styles, layout, and images
   - Handles complex DOM structures well

2. **html2pdf.js** - For generating PDF files directly in the browser
   - Built on top of html2canvas and jsPDF
   - Handles page breaks for large trees
   - Provides extensive configuration options
   - Supports custom page sizes and orientations

## Implementation Plan

### 1. Add Required Libraries

First, we'll need to include the necessary libraries in our project:

```html
<!-- For PNG export -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>

<!-- For PDF export (includes html2canvas internally) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
```

### 2. Create Export Utility Functions

We'll implement utility functions for both PNG and PDF export:

```javascript
/**
 * Export the pedigree tree as a PNG image
 * @param {string} elementId - ID of the element to export
 * @param {string} filename - Name for the downloaded file
 */
function exportAsPNG(elementId, filename = 'pedigree-tree.png') {
    const element = document.getElementById(elementId);
    
    // Configuration for better quality
    const options = {
        scale: 2, // Higher scale for better quality
        useCORS: true, // Enable if tree contains external images
        backgroundColor: '#FFFFFF' // Ensure white background
    };
    
    html2canvas(element, options).then(canvas => {
        // Create link for download
        const link = document.createElement('a');
        link.download = filename;
        link.href = canvas.toDataURL('image/png');
        link.click();
    });
}

/**
 * Export the pedigree tree as a PDF document
 * @param {string} elementId - ID of the element to export
 * @param {string} filename - Name for the downloaded file
 */
function exportAsPDF(elementId, filename = 'pedigree-tree.pdf') {
    const element = document.getElementById(elementId);
    
    // PDF export options
    const options = {
        margin: 10,
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { 
            scale: 2,
            useCORS: true,
            backgroundColor: '#FFFFFF'
        },
        jsPDF: {
            unit: 'mm',
            format: 'a4',
            orientation: 'landscape' // Use landscape for tree visualization
        }
    };
    
    // Generate and save PDF
    html2pdf().set(options).from(element).save();
}
```

### 3. Add Export UI Controls

We'll add export buttons to the tree visualization interface:

```html
<div class="export-controls">
    <button id="export-png" class="export-btn" title="Export as PNG">
        <span class="icon">📷</span> PNG
    </button>
    <button id="export-pdf" class="export-btn" title="Export as PDF">
        <span class="icon">📄</span> PDF
    </button>
</div>
```

### 4. Add Event Listeners

Connect the export functions to the UI controls:

```javascript
document.addEventListener('DOMContentLoaded', () => {
    // PNG export button
    document.getElementById('export-png').addEventListener('click', () => {
        exportAsPNG('pedigree-tree', `pedigree-${getCurrentAnimalName()}.png`);
    });
    
    // PDF export button
    document.getElementById('export-pdf').addEventListener('click', () => {
        exportAsPDF('pedigree-tree', `pedigree-${getCurrentAnimalName()}.pdf`);
    });
});

// Helper function to get current animal name for filename
function getCurrentAnimalName() {
    const title = document.querySelector('#pedigree-view h2').textContent;
    return title.replace('Pedigree: ', '').trim().replace(/\s+/g, '-').toLowerCase();
}
```

### 5. Style the Export Controls

Add CSS for the export controls:

```css
.export-controls {
    position: absolute;
    top: 15px;
    right: 15px;
    display: flex;
    gap: 8px;
    background-color: rgba(255, 255, 255, 0.8);
    padding: 6px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    z-index: 100;
}

.export-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 6px 12px;
    border-radius: 4px;
    background-color: #fff;
    border: 1px solid #ddd;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s ease;
}

.export-btn:hover {
    background-color: #f5f5f5;
    border-color: #ccc;
}

.export-btn:active {
    background-color: #e9e9e9;
    transform: translateY(1px);
}

.export-btn .icon {
    font-size: 16px;
}
```

### 6. Optimize for Large Pedigrees

For large pedigrees that might not fit on a single page, we'll need to add special handling:

```javascript
/**
 * Export a large pedigree tree as a multi-page PDF
 * @param {string} elementId - ID of the element to export
 * @param {string} filename - Name for the downloaded file
 */
function exportLargePedigreeAsPDF(elementId, filename = 'large-pedigree.pdf') {
    const element = document.getElementById(elementId);
    
    // PDF export options with page breaks
    const options = {
        margin: 10,
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { 
            scale: 2,
            useCORS: true,
            backgroundColor: '#FFFFFF'
        },
        jsPDF: {
            unit: 'mm',
            format: 'a3', // Larger paper size
            orientation: 'landscape'
        },
        pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
    };
    
    // Generate and save PDF
    html2pdf().set(options).from(element).save();
}
```

## Implementation Timeline

1. **Day 1**: Add libraries and basic export functionality
   - Add html2canvas and html2pdf.js to the project
   - Implement basic export functions
   - Add export buttons to UI

2. **Day 2**: Testing and optimization
   - Test with different tree sizes and layouts
   - Optimize for quality and performance
   - Handle edge cases (very large trees, trees with images)

3. **Day 3**: Advanced features
   - Add support for custom page sizes
   - Implement progress indicators for large exports
   - Add options for customizing the export (paper size, orientation)

## Potential Challenges and Solutions

1. **Large Trees**:
   - *Challenge*: Trees with many generations may not fit on a single page
   - *Solution*: Use paging options in html2pdf.js to split across multiple pages

2. **Image Quality**:
   - *Challenge*: Default export may have low resolution
   - *Solution*: Use higher scale factor (2x or 3x) in html2canvas options

3. **Browser Compatibility**:
   - *Challenge*: Different browsers may render exports differently
   - *Solution*: Test across major browsers and add browser-specific optimizations

4. **Performance**:
   - *Challenge*: Exporting large trees may cause browser lag
   - *Solution*: Add a loading indicator and potentially use Web Workers for processing

## Conclusion

This plan outlines a comprehensive approach to implementing client-side PDF and PNG export for the pedigree tree visualization. The implementation uses well-established JavaScript libraries that don't require server-side processing, making it suitable for both online and offline use.

The export functionality will enhance the value of the Pedigree Tracker application by allowing users to save, print, and share their pedigree trees easily.
