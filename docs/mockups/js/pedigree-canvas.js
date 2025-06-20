/**
 * Pedigree Canvas Visualization
 * This file handles drawing the pedigree connections on a canvas element
 */

class PedigreeCanvas {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.animalCards = {};
        this.relationships = {};
        
        // Only initialize the canvas if the container exists
        if (this.container) {
            this.initCanvas();
        } else {
            console.warn(`Container with ID "${containerId}" not found.`);
            return;
        }
        
        // Bind methods
        this.handleResize = this.handleResize.bind(this);
        
        // Add event listener for window resize
        window.addEventListener('resize', this.handleResize);
    }
    
    /**
     * Initialize the canvas element
     */
    initCanvas() {
        // Create canvas element if it doesn't exist
        if (!this.canvas) {
            this.canvas = document.createElement('canvas');
            this.canvas.className = 'pedigree-canvas';
            
            // Insert the canvas as the first child of the container
            if (this.container.firstChild) {
                this.container.insertBefore(this.canvas, this.container.firstChild);
            } else {
                this.container.appendChild(this.canvas);
            }
            
            this.ctx = this.canvas.getContext('2d');
        }
        
        // Set canvas size to match container
        this.resizeCanvas();
    }
    
    /**
     * Resize canvas to match container size
     */
    resizeCanvas() {
        const rect = this.container.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        
        // Redraw after resize
        this.draw();
    }
    
    /**
     * Handle window resize event
     */
    handleResize() {
        this.resizeCanvas();
    }
    
    /**
     * Register an animal card element with its ID
     * @param {string} animalId - The ID of the animal
     * @param {HTMLElement} cardElement - The DOM element for the animal card
     */
    registerAnimalCard(animalId, cardElement) {
        this.animalCards[animalId] = cardElement;
    }
    
    /**
     * Set relationship data
     * @param {Object} relationships - Map of animal IDs to their parent IDs
     * Example: { 'animal1': { mother: 'animal2', father: 'animal3' } }
     */
    setRelationships(relationships) {
        this.relationships = relationships;
        this.draw();
    }
    
    /**
     * Draw connecting lines between related animals
     */
    draw() {
        if (!this.ctx || !this.canvas || !this.animalCards || Object.keys(this.animalCards).length === 0) {
            return;
        }
        
        // Clear the canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Set line style
        this.ctx.lineWidth = 2;
        this.ctx.lineCap = 'round';
        
        // Draw connections based on relationships
        Object.entries(this.relationships).forEach(([animalId, parents]) => {
            const childCard = this.animalCards[animalId];
            
            if (!childCard) return;
            
            // Draw connection to mother
            if (parents.mother && this.animalCards[parents.mother]) {
                this.drawConnection(
                    childCard, 
                    this.animalCards[parents.mother], 
                    '#d14f69'  // Female color
                );
            }
            
            // Draw connection to father
            if (parents.father && this.animalCards[parents.father]) {
                this.drawConnection(
                    childCard, this.animalCards[parents.father], 
                    '#4f7bd1'  // Male color
                );
            }
        });
    }
    
    /**
     * Draw a connection between two animal cards
     * @param {HTMLElement} fromCard - The child card element
     * @param {HTMLElement} toCard - The parent card element
     * @param {string} color - Line color
     */
    drawConnection(fromCard, toCard, color) {
        const fromRect = this.getCardCenter(fromCard);
        const toRect = this.getCardCenter(toCard);
        
        // Start new path
        this.ctx.beginPath();
        this.ctx.strokeStyle = color;
        
        // Calculate control points for a smooth curve
        const midX = (fromRect.x + toRect.x) / 2;
        
        // Draw a bezier curve
        this.ctx.moveTo(fromRect.x, fromRect.y);
        this.ctx.bezierCurveTo(
            midX, fromRect.y,
            midX, toRect.y,
            toRect.x, toRect.y
        );
        
        // Draw the line
        this.ctx.stroke();
    }
    
    /**
     * Get the center point of a card element relative to the canvas
     * @param {HTMLElement} cardElement - The card DOM element
     * @returns {Object} - The center coordinates {x, y}
     */
    getCardCenter(cardElement) {
        const containerRect = this.container.getBoundingClientRect();
        const cardRect = cardElement.getBoundingClientRect();
        
        return {
            x: (cardRect.left + cardRect.right) / 2 - containerRect.left,
            y: (cardRect.top + cardRect.bottom) / 2 - containerRect.top
        };
    }
    
    /**
     * Clean up event listeners when no longer needed
     */
    destroy() {
        window.removeEventListener('resize', this.handleResize);
    }
}

// Initialize once the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create pedigree canvas for the pedigree container
    const pedigreeCanvas = new PedigreeCanvas('pedigree-container');
    
    // Wait a bit for the layout to stabilize before initial drawing
    setTimeout(() => {
        // Add IDs to all animal cards in the pedigree tree for easier reference
        const pedigreeContainer = document.getElementById('pedigree-container');
        if (!pedigreeContainer) {
            console.error('Pedigree container not found!');
            return;
        }
        
        console.log('Pedigree container found, registering cards...');
        
        // Register all animal cards with their IDs
        const animalCards = pedigreeContainer.querySelectorAll('.animal-card');
        console.log(`Found ${animalCards.length} animal cards in pedigree`);
        
        // Add gender class for styling
        animalCards.forEach(card => {
            // Find gender indicator
            const genderEl = card.querySelector('.gender');
            if (genderEl) {
                if (genderEl.classList.contains('female')) {
                    card.classList.add('female');
                } else if (genderEl.classList.contains('male')) {
                    card.classList.add('male');
                }
            }
            
            // Extract ID from parent node's data-id if available, or generate one
            const parentNode = card.closest('[data-id]');
            const animalId = parentNode ? parentNode.dataset.id : `card-${Math.random().toString(36).substring(2, 9)}`;
            
            // Set ID on the card if not already present
            if (!card.dataset.id) {
                card.dataset.id = animalId;
            }
            
            console.log(`Registering animal card with ID: ${animalId}`);
            pedigreeCanvas.registerAnimalCard(animalId, card);
        });
        
        // Example relationship data - in a real app, this would come from your data model
        const relationships = {
            '1': { mother: '3', father: '2' },  // Choco Chip's parents
            '3': { mother: '5', father: '4' },  // Sugar Cube's parents
            '2': { mother: '6', father: '4' }   // Trevor Crop's parents
        };
        
        pedigreeCanvas.setRelationships(relationships);
    }, 500);
    
    // Make the pedigree canvas instance globally accessible for debugging
    window.pedigreeCanvas = pedigreeCanvas;
});
