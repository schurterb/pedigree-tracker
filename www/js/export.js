/**
 * Pedigree Tracker - Export Functionality
 * 
 * This file handles exporting data in various formats.
 */

const Export = {
    /**
     * Initialize export functionality
     */
    init: function() {
        // Add event listeners to export buttons
        // const exportBtn = document.getElementById('export-btn');
        // if (exportBtn) {
        //     exportBtn.addEventListener('click', () => {
        //         Utils.showModal('export-modal');
        //     });
        // } else {
        //     console.error('Export button not found');
        // }
        
        const exportPedigreeBtn = document.getElementById('export-pedigree');
        if (exportPedigreeBtn) {
            exportPedigreeBtn.addEventListener('click', () => {
                Utils.showModal('export-modal');
            });
        } else {
            console.error('Export pedigree button not found');
        }
        
        const exportPdfBtn = document.getElementById('export-pdf-btn');
        if (exportPdfBtn) {
            exportPdfBtn.addEventListener('click', () => {
                this.exportPedigreeAsPDF();
            });
        } else {
            console.error('Export PDF button not found');
        }
        
        const exportPngBtn = document.getElementById('export-png-btn');
        if (exportPngBtn) {
            exportPngBtn.addEventListener('click', () => {
                this.exportPedigreeAsPNG();
            });
        } else {
            console.error('Export PNG button not found');
        }
        
        const exportJsonBtn = document.getElementById('export-json-btn');
        if (exportJsonBtn) {
            exportJsonBtn.addEventListener('click', () => {
                this.exportDataAsJSON();
            });
        } else {
            console.error('Export JSON button not found');
        }
        
        // Add this debugging line to check if HTML2PDF and HTML2Canvas are loaded
        console.log('Export libraries loaded:', {
            html2pdf: typeof html2pdf !== 'undefined',
            html2canvas: typeof html2canvas !== 'undefined'
        });
    },
    
    /**
     * Export current pedigree as PDF
     */
    exportPedigreeAsPDF: async function() {
        // Get pedigree data from the treant instance
        const pedigreeData = window.pedigreeTree && window.pedigreeTree.animalData;
        if (!pedigreeData || Object.keys(pedigreeData).length === 0) {
            Utils.showToast('No pedigree data to export.', 'error');
            return;
        }
        
        try {
            Utils.showLoading();
            Utils.hideModals();
            
            // Get the pedigree container
            const element = document.getElementById('pedigree-tree');
            if (!element) {
                throw new Error('Pedigree tree element not found');
            }
            
            console.log('Exporting pedigree as PDF', element);
            
            // Check if html2pdf is available
            if (typeof html2pdf === 'undefined') {
                throw new Error('html2pdf library not loaded');
            }
            
            // Create a timestamp for the filename
            const timestamp = Utils.generateTimestamp();
            const animalName = pedigreeData.name || 'animal';
            const filename = `pedigree_${animalName.replace(/\s+/g, '_')}_${timestamp}.pdf`;
            
            // Options for html2pdf
            const options = {
                margin: 10,
                filename: filename,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { 
                    scale: 2,
                    useCORS: true,
                    logging: true,
                    backgroundColor: '#FFFFFF'
                },
                jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' }
            };
            
            // Generate PDF
            await html2pdf().set(options).from(element).save();
            
            Utils.hideLoading();
            Utils.showToast('Pedigree exported as PDF!', 'success');
        } catch (error) {
            Utils.hideLoading();
            Utils.showToast(`Error exporting PDF: ${error.message}`, 'error');
            console.error('Failed to export PDF:', error);
        }
    },
    
    /**
     * Export current pedigree as PNG image
     */
    exportPedigreeAsPNG: async function() {
        // Get pedigree data from the treant instance
        const pedigreeData = window.pedigreeTree && window.pedigreeTree.animalData;
        if (!pedigreeData || Object.keys(pedigreeData).length === 0) {
            Utils.showToast('No pedigree data to export.', 'error');
            return;
        }
        
        try {
            Utils.showLoading();
            Utils.hideModals();
            
            // Get the pedigree container
            const element = document.getElementById('pedigree-tree');
            if (!element) {
                throw new Error('Pedigree tree element not found');
            }
            
            console.log('Exporting pedigree as PNG', element);
            
            // Check if html2canvas is available
            if (typeof html2canvas === 'undefined') {
                throw new Error('html2canvas library not loaded');
            }
            
            // Create a timestamp for the filename
            const timestamp = Utils.generateTimestamp();
            const animalName = pedigreeData.name || 'animal';
            const filename = `pedigree_${animalName.replace(/\s+/g, '_')}_${timestamp}.png`;
            
            // Use html2canvas to create a canvas from the element
            const canvas = await html2canvas(element, { 
                scale: 2,
                useCORS: true,
                logging: true,
                backgroundColor: '#FFFFFF'
            });
            
            // Convert canvas to blob
            canvas.toBlob(function(blob) {
                // Create a download link
                const link = document.createElement('a');
                link.download = filename;
                link.href = URL.createObjectURL(blob);
                document.body.appendChild(link);
                link.click();
                
                // Clean up
                document.body.removeChild(link);
                URL.revokeObjectURL(link.href);
                
                Utils.hideLoading();
                Utils.showToast('Pedigree exported as PNG!', 'success');
            }, 'image/png');
        } catch (error) {
            Utils.hideLoading();
            Utils.showToast(`Error exporting PNG: ${error.message}`, 'error');
            console.error('Failed to export PNG:', error);
        }
    },
    
    /**
     * Export animal data as JSON
     */
    exportDataAsJSON: function() {
        // Get pedigree data from the treant instance
        const pedigreeData = window.pedigreeTree && window.pedigreeTree.animalData;
        if (!pedigreeData || Object.keys(pedigreeData).length === 0) {
            Utils.showToast('No pedigree data to export.', 'error');
            return;
        }
        
        try {
            Utils.hideModals();
            
            // Create a copy of the data to export
            const exportData = Utils.deepClone(pedigreeData);
            
            // Convert data to JSON string
            const jsonString = JSON.stringify(exportData, null, 2);
            
            // Create a timestamp for the filename
            const timestamp = Utils.generateTimestamp();
            const animalName = pedigreeData.name || 'animal';
            const filename = `pedigree_${animalName.replace(/\s+/g, '_')}_${timestamp}.json`;
            
            // Create a blob with the JSON data
            const blob = new Blob([jsonString], { type: 'application/json' });
            
            // Create a download link
            const link = document.createElement('a');
            link.download = filename;
            link.href = URL.createObjectURL(blob);
            document.body.appendChild(link);
            link.click();
            
            // Clean up
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);
            
            Utils.showToast('Data exported as JSON!', 'success');
        } catch (error) {
            Utils.showToast(`Error exporting data: ${error.message}`, 'error');
            console.error('Failed to export data:', error);
        }
    }
};
