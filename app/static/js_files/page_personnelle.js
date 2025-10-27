const API_USERS_BASE_URL = '/api/v1/users';
const API_REVIEWS_BASE_URL = '/api/v1/reviews';


// Fonctions utilitaires: 
// Fonction qui fait correspondre les noms des inputs HTML aux clés API
function mapInputToUserField(name) {
	const mapping = {
		firstName: 'first_name',
		lastName: 'last_name',
		email: 'email',
		address: 'address',
		phone: 'phone_number'
	};

	// Ignore le mot de passe pour le remplissage
	if (name === 'password') {
		return null;
	}

	if (!(name in mapping)) {
		return null;
	}

	return mapping[name];
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
    }, 300);
  }, 4000);
}


// Fonction pour charger les données de l'utilisateur
async function loadUserData() {
	try {
		const response = await fetch(`${API_USERS_BASE_URL}/me`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			},
			credentials: 'include'
		});

		if (!response.ok) {
			throw new Error(`Erreur HTTP lors de la connexion: ${response.status}`);
		}

		const data = await response.json();
		const inputFields = document.querySelectorAll('.form-field input');

		if (data.id) {
			window.currentUserId = data.id;
		}

		const firstName = data['first_name'];
		if (firstName) {
			const fisrtNameSpan = document.getElementById('user_firstname');
			if (fisrtNameSpan) {
				fisrtNameSpan.textContent = firstName;
			}
		}

		inputFields.forEach(input => {
			const apiFieldKey = mapInputToUserField(input.name);

			if (input.name === 'password') {
				input.value = '********';
			} else if (apiFieldKey && data[apiFieldKey] !== undefined) {
				// Remplissage des autres champs
				input.value = data[apiFieldKey];
			}
		});

	} catch (error) {
		console.error("Erreur lors du chargement des données utilisateur: ", error);
		showFeedbackMessage("Impossible de charger vos informations. Veuillez réessayer plus tard", true);
	}
}

// Gère le clic sur le bouton Modifier côté informations personnelles
function setupModifierButton(modifierButton, inputFields) {
	modifierButton.addEventListener('click', function(e) {
		e.preventDefault();

		const isEditing = modifierButton.textContent === 'Modifier';
		toggleEditMode(modifierButton, inputFields);

		if (!isEditing) {
			saveUserData(inputFields);
		}
	});
}


// Active ou désactive le champ du formulaire côté informations personnelles
function toggleEditMode(modifierButton, inputFields) {
	const isEditing = modifierButton.textContent === 'Modifier';

	inputFields.forEach(input => {
		if (!input || !input.id) return;

		// On ne permet pas de modifier le mail et le mot de passe
		if (input.id !== 'email' && input.id !== 'password') {
			input.readOnly = !isEditing;
		}
	});

	// Met à jour le style et le texte du bouton
	modifierButton.textContent = isEditing ? 'Enregistrer' : 'Modifier';
	modifierButton.style.backgroundColor = isEditing ? 'var(--writing-light)' : 'var(--background-button)';
	modifierButton.style.color = isEditing ? 'var(--writing-dark)' : 'var(--background-card)';
}


// Envoie les données modifiées à l'API des informations modifiées
function saveUserData(inputFields) {
	const updateData = {};

	inputFields.forEach(input => {
		if (!input || !input.name || input.id == 'email' || input.id === 'password') return;

		const key = mapInputToUserField(input.name);
		if (!key || typeof input.value !== 'string') return;

		updateData[key] = input.value.trim();
	});

	try {
		validateUserData(updateData);
	} catch (error) {
		showFeedbackMessage(error.message);
		return;
	}

	// Vérifie que l'ID est disponible
	if (!window.currentUserId) {
		showFeedbackMessage("Impossible d'identifier l'utilisateur", true);
		return;
	}

	fetch(`${API_USERS_BASE_URL}/${window.currentUserId}`, {
		method: 'PATCH',
		credentials: 'include',
		headers: {
			'Content-type': 'application/json'
		},
		body: JSON.stringify(updateData)
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Erreur lors de la mise à jour des données', true);
		}
		return response.json();
	})
	.then(() => {
		showFeedbackMessage('Mise à jour réussie !');
	})
	.catch(error => {
		console.error(error);
		showFeedbackMessage('Echec lors de la mise à jour. Veuillez réessayer', true);
	});
}


