const API_APPOINTMENTS_URL = '/api/v1/appointments';
let allAppointmentsCache = [];
let currentAppointmentPage = 1;
let appointmentsPerPage = 10;
let isAppointmentDateAscending = false;


// Bouton pour effacer le champ
function setupAppointmentClearButton() {
	const inputFields = document.querySelectorAll('#section-appointments .search-field input');

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


// Fonction qui gère le format date de la colonne 'Date de création'
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


// Fonction qui valide les entrées
function isValidInput(input) {
	if (!input) {
		return false;
	}
	if (typeof input !== 'string') {
		return false;
	}
	if (input.trim().length === 0) {
		return false;
	}
	const dangerousChar = /[<>{}]/;
	if (dangerousChar.test(input.trim())) {
		return false;
	}
	return true;
}


// Fonction qui traduit le statut des rdv
function translateStatus(status) {
	const translations = {
		'PENDING': 'En attente',
		'CONFIRMED': 'Confirmé',
		'CANCELLED': 'Annulé',
		'COMPLETED': 'Terminé'
	};
	return translations[status] || status;
}


// Fonction qui affiche les lignes du tableau
function renderAppointments(appointments) {
	const tableBody = document.getElementById('appointment-result');
	if (!tableBody) return;

	tableBody.innerHTML = '';

	if (!appointments || appointments.length === 0) {
		tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center;">Aucun rendez-vous trouvé</td></tr>';
		return;
	}

	appointments.forEach(appointment => {
		const tr = document.createElement('tr');
		if (appointment.id) {
			tr.dataset.id = appointment.id;
		}

		const userEmail = appointment.user ? appointment.user.email : (appointment.user_email || 'Utilisateur anonyme');
		const userFirstName = appointment.user ? appointment.user.first_name : (appointment.user.first_name || '');
		const userLastName = appointment.user ? appointment.user.last_name : (appointment.user.last_name || '');
		const prestationName = appointment.prestation ? appointment.prestation.name : (appointment.prestation_name || 'N/A');
		const rawStatus = appointment.status || 'PENDING';
		const displayStatus = translateStatus(rawStatus);
		const message = appointment.message || '';
		const fullName = `${userFirstName} ${userLastName}`.trim() || userEmail;

		tr.innerHTML = `
			<td data-label="Statut">${displayStatus}</td>
			<td data-label="Email">${userEmail}</td>
			<td data-label="Prénom">${userFirstName}</td>
			<td data-label="Nom">${userLastName}</td>
			<td data-label="Prestation">${prestationName}</td>
			<td data-label="Message">${message}</td>
			<td data-label="Date de création">${formatDate(appointment.created_at)}</td>
			<td class="actions-cell" data-label="Actions">
				<button class="status-edit-button"
					data-id="${appointment.id}"
					data-status="${rawStatus}"
					data-user="${fullName}"
					data-prestation="${prestationName}">
					Modifier le statut
				</button>
			</td>
		`;
		tableBody.appendChild(tr);
	});

	document.querySelectorAll('.status-edit-button').forEach(button => {
		button.addEventListener('click', (e) => {
			const button = e.currentTarget;
			const id = button.dataset.id;
			const currentStatus = button.dataset.status;
			const userName = button.dataset.user;
			const prestationName = button.dataset.prestation;
			openStatusModal(id, currentStatus, userName, prestationName);
		});
	});
}


// Fonction qui gère la pagination et affiche la bonne page
function displayPaginatedAppointments() {
	sortDataByDate(allAppointmentsCache, 'created_at', isAppointmentDateAscending);
	updateSortIcon('sort-appointment-icon', isAppointmentDateAscending);

	const results = allAppointmentsCache;
	const totalAppointments = results.length;

	let totalPages = 1;
	if (appointmentsPerPage > 0) {
		totalPages = Math.ceil(totalAppointments / appointmentsPerPage);
	}

	if (currentAppointmentPage > totalPages) currentAppointmentPage = totalPages;
	if (currentAppointmentPage < 1) currentAppointmentPage = 1;

	let paginatedAppointments;
	if (appointmentsPerPage === 0) {
		paginatedAppointments = results;
	} else {
		const start = (currentAppointmentPage - 1) * appointmentsPerPage;
		const end = start + appointmentsPerPage;
		paginatedAppointments = results.slice(start, end);
	}

	renderAppointments(paginatedAppointments);
	setupAppointmentPaginationControls(totalPages, totalAppointments);
}


// Fonction qui crée les boutons 'Suivant' et 'Précédent' pour la pagination
function setupAppointmentPaginationControls(totalPages, totalAppointments) {
	let controlsContainer = document.getElementById('appointment-pagination-controls');

	if (!controlsContainer) {
		controlsContainer = document.createElement('div');
		controlsContainer.id = 'appointment-pagination-controls';
		controlsContainer.className = 'pagination-controls';

		const resultSection = document.querySelector('#section-appointments .result');
		if (resultSection) {
			resultSection.appendChild(controlsContainer);
		}
	}

	controlsContainer.innerHTML = '';

	// Affiche le nombre total de résultats
	const totalInfo = document.createElement('span');
	totalInfo.className = 'pagination-total';
	totalInfo.textContent = `${totalAppointments} rendez-vous trouvé(s)`;
	controlsContainer.appendChild(totalInfo);

	if (totalPages <= 1) {
		return;
	}

	// Bouton 'Précédent'
	const prevButton = document.createElement('button');
	prevButton.textContent = 'Précédent';
	prevButton.className = 'pagination-button';
	if (currentAppointmentPage === 1) {
		prevButton.disabled = true;
	}

	prevButton.addEventListener('click', () => {
		if (currentAppointmentPage > 1) {
			currentAppointmentPage--;
			displayPaginatedAppointments();
		}
	});

	// Info page
	const pageInfo = document.createElement('span');
	pageInfo.textContent = `Page ${currentAppointmentPage} / ${totalPages}`;
	pageInfo.className = 'pagination-info';

	// Bouton 'Suivant'
	const nextButton = document.createElement('button');
	nextButton.textContent = 'Suivant';
	nextButton.className = 'pagination-button';
	if (currentAppointmentPage === totalPages) {
		nextButton.disabled = true;
	}

	nextButton.addEventListener('click', () => {
		if (currentAppointmentPage < totalPages) {
			currentAppointmentPage++;
			displayPaginatedAppointments();
		}
	});

	controlsContainer.appendChild(prevButton);
	controlsContainer.appendChild(pageInfo);
	controlsContainer.appendChild(nextButton);
}


// Fonction qui gère le spinner
function toggleLoadingSpinner(show) {
	const loadingSpinner = document.getElementById('appointment-loading-spinner');
	if (loadingSpinner) {
		loadingSpinner.style.display = show ? 'block' : 'none';
	}
}


// Fonction qui récupère tous les rendez-vous
async function fetchAllAppointments() {
	toggleLoadingSpinner(true);

	try {
		const response = await fetch(API_APPOINTMENTS_URL, {
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
		allAppointmentsCache = data;  // Stocke les données dans le cache
		currentAppointmentPage = 1;
		displayPaginatedAppointments();  // Affiche la première page

	} catch (error) {
		console.error('Erreur lors de la récupération des rendez-vous: ', error);
		const tableBody = document.getElementById('appointment-result');
		if (tableBody) {
			tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: red;">Erreur de chargement des données</td></tr>';
		}
	} finally {
		toggleLoadingSpinner(false);
	}
}


// Fonction qui récupère l'ID de l'utilisateur via son email
async function resolveUserIdForAppointment(term) {
	if (!term || typeof term !== 'string') {
		return null;
	}

	const email = term.trim();
	if (!email) {
		return null;
	}

	try {
		// Vérifie si l'input est un mail complet
		const isExactEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

		if (!isExactEmail) {
			return null;
		}

		const response = await fetch(`${API_USERS_URL}/search?email=${encodeURIComponent(email)}`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			return null;
		}

		const data = await response.json();

		let results = [];

		if (Array.isArray(data)) {
			results = data;
		} else {
			if (data !== null && data !== undefined) {
				results = [data];
			}
		}

		// Filtre Ghost user
		results = results.filter(user =>
			user.email &&
			user.email.toLowerCase() !== 'deleted@system.local' &&
			!user.is_admin
		);

		if (results.length === 0) {
			return null;
		}

		const firstUser = results[0];
		if (!firstUser || !firstUser.id) {
			return null;
		}

		return firstUser.id;

	} catch (error) {
		console.error("Erreur lors de la résolution de l'utilisateur: ", error);
		return null;
	}
}


// Fonction qui récupère l'ID de la prestation via son nom
async function resolvePrestationIdForAppointment(term) {
	if (!term || typeof term !== 'string') {
		return null;
	}

	const name = term.trim();
	if (!name) {
		return null;
	}

	try {
		const response = await fetch(`${PRESTATION_API_URL}/search?name=${encodeURIComponent(name)}`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			return null;
		}

		const data = await response.json();

		let results = [];
		if (Array.isArray(data)) {
			results = data;
		} else if (data !== null && data !== undefined) {
			results = [data];
		}

		// Filtrer la Ghost prestation
		results = results.filter(prestation =>
			prestation.name &&
			prestation.name.toLowerCase() !== 'Ghost prestation'
		);

		if (results.length === 0) {
			return null;
		}

		const firstPrestation = results[0];
		if (!firstPrestation || !firstPrestation.id) {
			return null;
		}

		return firstPrestation.id;

	} catch (error) {
		console.error("Erreur lors de la résolution de la prestation: ", error);
		return null;
	}
}


// Fonction qui gère la recherche par utilisateur
async function fetchAppointmentsByUser() {
	const input = document.getElementById('appointment-search-user-input');
	if (!input) return;

	const term = input.value;
	if (!isValidInput(term)) {
		showFeedbackMessage("Veuillez entrer une adresse mail valide", true);
		return;
	}
	
	toggleLoadingSpinner(true);

	try {

		const userId = await resolveUserIdForAppointment(term);

		if (!userId) {
			showFeedbackMessage('Utilisateur non trouvé', true);
			allAppointmentsCache = [];
			displayPaginatedAppointments();
			return;
		}

		const response = await fetch(`${API_APPOINTMENTS_URL}/user/${userId}`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.ok) {
			const data = await response.json();
			if (Array.isArray(data)) {
				allAppointmentsCache = data;
			} else {
				allAppointmentsCache = [];
			}
		} else {
			allAppointmentsCache = [];
			showFeedbackMessage("Erreur lors de la récupération des rendez-vous par utilisateur", true);
		}

	} catch (error) {
		console.error("Erreur lors du chargement des rendez-vous par utilisateur: ", error);
		showFeedbackMessage("Erreur technique lors de la recherche", true);
	} finally {
		currentAppointmentPage = 1;
		displayPaginatedAppointments();
		toggleLoadingSpinner(false);
	}
}


// Fonction qui gère la recherche par prestation
async function fetchAppointmentsByPrestation() {
	const input = document.getElementById('appointment-search-prestation-input');
	if (!input) return;

	const term = input.value;
	if (!isValidInput(term)) {
		showFeedbackMessage("Veuillez entrer un nom de prestation", true);
		return;
	}

	toggleLoadingSpinner(true);

	try {
		const prestationId = await resolvePrestationIdForAppointment(term);

		if (!prestationId) {
			showFeedbackMessage('Prestation non trouvée', true);
			allAppointmentsCache = [];
			displayPaginatedAppointments();
			return;
		}

		const response = await fetch(`${API_APPOINTMENTS_URL}/prestation/${prestationId}`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.ok) {
			const data = await response.json();
			if (Array.isArray(data)) {
				allAppointmentsCache = data;
			} else {
				allAppointmentsCache = [];
			}
		} else {
			allAppointmentsCache = [];
			showFeedbackMessage("Erreur lors de la récupération des rendez-vous par prestation", true);
		}

	} catch (error) {
		console.error("Erreur lors du chargement des rendez-vous par prestation: ", error);
		showFeedbackMessage('Erreur technique lors de la recherche', true);
	} finally {
		currentAppointmentPage = 1;
		displayPaginatedAppointments();
		toggleLoadingSpinner(false);
	}
}


// Fonction qui gère la recherche par utilisateur et prestation
async function fetchAppointmentsByUserAndPrestation() {
	const input = document.getElementById('appointment-search-user-and-prestation-input');
	if (!input) return;

	const term = input.value;
	// Format attendu: EmailUtilisateur, NomPrestation
	if (!isValidInput(term) || !term.includes(',')) {
		showFeedbackMessage("Format requis: 'Email de l'utilisateur, Nom de la prestation'", true);
		return;
	}

	const parts = term.split(',');
	if (parts.length < 2) {
		showFeedbackMessage("Format requis: 'Email de l'utilisateur, Nom de la prestation'", true);
		return;
	}

	const userTerm = parts[0].trim();
	const prestationTerm = parts[1].trim();

	toggleLoadingSpinner(true);

	try {
		const [userId, prestationId] = await Promise.all([
			resolveUserIdForAppointment(userTerm),
			resolvePrestationIdForAppointment(prestationTerm)
		]);

		if (!userId) {
			showFeedbackMessage('Utilisateur non trouvé', true);
			allAppointmentsCache = [];
			displayPaginatedAppointments();
			return;
		}
	
		if (!prestationId) {
			showFeedbackMessage('Prestation non trouvée', true);
			allAppointmentsCache = [];
			displayPaginatedAppointments();
			return;
		}

		const response = await fetch(`${API_APPOINTMENTS_URL}/user/${userId}/prestation/${prestationId}`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.ok) {
			const data = await response.json();

			if (Array.isArray(data)) {
				allAppointmentsCache = data;
			} else if (data && typeof data === 'object') {
				allAppointmentsCache = [data];
			} else {
				allAppointmentsCache = [];
			}
		} else {
			allAppointmentsCache = [];
			showFeedbackMessage('Aucun rendez-vous trouvé pour cette combinaison', true);
		}

	} catch (error) {
		console.error("Erreur lors du chargement des rendez-vous combinés: ", error);
		showFeedbackMessage('Erreur technique lors de la recherche', true);
	} finally {
		currentAppointmentPage = 1;
		displayPaginatedAppointments();
		toggleLoadingSpinner(false);
	}
}


// Fonction qui gère la recherche par statut
async function fetchAppointmentsByStatus() {
	const input = document.getElementById('appointment-search-status-input');
	const status = input ? input.value : '';

	if (!status) {
		showFeedbackMessage("Veuillez sélectionner un statut", true);
		return;
	}

	toggleLoadingSpinner(true);

	try {
		const response = await fetch(`${API_APPOINTMENTS_URL}/search?status=${encodeURIComponent(status)}`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.ok) {
			const data = await response.json();
			if (Array.isArray(data)) {
				allAppointmentsCache = data;
			} else {
				allAppointmentsCache = [];
			}
		} else {
			allAppointmentsCache = [];
			showFeedbackMessage("Erreur lors de la récupération des rendez-vous par statut", true);
		}

	} catch (error) {
		console.error("Erreur lors du chargement des rendez-vous par statut: ", error);
		showFeedbackMessage("Erreur technique lors de la recherche", true);
	} finally {
		currentAppointmentPage = 1;
		displayPaginatedAppointments();
		toggleLoadingSpinner(false);
	}
}


// Fonction qui gère l'affichage des inputs de la recherche
function toggleAppointmentSearchVisibility() {
	const selectedElement = document.getElementById('appointment-search-type-select');
	if (!selectedElement) return;

	const selectedValue = selectedElement.value;

	// Masque tous les champs de recherche
	const allSearchFields = document.querySelectorAll('#section-appointments .search-field');
	allSearchFields.forEach(field => {
		field.style.display = 'none';
	});

	// Nettoie tous les champs de saisie et cache le bouton de suppression
	const allInputs = document.querySelectorAll('#section-appointments .search-field input');
	allInputs.forEach(input => {
		if (input.type !== 'hidden') {
			input.value = '';
		}

		const clearButton = input.nextElementSibling;
		if (clearButton && clearButton.classList.contains('clear-input-button')) {
			clearButton.style.display = 'none';
		}
	});

	let containerId = null;

	if (selectedValue === 'by-user') {
		containerId = 'appointment-search-by-user-container';
	} else if (selectedValue === 'by-prestation') {
		containerId = 'appointment-search-by-prestation-container';
	} else if (selectedValue === 'by-user-and-prestation') {
		containerId = 'appointment-search-by-user-and-prestation-container';
	} else if (selectedValue === 'by-status') {
		containerId = 'appointment-search-by-status-container';
	}

	if (containerId) {
		const container = document.getElementById(containerId);
		if (container) {
			container.style.display = 'flex';
		}
	} else {
		if (selectedValue === 'all') {
			fetchAllAppointments();
		}
	}
}


// Fonction qui gère le menu déroulant
function setupAppointmentCustomSelect() {
	const selected = document.getElementById('appointment-select-selected');
	const items = document.getElementById('appointment-select-items');
	const hiddenInput = document.getElementById('appointment-search-type-select');

	if (!selected || !items || !hiddenInput) return;
	
	// Evite les écouteurs multiples
	const newSelected = selected.cloneNode(true);
	selected.parentNode.replaceChild(newSelected, selected);

	newSelected.addEventListener('click', (e) => {
		e.stopPropagation();
		closeAllSelects(newSelected);
		items.classList.toggle('select-hide');
		newSelected.classList.toggle('select-arrow-active');
	});

	items.querySelectorAll('div').forEach(item => {
		item.addEventListener('click', (e) => {
			e.stopPropagation();
			newSelected.textContent = item.textContent;
			hiddenInput.value = item.dataset.value;
			items.classList.add('select-hide');
			newSelected.classList.remove('select-arrow-active');
			toggleAppointmentSearchVisibility();

			// Si 'Tous' est choisi, on réinitialise l'affichage
			if (item.dataset.value === 'all') {
				currentReviewPage = 1;
				displayPaginatedAppointments();
			}

			toggleAppointmentSearchVisibility();
		});
	});

	document.addEventListener('click', (e) => {
		if (!selected.contains(e.target) && !items.contains(e.target)) {
			items.classList.add('select-hide');
			newSelected.classList.remove('select-arrow-active');
		}
	});
}


// Fonction qui gère le menu déroulant pour les statuts
function setupStatusCustomSelect() {
	const selected = document.getElementById('appointment-status-select-selected');
	const items = document.getElementById('appointment-status-select-items');
	const hiddenInput = document.getElementById('appointment-search-status-input');

	if (!selected || !items || !hiddenInput) return;

	const newSelected = selected.cloneNode(true);
	selected.parentNode.replaceChild(newSelected, selected);

	newSelected.addEventListener('click', (e) => {
		e.stopPropagation();
		closeAllSelects(newSelected);
		items.classList.toggle('select-hide');
		newSelected.classList.toggle('select-arrow-active');
	});

	items.querySelectorAll('div').forEach(item => {
		item.addEventListener('click', (e) => {
			e.stopPropagation();
			newSelected.textContent = item.textContent;
			hiddenInput.value = item.dataset.value;
			items.classList.add('select-hide');
			newSelected.classList.remove('select-arrow-active');
		});
	});

	document.addEventListener('click', (e) => {
		if (!selected.contains(e.target) && !items.contains(e.target)) {
			items.classList.add('select-hide');
			newSelected.classList.remove('select-arrow-active');
		}
	});
}


// Fonction qui ferme les autres menus déroulants
function closeAllSelects(element) {
	const items = document.getElementsByClassName('select-items');
	const selected = document.getElementsByClassName('select-selected');

	for (let i = 0; i < items.length; i++) {
		if (element != selected[i] && element) {
			items[i].classList.remove('select-arrow-active');
		}
	}
}


// Fonction qui réinitialise la section après chaque clic ailleurs
function resetAppointmentsSection() {
	currentAppointmentPage = 1;
	appointmentsPerPage = 10;

	// Réinitialisation du tri par date
	isAppointmentDateAscending = false;
	updateSortIcon('sort-appointment-icon', isAppointmentDateAscending);

	// Reset du menu déroulant
	const searchSelectInput = document.getElementById('appointment-search-type-select');
	const searchSelectText =  document.getElementById('appointment-select-selected');
	if (searchSelectInput) {
		searchSelectInput.value = 'all';
	}
	if (searchSelectText) {
		searchSelectText.textContent = 'Tous les rendez-vous';
	}

	// Reset du menu déroulant de la pagination
	const paginSelectInput = document.getElementById('appointment-pagination-hidden');
	const paginSelectText = document.getElementById('appointment-pagination-selected');
	if (paginSelectInput) {
		paginSelectInput.value = '10';
	}
	if (paginSelectText) {
		paginSelectText.textContent = '10 par page';
	}

	// Reset du menu déroulant des statuts
	const statusInput = document.getElementById('appointment-search-status-input');
	const statusText = document.getElementById('appointment-status-select-selected');

	if (statusInput) {
		statusInput.value = '';
	}
	if (statusText) {
		statusText.textContent = 'Choisir un statut';
	}

	// Vide les champs de recherche
	const inputs = document.querySelectorAll('#section-appointments .search-field input');
	inputs.forEach(input => {
		if (input.type !== 'hidden') {
			input.value = '';
		}

		const clearButton = input.nextElementSibling;
		if (clearButton && clearButton.classList.contains('clear-input-button')) {
			clearButton.style.display = 'none';
		}
	});

	toggleAppointmentSearchVisibility();
	fetchAllAppointments();
}


// Configure la pagination avec le filtre (par 10, 20, 50 ou tous)
function setupAppointmentPaginationFilter() {
	const searchContainer = document.querySelector('#section-appointments .search-bar');
	if (!searchContainer) return;

	if (document.getElementById('appointment-pagination-select-wrapper')) {
		return;
	}

	const paginationSelectWrapper = document.createElement('div');
	paginationSelectWrapper.className = 'select-wrapper pagination-select-wrapper';
	paginationSelectWrapper.id = 'appointment-pagination-select-wrapper';

	paginationSelectWrapper.innerHTML = `
		<div class="select-selected" id="appointment-pagination-select-selected" tabindex="0" role="combobox" aria-label="Nombre de rendez-vous par page">
			10 par page
		</div>
		<div class="select-items select-hide" id="appointment-pagination-select-items" role="listbox">
			<div data-value="all">Tous</div>
			<div data-value="10">10 par page</div>
			<div data-value="20">20 par page</div>
			<div data-value="50">50 par page</div>
		</div>
		<input type="hidden" id="appointment-pagination-hidden-input" value="10">
	`;

	searchContainer.appendChild(paginationSelectWrapper);

	const selected = document.getElementById('appointment-pagination-select-selected');
	const items = document.getElementById('appointment-pagination-select-items');
	const hiddenInput = document.getElementById('appointment-pagination-hidden-input');

	if (!selected || !items || !hiddenInput) return;

	selected.addEventListener('click', () => {
		closeAllSelects(selected);
		items.classList.toggle('select-hide');
	});

	items.querySelectorAll('div').forEach(item => {
		item.addEventListener('click', (e) => {
			e.stopPropagation();
			selected.textContent = item.textContent;
			hiddenInput.value = item.dataset.value;
			items.classList.add('select-hide');

			const value = hiddenInput.value;
			if (value === 'all') {
				appointmentsPerPage = 0;
			} else {
				appointmentsPerPage = parseInt(value, 10);
			}
			currentAppointmentPage = 1;
			displayPaginatedAppointments();
		});
	});

	document.addEventListener('click', (e) => {
		if (!selected.contains(e.target) && !items.contains(e.target)) {
			items.classList.add('select-hide');
		}
	});
}


// Fonction pour la modale de changement de statut
async function updateAppointmentStatus(id) {
	if (!id) return;

	const csrfToken = getCookie('csrf_access_token');
    if (!csrfToken) {
        console.error('Token CSRF manquant');
        showFeedbackMessage('Session invalide, veuillez rafraichir la page', true);
        return;
    }

	// On récupère le statut sélectionné dans la modale
	const modal = document.getElementById('status-modal-overlay');
	const selectedRadio = modal.querySelector('input[name="appointment-status"]:checked');

	if (!selectedRadio) {
		showFeedbackMessage("Veuillez sélectionner un statut", true);
		return;
	}

	const newStatus = selectedRadio.value;

	const confirmButton = document.getElementById('status-modal-confirm-button');
	if (confirmButton) {
		confirmButton.textContent = 'Enregistrement...';
		confirmButton.disabled = true;
	}

	try {
		const response = await fetch(`${API_APPOINTMENTS_URL}/${id}`, {
			method: 'PUT',
			credentials: 'include', 
			headers: {
				'Content-Type': 'application/json',
				'X-CSRF-TOKEN': csrfToken
			},
			body: JSON.stringify({ status: newStatus })
		});

		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(errorData.error || `Erreur lors de la mise à jour`);
		}

		showFeedbackMessage('Statut mis à jour avec succès');
		closeStatusModal();

		const updatedAppointment = await response.json();
		const cachedIndex = allAppointmentsCache.findIndex(appointment => appointment.id === id);

		if (cachedIndex !== -1) {
			allAppointmentsCache[cachedIndex] = updatedAppointment;
		} else {
			await fetchAllAppointments();
			return;
		}

		displayPaginatedAppointments();

	} catch (error) {
		console.error('Erreur lors de la mise à jour du statut: ', error);
		showFeedbackMessage("Erreur technique lors de la mise à jour", true);

		if (confirmButton) {
			confirmButton.textContent = 'Confirmer';
			confirmButton.disabled = false;
		}
	}
}


// Fonction qui gère l'ouverture de la modale de changement de statut
function openStatusModal(id, currentStatus, userName, prestationName) {
	const modal = document.getElementById('status-modal-overlay');
	const confirmButton = document.getElementById('status-modal-confirm-button');
	const messageElement = document.getElementById('status-modal-message');
	if (!modal || !confirmButton) return;

	// Mise à jour du message dynamique
	if (messageElement) {
		if (userName && prestationName) {
			messageElement.innerHTML = `Sélectionnez le nouveau statut pour le rendez-vous de <strong>${userName}</strong> pour <strong>${prestationName}</strong>:`;
		} else {
			messageElement.textContent = 'Sélectionnez le nouveau statut pour ce rendez-vous:';
		}
	}

	// Décoche tout et coche le statut actuel
	const radios = modal.querySelectorAll('input[name="appointment-status"]');
	radios.forEach(radio => {
		radio.checked = false;
	});

	const normalizedStatus = (currentStatus || 'PENDING').toUpperCase();
	const targetRadio = modal.querySelector(`input[name="appointment-status"][value="${normalizedStatus}"]`);
	if (targetRadio) {
		targetRadio.checked = true;
	}

	// On clône le bouton 'Confirmer'
	const newConfirmButton = confirmButton.cloneNode(true);
	confirmButton.parentNode.replaceChild(newConfirmButton, confirmButton);

	// On réinitialise le bouton 'Confirmer'
	newConfirmButton.textContent = 'Confirmer';
	newConfirmButton.disabled = false;

	// On attache le nouvel écouteur avec l'ID spécifique
	newConfirmButton.addEventListener('click', () => {
		updateAppointmentStatus(id);
	});

	// On affiche la modale
	modal.style.display = 'flex';
}


// Fonction pour fermer la modale
function closeStatusModal() {
	const modal = document.getElementById('status-modal-overlay');
	if (modal) {
		modal.style.display = 'none';
	}
}


// Fonction d'initialisation pour la section Rendez-vous
function init_appointments() {
	if (window.appointmentsInitialized) {
		resetAppointmentsSection();
		return;
	}

	setupAppointmentClearButton();
	setupAppointmentCustomSelect();
	setupStatusCustomSelect();
	setupAppointmentPaginationFilter();
	toggleAppointmentSearchVisibility();

	const sortHeader = document.getElementById('sort-appointment-date-header');
	if (sortHeader) {
		sortHeader.addEventListener('click', () => {
			isAppointmentDateAscending = !isAppointmentDateAscending;
			displayPaginatedAppointments();
		});
	}

	const searchUserButton = document.getElementById('appointment-search-user-button');
	if (searchUserButton) {
		searchUserButton.addEventListener('click', async (e) => {
			e.preventDefault();
			fetchAppointmentsByUser();
			currentAppointmentPage = 1;
			displayPaginatedAppointments();
		});
	}

	const searchPrestationButton = document.getElementById('appointment-search-prestation-button');
	if (searchPrestationButton) {
		searchPrestationButton.addEventListener('click', async (e) => {
			e.preventDefault();
			fetchAppointmentsByPrestation();
			currentAppointmentPage = 1;
			displayPaginatedAppointments();
		});
	}

	const searchPrestationAndUserButton = document.getElementById('appointment-search-user-prestation-button');
	if (searchPrestationAndUserButton) {
		searchPrestationAndUserButton.addEventListener('click', async (e) => {
			e.preventDefault();
			fetchAppointmentsByUserAndPrestation();
			currentAppointmentPage = 1;
			displayPaginatedAppointments();
		});
	}

	const searchStatusButton = document.getElementById('appointment-search-status-button');
	if (searchStatusButton) {
		searchStatusButton.addEventListener('click', async (e) => {
			e.preventDefault();
			fetchAppointmentsByStatus();
			currentAppointmentPage = 1;
			displayPaginatedAppointments();
		});
	}

	const statusCancelButton = document.getElementById('status-modal-cancel-button');
	if (statusCancelButton) {
		statusCancelButton.addEventListener('click', () => {
			closeStatusModal();
		});
	}

	fetchAllAppointments();

	window.appointmentsInitialized = true;
}

window.init_appointments = init_appointments;
