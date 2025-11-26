const API_REVIEWS_URL = '/api/v1/reviews';
const PRESTATION_API_URL = '/api/v1/prestations';
let allReviewsCache = [];
let currentReviewPage = 1;
let reviewsPerPage = 10;


// Bouton pour effacer le champ
function setupReviewClearButton() {
    const inputFields = document.querySelectorAll('#section-reviews .search-field input');

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


// Fonction qui génère les étoiles dans un avis
function generateStarsForReviews(rating) {
	let stars = '';
	const maxStars = 5;
	const score = Math.round(rating);

	for (let i = 1; i <= maxStars; i++) {
	if (i <= score) {
		stars += '<i class="bx bxs-star star"></i>';
    } else {
	stars += '<i class="bx bx-star star"></i>';
		}
	}
	return `<div class="rating-stars">${stars}</div>`;
}


// Fonction qui affiche les lignes du tableau
function renderReviews(reviews) {
	const tableBody = document.getElementById('review-result');
	if (!tableBody) return;

	tableBody.innerHTML = '';

	if (!reviews || reviews.length === 0) {
		tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Aucun avis trouvé</td></tr>';
		return;
	}

	reviews.forEach(review => {
		const tr = document.createElement('tr');

		if (review.id) {
			tr.dataset.id = review.id;
		}

		const userEmail = review.user ? review.user.email : (review.user_email || 'Utilisateur anonyme');
		const userName = review.user ? `${review.user.first_name} ${review.user.last_name}` : 'N/A';
		const prestationName = review.prestation ? review.prestation.name : (review.prestation_name || 'N/A');
		const reviewText = review.text || '';

		tr.innerHTML = `
			<td data-label="Email">${userEmail}</td>
			<td data-label="Prénom et Nom">${userName}</td>
			<td data-label="Note">${generateStarsForReviews(review.rating)}</td>
			<td data-label="Avis">${reviewText || ''}</td>
			<td data-label="Date de création">${formatDate(review.created_at)}</td>
			<td data-label="Prestation">${prestationName}</td>
			<td class="actions-cell" data-label="Actions">
				<div class="action-top">
					<button class="delete-button review-delete-button" data-id="${review.id}" aria-label="Supprimer cet avis">Supprimer</button>
				</div>
			</td>
		`;
		tableBody.appendChild(tr);
	});

	attachReviewActionListeners();
}


// Fonction qui gère la pagination et affiche la bonne page
function displayPaginatedReviews() {
	const results = allReviewsCache;
	const totalReviews = results.length;

	let totalPages = 1;
	if (reviewsPerPage > 0) {
		totalPages = Math.ceil(totalReviews / reviewsPerPage);
	}

	if (currentReviewPage > totalPages) currentReviewPage = totalPages;
	if (currentReviewPage < 1) currentReviewPage = 1;

	let paginatedReviews;

	if (reviewsPerPage === 0) {
		paginatedReviews = results;
	} else {
		const start = (currentReviewPage - 1) * reviewsPerPage;
		const end = start + reviewsPerPage;
		paginatedReviews = results.slice(start, end);
	}

	renderReviews(paginatedReviews);
	setupReviewPaginationControls(totalPages, totalReviews);
}


// Fonction qui crée les boutons 'Suivant' et 'Précédent' pour la pagination
function setupReviewPaginationControls(totalPages, totalReviews) {
	let controlsContainer = document.getElementById('review-pagination-controls');

	if (!controlsContainer) {
		controlsContainer = document.createElement('div');
		controlsContainer.id = 'review-pagination-controls';
		controlsContainer.className = 'pagination-controls';

		const resultSection = document.querySelector('#section-reviews .result');
		if (resultSection) {
			resultSection.appendChild(controlsContainer);
		}
	}

	controlsContainer.innerHTML = '';

	// Affiche le nombre total de résultats
	const totalInfo = document.createElement('span');
	totalInfo.className = 'pagination-total';
	totalInfo.textContent = `${totalReviews} avis trouvé(s)`;
	controlsContainer.appendChild(totalInfo);

	if (totalPages <= 1) {
		return;
	}

	// Bouton 'Précédent'
	const prevButton = document.createElement('button');
	prevButton.textContent = 'Précédent';
	prevButton.className = 'pagination-button';
	if (currentReviewPage === 1) {
		prevButton.disabled = true;
	}

	prevButton.addEventListener('click', () => {
		if (currentReviewPage > 1) {
			currentReviewPage--;
			displayPaginatedReviews();
		}
	});

	// Info page
	const pageInfo = document.createElement('span');
	pageInfo.textContent = `Page ${currentReviewPage} / ${totalPages}`;
	pageInfo.className = 'pagination-info';

	// Bouton 'Suivant'
	const nextButton = document.createElement('button');
	nextButton.textContent = 'Suivant';
	nextButton.className = 'pagination-button';
	if (currentReviewPage === totalPages) {
		nextButton.disabled = true;
	}

	nextButton.addEventListener('click', () => {
		if (currentReviewPage < totalPages) {
			currentReviewPage++;
			displayPaginatedReviews();
		}
	});

	controlsContainer.appendChild(prevButton);
	controlsContainer.appendChild(pageInfo);
	controlsContainer.appendChild(nextButton);
}


// Fonction qui gère le spinner
function toggleLoadingSpinner(show) {
	const loadingSpinner = document.getElementById('review-loading-spinner');
	if (loadingSpinner) {
		loadingSpinner.style.display = show ? 'block' : 'none';
	}
}


// Fonction qui récupère tous les avis
async function fetchAllReviews() {
	toggleLoadingSpinner(true);

	try {
		const response = await fetch(API_REVIEWS_URL, {
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
		allReviewsCache = data;  // Stocke les données dans le cache
		currentReviewPage = 1;
		displayPaginatedReviews();  // Affiche la première page

	} catch (error) {
		console.error('Erreur lors de la récupération des avis: ', error);
		const tableBody = document.getElementById('review-result');
		if (tableBody) {
			tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: red;">Erreur de chargement des données</td></tr>';
		}
	} finally {
		toggleLoadingSpinner(false);
	}
}


// Fonction qui récupère l'ID de l'utilisateur via son email
async function resolveUserId(term) {
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
async function resolvePrestationId(term) {
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
async function fetchReviewsByUser() {
	const input = document.getElementById('search-user-input');
	if (!input) return;

	const term = input.value;
	if (!isValidInput(term)) {
		showFeedbackMessage("Veuillez entrer une adresse mail valide", true);
		return;
	}
	
	toggleLoadingSpinner(true);

	try {

		const userId = await resolveUserId(term);

		if (!userId) {
			showFeedbackMessage('Utilisateur non trouvé', true);
			allReviewsCache = [];
			displayPaginatedReviews();
			return;
		}

		const response = await fetch(`${API_REVIEWS_URL}/by-user/${userId}`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.ok) {
			const data = await response.json();
			if (Array.isArray(data)) {
				allReviewsCache = data;
			} else {
				allReviewsCache = [];
			}
		} else {
			allReviewsCache = [];
			showFeedbackMessage("Erreur lors de la récupération des avis utilisateur", true);
		}

	} catch (error) {
		console.error("Erreur lors du chargement des avis par utilisateur: ", error);
		showFeedbackMessage("Erreur technique lors de la recherche", true);
	} finally {
		currentReviewPage = 1;
		displayPaginatedReviews();
		toggleLoadingSpinner(false);
	}
}


// Fonction qui gère la recherche par prestation
async function fetchReviewsByPrestation() {
	const input = document.getElementById('search-prestation-input');
	if (!input) return;

	const term = input.value;
	if (!isValidInput(term)) {
		showFeedbackMessage("Veuillez entrer un nom de prestation", true);
		return;
	}

	toggleLoadingSpinner(true);

	try {
		const prestationId = await resolvePrestationId(term);

		if (!prestationId) {
			showFeedbackMessage('Prestation non trouvée', true);
			allReviewsCache = [];
			displayPaginatedReviews();
			return;
		}

		const response = await fetch(`${API_REVIEWS_URL}/prestation/${prestationId}`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.ok) {
			const data = await response.json();
			if (Array.isArray(data)) {
				allReviewsCache = data;
			} else {
				allReviewsCache = [];
			}
		} else {
			allReviewsCache = [];
			showFeedbackMessage("Erreur lors de la récupération des avis prestation", true);
		}

	} catch (error) {
		console.error("Erreur lors du chargement des avis par prestation: ", error);
		showFeedbackMessage('Erreur technique lors de la recherche', true);
	} finally {
		currentReviewPage = 1;
		displayPaginatedReviews();
		toggleLoadingSpinner(false);
	}
}


// Fonction qui gère la recherche par utilisateur et prestation
async function fetchReviewsByUserAndPrestation() {
	const input = document.getElementById('search-prestation-and-user-input');
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
			resolveUserId(userTerm),
			resolvePrestationId(prestationTerm)
		]);

		if (!userId) {
			showFeedbackMessage('Utilisateur non trouvé', true);
			toggleLoadingSpinner(false);
			return;
		}
	
		if (!prestationId) {
			showFeedbackMessage('Prestation non trouvée', true);
			toggleLoadingSpinner(false);
			return;
		}

		const response = await fetch(`${API_REVIEWS_URL}/user/${userId}/prestation/${prestationId}`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.ok) {
			const data = await response.json();

			if (Array.isArray(data)) {
				allReviewsCache = data;
			} else if (data && typeof data === 'object') {
				allReviewsCache = [data];
			} else {
				allReviewsCache = [];
			}
		} else {
			allReviewsCache = [];
			showFeedbackMessage('Aucun avis trouvé pour cette combinaison', true);
		}

	} catch (error) {
		console.error("Erreur lors du chargement des avis combinés: ", error);
		showFeedbackMessage('Erreur technique lors de la recherche', true);
	} finally {
		currentReviewPage = 1;
		displayPaginatedReviews();
		toggleLoadingSpinner(false);
	}
}


// Fonction qui gère la confirmation de la suppression d'un avis
function deleteReviewConfirmation(id) {
	const modalOverlay = document.getElementById('confirmation-modal-overlay');
	const modalMessage = document.getElementById('modal-message');
	const modalConfirmButton = document.getElementById('modal-confirm-button');

	if (!modalOverlay || !modalMessage || !modalConfirmButton) return;

	modalMessage.textContent = "Êtes-vous sûr de vouloir supprimer cet avis?";
	modalOverlay.style.display = 'flex';

	const newConfirmButton = modalConfirmButton.cloneNode(true);
	modalConfirmButton.parentNode.replaceChild(newConfirmButton, modalConfirmButton);

	newConfirmButton.dataset.deleteId = id;

	newConfirmButton.addEventListener('click', () => {
		const deleteId = newConfirmButton.dataset.deleteId;
		if (deleteId) {
			deleteReview(deleteId);
		}
		closeReviewModal();
	});
}


// Fonction qui ferme la modale
function closeReviewModal() {
    const modalOverlay = document.getElementById('confirmation-modal-overlay');
    const modalConfirmButton = document.getElementById('modal-confirm-button');

    if (modalOverlay) {
        modalOverlay.style.display = 'none';
    }
    if (modalConfirmButton) {
        modalConfirmButton.dataset.deleteId ='';
    }
}


// Fonction qui gère la suppression d'un avis
async function deleteReview(id) {
	try {
		const response = await fetch(`${API_REVIEWS_URL}/${id}`, {
			method: 'DELETE',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.ok) {
			showFeedbackMessage('Avis supprimé avec succès');
			await fetchAllReviews();
		} else {
			const errorData = await response.json();
			showFeedbackMessage(errorData.error || `Erreur lors de la suppression: ${response.status}`, true);
		}
	} catch (error) {
		console.error("Erreur lors de la suppression de l'avis: ", error);
		showFeedbackMessage(`Erreur: ${error.message}`, true);
	}
}


// Fonction qui gère le bouton 'Supprimer'
function attachReviewActionListeners() {
	document.querySelectorAll('.review-delete-button').forEach(button => {
		button.addEventListener('click', () => {
			deleteReviewConfirmation(button.dataset.id);
		});
	});
}


// Fonction qui gère l'affichage des inputs de la recherche
function toggleReviewSearchVisibility() {
	const selectedElement = document.getElementById('review-search-type-select');
	if (!selectedElement) return;

	const selectedValue = selectedElement.value;

	// Masque tous les champs de recherche
	const allSearchFields = document.querySelectorAll('#section-reviews .search-field');
	allSearchFields.forEach(field => {
		field.style.display = 'none';
	});

	// Nettoie tous les champs de saisie et cache le bouton de suppression
	const allInputs = document.querySelectorAll('#section-reviews .search-field input');
	allInputs.forEach(input => {
		input.value = '';
		const clearButton = input.nextElementSibling;
		if (clearButton && clearButton.classList.contains('clear-input-button')) {
			clearButton.style.display = 'none';
		}
	});

	let containerId = null;

	if (selectedValue === 'by-user') {
		containerId = 'search-by-user-container';
	} else if (selectedValue === 'by-prestation') {
		containerId = 'search-by-prestation-container';
	} else if (selectedValue === 'by-prestation-and-user') {
		containerId = 'search-by-prestation-and-user-container';
	} 

	if (containerId) {
		const container = document.getElementById(containerId);
		if (container) {
			container.style.display = 'flex';
		}
	} else {
		if (selectedValue === 'all') {
			fetchAllReviews();
		}
	}
}


// Fonction qui gère le menu déroulant
function setupReviewCustomSelect() {
	const selected = document.getElementById('review-select-selected');
	const items = document.getElementById('review-select-items');
	const hiddenInput = document.getElementById('review-search-type-select');

	if (!selected || !items || !hiddenInput) return;
	
	// Evite les écouteurs multiples
	const newSelected = selected.cloneNode(true);
	selected.parentNode.replaceChild(newSelected, selected);

	newSelected.addEventListener('click', (e) => {
		e.stopPropagation();
		items.classList.toggle('select-hide');
	});

	items.querySelectorAll('div').forEach(item => {
		item.addEventListener('click', (e) => {
			e.stopPropagation();
			newSelected.textContent = item.textContent;
			hiddenInput.value = item.dataset.value;
			items.classList.add('select-hide');

			// Si 'Tous' est choisi, on réinitialise l'affichage
			if (item.dataset.value === 'all') {
				currentReviewPage = 1;
				displayPaginatedReviews();
			}

			toggleReviewSearchVisibility();
		});
	});

	document.addEventListener('click', (e) => {
		if (!selected.contains(e.target) && !items.contains(e.target)) {
			items.classList.add('select-hide');
		}
	});
}


// Fonction qui réinitialise la section après chaque clic ailleurs
function resetReviewsSection() {
	currentReviewPage = 1;
	reviewsPerPage = 10;

	// Reset du menu déroulant
	const searchSelectInput = document.getElementById('review-search-type-select');
	const searchSelectText =  document.getElementById('review-select-selected');
	if (searchSelectInput) {
		searchSelectInput.value = 'all';
	}
	if (searchSelectText) {
		searchSelectText.textContent = 'Tous les avis';
	}

	// Reset du menu déroulant de la pagination
	const paginSelectInput = document.getElementById('review-pagination-hidden');
	const paginSelectText = document.getElementById('review-pagination-selected');
	if (paginSelectInput) {
		paginSelectInput.value = '10';
	}
	if (paginSelectText) {
		paginSelectText.textContent = '10 par page';
	}

	// Vide les champs de recherche
	const inputs = document.querySelectorAll('#section-reviews .search-field input');
	inputs.forEach(input => {
		input.value = '';
		const clearButton = input.nextElementSibling;
		if (clearButton && clearButton.classList.contains('clear-input-button')) {
			clearButton.style.display = 'none';
		}
	});

	toggleReviewSearchVisibility();
	fetchAllReviews();
}


// Configure la pagination avec le filtre (par 10, 20, 50 ou tous)
function setupReviewPaginationFilter() {
	const searchContainer = document.querySelector('#section-reviews .search-bar');
	if (!searchContainer) return;

	if (document.getElementById('review-pagination-select-wrapper')) {
		return;
	}

	const paginationSelectWrapper = document.createElement('div');
	paginationSelectWrapper.className = 'select-wrapper pagination-select-wrapper';
	paginationSelectWrapper.id = 'review-pagination-select-wrapper';

	paginationSelectWrapper.innerHTML = `
		<div class="select-selected" id="review-pagination-select-selected" tabindex="0" role="combobox" aria-label="Nombre d'avis par page">
			10 par page
		</div>
		<div class="select-items select-hide" id="review-pagination-select-items" role="listbox">
			<div data-value="all">Tous</div>
			<div data-value="10">10 par page</div>
			<div data-value="20">20 par page</div>
			<div data-value="50">50 par page</div>
		</div>
		<input type="hidden" id="review-pagination-hidden-input" value="10">
	`;

	searchContainer.appendChild(paginationSelectWrapper);

	const selected = document.getElementById('review-pagination-select-selected');
	const items = document.getElementById('review-pagination-select-items');
	const hiddenInput = document.getElementById('review-pagination-hidden-input');

	if (!selected || !items || !hiddenInput) return;

	selected.addEventListener('click', () => {
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
				reviewsPerPage = 0;
			} else {
				reviewsPerPage = parseInt(value, 10);
			}
			currentReviewPage = 1;
			displayPaginatedReviews();
		});
	});

	document.addEventListener('click', (e) => {
		if (!selected.contains(e.target) && !items.contains(e.target)) {
			items.classList.add('select-hide');
		}
	});
}


