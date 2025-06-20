/**
 * Pedigree Tracker - Main Application
 * 
 * This is the main JavaScript file that initializes and manages the Pedigree Tracker application.
 */

const App = {
    // Current application state
    state: {
        currentAnimalTypeId: null,
        currentAnimalId: null,
        animalTypes: [],
        animals: []
    },
    
    /**
     * Initialize the application
     */
    init: async function() {
        try {
            // Show loading indicator
            Utils.showLoading();
            
            // Initialize components
            PedigreeTree.init();
            Export.init();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Load initial data
            await this.loadAnimalTypes();
            
            // Hide loading indicator
            Utils.hideLoading();
        } catch (error) {
            Utils.hideLoading();
            Utils.showToast(`Error initializing application: ${error.message}`, 'error');
            console.error('Initialization error:', error);
        }
    },
    
    /**
     * Set up event listeners for UI interactions
     */
    setupEventListeners: function() {
        // Animal type tabs
        const tabs = document.querySelectorAll('.animal-tabs .tab-btn');
        tabs.forEach(tab => {
            if (!tab.classList.contains('tab-add')) {
                tab.addEventListener('click', (e) => {
                    const typeId = e.currentTarget.dataset.type;
                    this.switchAnimalType(typeId);
                });
            }
        });
        
        // Edit animal button
        document.getElementById('edit-animal-btn').addEventListener('click', () => {
            if (this.state.currentAnimalId) {
                this.loadAnimalDetails(this.state.currentAnimalId);
            }
        });
        
        // Add animal type button
        document.querySelector('.tab-add').addEventListener('click', () => {
            Utils.showModal('add-type-modal');
        });
        
        // Add animal buttons
        document.getElementById('sidebar-add-btn').addEventListener('click', () => {
            this.showAddAnimalForm();
        });
        
        // Cancel add animal
        document.getElementById('cancel-new-btn').addEventListener('click', () => {
            this.showPedigreeView();
        });
        
        // Save new animal
        document.getElementById('save-new-btn').addEventListener('click', () => {
            this.saveNewAnimal();
        });
        
        // Switch to pedigree view
        document.getElementById('show-pedigree-btn').addEventListener('click', () => {
            this.showPedigreeView();
        });
        
        // Save animal details
        document.getElementById('save-details-btn').addEventListener('click', () => {
            this.saveAnimalDetails();
        });
        
        // Close modal buttons
        document.querySelectorAll('.close-modal, .cancel-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                Utils.hideModals();
            });
        });
        
        // Save new animal type
        document.getElementById('save-type-btn').addEventListener('click', () => {
            this.saveNewAnimalType();
        });
        
        // Modal backdrop click to close
        document.getElementById('modal-backdrop').addEventListener('click', () => {
            Utils.hideModals();
        });
    },
    
    /**
     * Load all animal types from the API
     */
    loadAnimalTypes: async function() {
        try {
            // Get animal types from API
            const response = await API.animalTypes.getAll();
            this.state.animalTypes = response.data || [];
            
            // Update UI with animal types (even if empty)
            this.updateAnimalTypeTabs();
            
            // If no animal types exist, show a message
            if (this.state.animalTypes.length === 0) {
                Utils.showToast('No animal types found. Use the + button to create your first animal type.', 'info', CONFIG.NOTIFICATIONS.INFO * 2);
                // Show empty state
                document.querySelector('.main-display').innerHTML = `
                    <div class="empty-state">
                        <h2>Welcome to Pedigree Tracker</h2>
                        <p>Get started by creating your first animal type using the + button in the top navigation.</p>
                    </div>
                `;
            } else {
                // Select first animal type
                this.switchAnimalType(this.state.animalTypes[0].name.toLowerCase());
            }
        } catch (error) {
            Utils.showToast(`Error connecting to backend API: ${error.message}`, 'error');
            console.error('Failed to load animal types:', error);
            
            // Clear any existing tabs
            this.updateAnimalTypeTabs();
            
            // Show error state
            document.querySelector('.main-display').innerHTML = `
                <div class="empty-state error-state">
                    <h2>Connection Error</h2>
                    <p>Unable to connect to the backend API. Please make sure the backend server is running.</p>
                    <button id="retry-connection" class="primary-btn">Retry Connection</button>
                </div>
            `;
            
            // Add retry button event listener
            document.getElementById('retry-connection')?.addEventListener('click', () => {
                Utils.showLoading();
                setTimeout(() => {
                    this.loadAnimalTypes().finally(() => Utils.hideLoading());
                }, 500);
            });
        }
    },
    

    
    /**
     * Update animal type tabs in the UI
     */
    updateAnimalTypeTabs: function() {
        const tabContainer = document.querySelector('.animal-tabs');
        const addTab = document.querySelector('.tab-add');
        
        // Remove existing type tabs
        const existingTabs = document.querySelectorAll('.tab-btn:not(.tab-add)');
        existingTabs.forEach(tab => tab.remove());
        
        // Create tabs for each animal type
        this.state.animalTypes.forEach(type => {
            const tab = document.createElement('button');
            tab.className = 'tab-btn';
            tab.dataset.type = type.name.toLowerCase();
            tab.textContent = type.name;
            
            // Add event listener
            tab.addEventListener('click', () => {
                this.switchAnimalType(type.name.toLowerCase());
            });
            
            // Insert before the + tab
            tabContainer.insertBefore(tab, addTab);
        });
    },
    
    /**
     * Switch to a different animal type
     * @param {string} typeId - Animal type ID
     */
    switchAnimalType: async function(typeId) {
        try {
            // Show loading
            Utils.showLoading();
            
            // Update state
            this.state.currentAnimalTypeId = typeId;
            this.state.currentAnimalId = null;
            
            // Update UI
            Utils.setActiveTab(typeId);
            
            // Load animals of this type
            await this.loadAnimals(typeId);
            
            // Show pedigree view
            this.showPedigreeView();
            
            // Hide loading
            Utils.hideLoading();
        } catch (error) {
            Utils.hideLoading();
            Utils.showToast(`Error switching animal type: ${error.message}`, 'error');
            console.error('Failed to switch animal type:', error);
        }
    },
    
    /**
     * Load animals of a specific type
     * @param {string} typeId - Animal type ID
     */
    loadAnimals: async function(typeId) {
        try {
            // Get type ID number from name
            const typeObj = this.state.animalTypes.find(t => t.name.toLowerCase() === typeId);
            if (!typeObj) return;
            
            // Get animals of this type
            const response = await API.animals.getAll({ type_id: typeObj.id });
            this.state.animals = response.data || [];
            
            // Update UI
            this.updateAnimalList();
        } catch (error) {
            Utils.showToast(`Error loading animals: ${error.message}`, 'error');
            console.error('Failed to load animals:', error);
        }
    },
    
    /**
     * Update the animal list in the sidebar
     */
    updateAnimalList: function() {
        const listContainer = document.getElementById('animal-list-container');
        listContainer.innerHTML = '';
        
        if (this.state.animals.length === 0) {
            const emptyMessage = document.createElement('div');
            emptyMessage.className = 'empty-list-message';
            emptyMessage.textContent = 'No animals found. Create your first animal using the Add Animal button.';
            listContainer.appendChild(emptyMessage);
            return;
        }
        
        // Create list items for each animal
        this.state.animals.forEach(animal => {
            const item = document.createElement('div');
            item.className = 'animal-list-item';
            if (this.state.currentAnimalId && animal.id === this.state.currentAnimalId) {
                item.classList.add('selected');
            }
            item.dataset.id = animal.id;
            
            const itemContent = document.createElement('div');
            itemContent.className = 'animal-item-content';
            
            const genderIcon = document.createElement('span');
            genderIcon.className = `gender-icon ${animal.gender}`;
            genderIcon.textContent = Utils.getGenderIcon(animal.gender);
            
            const name = document.createElement('span');
            name.className = 'animal-name';
            name.textContent = animal.name || animal.identifier;
            
            // Add controls div with buttons
            const controls = document.createElement('div');
            controls.className = 'animal-item-controls';
            
            // Add details button
            const detailsBtn = document.createElement('button');
            detailsBtn.className = 'animal-details-btn';
            detailsBtn.title = 'View/Edit Details';
            detailsBtn.innerHTML = '✏️';
            detailsBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent triggering the parent click event
                this.loadAnimalDetails(animal.id);
            });
            
            // Assemble the item
            itemContent.appendChild(genderIcon);
            itemContent.appendChild(name);
            controls.appendChild(detailsBtn);
            
            item.appendChild(itemContent);
            item.appendChild(controls);
            
            // Add click event for pedigree view
            itemContent.addEventListener('click', () => {
                this.selectAnimal(animal.id);
            });
            
            listContainer.appendChild(item);
        });
    },
    
    /**
     * Select an animal and load its pedigree
     * @param {number} animalId - Animal ID to select
     */
    selectAnimal: async function(animalId) {
        try {
            // Show loading indicator
            Utils.showLoading();
            
            // Set current animal ID
            this.state.currentAnimalId = animalId;
            
            // Highlight selected animal in list
            const items = document.querySelectorAll('.animal-list-item');
            items.forEach(item => item.classList.remove('selected'));
            
            const selectedItem = document.querySelector(`.animal-list-item[data-id='${animalId}']`);
            if (selectedItem) {
                selectedItem.classList.add('selected');
            }
            
            // Load animal details
            const response = await API.animals.getById(animalId);
            const animal = response.data;
            
            // Update pedigree title
            document.getElementById('pedigree-title').textContent = `Pedigree: ${animal.name || animal.identifier}`;
            
            // Show edit button
            document.getElementById('edit-animal-btn').style.display = 'block';
            
            // Load pedigree view
            await PedigreeTree.loadPedigree(animalId);
            
            // Show pedigree view
            this.showPedigreeView();
            
            // Hide loading indicator
            Utils.hideLoading();
        } catch (error) {
            Utils.hideLoading();
            Utils.showToast(`Error loading animal: ${error.message}`, 'error');
            console.error('Failed to load animal:', error);
        }
    },
    
    /**
     * Load animal details for editing
     * @param {number} animalId - Animal ID to load details for
     */
    loadAnimalDetails: async function(animalId) {
        try {
            // Show loading
            Utils.showLoading();
            
            // Get animal details
            const response = await API.animals.getById(animalId);
            const animal = response.data;
            
            // Update state
            this.state.currentAnimalId = animalId;
            
            // Fill form with animal data
            document.getElementById('animal-id').value = animal.identifier || '';
            document.getElementById('animal-name').value = animal.name || '';
            document.getElementById('animal-gender').value = animal.gender || 'female';
            document.getElementById('animal-dob').value = Utils.formatDateForInput(animal.date_of_birth);
            document.getElementById('animal-notes').value = animal.notes || '';
            
            // Select correct animal type
            const typeSelect = document.getElementById('animal-type');
            typeSelect.innerHTML = '';
            this.state.animalTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type.id;
                option.textContent = type.name;
                option.selected = type.id === animal.type_id;
                typeSelect.appendChild(option);
            });
            
            // Load mother options
            const motherSelect = document.getElementById('animal-mother');
            motherSelect.innerHTML = '<option value="">-- No mother --</option>';
            
            // Load father options
            const fatherSelect = document.getElementById('animal-father');
            fatherSelect.innerHTML = '<option value="">-- No father --</option>';
            
            // Get potential parents
            const mothers = await API.parents.getPotential(animal.type_id, 'female');
            const fathers = await API.parents.getPotential(animal.type_id, 'male');
            
            // Add mother options
            if (mothers && mothers.data) {
                mothers.data.forEach(mother => {
                    // Skip if this is the current animal
                    if (mother.id === animalId) return;
                    
                    const option = document.createElement('option');
                    option.value = mother.id;
                    option.textContent = `${mother.name || 'Unknown'} (${mother.identifier})`;
                    option.selected = mother.id === animal.mother_id;
                    motherSelect.appendChild(option);
                });
            }
            
            // Add father options
            if (fathers && fathers.data) {
                fathers.data.forEach(father => {
                    // Skip if this is the current animal
                    if (father.id === animalId) return;
                    
                    const option = document.createElement('option');
                    option.value = father.id;
                    option.textContent = `${father.name || 'Unknown'} (${father.identifier})`;
                    option.selected = father.id === animal.father_id;
                    fatherSelect.appendChild(option);
                });
            }
            
            // Load offspring list
            const offspringList = document.getElementById('offspring-list');
            offspringList.innerHTML = '';
            
            const offspringResponse = await API.animals.getOffspring(animalId);
            const offspring = offspringResponse.data || [];
            
            if (offspring.length > 0) {
                offspring.forEach(child => {
                    const li = document.createElement('li');
                    li.textContent = `${child.name || 'Unknown'} (${child.identifier}) - born ${Utils.formatDate(child.date_of_birth)}`;
                    
                    // Add click event to show this animal
                    li.style.cursor = 'pointer';
                    li.addEventListener('click', () => {
                        this.selectAnimal(child.id);
                    });
                    
                    offspringList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'No offspring recorded.';
                offspringList.appendChild(li);
            }
            
            // Update title
            document.getElementById('details-title').textContent = `Animal Details: ${animal.name || animal.identifier}`;
            
            // Show details view
            Utils.showView('details-view');
            
            // Hide loading
            Utils.hideLoading();
        } catch (error) {
            Utils.hideLoading();
            Utils.showToast(`Error loading animal details: ${error.message}`, 'error');
            console.error('Failed to load animal details:', error);
        }
    },
    
    /**
     * Save animal details
     */
    saveAnimalDetails: async function() {
        try {
            // Show loading
            Utils.showLoading();
            
            // Get form values
            const animalData = {
                identifier: document.getElementById('animal-id').value,
                name: document.getElementById('animal-name').value,
                gender: document.getElementById('animal-gender').value,
                date_of_birth: document.getElementById('animal-dob').value,
                type_id: document.getElementById('animal-type').value,
                mother_id: document.getElementById('animal-mother').value || null,
                father_id: document.getElementById('animal-father').value || null,
                notes: document.getElementById('animal-notes').value
            };
            
            // Validate required fields
            if (!animalData.identifier) {
                Utils.hideLoading();
                Utils.showToast('ID/Tag is required.', 'error');
                return;
            }
            
            // Update animal
            await API.animals.update(this.state.currentAnimalId, animalData);
            
            // Reload animals list
            await this.loadAnimals(this.state.currentAnimalTypeId);
            
            // Reload pedigree
            await PedigreeTree.loadPedigree(this.state.currentAnimalId);
            
            // Show toast
            Utils.showToast('Animal updated successfully!', 'success');
            
            // Show pedigree view
            this.showPedigreeView();
            
            // Hide loading
            Utils.hideLoading();
        } catch (error) {
            Utils.hideLoading();
            Utils.showToast(`Error saving animal: ${error.message}`, 'error');
            console.error('Failed to save animal:', error);
        }
    },
    
    /**
     * Show the add animal form
     */
    showAddAnimalForm: async function() {
        try {
            // IMPORTANT: First make the view visible before accessing elements
            Utils.showView('add-animal-view');
            
            // Get current animal type
            const typeObj = this.state.animalTypes.find(t => t.name.toLowerCase() === this.state.currentAnimalTypeId);
            
            // Now clear form fields AFTER the view is visible
            document.getElementById('new-animal-id').value = '';
            document.getElementById('new-animal-name').value = '';
            document.getElementById('new-animal-dob').value = '';
            document.getElementById('new-animal-notes').value = '';
            
            // Set gender to female by default
            document.querySelector('input[name="gender"][value="female"]').checked = true;
            
            // Load animal types
            const typeSelect = document.getElementById('new-animal-type');
            typeSelect.innerHTML = '';
            this.state.animalTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type.id;
                option.textContent = type.name;
                option.selected = type.id === typeObj?.id;
                typeSelect.appendChild(option);
            });
            
            // Load potential mothers
            const motherSelect = document.getElementById('new-animal-mother');
            motherSelect.innerHTML = '<option value="">-- Select mother --</option>';
            
            // Load potential fathers
            const fatherSelect = document.getElementById('new-animal-father');
            fatherSelect.innerHTML = '<option value="">-- Select father --</option>';
            
            if (typeObj) {
                // Get potential parents
                const mothers = await API.parents.getPotential(typeObj.id, 'female');
                const fathers = await API.parents.getPotential(typeObj.id, 'male');
                
                // Add mother options
                if (mothers && mothers.data) {
                    mothers.data.forEach(mother => {
                        const option = document.createElement('option');
                        option.value = mother.id;
                        option.textContent = `${mother.name || 'Unknown'} (${mother.identifier})`;
                        motherSelect.appendChild(option);
                    });
                }
                
                // Add father options
                if (fathers && fathers.data) {
                    fathers.data.forEach(father => {
                        const option = document.createElement('option');
                        option.value = father.id;
                        option.textContent = `${father.name || 'Unknown'} (${father.identifier})`;
                        fatherSelect.appendChild(option);
                    });
                }
            }
        } catch (error) {
            Utils.showToast(`Error preparing form: ${error.message}`, 'error');
            console.error('Failed to prepare add animal form:', error);
        }
    },
    
    /**
     * Save a new animal
     */
    saveNewAnimal: async function() {
        try {
            // Show loading
            Utils.showLoading();
            
            // Get form values
            const animalData = {
                identifier: document.getElementById('new-animal-id').value,
                name: document.getElementById('new-animal-name').value,
                gender: document.querySelector('input[name="gender"]:checked').value,
                date_of_birth: document.getElementById('new-animal-dob').value,
                type_id: document.getElementById('new-animal-type').value,
                mother_id: document.getElementById('new-animal-mother').value || null,
                father_id: document.getElementById('new-animal-father').value || null,
                notes: document.getElementById('new-animal-notes').value
            };
            
            // Validate required fields
            if (!animalData.identifier) {
                Utils.hideLoading();
                Utils.showToast('ID/Tag is required.', 'error');
                return;
            }
            
            // Create animal
            const response = await API.animals.create(animalData);
            const newAnimal = response.data;
            
            // Reload animals list
            await this.loadAnimals(this.state.currentAnimalTypeId);
            
            // Select the new animal
            await this.selectAnimal(newAnimal.id);
            
            // Show toast
            Utils.showToast('Animal added successfully!', 'success');
            
            // Hide loading
            Utils.hideLoading();
        } catch (error) {
            Utils.hideLoading();
            Utils.showToast(`Error adding animal: ${error.message}`, 'error');
            console.error('Failed to add animal:', error);
        }
    },
    
    /**
     * Save a new animal type
     */
    saveNewAnimalType: async function() {
        try {
            // Show loading
            Utils.showLoading();
            
            // Get form values
            const typeData = {
                name: document.getElementById('new-type-name').value,
                description: document.getElementById('new-type-description').value
            };
            
            // Validate required fields
            if (!typeData.name) {
                Utils.hideLoading();
                Utils.showToast('Type name is required.', 'error');
                return;
            }
            
            // Create animal type
            const response = await API.animalTypes.create(typeData);
            
            // The API handler now ensures response.data is always available
            const newType = response.data;
            
            // Reload animal types
            await this.loadAnimalTypes();
            
            // Switch to new type
            if (newType && newType.name) {
                await this.switchAnimalType(newType.name.toLowerCase());
            } else {
                console.warn('Created animal type has unexpected format:', newType);
            }
            
            // Hide modal
            Utils.hideModals();
            
            // Show toast
            Utils.showToast('Animal type added successfully!', 'success');
            
            // Hide loading
            Utils.hideLoading();
        } catch (error) {
            Utils.hideLoading();
            
            // Prepare a more informative error message
            let errorMessage = error.message || 'Unknown error';
            
            // For conflict errors (409), make the message more user-friendly
            if (error.statusCode === 409) {
                errorMessage = `This animal type already exists. Please use a different name.`;
            }
            
            // Show the error message to the user
            Utils.showToast(`Error adding animal type: ${errorMessage}`, 'error');
            
            // Log detailed error information for debugging
            console.error('Failed to add animal type:', {
                message: error.message,
                statusCode: error.statusCode,
                stack: error.stack,
                responseData: error.responseData || 'No response data'
            });
            
            // Additional logging to ensure we capture all information
            if (error.responseData) {
                console.error('Error response data:', JSON.stringify(error.responseData));
            }
        }
    },
    
    /**
     * Show the pedigree view
     */
    showPedigreeView: function() {
        Utils.showView('pedigree-view');
    }
};

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    App.init();
});