// Fonction qui récupère les commentaires laissés par l'utilisateur
async function loadUserReviews() {
	const reviewsContainer = document.querySelector('.review-container-grid');
	if (!reviewsContainer) {
		return;
	}

	try {
		const response = await fetch(`${API_USERS_BASE_URL}/me/reviews`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.status === 401) {
			window.location.href = '/login';
			return;
		}

		if (!response.ok) {
			throw new Error(`Erreur HTTP ${response.status}`);
		}

		const reviews = await response.json();
		reviewsContainer.innerHTML = '';

		// S'il n'y a aucun commentaire de laissé
		if (!reviews || reviews.length === 0) {
			const emptyMessage = document.createElement('p');
			emptyMessage.textContent = 'Vous n\'avez pas encore laissé de commentaires';
			emptyMessage.className = 'empty-message';
			reviewsContainer.appendChild(emptyMessage);
			return;
		}

		for (const review of reviews) {
			const box = document.createElement('div');
			box.className = 'review-box';
			box.dataset.reviewId = review.id;

			// Etoiles visibles
			const stars = document.createElement('div');
			stars.className = 'rating-stars';

			for (let i = 0; i < 5; i++) {
				const star = document.createElement('i');
				const starValue = i + 1;

				star.className = starValue <= review.rating ? 'bx bxs-star star-icon' : 'bx bx-star star-icon';
				star.dataset.value = starValue;
				star.dataset.reviewId = review.id;
				stars.appendChild(star);
			}

			// Texte visible
			const text = document.createElement('div');
			text.className = 'review-text';
			text.innerHTML = `<p>${review.text || "(Commentaire vide)"}</p>`;

			// Champs cachés pour modification
			const commentInput = document.createElement('textarea');
			commentInput.value = review.text || '';
			commentInput.readOnly = true;
			commentInput.className = 'review-textarea review-field';
			commentInput.dataset.reviewId = review.id;
			commentInput.style.display = 'none';

			// Champ caché pour la note
			const ratingInputHidden = document.createElement('input');
			ratingInputHidden.type = 'hidden';
			ratingInputHidden.value = review.rating;
			ratingInputHidden.readOnly = true;
			ratingInputHidden.className = 'review-rating review-field';
			ratingInputHidden.dataset.reviewId = review.id;			

			// Logique pour les étoiles en mode édition (clic pour la note)
			stars.querySelectorAll('.star-icon').forEach(starIcon => {
				starIcon.addEventListener('click', () => {
					if (box.classList.contains('editing')) {
						const newRating = parseInt(starIcon.dataset.value);
						ratingInputHidden.value = newRating;

						stars.querySelectorAll('.star-icon').forEach(s => {
							const starValue = parseInt(s.dataset.value);
							s.classList.toggle('bxs-star', starValue <= newRating);
							s.classList.toggle('bx-star', starValue > newRating);
						});
					}
				});
			});

			box.appendChild(stars);
			box.appendChild(text);
			box.appendChild(commentInput);
			box.appendChild(ratingInputHidden);
			reviewsContainer.appendChild(box);
		}
	} catch (error) {
		console.error("Erreur lors du chargement des commentaires: ", error);
		const errorMessage = document.createElement('p');
		errorMessage.textContent = "Impossible de charger les commentaires";
		errorMessage.className = 'error-review-message';
		reviewsContainer.appendChild(errorMessage);
	}
}


// Vérifie que les champs obligatoires sont valides
function validateUserData(data) {
	const requiredFields = ['first_name', 'last_name'];
	for (const field of requiredFields) {
		if (!data[field] || typeof data[field] !== 'string' || data[field].trim() === '') {
			throw new Error(`Le champ "${field}" est requis et ne peut pas être vide`);
		}
	}
}