// Fonction d'initialisation pour la section Avis
function init_reviews() {
	if (window.reviewsInitialized) {
		resetReviewsSection();
		return;
	}

	setupReviewClearButton();
	setupReviewCustomSelect();
	setupReviewPaginationFilter();
	toggleReviewSearchVisibility();

	const searchUserButton = document.getElementById('review-search-user-button');
	if (searchUserButton) {
		searchUserButton.addEventListener('click', async (e) => {
			e.preventDefault();
			fetchReviewsByUser();
			currentReviewPage = 1;
			displayPaginatedReviews();
		});
	}

	const searchPrestationButton = document.getElementById('review-search-prestation-button');
	if (searchPrestationButton) {
		searchPrestationButton.addEventListener('click', async (e) => {
			e.preventDefault();
			fetchReviewsByPrestation();
			currentReviewPage = 1;
			displayPaginatedReviews();
		});
	}

	const searchPrestationAndUserButton = document.getElementById('review-search-prestation-and-user-button');
	if (searchPrestationAndUserButton) {
		searchPrestationAndUserButton.addEventListener('click', async (e) => {
			e.preventDefault();
			fetchReviewsByUserAndPrestation();
			currentReviewPage = 1;
			displayPaginatedReviews();
		});
	}

	fetchAllReviews();

	window.reviewsInitialized = true;
}

window.init_reviews = init_reviews;
