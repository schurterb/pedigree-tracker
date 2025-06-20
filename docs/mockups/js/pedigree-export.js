/**
 * Pedigree Export Utilities
 * 
 * Provides functionality to export pedigree trees as PNG images or PDF documents
 */

class PedigreeExport {
    /**
     * Initialize the export functionality
     * @param {string} containerId - ID of the container element
     * @param {string} treeId - ID of the tree element to export
     */
    constructor(containerId, treeId) {
        this.container = document.getElementById(containerId);
        this.treeId = treeId;
        
        // Create export controls
        this.createExportControls();
        
        // Create loading indicator
        this.createLoadingIndicator();
        
        // Initialize event listeners
        this.initEvents();
    }
    
    /**
     * Create export control buttons
     */
    createExportControls() {
        // Create export controls container
        this.exportControls = document.createElement('div');
        this.exportControls.className = 'export-controls';
        
        // PNG export button
        this.pngButton = document.createElement('button');
        this.pngButton.className = 'export-btn';
        this.pngButton.id = 'export-png';
        this.pngButton.title = 'Export as PNG';
        this.pngButton.innerHTML = '<span class="icon">📷</span> PNG';
        
        // PDF export button
        this.pdfButton = document.createElement('button');
        this.pdfButton.className = 'export-btn';
        this.pdfButton.id = 'export-pdf';
        this.pdfButton.title = 'Export as PDF';
        this.pdfButton.innerHTML = '<span class="icon">📄</span> PDF';
        
        // Add buttons to controls
        this.exportControls.appendChild(this.pngButton);
        this.exportControls.appendChild(this.pdfButton);
        
        // Add controls to container
        this.container.appendChild(this.exportControls);
    }
    
    /**
     * Create loading indicator
     */
    createLoadingIndicator() {
        // Create loading indicator
        this.loadingIndicator = document.createElement('div');
        this.loadingIndicator.className = 'export-loading';
        
        // Create spinner
        const spinner = document.createElement('div');
        spinner.className = 'export-loading-spinner';
        
        // Create text
        const text = document.createElement('div');
        text.className = 'export-loading-text';
        text.textContent = 'Generating export...';
        
        // Add elements to loading indicator
        this.loadingIndicator.appendChild(spinner);
        this.loadingIndicator.appendChild(text);
        
        // Add loading indicator to container
        this.container.appendChild(this.loadingIndicator);
    }
    
    /**
     * Initialize event listeners
     */
    initEvents() {
        // PNG export button click
        this.pngButton.addEventListener('click', () => {
            this.exportAsPNG();
        });
        
        // PDF export button click
        this.pdfButton.addEventListener('click', () => {
            this.exportAsPDF();
        });
    }
    
    /**
     * Show loading indicator
     */
    showLoading() {
        this.loadingIndicator.classList.add('active');
    }
    
    /**
     * Hide loading indicator
     */
    hideLoading() {
        this.loadingIndicator.classList.remove('active');
    }
    
    /**
     * Get the current animal name for the filename
     * @returns {string} - Formatted animal name
     */
    getCurrentAnimalName() {
        const titleElement = document.querySelector('#pedigree-view h2');
        if (titleElement) {
            const title = titleElement.textContent;
            return title.replace('Pedigree: ', '').trim().replace(/\s+/g, '-').toLowerCase();
        }
        return 'pedigree';
    }
    
    /**
     * Export the pedigree tree as a PNG image
     */
    exportAsPNG() {
        const element = document.getElementById(this.treeId);
        if (!element) {
            console.error(`Element with ID "${this.treeId}" not found`);
            return;
        }
        
        // Show loading indicator
        this.showLoading();
        
        // Configuration for better quality
        const options = {
            scale: 2, // Higher scale for better quality
            useCORS: true, // Enable if tree contains external images
            backgroundColor: '#FFFFFF' // Ensure white background
        };
        
        // Check if html2canvas is available
        if (typeof html2canvas === 'undefined') {
            console.error('html2canvas library not found. Make sure it is included in your HTML.');
            this.hideLoading();
            return;
        }
        
        // Generate PNG
        html2canvas(element, options).then(canvas => {
            // Create link for download
            const link = document.createElement('a');
            link.download = `${this.getCurrentAnimalName()}-pedigree.png`;
            link.href = canvas.toDataURL('image/png');
            
            // Click link to download
            link.click();
            
            // Hide loading indicator
            this.hideLoading();
        }).catch(error => {
            console.error('Error generating PNG:', error);
            this.hideLoading();
        });
    }
    
    /**
     * Export the pedigree tree as a PDF document
     */
    exportAsPDF() {
        const element = document.getElementById(this.treeId);
        if (!element) {
            console.error(`Element with ID "${this.treeId}" not found`);
            return;
        }
        
        // Show loading indicator
        this.showLoading();
        
        // Check if html2pdf is available
        if (typeof html2pdf === 'undefined') {
            console.error('html2pdf library not found. Make sure it is included in your HTML.');
            this.hideLoading();
            return;
        }
        
        // PDF export options
        const options = {
            margin: 10,
            filename: `${this.getCurrentAnimalName()}-pedigree.pdf`,
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
        html2pdf()
            .set(options)
            .from(element)
            .save()
            .then(() => {
                // Hide loading indicator
                this.hideLoading();
            })
            .catch(error => {
                console.error('Error generating PDF:', error);
                this.hideLoading();
            });
    }
}
