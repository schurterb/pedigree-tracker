/**
 * Pedigree Tree Visualization using Treant.js
 * 
 * This module handles the pedigree tree visualization using Treant.js
 */

class PedigreeTreeant {
    /**
     * Initialize the pedigree tree visualization
     */
    constructor() {
        this.config = null;
        this.chart = null;
        this.selectedAnimalId = null;
        this.animalData = {};

        // Initialize event listeners
        this.initEvents();
    }

    /**
     * Initialize event listeners
     */
    initEvents() {
        // Listen for animal selection in the sidebar
        document.querySelectorAll('.animal-item').forEach(item => {
            item.addEventListener('click', () => {
                const animalId = item.dataset.id;
                this.selectAnimal(animalId);
            });
        });

        // Listen for window resize
        window.addEventListener('resize', () => {
            if (this.chart) {
                // Redraw the chart on window resize
                this.drawTree();
            }
        });
        
        // Initialize tree control buttons
        this.initTreeControls();
    }
    
    /**
     * Initialize tree control buttons (zoom, reset, etc.)
     */
    initTreeControls() {
        // Zoom in button
        const zoomInBtn = document.getElementById('zoom-in');
        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', () => {
                this.zoomTree(0.1); // Zoom in by 10%
            });
        }
        
        // Zoom out button
        const zoomOutBtn = document.getElementById('zoom-out');
        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', () => {
                this.zoomTree(-0.1); // Zoom out by 10%
            });
        }
        
        // Reset view button
        const resetBtn = document.getElementById('reset-view');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetTreeView();
            });
        }
    }
    
    /**
     * Zoom the tree view
     * @param {number} factor - Zoom factor (positive to zoom in, negative to zoom out)
     */
    zoomTree(factor) {
        const treeContainer = document.getElementById('pedigree-tree');
        if (!treeContainer) return;
        
        // Get the current scale from transform or set default
        let currentScale = 1;
        const transform = treeContainer.style.transform;
        if (transform) {
            const match = transform.match(/scale\(([^)]+)\)/);
            if (match && match[1]) {
                currentScale = parseFloat(match[1]);
            }
        }
        
        // Calculate new scale (limit to 0.5 - 2.0)
        const newScale = Math.max(0.5, Math.min(2.0, currentScale + factor));
        
        // Apply new scale
        treeContainer.style.transform = `scale(${newScale})`;
        treeContainer.style.transformOrigin = 'center';
    }
    
    /**
     * Reset the tree view to default
     */
    resetTreeView() {
        const treeContainer = document.getElementById('pedigree-tree');
        if (!treeContainer) return;
        
        // Reset scale and position
        treeContainer.style.transform = 'scale(1)';
        
        // Redraw the tree
        this.drawTree();
    }

    /**
     * Select an animal and display its pedigree
     * @param {string} animalId - ID of the animal to select
     */
    selectAnimal(animalId) {
        this.selectedAnimalId = animalId;
        
        // Update animal list selection
        document.querySelectorAll('.animal-item').forEach(item => {
            if (item.dataset.id === animalId) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });

        // Update the title - safely get the animal name if available in the sidebar
        let animalName = 'Animal';
        const nameElement = document.querySelector(`.animal-item[data-id="${animalId}"] .animal-name`);
        if (nameElement) {
            animalName = nameElement.textContent;
        }
        
        // Update the title if the element exists
        const titleElement = document.querySelector('#pedigree-view h2');
        if (titleElement) {
            titleElement.textContent = `Pedigree: ${animalName}`;
        }
        
        // Build and display the pedigree tree
        this.loadPedigreeData(animalId);
    }
    
    /**
     * Load pedigree data from the API
     * @param {string} animalId - ID of the animal to build pedigree for
     */
    async loadPedigreeData(animalId) {
        try {
            Utils.showLoading();
            
            // Fetch pedigree data from API
            const response = await API.animals.getPedigree(animalId);
            
            // Store the data
            this.animalData = response.data;
            
            // Build the pedigree structure
            this.buildPedigreeData(animalId);
            
            // Draw the tree
            this.drawTree();
            
            Utils.hideLoading();
        } catch (error) {
            Utils.hideLoading();
            Utils.showToast(`Error loading pedigree: ${error.message}`, 'error');
            console.error('Failed to load pedigree:', error);
        }
    }

    /**
     * Build the pedigree data structure for the selected animal
     * @param {string} animalId - ID of the animal to build pedigree for
     */
    buildPedigreeData(animalId) {
        // Get the data for the root animal
        const rootAnimal = this.animalData;
        
        // Build chart configuration
        this.config = {
            chart: {
                container: "#pedigree-tree",
                rootOrientation: "WEST", // Left to right layout
                levelSeparation: 80,
                siblingSeparation: 40,
                subTeeSeparation: 60,
                nodeAlign: "BOTTOM",
                
                connectors: {
                    type: "step", // Use step connectors for cleaner layout
                    style: {
                        "stroke-width": 2,
                        "stroke": "#aaa"
                    }
                },
                
                node: {
                    HTMLclass: "pedigree-node",
                    collapsable: true
                },
                
                animation: {
                    nodeAnimation: "easeOutBounce",
                    nodeSpeed: 450,
                    connectorsAnimation: "bounce",
                    connectorsSpeed: 500
                }
            },
            
            nodeStructure: this.buildNode(rootAnimal)
        };
    }
    
    /**
     * Build a node for the Treant.js tree
     * @param {Object} animal - Animal data object
     * @returns {Object} - Node structure for Treant.js
     */
    buildNode(animal) {
        if (!animal) return null;
        
        // Create the node object
        const node = {
            innerHTML: this.generateNodeHTML(animal),
            HTMLclass: `pedigree-node ${animal.gender || 'unknown'} ${animal.id === this.selectedAnimalId ? 'selected' : ''}`,
            HTMLid: `pedigree-node-${animal.id}`,
            children: [],
            data: { id: animal.id }
        };
        
        // Add parent nodes if available
        if (animal.mother) {
            const motherNode = this.buildNode(animal.mother);
            if (motherNode) node.children.push(motherNode);
        }
        
        if (animal.father) {
            const fatherNode = this.buildNode(animal.father);
            if (fatherNode) node.children.push(fatherNode);
        }
        
        return node;
    }
    
    /**
     * Generate HTML content for a node
     * @param {Object} animal - Animal data
     * @returns {string} - HTML content
     */
    generateNodeHTML(animal) {
        let html = '';
        
        // Format birth date
        const birthYear = animal.date_of_birth ? new Date(animal.date_of_birth).getFullYear() : '';
        
        // Gender icon
        const genderSymbol = animal.gender === 'female' ? '♀' : '♂';
        
        // Add name with gender icon
        html += '<div class="node-name">';
        html += `<div class="gender-icon ${animal.gender}">${genderSymbol}</div>`;
        html += `${animal.name}</div>`;
        
        html += `<div class="node-details">Born: ${birthYear}</div>`;
        html += `<div class="node-metadata">ID: ${animal.identifier || ''}</div>`;
        
        return html;
    }
    
    /**
     * Draw the pedigree tree using Treant.js
     */
    drawTree() {
        // Clear existing tree
        const container = document.getElementById('pedigree-tree');
        if (!container) return;
        
        container.innerHTML = '';
        
        // Create the tree
        if (this.config) {
            this.chart = new Treant(this.config, () => {
                // After tree is loaded, mark selected animal
                this.highlightSelectedAnimal();
                
                // Add click event listeners to nodes
                this.addNodeEventListeners();
            });
        }
    }
    
    /**
     * Add event listeners to pedigree nodes
     */
    addNodeEventListeners() {
        document.querySelectorAll('.pedigree-node').forEach(node => {
            // Set the data-id attribute from the HTMLid
            const nodeId = node.id;
            if (nodeId && nodeId.startsWith('pedigree-node-')) {
                const animalId = nodeId.replace('pedigree-node-', '');
                node.setAttribute('data-id', animalId);
            }
            
            node.addEventListener('click', (e) => {
                // Extract animal ID from the data-id attribute
                const animalId = node.getAttribute('data-id');
                if (animalId && typeof App !== 'undefined') {
                    // Load animal details in the application
                    App.loadAnimalDetails(animalId);
                }
                // Prevent event bubbling
                e.stopPropagation();
            });
        });
    }
    
    /**
     * Highlight the selected animal in the tree
     */
    highlightSelectedAnimal() {
        const rootNode = document.querySelector('#pedigree-tree .pedigree-node');
        if (rootNode) {
            rootNode.classList.add('selected');
        }
    }
}

// Initialize the pedigree tree when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Make sure the necessary libraries and elements exist
    if (typeof Treant === 'undefined' || !document.getElementById('pedigree-tree')) {
        console.error('Treant.js library or pedigree-tree element not found');
        return;
    }
    
    // Initialize pedigree visualization
    window.pedigreeTree = new PedigreeTreeant();
});

// Make PedigreeTreeant globally accessible
window.PedigreeTreeant = PedigreeTreeant;