// Gère le clic sur le bouton Modifier côté commentaires laissés par l'utilisateur
function setupReviewModifierButton(modifierReviewButton) {
	modifierReviewButton.addEventListener('click', async function (e) {
		e.preventDefault();

		const isEditing = modifierReviewButton.textContent === 'Modifier';
		const ratingFields = document.querySelectorAll('.review-rating');
		const textFields = document.querySelectorAll('.review-textarea');

		if (!isEditing) {
			await saveAllReviewData(ratingFields, textFields);
			await loadUserReviews();
		}

		toggleReviewEditMode(modifierReviewButton, ratingFields, textFields);
	});
}


// Active ou désactive le champ du formulaire côté commentaires laissés par l'utilisateur
function toggleReviewEditMode(modifierReviewButton) {
	const isEditing = modifierReviewButton.textContent === 'Modifier';
	const reviewBoxes = document.querySelectorAll('.review-box');

	reviewBoxes.forEach(box => {
		const text = box.querySelector('.review-text');
		const textarea = box.querySelector('.review-textarea');
		const stars = box.querySelector('.rating-stars');

		// On a appuyé sur le bouton Modifier
		if (isEditing) {
			box.classList.add('editing');
			if (text) text.style.display = 'none'; // Masque le texte stylisé
			if (textarea) {
				textarea.style.display = 'block';
				textarea.readOnly = false; // Rend le champ modifiable
			}
		} else {
			// On quitte le mode édition
			box.classList.remove('editing');
			if (text) text.style.display = 'block';
			if (textarea) {
				textarea.style.display = 'none';
				textarea.readOnly = true;
			}

			if (text && textarea) {
				text.innerHTML = `<p>${textarea.value || "Commentaire vide)"}</p>`;
			}
		}
	});

	modifierReviewButton.textContent = isEditing ? 'Enregistrer' : 'Modifier';
	modifierReviewButton.style.backgroundColor = isEditing ? 'var(--writing-light)' : 'var(--background-button)';
	modifierReviewButton.style.color = isEditing ? 'var(--writing-dark)' : 'var(--background-card)';
}


// Envoie les données modifiées à l'API des commentaires modifiés
async function saveAllReviewData() {
	const reviewBoxes = document.querySelectorAll('.review-box');
	let hasError = false;

	for (const box of reviewBoxes) {
		const ratingInput = box.querySelector('.review-rating');
		const textInput = box.querySelector('.review-textarea');

		if (!ratingInput || !textInput) continue;

		const reviewId = ratingInput.dataset.reviewId;
		const rating = parseInt(ratingInput.value);
		const text = textInput.value;

		if (!reviewId || isNaN(rating) || rating < 1 || rating > 5) {
			console.error(`Données invalides pour l'avis: ${reviewId}`);
			hasError = true;
			continue;
		}

		try {
			const response = await fetch(`${API_REVIEWS_BASE_URL}/${reviewId}`, {
				method: 'PATCH', 
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ rating, text })
			});

			if (!response.ok) {
				hasError = true;
				throw new Error(`Erreur pour le commentaire ${reviewId}`);
			}
		} catch (error) {
			console.error(`Erreur lors de la mise à jour du commentaire ${reviewId}`, error);
			hasError = true;
		}
	}

	if (hasError) {
		showFeedbackMessage("Certains commentaires n'ont pas pu être mis à jour. Veuillez réessayer", true);
	} else {
		showFeedbackMessage('Tous les commentaires ont été mis à jour !');
	}

	await loadUserReviews();
}


document.addEventListener('DOMContentLoaded', () => {
	// Infos personnelles
	const modifierButton = document.getElementById('modifier-button');
	const infoForm = document.getElementById('personal-info-form');

	// Vérifie que les éléments existent
	if (!modifierButton || !infoForm) {
		return;
	}

	const inputFields = infoForm.querySelectorAll('input');
	if (!inputFields || inputFields.length === 0) {
		return;
	}

	loadUserData(inputFields);
	setupModifierButton(modifierButton, inputFields);

	// Commentaires
	const modifierReviewButton = document.getElementById('modifier-review-button');
	if (!modifierReviewButton) {
		return;
	}

	loadUserReviews();
	setupReviewModifierButton(modifierReviewButton);
});

window.addEventListener('error', function (e) {
    console.error("Erreur JS globale :", e.message);
});
