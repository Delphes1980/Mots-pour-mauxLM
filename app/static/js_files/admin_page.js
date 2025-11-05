const API_PRESTATIONS_URL = '/api/v1/prestations';
let editingPrestationId = null;


// Bouton pour effacer le champ
function setupClearButton() {
    const inputFields = document.querySelectorAll('.search-field input, .creation-field input');

    inputFields.forEach(input => {
        const clearButton = input.nextElementSibling;

        if (clearButton) {
            clearButton.style.display = 'none';

            input.addEventListener('input', () => {
                if (clearButton) {
                    if (input.value.length > 0) {
                        clearButton.style.display = 'block';
                    } else {
                        clearButton.style.display = 'none';
                    }
                }
            });

            if (clearButton) {
                clearButton.addEventListener('click', () => {
                    input.value = '';
                    clearButton.style.display = 'none';
                    input.focus();
                });
            }
        }
    });
}


// Fonction pour les messages d'alerte
function showFeedbackMessage(message, isError = false) {
    const banner = document.getElementById('feedback-message');
    if (!banner) return;

    banner.textContent = message;
    banner.classList.remove('error', 'show');
    if (isError) banner.classList.add('error');

    banner.style.display = 'block';
    setTimeout(() => banner.classList.add('show'), 10);

    setTimeout(() => {
        banner.classList.remove('show');
        setTimeout(() => {
        banner.style.display = 'none';
        banner.classList.remove('error');
        }, 100);
    }, 3000);
}


// Fonction qui remplit les lignes du tableau avec les 2 boutons (Modifier et Supprimer) en bout de ligne
function renderPrestations(prestations) {
    const tableBody = document.getElementById('prestation-name-result');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    if (!prestations || prestations.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="3" style="text-align: center;">Aucune prestation trouvée</td></tr>';
        return;
    }

    prestations.forEach(prestation => {
        const tr = document.createElement('tr');
        tr.dataset.id = prestation.id;

        tr.innerHTML = `
            <td data-label="ID">${prestation.id}</td>
            <td data-label="Nom" class="prestation-name-cell">${prestation.name}</td>
            <td class="actions-cell" data-label="Actions">
                <button class="modify-button" data-id="${prestation.id}" data-name="${prestation.name}" aria-label="Modifier ${prestation.name}">Modifier</button>
                <button class="delete-button" data-id="${prestation.id}" data-name="${prestation.name}" aria-label="Supprimer ${prestation.name}">Supprimer</button>
            </td>
            `;
            tableBody.appendChild(tr);
    });

    attachActionListeners();
}


// Fonction qui récupère toutes les prestations
async function fetchAllPrestations() {
    const loadingSpinner = document.getElementById('loading-spinner');
    const tableBody = document.getElementById('prestation-name-result');

    if (loadingSpinner) {
        loadingSpinner.style.display = 'block';
    }
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
        renderPrestations(data);
    
    } catch (error) {
        console.error('Erreur lors de la récupération des prestations: ', error);
        if (tableBody) {
            tableBody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: red;">Erreur de chargement des données</td></tr>';
        }
    } finally {
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
    }
}


