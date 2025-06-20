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

        // Update the title
        const animalName = document.querySelector(`.animal-item[data-id="${animalId}"] .animal-name`).textContent;
        document.querySelector('#pedigree-view h2').textContent = `Pedigree: ${animalName}`;
        
        // Build and display the pedigree tree
        this.buildPedigreeData(animalId);
        this.drawTree();
    }

    /**
     * Build the pedigree data structure for the selected animal
     * @param {string} animalId - ID of the animal to build pedigree for
     */
    buildPedigreeData(animalId) {
        // For mockup, we'll use static data
        // In the real app, this would fetch data from a database or API
        
        // Define our mockup relationships
        const relationships = {
            '1': { mother: '3', father: '4' },    // Choco Chip
            '2': { mother: '6', father: '4' },    // Trevor Crop
            '3': { mother: 'gm1', father: 'gm2' },  // Sugar Cube
            '4': { mother: 'gp1', father: 'gp2' },  // Dark Thunder
            'gm1': { mother: 'ggm1', father: 'ggm2' }, // Caramel Delight
            'gm2': { mother: 'ggm3', father: 'ggm4' }, // Coffee Bean
            'gp1': { mother: 'ggp1', father: 'ggp2' }, // Black Beauty
            'gp2': { mother: 'ggp3', father: 'ggp4' }  // Storm Cloud
        };
        
        // Animal details for our mockup
        const animals = {
            '1': { name: 'Choco Chip', gender: 'female', birthDate: '2020-03-15', breed: 'Quarter Horse', color: 'Bay' },
            '2': { name: 'Trevor Crop', gender: 'male', birthDate: '2019-05-22', breed: 'Thoroughbred', color: 'Chestnut' },
            '3': { name: 'Sugar Cube', gender: 'female', birthDate: '2015-04-10', breed: 'Quarter Horse', color: 'Palomino' },
            '4': { name: 'Dark Thunder', gender: 'male', birthDate: '2014-06-18', breed: 'Thoroughbred', color: 'Black' },
            '5': { name: 'Cocoa Bean', gender: 'female', birthDate: '2018-02-28', breed: 'Arabian', color: 'Brown' },
            '6': { name: 'Mocha Swirl', gender: 'female', birthDate: '2016-09-05', breed: 'Andalusian', color: 'Dapple Gray' },
            'gm1': { name: 'Caramel Delight', gender: 'female', birthDate: '2010-05-20', breed: 'Quarter Horse', color: 'Buckskin' },
            'gm2': { name: 'Coffee Bean', gender: 'male', birthDate: '2009-03-12', breed: 'Paint Horse', color: 'Brown/White' },
            'gp1': { name: 'Black Beauty', gender: 'female', birthDate: '2008-07-30', breed: 'Thoroughbred', color: 'Black' },
            'gp2': { name: 'Storm Cloud', gender: 'male', birthDate: '2007-04-25', breed: 'Thoroughbred', color: 'Gray' },
            'ggm1': { name: 'Golden Mist', gender: 'female', birthDate: '2005-06-10', breed: 'Quarter Horse', color: 'Palomino' },
            'ggm2': { name: 'Sweet Barley', gender: 'male', birthDate: '2004-08-15', breed: 'Quarter Horse', color: 'Sorrel' },
            'ggm3': { name: 'Honey Crisp', gender: 'female', birthDate: '2004-03-20', breed: 'Paint Horse', color: 'Sorrel/White' },
            'ggm4': { name: 'Dark Roast', gender: 'male', birthDate: '2003-05-12', breed: 'Paint Horse', color: 'Bay/White' },
            'ggp1': { name: 'Midnight Star', gender: 'female', birthDate: '2003-09-08', breed: 'Thoroughbred', color: 'Black' },
            'ggp2': { name: 'Silver Streak', gender: 'male', birthDate: '2002-07-14', breed: 'Thoroughbred', color: 'Gray' },
            'ggp3': { name: 'Thunder Bolt', gender: 'female', birthDate: '2002-04-30', breed: 'Thoroughbred', color: 'Bay' },
            'ggp4': { name: 'Rain Cloud', gender: 'male', birthDate: '2001-08-22', breed: 'Thoroughbred', color: 'Gray Dapple' }
        };
        
        // Build the tree configuration for Treant.js
        this.animalData = animals;
        
        // Create the tree structure starting from the selected animal
        const buildNode = (id) => {
            if (!id || !animals[id]) return null;
            
            const animal = animals[id];
            const node = {
                HTMLclass: animal.gender, // 'male' or 'female' class
                text: {
                    name: animal.name
                },
                innerHTML: this.generateNodeHTML(animal),
                children: []
            };
            
            // If this animal has parents, add them
            if (relationships[id]) {
                const parents = relationships[id];
                
                if (parents.mother && animals[parents.mother]) {
                    const motherNode = buildNode(parents.mother);
                    if (motherNode) node.children.push(motherNode);
                }
                
                if (parents.father && animals[parents.father]) {
                    const fatherNode = buildNode(parents.father);
                    if (fatherNode) node.children.push(fatherNode);
                }
            }
            
            return node;
        };
        
        // Create the full tree configuration
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
            
            nodeStructure: buildNode(animalId)
        };
    }
    
    /**
     * Generate HTML content for a node
     * @param {Object} animal - Animal data
     * @returns {string} - HTML content
     */
    generateNodeHTML(animal) {
        let html = '';
        
        // Format birth date
        const birthYear = animal.birthDate ? new Date(animal.birthDate).getFullYear() : '';
        
        // Gender icon
        const genderSymbol = animal.gender === 'female' ? '♀' : '♂';
        
        // Add name with gender icon
        html += '<div class="node-name">';
        html += `<div class="gender-icon ${animal.gender}">${genderSymbol}</div>`;
        html += `${animal.name}</div>`;
        
        html += `<div class="node-details">Born: ${birthYear}</div>`;
        html += `<div class="node-metadata">Breed: ${animal.breed}</div>`;
        html += `<div class="node-metadata">Color: ${animal.color}</div>`;
        
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
            });
        }
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
    const pedigreeTree = new PedigreeTreeant();
    
    // Select the first animal by default
    setTimeout(() => {
        pedigreeTree.selectAnimal('1');
        
        // Initialize export functionality after tree is drawn
        const pedigreeExport = new PedigreeExport('pedigree-container', 'pedigree-tree');
        
        // Make export instance globally accessible for debugging
        window.pedigreeExport = pedigreeExport;
    }, 500);
    
    // Make the tree instance globally accessible for debugging
    window.pedigreeTree = pedigreeTree;
});
