/**
 * Pedigree Tracker - Pedigree Tree Visualization
 * 
 * This file integrates the Treant.js pedigree visualization with the application.
 * It serves as an adapter between the application API and the PedigreeTreeant class.
 */

// Create the pedigree tree adapter as a global object
var PedigreeTree = (function() {
    // Create an object to hold the public methods and properties
    var publicAPI = {};
    
    // Private variables
    var treantInstance = null;
    var pedigreeData = null;
    var currentZoom = 1;
    
    /**
     * Initialize pedigree tree functionality
     */
    publicAPI.init = function() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeTreeant);
        } else {
            initializeTreeant();
        }
        
        // Initialize zoom controls
        var zoomInBtn = document.getElementById('zoom-in');
        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', publicAPI.zoomIn);
        }
        
        var zoomOutBtn = document.getElementById('zoom-out');
        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', publicAPI.zoomOut);
        }
        
        var resetBtn = document.getElementById('reset-view');
        if (resetBtn) {
            resetBtn.addEventListener('click', publicAPI.resetView);
        }
    };
    
    /**
     * Initialize the Treant.js pedigree visualization
     */
    function initializeTreeant() {
        // Make sure the PedigreeTreeant class is available
        if (typeof window.PedigreeTreeant !== 'undefined') {
            // Create a new instance if one doesn't already exist
            if (!window.pedigreeTree) {
                window.pedigreeTree = new window.PedigreeTreeant();
            }
            treantInstance = window.pedigreeTree;
            console.log('Pedigree Treant visualization initialized');
        } else {
            console.error('PedigreeTreeant class not found');
        }
    }
    
    /**
     * Load and display pedigree data for an animal
     * @param {number} animalId - Animal ID to load pedigree for
     * @param {number} generations - Number of generations to include
     */
    publicAPI.loadPedigree = async function(animalId, generations) {
        // Default to configured generations if not specified
        if (typeof generations === 'undefined' && typeof CONFIG !== 'undefined') {
            generations = CONFIG.DEFAULT_GENERATIONS || 3;
        }
        
        try {
            if (typeof Utils !== 'undefined') {
                Utils.showLoading();
            }
            
            // Fetch pedigree data from API
            const response = await API.animals.getPedigree(animalId, generations);
            pedigreeData = response.data;
            
            // Update animal name in the title
            const animalName = pedigreeData.name || 'Unknown';
            const titleElement = document.querySelector('#pedigree-title');
            if (titleElement) {
                titleElement.textContent = `Pedigree: ${animalName}`;
            }
            
            // Show the edit button
            const editButton = document.getElementById('edit-animal-btn');
            if (editButton) {
                editButton.style.display = 'block';
            }
            
            // Use the Treant.js implementation if available
            if (treantInstance) {
                treantInstance.animalData = pedigreeData;
                treantInstance.selectedAnimalId = animalId.toString();
                treantInstance.buildPedigreeData(animalId.toString());
                treantInstance.drawTree();
            } else {
                console.error('Treant pedigree instance not initialized');
                // Fallback - try to initialize again
                initializeTreeant();
                if (treantInstance) {
                    treantInstance.animalData = pedigreeData;
                    treantInstance.selectedAnimalId = animalId.toString();
                    treantInstance.buildPedigreeData(animalId.toString());
                    treantInstance.drawTree();
                }
            }
            
            if (typeof Utils !== 'undefined') {
                Utils.hideLoading();
            }
        } catch (error) {
            if (typeof Utils !== 'undefined') {
                Utils.hideLoading();
                Utils.showToast(`Error loading pedigree: ${error.message}`, 'error');
            }
            console.error('Failed to load pedigree:', error);
        }
    };
    
    /**
     * Zoom in the pedigree view
     */
    publicAPI.zoomIn = function() {
        if (treantInstance) {
            treantInstance.zoomTree(0.1);
        }
    };
    
    /**
     * Zoom out the pedigree view
     */
    publicAPI.zoomOut = function() {
        if (treantInstance) {
            treantInstance.zoomTree(-0.1);
        }
    };
    
    /**
     * Reset the pedigree view
     */
    publicAPI.resetView = function() {
        if (treantInstance) {
            treantInstance.resetTreeView();
        }
    };
    
    // Return the public API
    return publicAPI;
})();