// Fonction pour chercher une prestation par nom
async function fetchPrestationByName() {
    const searchNameInput = document.getElementById('search-name-input');
    const name = searchNameInput ? searchNameInput.value.trim() : '';

    if (!name) {
        showFeedbackMessage('Veuillez entrer un nom de prestation à rechercher', true);
        return;
    }

    const loadingSpinner = document.getElementById('loading-spinner');
    if (loadingSpinner) {
        loadingSpinner.style.display = 'block';
    }

    try {
        const response = await fetch(`${API_PRESTATIONS_URL}/search?name=${encodeURIComponent(name)}`, {
        method: 'GET', 
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
        });

        if (!response.ok) {
            if (response.status === 403 || response.status === 401) {
                showFeedbackMessage('Accès refusé ou erreur de connexion', true);
                return;
            }
            if (response.status === 404) {
                renderPrestations([]);
                return;
            }
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        let dataArray = [];
        if (Array.isArray(data)) {
            dataArray = data;
        } else if (data) {
            dataArray = [data];
        }
        renderPrestations(dataArray);

    } catch (error) {
        console.error('Erreur lors de la recherche de la prestation: ', error);
        showFeedbackMessage('Erreur lors de la recherche', true);
        renderPrestations([]);
    } finally {
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
    }
}


// Fonction pour la création de la prestation
async function createPrestation(event) {
    event.preventDefault();

    const createNameInput = document.getElementById('creation');
    const createButton = document.getElementById('create-prestation-button');
    const searchTypeSelect = document.getElementById('search-type-select');

    const name = createNameInput ? createNameInput.value.trim() : '';

    if (!name) {
        showFeedbackMessage('Veuillez entrer le nom d\'une prestation', true);
        return;
    }

    const data = { name: name };

    createButton.disabled = true;
    createButton.textContent = 'Enregistrement...';

    try {
        const response = await fetch(API_PRESTATIONS_URL, {
            method: 'POST', 
            credentials: 'include', 
            headers: {
                'Content-Type': 'application/json'
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

        if (searchTypeSelect && searchTypeSelect.value === 'all') {
            fetchAllPrestations();
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

        attachSaveAndCancelListeners(id, currentName);
    }
}


// Fonction pour la modification de la prestation
async function modifyPrestation(id, newName) {
    if (!id || !newName) return;

    const data = { name: newName };
    const saveButton = document.querySelector(`.save-edit-button[data-id="${id}"]`);

    if (saveButton) saveButton.textContent = 'Enregistrement...';

    try {
        const response = await fetch(`${API_PRESTATIONS_URL}/${id}`, {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Echec de la modification de ${id}`);
        }

        showFeedbackMessage('Prestation modifiée avec succès');

        fetchAllPrestations();

    } catch (error) {
        console.error('Erreur lors de la modification de la prestation: ', error);
        showFeedbackMessage(`Echec de la modification: ${error.message}`, true);

        if (saveButton) saveButton.textContent = 'Enregistrer';
    } finally {
        editingPrestationId = null;
    }
}


// Fonction qui gère la confirmation de la suppression d'une prestation
function deleteConfirmation(id, name) {
    const modalOverlay = document.getElementById('confirmation-modal-overlay');
    const modalMessage = document.getElementById('modal-message');
    const modalConfirmButton = document.getElementById('modal-confirm-button');

    if (!modalOverlay || !modalMessage || !modalConfirmButton) return;

    modalMessage.textContent = `Êtes-vous sûr de vouloir supprimer la prestation: "${name}?`;

    modalConfirmButton.dataset.deleteId = id;

    modalOverlay.style.display = 'flex';
}


// Fonction qui gère la suppression d'une prestation
async function deletePrestation(id) {
    try {
        const response = await fetch(`${API_PRESTATIONS_URL}/${id}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.status === 200 || response.status === 204) {
            showFeedbackMessage('Prestation supprimée avec succès');
            fetchAllPrestations();
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
    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.dataset.id;
            const name = button.dataset.name;
            deleteConfirmation(id, name);
        });
    });

    // Ecouteur pour le bouton 'Modifier'
    document.querySelectorAll('.modify-button').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.dataset.id;
            const currentName = button.dataset.name;

            handleModifyClick(id, currentName);
        });
    });
}


// Fonction qui gère les boutons 'Enregistrer' et 'Annuler'
function attachSaveAndCancelListeners(id, originalName) {
    // Ecouteur pour le bouton 'Enregistrer'
    const saveButton = document.querySelector(`.save-edit-button[data-id="${id}"]`);
    if (saveButton) {
        saveButton.addEventListener('click', () => {
            const inputField = document.getElementById(`edit-input-${id}`);
            if (inputField) {
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


// Fonction pour basculer l'affichage de la recherce
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


document.addEventListener('DOMContentLoaded', () => {
    setupClearButton();

    const searchNameButton = document.getElementById('search-name-button');
    const createForm = document.getElementById('create-prestation-form');

    // Ecouteurs pour la modale
    const modalOverlay = document.getElementById('confirmation-modal-overlay');
    const modalConfirmButton = document.getElementById('modal-confirm-button');
    const modalCancelButton = document.getElementById('modal-cancel-button');

    function closeModal() {
        if (modalOverlay) {
            modalOverlay.style.display = 'none';
        }
        if (modalConfirmButton) {
            modalConfirmButton.dataset.deleteId = '';
        }
    }

    if (modalConfirmButton) {
        modalConfirmButton.addEventListener('click', () => {
            const id = modalConfirmButton.dataset.deleteId;
            if (id) {
                deletePrestation(id);
            }
            closeModal();
        });
    }

    if (modalCancelButton) {
        modalCancelButton.addEventListener('click', closeModal);
    }

    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                closeModal();
            }
        });
    }

    setupCustomSelect();

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
});
