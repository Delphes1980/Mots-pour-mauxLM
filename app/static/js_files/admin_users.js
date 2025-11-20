const API_USERS_URL = '/api/v1/users';
let editingUserId = null;
let allUsersCache = [];
let currentUserPage = 1;
let usersPerPage = 10;


// Bouton pour effacer le champ
function setupUserClearButton() {
    const inputFields = document.querySelectorAll('#section-users .search-field input');

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


// Fonction qui gère le format date de la colonne 'Date d'inscription'
function formatDate(dateString) {
	if (!dateString) {
		return 'N/A';
	}

	const date = new Date(dateString);
	return date.toLocaleDateString('fr-FR', {
		day: '2-digit',
		month: '2-digit',
		year: 'numeric'
	});
}


// Fonction qui affiche les lignes du tableau
function renderUsers(users) {
	const tableBody = document.getElementById('user-name-result');
	if (!tableBody) return;

	tableBody.innerHTML = '';

	if (!users || users.length === 0) {
		tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Aucun utilisateur trouvé</td></tr';
		return;
	}

	users.forEach(user => {
		const tr = document.createElement('tr');
		tr.dataset.id = user.id;

		tr.innerHTML = `
		<td data-label="Prénom" class="user-cell-firstname">${user.first_name || 'N/A'}</td>
		<td data-label="Nom" class="user-cell-lastname">${user.last_name || 'N/A'}</td>
		<td data-label="Email" class="user-cell-email">${user.email}</td>
		<td data-label="Adresse" class="user-cell-address">${user.address || 'N/A'}</td>
		<td data-label="Téléphone" class="user-cell-phone">${user.phone_number || 'N/A'}</td>
		<td data-label="Date d'inscription" class="user-cell-date">${formatDate(user.created_at)}</td>
		<td class="actions-cell" data-label="Actions">
			<div class="action-top">
				<button class="modify-button user-modify-button" data-id="${user.id}" aria-label="Modifier ${user.first_name}">Modifier</button>
				<button class="delete-button user-delete-button" data-id="${user.id}" data-name="${user.first_name} ${user.last_name}" aria-label="Spprimer ${user.first_name}">Supprimer</button>
			</div>
			<div class="action-bottom">
				<button class="reset-pass-button" data-id="${user.id}" data-name="${user.first_name} ${user.last_name}" aria-label="Réinitialiser le mot de passe de ${user.first_name}">Réinitialiser le mot de passe</button>
			</div>
		</td>
		`;
		tableBody.appendChild(tr);
	});

	attachUserActionListeners();
}


// Fonction qui gère la pagination et affiche la bonne page
function displayPaginatedUsers() {
	const filteredUsers = filterUsersFromCache();
	// Filtre le Ghost user
	const usersToDisplay = filteredUsers.filter(user => user.email.toLowerCase() !== "deleted@system.local" && !user.is_admin);
	const totalUsers = usersToDisplay.length;

	let totalPages = 1;
	if (usersPerPage > 0) {
		totalPages = Math.ceil(totalUsers / usersPerPage);
	}

	// S'assure que la page actuelle est valide
	if (currentUserPage > totalPages) {
		currentUserPage = totalPages;
	}
	if (currentUserPage < 1) {
		currentUserPage = 1;
	}

	let paginatedUsers;

	if (usersPerPage === 0) {
		paginatedUsers = usersToDisplay;
	} else {
		const start = (currentUserPage - 1) * usersPerPage;
		const end = start + usersPerPage;
		paginatedUsers = usersToDisplay.slice(start, end);
	}

	renderUsers(paginatedUsers);
	setupPaginationControls(totalPages, totalUsers);
}


// Fonction qui crée les boutons 'Suivant' et 'Précédent' pour la pagination
function setupPaginationControls(totalPages, totalUsers) {
	let controlsContainer = document.getElementById('user-pagination-controls');
	if (!controlsContainer) {
		controlsContainer = document.createElement('div');
		controlsContainer.id = 'user-pagination-controls';
		controlsContainer.className = 'pagination-controls';

		const resultSection = document.querySelector('#section-users .result');
		if (resultSection) {
			resultSection.appendChild(controlsContainer);
		}
	}

	controlsContainer.innerHTML = '';

	// Affiche le nombre total de résultats
	const totalInfo = document.createElement('span');
	totalInfo.className = 'pagination-total';
	totalInfo.textContent = `${totalUsers} utilisateur(s) trouvé(s)`;
	controlsContainer.appendChild(totalInfo);

	if (totalPages <= 1) {
		return;
	}

	const prevButton = document.createElement('button');
	prevButton.textContent = 'Précédent';
	prevButton.className = 'pagination-button';
	if (currentUserPage === 1) {
		prevButton.disabled = true;
	}
	prevButton.addEventListener('click', () => {
		if (currentUserPage > 1) {
			currentUserPage--;
			displayPaginatedUsers();
		}
	});

	const pageInfo = document.createElement('span');
	pageInfo.textContent = `Page ${currentUserPage} / ${totalPages}`;
	pageInfo.className = 'pagination-info';

	const nextButton = document.createElement('button');
	nextButton.textContent = 'Suivant';
	nextButton.className = 'pagination-button';
	if (currentUserPage === totalPages) {
		nextButton.disabled = true;
	}
	nextButton.addEventListener('click', () => {
		if (currentUserPage < totalPages) {
			currentUserPage++;
			displayPaginatedUsers();
		}
	});

	controlsContainer.appendChild(prevButton);
	controlsContainer.appendChild(pageInfo);
	controlsContainer.appendChild(nextButton);
}


// Fonction qui récupère tous les utilisateurs
async function fetchAllUsers() {
	const loadingSpinner = document.getElementById('user-loading-spinner');
	if (loadingSpinner) {
		loadingSpinner.style.display = 'block';
	}

	try {
		const response = await fetch(API_USERS_URL, {
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
		allUsersCache = data;  // Stocke les données dans le cache

		currentUserPage = 1;
		displayPaginatedUsers();  // Affiche la première page

	} catch (error) {
		console.error('Erreur lors de la récupération des utilisateurs: ', error);
		const tableBody = document.getElementById('user-name-result');
		if (tableBody) {
			tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: red;">Erreur de chargement des données</td></tr>';
		}
	} finally {
		if (loadingSpinner) {
			loadingSpinner.style.display = 'none';
		}
	}
}


// Fonction qui filtre les utilisateurs par email
async function fetchUserByEmail() {
	const searchEmailInput = document.getElementById('search-email-input');
	const email = searchEmailInput ? searchEmailInput.value.trim() : '';

	if (!email) {
		showFeedbackMessage('Veuillez entrer un email à rechercher', true);
		return;
	}

	const loadingSpinner = document.getElementById('user-loading-spinner');
	if (loadingSpinner) {
		loadingSpinner.style.display = 'block';
	}

	try {
		// Vérifie si l'input est un mail complet
		const isExactEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

		let response;
		if (isExactEmail) {
			// Recherche par mail exact
			response = await fetch(`${API_USERS_URL}/search?email=${encodeURIComponent(email)}`, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include'
			});
		} else {
			// Recherche partielle
			response = await fetch(`${API_USERS_URL}/search-partial?email=${encodeURIComponent(email)}`, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include'
			});
		}

		if (!response.ok) {
			if (response.status === 404) {
				currentUserPage = 1;
				renderUsers([]);
				setupPaginationControls(1, 0);
				return;
			}
			if (response.status === 403 || response.status === 401) {
				showFeedbackMessage('Accès refusé ou erreur de connextion', true);
				return;
			}
			throw new Error(`Erreur HTTP: ${response.status}`);
		}

		const data = await response.json();

		let results = Array.isArray(data) ? data : (data ? [data] : []);

		// Filtre Ghost user
		results = results.filter(user =>
			user.email &&
			user.email.toLowerCase() !== 'deleted@system.local' &&
			!user.is_admin
		);

		// Réinitialise la pagination
		currentUserPage = 1;

		let totalUsers = results.length;
		let totalPages = 1;

		const showAll =
			(usersPerPage === 'all') ||
			(usersPerPage === 0) ||
			(typeof usersPerPage === 'string' && usersPerPage.toLowerCase() === 'all');

		if (!showAll) {
			totalPages = Math.max(1, Math.ceil(totalUsers / usersPerPage));
			const start = (currentUserPage - 1) * usersPerPage;
			const end = start + usersPerPage;
			renderUsers(results.slice(start, end));
		} else {
			renderUsers(results);
		}

		setupPaginationControls(totalPages, totalUsers);

	} catch (error) {
		console.error("Erreur lors de la recherche de l'utilisateur: ", error);
		showFeedbackMessage('Erreur lors de la recherche', true);

		currentUserPage = 1;
		renderUsers([]);
		setupPaginationControls(1, 0);
	} finally {
		if (loadingSpinner) {
			loadingSpinner.style.display = 'none';
		}
	}
}


// Fonction qui gère la modification d'un utilisateur
async function modifyUser(id, userData) {
	if (!id || !userData) return;

	const saveButton = document.querySelector(`.user-save-edit-button[data-id="${id}"]`);
	if (saveButton) {
		saveButton.textContent = 'Enregistrement...';
	}

	try {
		const response = await fetch(`${API_USERS_URL}/${id}`, {
			method: 'PATCH',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(userData)
		});

		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(errorData.error || `Echec de la modification de ${id}`);
		}

		showFeedbackMessage('Utilisateur modifié avec succès');
		await fetchAllUsers();  // Mettre à jour le cache et rafraîchir la vue

	} catch (error) {
		console.error(`Erreur lors de la modification de l'utilisateur: `, error);
		showFeedbackMessage(`Echec de la modification: ${error.message}`, true);

		if (saveButton) {
			saveButton.textContent = 'Enregistrer';
		}

	} finally {
		editingUserId = null;
	}
}


