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
                if (toast.parentNode === container) {
                    container.removeChild(toast);
                }
            }, 300);
        }, displayDuration);
    },
    
    /**
     * Parse an ISO date string (YYYY-MM-DD) into parts without creating a
     * Date object - avoids timezone shifts on calendar dates.
     * @param {string} dateString - ISO date string
     * @returns {?Object} - {year, month, day} or null when unparseable
     */
    parseISODate: function(dateString) {
        if (!dateString || typeof dateString !== 'string') return null;
        const match = dateString.match(/^(\d{4})-(\d{2})-(\d{2})/);
        if (!match) return null;
        return {
            year: parseInt(match[1], 10),
            month: parseInt(match[2], 10),
            day: parseInt(match[3], 10)
        };
    },

    /**
     * Extract the calendar year from an ISO date string.
     * @param {string} dateString - ISO date string
     * @returns {string|number} - Year or empty string
     */
    birthYear: function(dateString) {
        const parts = this.parseISODate(dateString);
        return parts ? parts.year : '';
    },

    /**
     * Format a date string to MM/DD/YYYY format
     * @param {string} dateString - ISO date string
     * @returns {string} - Formatted date
     */
    formatDate: function(dateString) {
        const parts = this.parseISODate(dateString);
        if (!parts) return '';
        const month = String(parts.month).padStart(2, '0');
        const day = String(parts.day).padStart(2, '0');
        return `${month}/${day}/${parts.year}`;
    },

    /**
     * Format a date as YYYY-MM-DD for input[type=date]
     * @param {string} dateString - ISO date string
     * @returns {string} - Formatted date for HTML date input
     */
    formatDateForInput: function(dateString) {
        const parts = this.parseISODate(dateString);
        if (!parts) return '';
        const pad = (n) => String(n).padStart(2, '0');
        return `${parts.year}-${pad(parts.month)}-${pad(parts.day)}`;
    },

    /**
     * Escape a string for safe insertion into HTML.
     * @param {*} value - Value to escape
     * @returns {string} - Escaped text
     */
    escapeHTML: function(value) {
        if (value === null || value === undefined) return '';
        return String(value).replace(/[&<>"']/g, (ch) => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[ch]));
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
    
    // Modal accessibility state
    _modalState: {
        trigger: null,
        keyHandler: null
    },

    /**
     * Get the focusable elements inside a container
     * @param {HTMLElement} container - Element to search
     * @returns {Array} - Focusable elements
     */
    _getFocusable: function(container) {
        const selector = 'button, [href], input, select, textarea, ' +
            '[tabindex]:not([tabindex="-1"])';
        return Array.from(container.querySelectorAll(selector))
            .filter(el => !el.disabled && el.offsetParent !== null);
    },

    /**
     * Show a modal with dialog semantics and focus management
     * @param {string} modalId - ID of the modal to show
     * @param {HTMLElement} [trigger] - Element that opened the modal
     */
    showModal: function(modalId, trigger = null) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.remove('hidden');
        document.getElementById('modal-backdrop').classList.remove('hidden');

        // Remember what opened the modal so focus can be restored
        this._modalState.trigger = trigger || document.activeElement;

        // Make the underlying page inert so background controls cannot
        // be reached by keyboard or pointer while the dialog is open
        const appContainer = document.querySelector('.app-container');
        if (appContainer) {
            appContainer.setAttribute('inert', '');
        }

        const dialog = modal.querySelector('.modal-content') || modal;
        const focusable = this._getFocusable(dialog);
        (focusable[0] || dialog).focus();

        // Trap Tab/Shift+Tab inside the dialog, close on Escape
        this._modalState.keyHandler = (e) => {
            if (modal.classList.contains('hidden')) return;
            if (e.key === 'Escape') {
                e.preventDefault();
                this.hideModals();
                return;
            }
            if (e.key !== 'Tab') return;
            const items = this._getFocusable(dialog);
            if (items.length === 0) {
                e.preventDefault();
                return;
            }
            const first = items[0];
            const last = items[items.length - 1];
            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        };
        document.addEventListener('keydown', this._modalState.keyHandler, true);
    },

    /**
     * Hide all modals and restore focus to the element that opened them
     */
    hideModals: function() {
        // Hide all modals
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.classList.add('hidden');
        });

        // Hide backdrop
        document.getElementById('modal-backdrop').classList.add('hidden');

        // Remove focus trap
        if (this._modalState.keyHandler) {
            document.removeEventListener('keydown', this._modalState.keyHandler, true);
            this._modalState.keyHandler = null;
        }

        // Re-enable the underlying page
        const appContainer = document.querySelector('.app-container');
        if (appContainer) {
            appContainer.removeAttribute('inert');
        }

        // Return focus to the trigger element
        const trigger = this._modalState.trigger;
        if (trigger && typeof trigger.focus === 'function' && trigger.isConnected) {
            trigger.focus();
        }
        this._modalState.trigger = null;
    },
    
    /**
     * Set active tab
     * @param {number|string} typeId - Animal type ID
     */
    setActiveTab: function(typeId) {
        // Remove active class from all tabs
        const tabs = document.querySelectorAll('.tab-btn');
        tabs.forEach(tab => {
            tab.classList.remove('active');
            tab.setAttribute('aria-selected', 'false');
        });

        // Set active class on selected tab
        const activeTab = document.querySelector(`.tab-btn[data-type-id="${typeId}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
            activeTab.setAttribute('aria-selected', 'true');
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
     * @param {string} gender - Gender ('male', 'female' or 'unknown')
     * @returns {string} - Gender icon
     */
    getGenderIcon: function(gender) {
        if (gender === 'female') return '♀';
        if (gender === 'male') return '♂';
        return '?';
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
