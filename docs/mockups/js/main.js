/**
 * Pedigree Tracker Application
 * Main JavaScript file for UI interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const tabButtons = document.querySelectorAll('.tab-btn');
    const animalItems = document.querySelectorAll('.animal-item');
    const addAnimalBtn = document.getElementById('add-animal-btn');
    const sidebarAddBtn = document.getElementById('sidebar-add-btn');
    const saveDetailsBtn = document.getElementById('save-details-btn');
    const showPedigreeBtn = document.getElementById('show-pedigree-btn');
    const saveNewBtn = document.getElementById('save-new-btn');
    const cancelNewBtn = document.getElementById('cancel-new-btn');
    const modalBackdrop = document.getElementById('modal-backdrop');
    
    // Views
    const pedigreeView = document.getElementById('pedigree-view');
    const detailsView = document.getElementById('details-view');
    const addAnimalView = document.getElementById('add-animal-view');
    
    // Tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked tab
            button.classList.add('active');
            
            // Here we would normally fetch animals of the selected type
            console.log(`Switched to ${button.dataset.type} tab`);
        });
    });
    
    // Animal selection
    animalItems.forEach(item => {
        item.addEventListener('click', () => {
            // Remove selected class from all animals
            animalItems.forEach(animal => animal.classList.remove('selected'));
            // Add selected class to clicked animal
            item.classList.add('selected');
            
            // Show details view for the selected animal
            showView(detailsView);
            console.log(`Selected animal with ID ${item.dataset.id}`);
        });
    });
    
    // Add animal button (header)
    addAnimalBtn.addEventListener('click', () => {
        showView(addAnimalView);
        console.log('Add animal button clicked (header)');
    });
    
    // Add animal button (sidebar)
    sidebarAddBtn.addEventListener('click', () => {
        showView(addAnimalView);
        console.log('Add animal button clicked (sidebar)');
    });
    
    // Save details button
    saveDetailsBtn.addEventListener('click', () => {
        // Here we would normally save the animal details
        console.log('Animal details saved');
        showView(pedigreeView);
    });
    
    // Show pedigree button
    showPedigreeBtn.addEventListener('click', () => {
        showView(pedigreeView);
        console.log('Switched to pedigree view');
    });
    
    // Save new animal button
    saveNewBtn.addEventListener('click', () => {
        // Here we would normally create a new animal
        console.log('New animal created');
        showView(pedigreeView);
    });
    
    // Cancel new animal button
    cancelNewBtn.addEventListener('click', () => {
        showView(pedigreeView);
        console.log('New animal creation cancelled');
    });
    
    // Animal cards in pedigree view
    const animalCards = document.querySelectorAll('.animal-card');
    animalCards.forEach(card => {
        card.addEventListener('click', () => {
            // Here we would normally show details for the clicked animal
            console.log(`Clicked on ${card.querySelector('.name').textContent} in pedigree view`);
            showView(detailsView);
        });
    });
    
    // Helper function to switch views
    function showView(viewToShow) {
        // Hide all views
        pedigreeView.classList.remove('active');
        detailsView.classList.remove('active');
        addAnimalView.classList.remove('active');
        
        // Show the requested view
        viewToShow.classList.add('active');
    }
});