// Fonction qui gère la confirmation de la suppression d'un utilisateur
function deleteUserConfirmation(id, name) {
	const modalOverlay = document.getElementById('confirmation-modal-overlay');
	const modalMessage = document.getElementById('modal-message');
	const modalConfirmButton = document.getElementById('modal-confirm-button');

	if (!modalOverlay || !modalMessage || !modalConfirmButton) return;

	modalMessage.textContent = `Êtes-vous sûr de vouloir supprimer l'utilisateur: "${name}"?`;
	modalOverlay.style.display = 'flex';

	const newConfirmButton = modalConfirmButton.cloneNode(true);
	modalConfirmButton.parentNode.replaceChild(newConfirmButton, modalConfirmButton);

	newConfirmButton.dataset.deleteId = id;

	newConfirmButton.addEventListener('click', () => {
		const deleteId = newConfirmButton.dataset.deleteId;
		if (deleteId) {
			deleteUser(deleteId);
		}
		closeUserModal();
	});
}


// Fonction qui ferme la modale
function closeUserModal() {
    const modalOverlay = document.getElementById('confirmation-modal-overlay');
    const modalConfirmButton = document.getElementById('modal-confirm-button');

    if (modalOverlay) {
        modalOverlay.style.display = 'none';
    }
    if (modalConfirmButton) {
        modalConfirmButton.dataset.deleteId ='';
    }
}


