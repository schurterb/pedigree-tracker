/**
 * Pedigree Tracker - API Service
 * 
 * This file contains functions to interact with the backend API.
 */

const API = {
    /**
     * General API request handler
     * @param {string} endpoint - API endpoint
     * @param {string} method - HTTP method
     * @param {Object} data - Request body for POST/PUT requests
     * @param {Object} queryParams - Query parameters
     * @returns {Promise} - API response with consistent data structure
     */
    request: async function(endpoint, method = 'GET', data = null, queryParams = {}) {
        try {
            // Build URL with query parameters
            let url = `${CONFIG.API_BASE_URL}${endpoint}`;
            if(!url.endsWith('/')) {
                url += '/';
            }
            if (Object.keys(queryParams).length > 0) {
                const params = new URLSearchParams();
                for (const [key, value] of Object.entries(queryParams)) {
                    if (value !== null && value !== undefined) {
                        params.append(key, value);
                    }
                }
                url += `?${params.toString()}`;
            }
            
            // Set up request options
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            
            // Add request body for POST/PUT methods
            if (['POST', 'PUT'].includes(method) && data) {
                options.body = JSON.stringify(data);
            }
            
            // Make the fetch request
            const response = await fetch(url, options);
            
            // Parse response
            if (response.status === 204) {
                return { success: true, data: null }; // No content
            }
            
            // For all other responses, try to parse JSON
            const responseData = await response.json();
            
            // Handle API error responses
            if (!response.ok) {
                // Log the full response data for debugging
                console.log('API Error Response:', responseData);
                
                // The Flask API returns errors in format { message: "error text" }
                // or potentially { errors: [{ message: "error text" }] }
                let errorMessage = 'An error occurred';
                
                if (responseData && typeof responseData === 'object') {
                    if (responseData.message) {
                        errorMessage = responseData.message;
                    } else if (responseData.errors && responseData.errors.length > 0 && responseData.errors[0].message) {
                        errorMessage = responseData.errors[0].message;
                    }
                }
                
                const error = new Error(errorMessage);
                error.statusCode = response.status;
                error.responseData = responseData;
                throw error;
            }
            
            // Wrap the response in a consistent data structure
            // This ensures all API responses have a consistent format
            // with the actual data in the 'data' property
            if (responseData && typeof responseData === 'object') {
                // If it already has a data property, return as is
                if ('data' in responseData) {
                    return responseData;
                }
                // If the response is an array, wrap it in a data property
                else if (Array.isArray(responseData)) {
                    return { data: responseData };
                }
                // If the response is an object and contains success property,
                // it might be a status response, so don't wrap it
                else if ('success' in responseData) {
                    return responseData;
                }
                // Otherwise, wrap the object in a data property
                else {
                    return { data: responseData };
                }
            }
            
            return { data: responseData };
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    

    
    // Animal Types API
    animalTypes: {
        /**
         * Get all animal types
         * @param {Object} options - Sort and filter options
         * @returns {Promise} - List of animal types
         */
        getAll: function(options = {}) {
            return API.request('/animal-types', 'GET', null, options);
        },
        
        /**
         * Get a specific animal type
         * @param {number} id - Animal type ID
         * @returns {Promise} - Animal type details
         */
        getById: function(id) {
            return API.request(`/animal-types/${id}`, 'GET');
        },
        
        /**
         * Create a new animal type
         * @param {Object} animalType - Animal type data
         * @returns {Promise} - Created animal type
         */
        create: function(animalType) {
            return API.request('/animal-types', 'POST', animalType);
        },
        
        /**
         * Update an animal type
         * @param {number} id - Animal type ID
         * @param {Object} animalType - Updated animal type data
         * @returns {Promise} - Updated animal type
         */
        update: function(id, animalType) {
            return API.request(`/animal-types/${id}`, 'PUT', animalType);
        },
        
        /**
         * Delete an animal type
         * @param {number} id - Animal type ID
         * @returns {Promise} - Delete status
         */
        delete: function(id) {
            return API.request(`/animal-types/${id}`, 'DELETE');
        }
    },
    
    // Animals API
    animals: {
        /**
         * Get all animals with optional filtering
         * @param {Object} options - Filter options (type_id, search, sort, direction, page, limit)
         * @returns {Promise} - List of animals
         */
        getAll: function(options = {}) {
            return API.request('/animals', 'GET', null, options);
        },
        
        /**
         * Get a specific animal by ID
         * @param {number} id - Animal ID
         * @returns {Promise} - Animal details
         */
        getById: function(id) {
            return API.request(`/animals/${id}`, 'GET');
        },
        
        /**
         * Create a new animal
         * @param {Object} animal - Animal data
         * @returns {Promise} - Created animal
         */
        create: function(animal) {
            return API.request('/animals', 'POST', animal);
        },
        
        /**
         * Update an animal
         * @param {number} id - Animal ID
         * @param {Object} animal - Updated animal data
         * @returns {Promise} - Updated animal
         */
        update: function(id, animal) {
            return API.request(`/animals/${id}`, 'PUT', animal);
        },
        
        /**
         * Delete an animal
         * @param {number} id - Animal ID
         * @returns {Promise} - Delete status
         */
        delete: function(id) {
            return API.request(`/animals/${id}`, 'DELETE');
        },
        
        /**
         * Get pedigree data for an animal
         * @param {number} id - Animal ID
         * @param {number} generations - Number of generations to include
         * @returns {Promise} - Pedigree data
         */
        getPedigree: function(id, generations = CONFIG.DEFAULT_GENERATIONS) {
            return API.request(`/animals/${id}/pedigree`, 'GET', null, { generations });
        },
        
        /**
         * Get offspring for an animal
         * @param {number} id - Animal ID
         * @param {Object} options - Sort options
         * @returns {Promise} - List of offspring
         */
        getOffspring: function(id, options = {}) {
            return API.request(`/animals/${id}/offspring`, 'GET', null, options);
        }
    },
    
    // Parents API
    parents: {
        /**
         * Get potential parents for a new animal
         * @param {number} typeId - Animal type ID
         * @param {string} gender - Filter by gender ('male' or 'female')
         * @returns {Promise} - List of potential parents
         */
        getPotential: function(typeId, gender = null) {
            const options = gender ? { gender } : {};
            return API.request(`/animal-types/${typeId}/potential-parents`, 'GET', null, options);
        }
    }
};
