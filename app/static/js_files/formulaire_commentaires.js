const API_USERS_BASE_URL = '/api/v1/users';
const API_REVIEWS_BASE_URL = '/api/v1/reviews/';
const API_PRESTATIONS_BASE_URL = '/api/v1/prestations/';

// Fonction utilitaire: fait correspondre les noms des inputs HTML aux clés API
function mapInputToUserField(name) {
	const mapping = {
		'first-name': 'first_name',
		'last-name': 'last_name',
	};

	return mapping[name];
}


// Fonction pour soumettre la notation par étoiles
function ratingSubmit() {
    const allStar = document.querySelectorAll('.rating .star');
    const ratingInput = document.getElementById('rating-input');

    if (!allStar.length || !ratingInput) {
      return;
    }

    allStar.forEach((item, idx) => {
        item.addEventListener('click', () => {
          let click = 0;

        ratingInput.value = item.dataset.value;

        // Réinitialisation de toutes les étoiles
        allStar.forEach(star => {
            star.classList.replace('bxs-star', 'bx-star');
            star.classList.remove('active');
            star.setAttribute('aria-checked', 'false');
        });

        // Pour les effets visuels
        for(let i = 0; i < allStar.length; i++) {
          const starCurrentValue = parseInt(allStar[i].dataset.value);
          const selectedRating = parseInt(ratingInput.value);

            if (starCurrentValue <= selectedRating) {
                allStar[i].classList.replace('bx-star', 'bxs-star');
                allStar[i].classList.add('active');
                allStar[i].style.setProperty('--i', i);
                allStar[i].setAttribute('aria-checked', 'true');

            } else {
                allStar[i].classList.replace('bxs-star', 'bx-star');
                allStar[i].classList.remove('active');
                allStar[i].style.setProperty('--i', click);
                allStar[i].setAttribute('aria-checked', 'false');
                click++;
            }
        }
    });
});
}


// Bouton pour effacer le champ
function setupClearButton() {
  // Pour faire apparaitre / disparaître la croix pour effacer le contenu
	const inputFields = document.querySelectorAll('.form-field input, .form-field textarea');

	inputFields.forEach(input => {
		// Ignore l'input de notation caché pour éviter de masquer la première étoile
		if (input.id === 'rating-input') return;

		const clearButton = input.nextElementSibling;

		if (clearButton) {
			clearButton.style.display = 'none';
		}

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
	});
}


// Fonction pour le menu déroulant
function setupCustomSelects() {
  const customSelects = document.querySelectorAll('.select-wrapper');

  customSelects.forEach(customSelect => {
    const selectedItem = customSelect.querySelector('.select-selected');
    const itemsList = customSelect.querySelector('.select-items');
    const hiddenInput = customSelect.querySelector('input[type="hidden"]');

    selectedItem.addEventListener('click', function(e) {
      e.stopPropagation();
      itemsList.classList.toggle('select-hide');
    });

    itemsList.querySelectorAll('div').forEach(item => {
      item.addEventListener('click', function(e) {
        selectedItem.innerHTML = this.innerHTML;
        hiddenInput.value = this.innerHTML;
        itemsList.classList.add('select-hide');
      });
    });

    document.addEventListener('click', function(e) {
      const isClickInside = customSelect.contains(e.target);
      if (!isClickInside) {
        itemsList.classList.add('select-hide');
      }
    });
  });
}


// Fonction pour préremplir les champs nom et prénom
async function loadUserData() {
	try {
		const response = await fetch(`${API_USERS_BASE_URL}/me`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			},
			credentials: 'include'
		});

    if (response.status === 401) {
      window.location.href = '/login';
      return;
    }

		if (!response.ok) {
			throw new Error(`Erreur HTTP lors de la connexion: ${response.status}`);
		}

		const data = await response.json();
		const inputFields = document.querySelectorAll('.form-field input');

		if (data.id) {
			window.currentUserId = data.id;
		}

		inputFields.forEach(input => {
			const apiFieldKey = mapInputToUserField(input.name);

			if (apiFieldKey && data[apiFieldKey] !== undefined) {
				// Remplissage des autres champs
				input.value = data[apiFieldKey];
			}
		});

	} catch (error) {
		console.error("Erreur lors du chargement des données utilisateur: ", error);
		showFeedbackMessage("Impossible de charger vos informations. Veuillez réessayer plus tard", true);
	}
}


// Fonction pour charger les prestations dans le menu déroulant
async function loadPrestationsForDropdown() {
  const dropdownContainer = document.querySelector('.select-items');
  const selectedDisplay = document.querySelector('.select-selected');
  const hiddenInput = document.getElementById('prestation-id');

  if (!dropdownContainer || !selectedDisplay || !hiddenInput) {
    return;
  }

  try {
    const response = await fetch(API_PRESTATIONS_BASE_URL, {
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
      throw new Error(`Erreur lors du chargement des prestations: ${response.status}`);
    }

    const prestations = await response.json();

    if (!Array.isArray(prestations)) {
      return;
    }
    
    // Nettoie le menu existant
    dropdownContainer.innerHTML = '';

    if (prestations.length === 0) {
      dropdownContainer.innerHTML = '<div>Aucune prestation disponible</div>';
      return;
    }

    prestations.forEach(prestation => {
      const item = document.createElement('div');
      item.textContent = prestation.name;
      item.dataset.id = prestation.id;

      item.addEventListener('click', () => {
        selectedDisplay.textContent = prestation.name;
        hiddenInput.value = prestation.id;
        dropdownContainer.classList.add('select-hide');
      });

      dropdownContainer.appendChild(item);
    });
  } catch (error) {
    console.error('Erreur lors du chargement des prestations: ', error);
    showFeedbackMessage("Erreur lors du chargement des prestations. Veuillez réessayer plus tard", true);
  }
}



// Fonction pour soumettre le formulaire
function setupReviewForm() {
  const form = document.querySelector('.review-form');
  if (!form) return;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const rating = parseInt(document.getElementById('rating-input').value);
    const message = document.getElementById('message').value.trim();
    const prestationId = document.getElementById('prestation-id').value;

    if (!rating || rating < 1 || rating > 5) {
      showFeedbackMessage("Veuillez saisir une note entre 1 et 5", true);
      return;
    }

    if (!message || message.replace(/\s/g, '').length < 2) {
      showFeedbackMessage("Veuillez saisir un commentaire valide", true);
      return;
    }

    if (!prestationId) {
      showFeedbackMessage("Veuillez sélectionner une prestation", true);
      return;
    }

    const csrfToken = getCookie('csrf_access_token');
    if (!csrfToken) {
    console.error('Token CSRF manquant');
        showFeedbackMessage('Session invalide, veuillez rafraichir la page', true);
        return;
    }

    try {
      const response = await fetch(API_REVIEWS_BASE_URL, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-TOKEN': csrfToken
        },
        body: JSON.stringify({
          rating,
          text: message,
          prestation_id: prestationId
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Erreur lors de l'envoi du commentaire");
      }

      showFeedbackMessage("Merci pour votre commentaire!");
      setTimeout(() => {
        window.location.href = '/avis';
      }, 3500);

    } catch (error) {
      console.error("Erreur lors de l'envoi du commentaire: ", error);
      showFeedbackMessage("Une erreur est survenue lors de l'envoi du commentaire. Veuillez réessayer", true);
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


document.addEventListener('DOMContentLoaded', function() {
  ratingSubmit();
  setupClearButton();
  setupCustomSelects();
  loadUserData();
  loadPrestationsForDropdown();
  setupReviewForm();
});