// Fonction qui gère la suppression d'un utilisateur
async function deleteUser(id) {
	try {
		const response = await fetch(`${API_USERS_URL}/${id}`, {
			method: 'DELETE',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.status === 200 || response.status === 204) {
			showFeedbackMessage('Utilisateur supprimé avec succès');
			await fetchAllUsers();
		} else {
			const errorData = await response.json();
			throw new Error(errorData.error || `Echec de la suppression: ${response.status}`);
		}

	} catch (error) {
		console.error("Erreur lors de la suppression de l'utilisateur: ", error);
		showFeedbackMessage(`Erreur: ${error.message}`, true);
	}
}


// Ouvre la modale de confirmation avant réinitialisation du mot de passe
function resetPasswordConfirmation(id, name) {
	const modalOverlay = document.getElementById('confirmation-modal-overlay');
	const modalMessage = document.getElementById('modal-message');
	const modalConfirmButton = document.getElementById('modal-confirm-button');

	if (!modalOverlay || !modalMessage || !modalConfirmButton) return;

	modalMessage.textContent = `Êtes-vous sûr de vouloir réinitialiser le mot de passe de l'utilisateur: "${name}"?`;
	modalOverlay.style.display = 'flex';

	const newConfirmButton = modalConfirmButton.cloneNode(true);
	modalConfirmButton.parentNode.replaceChild(newConfirmButton, modalConfirmButton);

	newConfirmButton.addEventListener('click', () => {
		resetPassword(id);
		closeUserModal();
	});
}


// Fonction qui exécute la réinitialisation du mot de passe
async function resetPassword(id) {
	try {
		const response = await fetch(`${API_USERS_URL}/${id}/reset-password`, {
			method: 'POST',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.ok) {
			showFeedbackMessage('Mot de passe réinitialisé et envoyé avec succès');
		} else {
			const errorData = await response.json();
			throw new Error(errorData.error || `Echec de la réinitialisation du mot de passe: ${response.status}`);
		}

	} catch (error) {
		console.error("Erreur lors de la réinitialisation du mot de passe: ", error);
		showFeedbackMessage(`Erreur: ${error.message}`, true);
	}
}


// Fonction qui gère les boutons 'Modifier', 'Supprimer' et 'Réinitialiser'
function attachUserActionListeners() {
	// Ecouteur pour le bouton 'Supprimer'
	document.querySelectorAll('.user-delete-button').forEach(button => {
		button.addEventListener('click', () => {
			deleteUserConfirmation(button.dataset.id, button.dataset.name);
		});
	});

	// Ecouteur pour le bouton 'Modifier'
	document.querySelectorAll('.user-modify-button').forEach(button => {
		button.addEventListener('click', () => {
			const id = button.dataset.id;
			const currentUser = allUsersCache.find(user => user.id === id);
			if (currentUser) {
				handleUserModifyClick(currentUser);
			}
		});
	});

	// Ecouteur pour le bouton 'Réinitialiser'
	document.querySelectorAll('.reset-pass-button').forEach(button => {
		button.addEventListener('click', () => {
			resetPasswordConfirmation(button.dataset.id, button.dataset.name);
		});
	});
}


// Fonction pour la modification d'un utilisateur
function handleUserModifyClick(user) {
	if (editingUserId) {
		showFeedbackMessage('Veuillez enregistrer ou annuler la modification en cours avant de commencer une nouvelle modification', true);
		return;
	}
	editingUserId = user.id;

	const row = document.querySelector(`tr[data-id="${user.id}"]`);
	if (!row) return;

	// Rend chaque cellule modifiable
	row.querySelector('.user-cell-lastname').innerHTML = 
		`<input type="text" id="edit-lastname-${user.id}" value="${user.last_name || ''}" class="modify-input">`;
	row.querySelector('.user-cell-firstname').innerHTML = 
		`<input type="text" id="edit-firstname-${user.id}" value="${user.first_name || ''}" class="modify-input">`;
	row.querySelector('.user-cell-email').innerHTML = 
		`<input type="email" id="edit-email-${user.id}" value="${user.email}" class="modify-input">`;
	row.querySelector('.user-cell-address').innerHTML = 
		`<input type="text" id="edit-address-${user.id}" value="${user.address || ''}" class="modify-input">`;
	row.querySelector('.user-cell-phone').innerHTML = 
		`<input type="tel" id="edit-phone-${user.id}" value="${user.phone_number || ''}" class="modify-input">`;

	// Change les boutons d'action
	const actionsCell = row.querySelector('.actions-cell');
	if (actionsCell) {
		actionsCell.innerHTML = `
			<button class="user-save-edit-button" data-id="${user.id}" aria-label="Enregistrer">Enregistrer</button>
			<button class="user-cancel-edit-button" data-id="${user.id}" aria-label="Annuler">Annuler</button>
			`;
	}

	attachUserSaveAndCancelListeners(user);
}


// Fonction qui gère les boutons 'Enregistrer' et 'Annuler'
function attachUserSaveAndCancelListeners(originalUser) {
	const id = originalUser.id;

	// Ecouteur pour le bouton 'Enregistrer'
	const saveButton = document.querySelector(`.user-save-edit-button[data-id="${id}"]`);
	if (saveButton) {
		saveButton.addEventListener('click', () => {
			const data = {
				last_name: document.getElementById(`edit-lastname-${id}`).value,
				first_name: document.getElementById(`edit-firstname-${id}`).value,
				email: document.getElementById(`edit-email-${id}`).value,
				address: document.getElementById(`edit-address-${id}`).value,
				phone_number: document.getElementById(`edit-phone-${id}`).value
			};
			modifyUser(id, data);
		});
	}

	// Ecouteur pour le bouton 'Annuler'
	const cancelButton = document.querySelector(`.user-cancel-edit-button[data-id="${id}"]`);
	if (cancelButton) {
		cancelButton.addEventListener('click', () => {
			displayPaginatedUsers();
			editingUserId = null;
		});
	}
}


// Fonction qui gère le menu déroulant
function setupUserCustomSelect() {
	const selected = document.getElementById('user-select-selected');
	const items = document.getElementById('user-select-items');
	const hiddenInput = document.getElementById('user-search-type-select');

	if (!selected || !items ||!hiddenInput) return;

	selected.addEventListener('click', () => {
		items.classList.toggle('select-hide');
	});

	items.querySelectorAll('div').forEach(item => {
		item.addEventListener('click', () => {
			selected.textContent = item.textContent;
			hiddenInput.value = item.dataset.value;
			items.classList.add('select-hide');

			// Si 'Tous' est choisi, on réinitialise l'affichage
			if (item.dataset.value === 'all') {
				currentUserPage = 1;
				displayPaginatedUsers();
			}

			toggleUserSearchVisibility();
		});
	});

	document.addEventListener('click', (e) => {
		if (!selected.contains(e.target) && !items.contains(e.target)) {
			items.classList.add('select-hide');
		}
	});
}


// Fonction pour basculer l'affichage de la recherche
function toggleUserSearchVisibility() {
	const selectedValue = document.getElementById('user-search-type-select').value;

	// Masque tous les champs de recherche
	const allSearchFields = document.querySelectorAll('#section-users .search-field');
	allSearchFields.forEach(field => {
		field.style.display = 'none';
	});

	// Nettoie tous les champs de saisie et cache le bouton de suppression
	const allInputs = document.querySelectorAll('#section-users .search-field input');
	allInputs.forEach(input => {
		input.value = '';
		const clearButton = input.nextElementSibling;
		if (clearButton && clearButton.classList.contains('clear-input-button')) {
			clearButton.style.display = 'none';
		}
	});

	let containerId = null;

	if (selectedValue === 'by-email') {
		containerId = 'search-by-email-container';
	} else if (selectedValue === 'by-name') {
		containerId = 'search-by-user-name-container';
	} else if (selectedValue === 'by-firstname') {
		containerId = 'search-by-firstname-container';
	} else if (selectedValue === 'by-phone') {
		containerId = 'search-by-phone-container';
	}

	if (containerId) {
		const container = document.getElementById(containerId);
		if (container) {
			container.style.display = 'flex';
		}
	}
}


// Fonction qui filtre par nom, prénom et téléphone
function filterUsersFromCache() {
	const searchType = document.getElementById('user-search-type-select').value;

	if (searchType === 'all' || searchType === 'by-email') {
		return allUsersCache;
	}

	let searchTerm = '';
	let results = allUsersCache;

	if (searchType === 'by-name') {
		searchTerm = document.getElementById('search-user-name-input').value.toLowerCase();
		results = allUsersCache.filter(user => {
			if (typeof user.last_name === 'string') {
				return user.last_name.toLowerCase().includes(searchTerm);
			}
			return false;
		});
	}

	if (searchType === 'by-firstname') {
		searchTerm = document.getElementById('search-user-firstname-input').value.toLowerCase();
		results = allUsersCache.filter(user => {
			if (typeof user.first_name === 'string') {
				return user.first_name.toLowerCase().includes(searchTerm);
			}
			return false;
		});
	}

	if (searchType === 'by-phone') {
		searchTerm = document.getElementById('search-user-phone-input').value.toLowerCase();
		const normalizedSearchTerm = searchTerm.replace(/[^0-9]/g, '');

		results = allUsersCache.filter(user => {
			if (typeof user.phone_number === 'string') {
				const normalizedPhone = user.phone_number.replace(/[^0-9]/g, '');
				return normalizedPhone.includes(normalizedSearchTerm);
			}
			return false;
		});
	}

	return results.filter(user =>
		user.email &&
		user.email.toLowerCase() !== 'deleted@system.local' &&
		!user.is_admin
	);
}


// Configure la pagination avec le filtre (par 10, 20, 50 ou tous)
function setupPaginationFilter() {
	const searchContainer = document.querySelector('#section-users .search-bar');
	if (!searchContainer) return;

	if (document.getElementById('pagination-select-wrapper')) {
		return;
	}

	const paginationSelectWrapper = document.createElement('div');
	paginationSelectWrapper.className = 'select-wrapper pagination-select-wrapper';
	paginationSelectWrapper.id = 'pagination-select-wrapper';

	paginationSelectWrapper.innerHTML = `
		<div class="select-selected" id="pagination-select-selected" tabindex="0" role="combobox" aria-label="Nombre d'utilisateurs par page">
			10 par page
		</div>
		<div class="select-items select-hide" id="pagination-select-items" role="listbox">
			<div data-value="all">Tous</div>
			<div data-value="10">10 par page</div>
			<div data-value="20">20 par page</div>
			<div data-value="50">50 par page</div>
		</div>
		<input type="hidden" id="pagination-hidden-input" value="10">
	`;

	searchContainer.appendChild(paginationSelectWrapper);

	const selected = document.getElementById('pagination-select-selected');
	const items = document.getElementById('pagination-select-items');
	const hiddenInput = document.getElementById('pagination-hidden-input');

	if (!selected || !items || !hiddenInput) return;

	selected.addEventListener('click', () => {
		items.classList.toggle('select-hide');
	});

	items.querySelectorAll('div').forEach(item => {
		item.addEventListener('click', () => {
			selected.textContent = item.textContent;
			hiddenInput.value = item.dataset.value;
			items.classList.add('select-hide');

			const value = hiddenInput.value;
			if (value === 'all') {
				usersPerPage = 0;
			} else {
				usersPerPage = parseInt(value, 10);
			}
			currentUserPage = 1;
			displayPaginatedUsers();
		});
	});

	document.addEventListener('click', (e) => {
		if (!selected.contains(e.target) && !items.contains(e.target)) {
			items.classList.add('select-hide');
		}
	});
}


// Fonction qui réinitialise la section après chaque clic ailleurs
function resetUsersSection() {
	currentUserPage = 1;
	usersPerPage = 10;

	// Reset du menu déroulant
	const searchSelectInput = document.getElementById('user-search-type-select');
	const searchSelectText =  document.getElementById('user-select-selected');
	if (searchSelectInput) {
		searchSelectInput.value = 'all';
	}
	if (searchSelectText) {
		searchSelectText.textContent = 'Tous les utilisateurs';
	}

	// Reset du menu déroulant de la pagination
	const paginSelectInput = document.getElementById('pagination-hidden-input');
	const paginSelectText = document.getElementById('pagination-select-selected');
	if (paginSelectInput) {
		paginSelectInput.value = '10';
	}
	if (paginSelectText) {
		paginSelectText.textContent = '10 par page';
	}

	// Vide les champs de recherche
	const inputs = document.querySelectorAll('#section-users .search-field input');
	inputs.forEach(input => {
		input.value = '';
		const clearButton = input.nextElementSibling;
		if (clearButton && clearButton.classList.contains('clear-input-button')) {
			clearButton.style.display = 'none';
		}
	});

	toggleUserSearchVisibility();
	fetchAllUsers();
}


// Fonction d'initialisation pour la section Utilisateurs
function init_users() {
	resetUsersSection();

	if (window.usersInitialized) {
		return;
	}

	setupUserClearButton();
	setupUserCustomSelect();
	setupPaginationFilter();
	toggleUserSearchVisibility();

	document.getElementById('search-email-button').addEventListener('click', (e) => {
		e.preventDefault();
		fetchUserByEmail();
	});

	document.getElementById('search-user-name-button').addEventListener('click', (e) => {
		e.preventDefault();
		currentUserPage = 1;
		displayPaginatedUsers();
	});

	document.getElementById('search-user-firstname-button').addEventListener('click', (e) => {
		e.preventDefault();
		currentUserPage = 1;
		displayPaginatedUsers();
	});

	document.getElementById('search-user-phone-button').addEventListener('click', (e) => {
		e.preventDefault();
		currentUserPage = 1;
		displayPaginatedUsers();
	});

	fetchAllUsers();

	window.usersInitialized = true;
}

window.init_users = init_users;
