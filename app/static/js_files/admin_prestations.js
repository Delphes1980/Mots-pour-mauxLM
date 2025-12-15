const API_PRESTATIONS_URL = '/api/v1/prestations';
let editingPrestationId = null;


// Fonction qui remplit les lignes du tableau avec les 2 boutons (Modifier et Supprimer) en bout de ligne
function renderPrestations(prestations) {
    const tableBody = document.getElementById('prestation-name-result');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    if (!prestations || prestations.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="2" style="text-align: center;">Aucune prestation trouvée</td></tr>';
        return;
    }

    prestations.forEach(prestation => {
        const tr = document.createElement('tr');
        tr.dataset.id = prestation.id;

        tr.innerHTML = `
            <td data-label="Nom" class="prestation-name-cell">${prestation.name}</td>
            <td class="actions-cell prestation-actions" data-label="Actions">
                <button class="modify-button prestation-modify-button" data-id="${prestation.id}" data-name="${prestation.name}" aria-label="Modifier ${prestation.name}">Modifier</button>
                <button class="delete-button prestation-delete-button" data-id="${prestation.id}" data-name="${prestation.name}" aria-label="Supprimer ${prestation.name}">Supprimer</button>
            </td>
            `;
            tableBody.appendChild(tr);
    });

    attachActionListeners();
}


