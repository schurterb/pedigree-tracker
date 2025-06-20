/**
 * Pedigree Tracker - Utility Functions
 * 
 * This file contains various utility functions used throughout the application.
 */

const Utils = {
    /**
     * Display a toast notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, info)
     * @param {number} duration - Duration in milliseconds
     */
    showToast: function(message, type = 'info', duration = null) {
        const container = document.getElementById('toast-container');
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        // Add toast to container
        container.appendChild(toast);
        
        // Set automatic timeout
        const displayDuration = duration || CONFIG.NOTIFICATIONS[type.toUpperCase()] || 3000;
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                container.removeChild(toast);
            }, 300);
        }, displayDuration);
    },
    
    /**
     * Format a date string to MM/DD/YYYY format
     * @param {string} dateString - ISO date string
     * @returns {string} - Formatted date
     */
    formatDate: function(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '';
        
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const year = date.getFullYear();
        
        return `${month}/${day}/${year}`;
    },
    
    /**
     * Format a date as YYYY-MM-DD for input[type=date]
     * @param {string} dateString - ISO date string
     * @returns {string} - Formatted date for HTML date input
     */
    formatDateForInput: function(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '';
        
        return date.toISOString().split('T')[0];
    },
    
    /**
     * Show loading indicator
     */
    showLoading: function() {
        document.getElementById('loading-indicator').classList.remove('hidden');
    },
    
    /**
     * Hide loading indicator
     */
    hideLoading: function() {
        document.getElementById('loading-indicator').classList.add('hidden');
    },
    
    /**
     * Show a modal
     * @param {string} modalId - ID of the modal to show
     */
    showModal: function(modalId) {
        document.getElementById(modalId).classList.remove('hidden');
        document.getElementById('modal-backdrop').classList.remove('hidden');
    },
    
    /**
     * Hide all modals
     */
    hideModals: function() {
        // Hide all modals
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.classList.add('hidden');
        });
        
        // Hide backdrop
        document.getElementById('modal-backdrop').classList.add('hidden');
    },
    
    /**
     * Set active tab
     * @param {string} typeId - Animal type ID
     */
    setActiveTab: function(typeId) {
        // Remove active class from all tabs
        const tabs = document.querySelectorAll('.tab-btn');
        tabs.forEach(tab => tab.classList.remove('active'));
        
        // Set active class on selected tab
        const activeTab = document.querySelector(`.tab-btn[data-type="${typeId}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
    },
    
    /**
     * Show a specific view and hide others
     * @param {string} viewId - ID of the view to show
     */
    showView: function(viewId) {
        // Hide all views
        const views = document.querySelectorAll('.view');
        views.forEach(view => view.classList.remove('active'));
        
        // Show selected view
        const activeView = document.getElementById(viewId);
        if (activeView) {
            activeView.classList.add('active');
        }
    },
    
    /**
     * Get the gender icon
     * @param {string} gender - Gender ('male' or 'female')
     * @returns {string} - Gender icon
     */
    getGenderIcon: function(gender) {
        return gender === 'female' ? '♀' : '♂';
    },
    
    /**
     * Generate a timestamp for filenames
     * @returns {string} - Timestamp string
     */
    generateTimestamp: function() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        
        return `${year}${month}${day}_${hours}${minutes}`;
    },
    
    /**
     * Deep clone an object
     * @param {Object} obj - Object to clone
     * @returns {Object} - Cloned object
     */
    deepClone: function(obj) {
        return JSON.parse(JSON.stringify(obj));
    },
    
    /**
     * Get formdata from a form
     * @param {HTMLFormElement} form - Form element
     * @returns {Object} - Form data as an object
     */
    getFormData: function(formElement) {
        const data = {};
        
        // Get all input, select, and textarea elements in the form
        const elements = formElement.querySelectorAll('input, select, textarea');
        
        elements.forEach(element => {
            if (element.name) {
                if (element.type === 'radio' || element.type === 'checkbox') {
                    if (element.checked) {
                        data[element.name] = element.value;
                    }
                } else {
                    data[element.name] = element.value;
                }
            }
        });
        
        return data;
    }
};
