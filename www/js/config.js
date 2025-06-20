/**
 * Pedigree Tracker - Configuration
 * 
 * This file contains global configuration settings for the Pedigree Tracker application.
 */

// Define CONFIG as a global variable
window.CONFIG = {
    // API base URL - no trailing slash (using relative path since API and frontend are on same server)
    API_BASE_URL: '/api/v1',
    
    // Default number of generations to display in pedigree view
    DEFAULT_GENERATIONS: 3,
    
    // Maximum number of generations available
    MAX_GENERATIONS: 5,
    
    // Pedigree tree layout settings
    PEDIGREE_TREE: {
        // Animation duration in milliseconds
        ANIMATION_DURATION: 300,
        
        // Node spacing
        NODE_SPACING: 60,
        
        // Level spacing
        LEVEL_SPACING: 120
    },
    
    // Notification display times in milliseconds
    NOTIFICATIONS: {
        SUCCESS: 3000,
        ERROR: 5000,
        INFO: 4000
    },
    

};