// Fonction qui récupère toutes les prestations
async function fetchAllPrestations() {
    toggleLoadingSpinner('prestation-loading-spinner', true);

    const tableBody = document.getElementById('prestation-name-result');

    if (tableBody) {
        tableBody.innerHTML = '';
    }

    try {
        const response = await fetch(API_PRESTATIONS_URL, {
            method: 'GET', 
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 403 || response.status === 401) {
                showFeedbackMessage("Accès refusé. Vous devez être connecté en tant qu'administrateur", true);
                return;
            }
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();

        // Stocke les données dans le cache
        allPrestationsCache = data;

        // Filtre "Ghost prestation" de l'affichage
        const filteredData = data.filter(prestation => prestation.name !== "Ghost prestation");
        renderPrestations(filteredData);
    
    } catch (error) {
        console.error('Erreur lors de la récupération des prestations: ', error);
        if (tableBody) {
            tableBody.innerHTML = '<tr><td colspan="2" style="text-align: center; color: red;">Erreur de chargement des données</td></tr>';
        }
    } finally {
        toggleLoadingSpinner('prestation-loading-spinner', false);
    }
}


// Fonction pour chercher une prestation par nom
async function fetchPrestationByName() {
    const searchNameInput = document.getElementById('search-name-input');
    const name = searchNameInput ? searchNameInput.value.trim() : '';

    if (!isValidInput(name)) {
        showFeedbackMessage('Veuillez entrer un nom de prestation à rechercher', true);
        return;
    }

    toggleLoadingSpinner('prestation-loading-spinner', true);

    try {
        const filteredResults = allPrestationsCache.filter(prestation =>
            prestation.name.toLowerCase().includes(name)
        );

        const finalData = filteredResults.filter(prestation => prestation.name !== "Ghost prestation");

        renderPrestations(finalData);

    } catch (error) {
        console.error('Erreur lors de la recherche de la prestation: ', error);
        showFeedbackMessage('Erreur lors de la recherche', true);
        renderPrestations([]);
    } finally {
        toggleLoadingSpinner('prestation-loading-spinner', false);
    }
}


// Fonction pour la création de la prestation
async function createPrestation(event) {
    event.preventDefault();

    const createNameInput = document.getElementById('creation');
    const createButton = document.getElementById('create-prestation-button');
    const searchTypeSelect = document.getElementById('search-type-select');

    const name = createNameInput ? createNameInput.value.trim() : '';

    if (!isValidInput(name)) {
        showFeedbackMessage('Veuillez entrer le nom d\'une prestation', true);
        return;
    }

    if (name.toLowerCase() === "ghost prestation") {
        showFeedbackMessage('Ce nom est réservé au système', true);
        return;
    }

    const data = { name: name };

    const csrfToken = getCookie('csrf_access_token');
    if (!csrfToken) {
        console.error('Token CSRF manquant');
        showFeedbackMessage('Session invalide, veuillez rafraichir la page', true);
        return;
    }

    createButton.disabled = true;
    createButton.textContent = 'Enregistrement...';

    try {
        const response = await fetch(API_PRESTATIONS_URL, {
            method: 'POST', 
            credentials: 'include', 
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrfToken
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erreur lors de la création');
        }

        showFeedbackMessage('Prestation créée avec succès');
        createNameInput.value = '';

        const clearButton = createNameInput.nextElementSibling;
        if (clearButton && clearButton.classList.contains('clear-input-button')) {
            clearButton.style.display = 'none';
        }

        const hiddenInput = document.getElementById('search-type-select');
        const newPrestation = await response.json();
        allPrestationsCache.push(newPrestation);

        if (hiddenInput && hiddenInput.value === 'all') {
            await fetchAllPrestations();
        }

    } catch (error) {
        console.error('Erreur lors de la création de la prestation: ', error);
        showFeedbackMessage(`Erreur: ${error.message}`, true);
    } finally {
        createButton.disabled = false;
        createButton.textContent = 'Enregistrer';
    }
}


// Fonction qui déclenche le mode édition quand on clique sur 'Modifier'
function handleModifyClick(id, currentName) {
    if (editingPrestationId) {
        showFeedbackMessage('Veuillez enregistrer ou annuler la modification en cours', true);
        return;
    }

    editingPrestationId = id;

    const row = document.querySelector(`tr[data-id="${id}"]`);
    const nameCell = row ? row.querySelector('.prestation-name-cell') : null;
    const actionsCell = row ? row.querySelector('.actions-cell') : null;

    if (nameCell && actionsCell) {
        nameCell.innerHTML = `
            <input type="text" id="edit-input-${id}" value="${currentName}" class="modify-input" aria-label="Modifier le nom de la prestation">
        `;
        
        actionsCell.innerHTML = `
            <button class="save-edit-button" data-id="${id}" aria-label="Enregister la modification">Enregistrer</button>
            <button class="cancel-edit-button" data-id="${id}" data-original-name="${currentName}" aria-label="Annuler la modification">Annuler</button>
            `;

        attachPrestationSaveAndCancelListeners(id, currentName);
    }
}


// Fonction pour la modification de la prestation
async function modifyPrestation(id, newName) {
    if (!id || !newName) return;

    if (!isValidInput(newName)) {
        showFeedbackMessage('Veuillez entrer le nom d\'une prestation', true);
        return;
    }

    // Empêche de renommer en "Ghost prestation"
    if (newName.trim().toLowerCase() === "ghost prestation") {
        showFeedbackMessage('Ce nom est réservé au système', true);
        return;
    }

    const csrfToken = getCookie('csrf_access_token');
    if (!csrfToken) {
        console.error('Token CSRF manquant');
        showFeedbackMessage('Session invalide, veuillez rafraichir la page', true);
        return;
    }

    const data = { name: newName };
    const saveButton = document.querySelector(`.save-edit-button[data-id="${id}"]`);

    if (saveButton) saveButton.textContent = 'Enregistrement...';

    try {
        const response = await fetch(`${API_PRESTATIONS_URL}/${id}`, {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrfToken
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Echec de la modification de ${id}`);
        }

        showFeedbackMessage('Prestation modifiée avec succès');
        await fetchAllPrestations();

    } catch (error) {
        console.error('Erreur lors de la modification de la prestation: ', error);
        showFeedbackMessage(`Echec de la modification: ${error.message}`, true);

        if (saveButton) saveButton.textContent = 'Enregistrer';
        await fetchAllPrestations();
    } finally {
        editingPrestationId = null;
    }
}


// Fonction qui gère la confirmation de la suppression d'une prestation
function deletePrestationConfirmation(id, name) {
    const modalOverlay = document.getElementById('confirmation-modal-overlay');
    const modalMessage = document.getElementById('modal-message');
    const modalConfirmButton = document.getElementById('modal-confirm-button');

    if (!modalOverlay || !modalMessage || !modalConfirmButton) return;

    modalMessage.textContent = `Êtes-vous sûr de vouloir supprimer la prestation: "${name}?`;
    modalOverlay.style.display = 'flex';

    const newConfirmButton = modalConfirmButton.cloneNode(true);
    modalConfirmButton.parentNode.replaceChild(newConfirmButton, modalConfirmButton);

    newConfirmButton.dataset.deleteId = id;

    newConfirmButton.addEventListener('click', () => {
        const deleteId = newConfirmButton.dataset.deleteId;
        if (deleteId) {
            deletePrestation(deleteId);
        }
        closePrestationModal();
    });
}


// Fonction qui ferme la modale
function closePrestationModal() {
    const modalOverlay = document.getElementById('confirmation-modal-overlay');
    const modalConfirmButton = document.getElementById('modal-confirm-button');

    if (modalOverlay) {
        modalOverlay.style.display = 'none';
    }
    if (modalConfirmButton) {
        modalConfirmButton.dataset.deleteId ='';
    }
}


// Fonction qui gère la suppression d'une prestation
async function deletePrestation(id) {
    const csrfToken = getCookie('csrf_access_token');
    if (!csrfToken) {
        console.error('Token CSRF manquant');
        showFeedbackMessage('Session invalide, veuillez rafraichir la page', true);
        return;
    }

    try {
        const response = await fetch(`${API_PRESTATIONS_URL}/${id}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrfToken
            }
        });

        if (response.status === 200 || response.status === 204) {
            showFeedbackMessage('Prestation supprimée avec succès');
            await fetchAllPrestations();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || `Echec de la suppression: ${response.status}`);
        }

    } catch (error) {
        console.error('Erreur lors de la suppression de la prestation: ', error);
        showFeedbackMessage(`Erreur: ${error.message}`, true);
    }
}


// Fonction qui gère les boutons 'Modifier' et 'Supprimer'
function attachActionListeners() {
    // Ecouteur pour le bouton 'Supprimer'
    document.querySelectorAll('.prestation-delete-button').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.dataset.id;
            const name = button.dataset.name;
            deletePrestationConfirmation(id, name);
        });
    });

    // Ecouteur pour le bouton 'Modifier'
    document.querySelectorAll('.prestation-modify-button').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.dataset.id;
            const currentName = button.dataset.name;

            handleModifyClick(id, currentName);
        });
    });
}


// Fonction qui gère les boutons 'Enregistrer' et 'Annuler'
function attachPrestationSaveAndCancelListeners(id, originalName) {
    // Ecouteur pour le bouton 'Enregistrer'
    const saveButton = document.querySelector(`.save-edit-button[data-id="${id}"]`);
    if (saveButton) {
        saveButton.addEventListener('click', () => {
            const inputField = document.getElementById(`edit-input-${id}`);
            if (inputField) {
                const newValue = inputField.value.trim();
                if (!isValidInput(newValue)) {
                    showFeedbackMessage('Veuillez entrer le nom d\'une prestation', true);
                    return;
                }
                modifyPrestation(id, inputField.value);
            } else {
                showFeedbackMessage('Erreur: Champ de saisie introuvable', true);
            }
        });
    }

    // Ecouteur pour le bouton 'Annuler'
    const cancelButton = document.querySelector(`.cancel-edit-button[data-id="${id}"]`);
    if (cancelButton) {
        cancelButton.addEventListener('click', () => {
            fetchAllPrestations();
            editingPrestationId = null;
        });
    }
}


// Fonction qui gère le menu déroulant
function setupCustomSelect() {
    const selected = document.getElementById('admin-select-selected');
    const items = document.getElementById('admin-select-items');
    const hiddenInput = document.getElementById('search-type-select');

    if (!selected || !items ||!hiddenInput) return;

    selected.addEventListener('click', () => {
        items.classList.toggle('select-hide');
    });

    items.querySelectorAll('div').forEach(item => {
        item.addEventListener('click', () => {
            selected.textContent = item.textContent;
            hiddenInput.value = item.dataset.value;
            items.classList.add('select-hide');

            toggleSearchVisibility();
        });
    });

    document.addEventListener('click', (e) => {
        if (!selected.contains(e.target) && !items.contains(e.target)) {
            items.classList.add('select-hide');
        }
    });
}


// Fonction pour basculer l'affichage de la recherche
function toggleSearchVisibility() {
    const searchByNameContainer = document.getElementById('search-by-name-container');
    const hiddenInput = document.getElementById('search-type-select');
    const searchNameInput = document.getElementById('search-name-input');

    if (!searchByNameContainer || !hiddenInput || !searchNameInput) return;

    const selectedValue = hiddenInput.value;

    if (selectedValue === 'by-name') {
        if (searchByNameContainer) {
            searchByNameContainer.style.display = 'flex';
        }
    } else if (selectedValue === 'all') {
        if (searchByNameContainer) {
            searchByNameContainer.style.display = 'none';
            searchNameInput.value = '';
            const clearButton = searchNameInput.nextElementSibling;
            if (clearButton && clearButton.classList.contains('clear-input-button')) {
                clearButton.style.display = 'none';
            }
        }
        fetchAllPrestations();
    }
}


// Fonction qui réinitialise la section après chaque clic ailleurs
function resetPrestationsSection() {
    // Reset du menu déroulant
    const searchSelectInput = document.getElementById('search-type-select');
    const searchSelectText = document.getElementById('admin-select-selected');
    if (searchSelectInput) {
        searchSelectInput.value = 'all';
    }
    if (searchSelectText) {
        searchSelectText.textContent = 'Toutes les prestations';
    }

    // Vide les champs de recherche
    const nameInput = document.getElementById('search-name-input');
    if (nameInput) {
        nameInput.value = '';
        const clearButton = nameInput.nextElementSibling;
        if (clearButton && clearButton.classList.contains('clear-input-button')) {
            clearButton.style.display = 'none';
        }
    }

    toggleSearchVisibility();
    fetchAllPrestations();
}


// Fonction d'initialisation pour la section prestations
function init_prestations() {
    resetPrestationsSection();

    fetchAllPrestations();
    if (window.prestationsInitialized) {
        return;
    }

    setupClearButton('.search-field input, .creation-field input');
    setupCustomSelect();

    // Gestion unique du toggle initial
    const searchByNameContainer = document.getElementById('search-by-name-container');
    const hiddenInput = document.getElementById('search-type-select');
    if (searchByNameContainer && hiddenInput && hiddenInput.value === 'all') {
        searchByNameContainer.style.display = 'none';
    }

    const searchNameButton = document.getElementById('search-name-button');
    const createForm = document.getElementById('create-prestation-form');

    // Ecouteurs pour la modale
    const modalOverlay = document.getElementById('confirmation-modal-overlay');
    const modalCancelButton = document.getElementById('modal-cancel-button');

    if (modalCancelButton) {
        modalCancelButton.addEventListener('click', closePrestationModal);
    }

    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                closePrestationModal();
            }
        });
    }

    toggleSearchVisibility();

    if (searchNameButton) {
        searchNameButton.addEventListener('click', (e) => {
            e.preventDefault();
            fetchPrestationByName();
        });
    }

    if (createForm) {
        createForm.addEventListener('submit', createPrestation);
    }

    fetchAllPrestations();

    window.prestationsInitialized = true;
}

window.init_prestations = init_prestations;
