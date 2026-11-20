/**
 * Pedigree Tracker - Main Application
 *
 * This is the main JavaScript file that initializes and manages the Pedigree Tracker application.
 */

const App = {
    // Current application state
    state: {
        currentAnimalTypeId: null,  // numeric animal-type id
        currentAnimalId: null,
        animalTypes: [],
        animals: [],
        dirtyForm: null,  // 'add' | 'details' | null
        savingNew: false,
        parentRequestSeq: {}  // select id -> latest request sequence
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
            this.setupDirtyTracking();

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
        // Edit animal button
        document.getElementById('edit-animal-btn').addEventListener('click', (e) => {
            if (this.state.currentAnimalId && this.confirmDiscardChanges()) {
                this.loadAnimalDetails(this.state.currentAnimalId);
            }
        });

        // Add animal type button
        document.querySelector('.tab-add').addEventListener('click', (e) => {
            if (!this.confirmDiscardChanges()) return;
            document.getElementById('new-type-name').value = '';
            document.getElementById('new-type-description').value = '';
            Utils.showModal('add-type-modal', e.currentTarget);
        });

        // Edit animal type button
        document.getElementById('edit-type-btn').addEventListener('click', (e) => {
            if (!this.confirmDiscardChanges()) return;
            this.openEditTypeModal(e.currentTarget);
        });

        // Add animal buttons
        document.getElementById('sidebar-add-btn').addEventListener('click', () => {
            if (this.confirmDiscardChanges()) {
                this.showAddAnimalForm();
            }
        });

        // Cancel add animal
        document.getElementById('cancel-new-btn').addEventListener('click', () => {
            if (this.confirmDiscardChanges()) {
                this.showPedigreeView();
            }
        });

        // Save new animal
        document.getElementById('save-new-btn').addEventListener('click', () => {
            this.saveNewAnimal();
        });

        // Switch to pedigree view
        document.getElementById('show-pedigree-btn').addEventListener('click', () => {
            if (this.confirmDiscardChanges()) {
                this.showPedigreeView();
            }
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

        // Save edited animal type
        document.getElementById('save-edit-type-btn').addEventListener('click', () => {
            this.saveEditAnimalType();
        });

        // Delete animal type
        document.getElementById('delete-type-btn').addEventListener('click', () => {
            this.deleteAnimalType();
        });

        // Reload parent options when the type changes in either form
        document.getElementById('new-animal-type').addEventListener('change', (e) => {
            this.populateParentSelects({
                typeId: parseInt(e.target.value, 10),
                motherSelect: document.getElementById('new-animal-mother'),
                fatherSelect: document.getElementById('new-animal-father')
            }).catch((err) => {
                Utils.showToast(`Error loading parents: ${err.message}`, 'error');
                console.error('Failed to load parents:', err);
            });
        });
        document.getElementById('animal-type').addEventListener('change', (e) => {
            this.populateParentSelects({
                typeId: parseInt(e.target.value, 10),
                motherSelect: document.getElementById('animal-mother'),
                fatherSelect: document.getElementById('animal-father'),
                excludeId: this.state.currentAnimalId
            }).catch((err) => {
                Utils.showToast(`Error loading parents: ${err.message}`, 'error');
                console.error('Failed to load parents:', err);
            });
        });

        // Modal backdrop click to close
        document.getElementById('modal-backdrop').addEventListener('click', () => {
            Utils.hideModals();
        });

        // Retry button on the connection-error view
        document.getElementById('retry-connection').addEventListener('click', () => {
            Utils.showLoading();
            setTimeout(() => {
                this.loadAnimalTypes().finally(() => Utils.hideLoading());
            }, 500);
        });
    },

    /**
     * Track dirty state on the add-animal and details forms so navigation
     * away can warn before discarding unsaved input.
     */
    setupDirtyTracking: function() {
        const markDirty = (formKey) => () => {
            this.state.dirtyForm = formKey;
        };

        document.querySelectorAll('#add-animal-view input, #add-animal-view select, #add-animal-view textarea')
            .forEach(el => {
                el.addEventListener('input', markDirty('add'));
                el.addEventListener('change', markDirty('add'));
            });

        document.querySelectorAll('#details-view input, #details-view select, #details-view textarea')
            .forEach(el => {
                el.addEventListener('input', markDirty('details'));
                el.addEventListener('change', markDirty('details'));
            });

        window.addEventListener('beforeunload', (e) => {
            if (this.state.dirtyForm) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    },

    /**
     * Ask the user before discarding an unsaved form.
     * @returns {boolean} - true when it is safe to navigate away
     */
    confirmDiscardChanges: function() {
        if (!this.state.dirtyForm) return true;
        return confirm('You have unsaved changes. Discard them?');
    },

    /**
     * Load all animal types from the API
     * @param {Object} options - preserveView: refresh tabs without switching
     *                           away from the current view/selection
     */
    loadAnimalTypes: async function({ preserveView = false } = {}) {
        try {
            // Get animal types from API
            const response = await API.animalTypes.getAll();
            this.state.animalTypes = response.data || [];

            // Update UI with animal types (even if empty)
            this.updateAnimalTypeTabs();

            // If no animal types exist, show a message
            if (this.state.animalTypes.length === 0) {
                this.state.currentAnimalTypeId = null;
                Utils.showToast('No animal types found. Use the + button to create your first animal type.', 'info', CONFIG.NOTIFICATIONS.INFO * 2);
                // Show empty state (static view - innerHTML replacement would
                // permanently destroy the other views)
                Utils.showView('welcome-view');
            } else {
                // Keep current selection if it still exists, else first type
                const stillExists = this.state.animalTypes.some(
                    t => t.id === this.state.currentAnimalTypeId);
                if (preserveView && stillExists) {
                    // Tabs were already rebuilt above; stay on current view.
                    return;
                }
                const target = stillExists ? this.state.currentAnimalTypeId
                                           : this.state.animalTypes[0].id;
                this.switchAnimalType(target);
            }
        } catch (error) {
            Utils.showToast(`Error connecting to backend API: ${error.message}`, 'error');
            console.error('Failed to load animal types:', error);

            // Clear any existing tabs
            this.updateAnimalTypeTabs();

            // Show error state
            Utils.showView('error-view');
        }
    },

    /**
     * Update animal type tabs in the UI
     */
    updateAnimalTypeTabs: function() {
        const tabContainer = document.querySelector('.animal-tabs');
        const editTab = document.getElementById('edit-type-btn');

        // Remove existing type tabs
        const existingTabs = document.querySelectorAll('.tab-btn:not(.tab-add):not(.tab-edit)');
        existingTabs.forEach(tab => tab.remove());

        // Create tabs for each animal type
        this.state.animalTypes.forEach(type => {
            const tab = document.createElement('button');
            tab.className = 'tab-btn';
            tab.dataset.typeId = type.id;
            tab.setAttribute('role', 'tab');
            tab.setAttribute('aria-selected', 'false');
            tab.textContent = type.name;
            if (type.id === this.state.currentAnimalTypeId) {
                tab.classList.add('active');
                tab.setAttribute('aria-selected', 'true');
            }

            // Add event listener
            tab.addEventListener('click', () => {
                if (this.confirmDiscardChanges()) {
                    this.switchAnimalType(type.id);
                }
            });

            // Insert before the edit/+ buttons
            tabContainer.insertBefore(tab, editTab);
        });

        // Show the edit-category control only when a category is selected
        const editBtn = document.getElementById('edit-type-btn');
        if (editBtn) {
            editBtn.style.display =
                this.state.currentAnimalTypeId ? 'inline-block' : 'none';
        }
    },

    /**
     * Switch to a different animal type
     * @param {number} typeId - Animal type ID
     */
    switchAnimalType: async function(typeId) {
        try {
            // Show loading
            Utils.showLoading();

            // Update state
            this.state.currentAnimalTypeId = typeId;
            this.state.currentAnimalId = null;
            this.state.dirtyForm = null;

            // Update UI
            Utils.setActiveTab(typeId);
            this.updateAnimalTypeTabs();

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
     * @param {number} typeId - Animal type ID
     */
    loadAnimals: async function(typeId) {
        try {
            // Get animals of this type
            const response = await API.animals.getAll({ type_id: typeId });
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

            // Keyboard-accessible selection button
            const selectBtn = document.createElement('button');
            selectBtn.type = 'button';
            selectBtn.className = 'animal-item-content animal-select-btn';
            if (this.state.currentAnimalId && animal.id === this.state.currentAnimalId) {
                selectBtn.setAttribute('aria-current', 'true');
            }

            const genderIcon = document.createElement('span');
            genderIcon.className = `gender-icon ${animal.gender}`;
            genderIcon.textContent = Utils.getGenderIcon(animal.gender);

            const name = document.createElement('span');
            name.className = 'animal-name';
            const displayName = animal.name || animal.identifier || `(unnamed #${animal.id})`;
            name.textContent = displayName;

            // Add controls div with buttons
            const controls = document.createElement('div');
            controls.className = 'animal-item-controls';

            // Add details button
            const detailsBtn = document.createElement('button');
            detailsBtn.type = 'button';
            detailsBtn.className = 'animal-details-btn';
            detailsBtn.title = 'View/Edit Details';
            detailsBtn.setAttribute('aria-label', `Edit details for ${displayName}`);
            detailsBtn.innerHTML = '&#9998;';
            detailsBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent triggering the parent click event
                if (this.confirmDiscardChanges()) {
                    this.loadAnimalDetails(animal.id);
                }
            });

            // Assemble the item
            selectBtn.appendChild(genderIcon);
            selectBtn.appendChild(name);
            controls.appendChild(detailsBtn);

            item.appendChild(selectBtn);
            item.appendChild(controls);

            // Add click event for pedigree view
            selectBtn.addEventListener('click', () => {
                if (this.confirmDiscardChanges()) {
                    this.selectAnimal(animal.id);
                }
            });

            listContainer.appendChild(item);
        });
    },

    /**
     * Select an animal and load its pedigree
     * @param {number} animalId - Animal ID to select
     * @param {Object} options - silent: suppress the error toast
     * @returns {boolean} - true when the pedigree loaded, false otherwise
     */
    selectAnimal: async function(animalId, { silent = false } = {}) {
        try {
            // Show loading indicator
            Utils.showLoading();

            // Set current animal ID
            this.state.currentAnimalId = animalId;

            // Highlight selected animal in list
            const items = document.querySelectorAll('.animal-list-item');
            items.forEach(item => item.classList.remove('selected'));
            document.querySelectorAll('.animal-select-btn')
                .forEach(b => b.removeAttribute('aria-current'));

            const selectedItem = document.querySelector(`.animal-list-item[data-id='${animalId}']`);
            if (selectedItem) {
                selectedItem.classList.add('selected');
                selectedItem.querySelector('.animal-select-btn')
                    ?.setAttribute('aria-current', 'true');
            }

            // Load animal details
            const response = await API.animals.getById(animalId);
            const animal = response.data;

            // Update pedigree title
            document.getElementById('pedigree-title').textContent = `Pedigree: ${animal.name || animal.identifier}`;

            // Show edit button
            document.getElementById('edit-animal-btn').style.display = 'block';

            // Load pedigree view
            await PedigreeTree.loadPedigree(animalId, undefined, { throwOnError: true });

            // Show pedigree view
            this.showPedigreeView();

            // Hide loading indicator
            Utils.hideLoading();
            return true;
        } catch (error) {
            Utils.hideLoading();
            // Clear stale pedigree so the previous animal's tree is not
            // shown under the newly selected row.
            document.getElementById('pedigree-tree').innerHTML = '';
            if (window.pedigreeTree) {
                window.pedigreeTree.animalData = {};
            }
            document.getElementById('pedigree-title').textContent =
                'Pedigree could not be loaded';
            document.getElementById('edit-animal-btn').style.display = 'none';
            this.showPedigreeView();
            if (!silent) {
                Utils.showToast(`Error loading animal: ${error.message}`, 'error');
            }
            console.error('Failed to load animal:', error);
            return false;
        }
    },

    /**
     * Fill a mother/father select pair with eligible parents of a type.
     * Options are rebuilt from the server; a previous selection is kept
     * only when it remains valid for the new type.
     */
    populateParentSelects: async function({typeId, motherSelect, fatherSelect,
                                           excludeId = null,
                                           selectedMotherId = null,
                                           selectedFatherId = null}) {
        // Sequence guard: only the latest request for this select pair may
        // apply its results (ISSUE-005: rapid type changes used to let a
        // slow response for the old type repopulate the selects).
        const key = motherSelect.id;
        const seq = (this.state.parentRequestSeq[key] || 0) + 1;
        this.state.parentRequestSeq[key] = seq;

        // Reset options
        motherSelect.innerHTML = '<option value="">-- No mother --</option>';
        fatherSelect.innerHTML = '<option value="">-- No father --</option>';
        if (!typeId) return;

        let mothers, fathers;
        try {
            [mothers, fathers] = await Promise.all([
                API.parents.getPotential(typeId, 'female'),
                API.parents.getPotential(typeId, 'male')
            ]);
        } catch (error) {
            if (seq !== this.state.parentRequestSeq[key]) return;
            throw error;
        }
        if (seq !== this.state.parentRequestSeq[key]) return;

        const fill = (select, list, selectedId) => {
            (list && list.data || []).forEach(parent => {
                if (excludeId && parent.id === excludeId) return;
                const option = document.createElement('option');
                option.value = parent.id;
                option.textContent = `${parent.name || 'Unknown'} (${parent.identifier})`;
                option.selected = selectedId !== null && parent.id === selectedId;
                select.appendChild(option);
            });
        };

        fill(motherSelect, mothers, selectedMotherId);
        fill(fatherSelect, fathers, selectedFatherId);
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
            this.state.dirtyForm = null;

            // Fill form with animal data
            document.getElementById('animal-id').value = animal.identifier || '';
            document.getElementById('animal-name').value = animal.name || '';
            document.getElementById('animal-gender').value = animal.gender || 'unknown';
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

            // Load mother/father options for the animal's type
            await this.populateParentSelects({
                typeId: animal.type_id,
                motherSelect: document.getElementById('animal-mother'),
                fatherSelect: document.getElementById('animal-father'),
                excludeId: animalId,
                selectedMotherId: animal.mother_id,
                selectedFatherId: animal.father_id
            });

            // Load offspring list
            const offspringList = document.getElementById('offspring-list');
            offspringList.innerHTML = '';

            const offspringResponse = await API.animals.getOffspring(animalId);
            const offspring = offspringResponse.data || [];

            if (offspring.length > 0) {
                offspring.forEach(child => {
                    const li = document.createElement('li');
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'offspring-link';
                    btn.textContent = `${child.name || 'Unknown'} (${child.identifier}) - born ${Utils.formatDate(child.date_of_birth)}`;
                    btn.addEventListener('click', () => {
                        if (this.confirmDiscardChanges()) {
                            this.selectAnimal(child.id);
                        }
                    });
                    li.appendChild(btn);
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

            const dobValue = document.getElementById('animal-dob').value;

            // Get form values
            const animalData = {
                identifier: document.getElementById('animal-id').value.trim(),
                name: document.getElementById('animal-name').value.trim() || null,
                gender: document.getElementById('animal-gender').value,
                date_of_birth: dobValue || null,
                type_id: parseInt(document.getElementById('animal-type').value, 10),
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
            this.state.dirtyForm = null;

            // Reload animals list
            await this.loadAnimals(this.state.currentAnimalTypeId);

            // Reload pedigree
            try {
                await PedigreeTree.loadPedigree(this.state.currentAnimalId);
            } catch (pedigreeError) {
                console.error('Failed to reload pedigree after save:', pedigreeError);
            }

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
            if (this.state.animalTypes.length === 0) {
                Utils.showToast('Create an animal type first (+ in the top navigation).', 'info');
                return;
            }
            // IMPORTANT: First make the view visible before accessing elements
            Utils.showView('add-animal-view');
            this.state.dirtyForm = null;

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
                option.selected = type.id === this.state.currentAnimalTypeId;
                typeSelect.appendChild(option);
            });

            // Load potential parents for the currently selected type
            await this.populateParentSelects({
                typeId: parseInt(typeSelect.value, 10) || null,
                motherSelect: document.getElementById('new-animal-mother'),
                fatherSelect: document.getElementById('new-animal-father')
            });

            // Focus the identifier field for keyboard users
            document.getElementById('new-animal-id').focus();
        } catch (error) {
            Utils.showToast(`Error preparing form: ${error.message}`, 'error');
            console.error('Failed to prepare add animal form:', error);
        }
    },

    /**
     * Save a new animal
     */
    saveNewAnimal: async function() {
        const saveBtn = document.getElementById('save-new-btn');
        // Guard against synthetic/duplicate invocations while a save is in flight
        if (this.state.savingNew) {
            return;
        }
        this.state.savingNew = true;
        try {
            // Prevent duplicate submissions while a save is in flight
            saveBtn.disabled = true;
            Utils.showLoading();

            const dobValue = document.getElementById('new-animal-dob').value;

            // Get form values
            const animalData = {
                identifier: document.getElementById('new-animal-id').value.trim(),
                name: document.getElementById('new-animal-name').value.trim() || null,
                gender: document.querySelector('input[name="gender"]:checked').value,
                date_of_birth: dobValue || null,
                type_id: parseInt(document.getElementById('new-animal-type').value, 10),
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

            // Creation succeeded - leave create mode even if the follow-up
            // read fails (ISSUE-003: a view error is not a save error).
            this.state.dirtyForm = null;
            this.state.currentAnimalId = newAnimal.id;

            // Clear the create form so it never stays populated
            document.getElementById('new-animal-id').value = '';
            document.getElementById('new-animal-name').value = '';
            document.getElementById('new-animal-dob').value = '';
            document.getElementById('new-animal-notes').value = '';

            // Reload animals list
            await this.loadAnimals(this.state.currentAnimalTypeId);

            // Leave the create form
            this.showPedigreeView();
            Utils.hideLoading();

            // Try to show the new animal's pedigree; a failure here must not
            // resurrect the create form (ISSUE-003: a view error is not a
            // save error, so report it specifically).
            const loaded = await this.selectAnimal(newAnimal.id, { silent: true });
            if (loaded) {
                Utils.showToast('Animal added successfully!', 'success');
            } else {
                Utils.showToast(
                    'Animal saved, but its pedigree could not be loaded. ' +
                    'Select it in the list to retry.',
                    'error'
                );
            }
        } catch (error) {
            Utils.hideLoading();
            Utils.showToast(`Error adding animal: ${error.message}`, 'error');
            console.error('Failed to add animal:', error);
        } finally {
            saveBtn.disabled = false;
            this.state.savingNew = false;
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
                name: document.getElementById('new-type-name').value.trim(),
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
            if (newType && newType.id) {
                await this.switchAnimalType(newType.id);
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
        }
    },

    /**
     * Open the edit-category modal for the current animal type
     * @param {HTMLElement} trigger - Button that opened the modal
     */
    openEditTypeModal: function(trigger) {
        const type = this.state.animalTypes.find(
            t => t.id === this.state.currentAnimalTypeId);
        if (!type) {
            Utils.showToast('No category selected.', 'error');
            return;
        }
        document.getElementById('edit-type-name').value = type.name || '';
        document.getElementById('edit-type-description').value = type.description || '';
        Utils.showModal('edit-type-modal', trigger);
    },

    /**
     * Save changes to the current animal type (rename / description)
     */
    saveEditAnimalType: async function() {
        try {
            Utils.showLoading();

            const typeData = {
                name: document.getElementById('edit-type-name').value.trim(),
                description: document.getElementById('edit-type-description').value
            };

            if (!typeData.name) {
                Utils.hideLoading();
                Utils.showToast('Type name is required.', 'error');
                return;
            }

            await API.animalTypes.update(this.state.currentAnimalTypeId, typeData);

            // Reload tabs without resetting the current view
            await this.loadAnimalTypes({ preserveView: true });

            Utils.hideModals();
            Utils.hideLoading();
            Utils.showToast('Category updated successfully!', 'success');
        } catch (error) {
            Utils.hideLoading();
            Utils.showToast(`Error updating category: ${error.message}`, 'error');
            console.error('Failed to update animal type:', error);
        }
    },

    /**
     * Delete the current animal type after confirmation
     */
    deleteAnimalType: async function() {
        const type = this.state.animalTypes.find(
            t => t.id === this.state.currentAnimalTypeId);
        if (!type) return;

        if (!confirm(`Delete category "${type.name}"? This cannot be undone.`)) {
            return;
        }

        try {
            Utils.showLoading();
            await API.animalTypes.delete(type.id);

            Utils.hideModals();
            this.state.currentAnimalTypeId = null;

            // Reload and switch to the first remaining type (or empty state)
            await this.loadAnimalTypes();

            Utils.hideLoading();
            Utils.showToast('Category deleted.', 'success');
        } catch (error) {
            Utils.hideLoading();
            Utils.showToast(`Error deleting category: ${error.message}`, 'error');
            console.error('Failed to delete animal type:', error);
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
