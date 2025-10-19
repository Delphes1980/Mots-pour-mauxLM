const API_USERS_BASE_URL = 'http://localhost:5000/api/v1/users';
const API_PRESTATIONS_BASE_URL = 'http://localhost:5000/api/v1/prestations/';
const API_APPOINTMENTS_BASE_URL = 'http://localhost:5000/api/v1/appointments/';


// Fonctions utilitaires: 
// Fonction qui fait correspondre les noms des inputs HTML aux clés API
function mapInputToUserField(name) {
	const mapping = {
		'first-name': 'first_name',
		'last-name': 'last_name',
	};

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
    }, 100);
  }, 3000);
}


// Fonction pour effacer le champ
function setupClearButton() {
    const inputFields = document.querySelectorAll('.form-field input, .form-field textarea');

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


// Fonction pour charger les prestations dans le menu déroulant
async function loadPrestationsForDropdown() {
    const dropdownContainer = document.querySelector('.select-items');
    const selectedDisplay = document.querySelector('.select-selected');
    const hiddenInput = document.querySelector('input[name="prestation-type"]');

    if (!dropdownContainer || !selectedDisplay || !hiddenInput) {
        console.error("Eléments du menu déroulant non trouvés");
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

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const prestations = await response.json();

        if (!Array.isArray(prestations)) {
            console.error("Format de données inattendu pour les prestations");
            return;
        }

        // Nettoyage du menu existant
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
        console.error("Erreur lors du chargement des prestations: ", error);
        showFeedbackMessage("Impossible de charger les presdtations. Veuillez réessayer plus tard");
    }
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
		showFeedbackMessage("Impossible de charger vos informations. Veuillez réessayer plus tard");
	}
}


// Fonction pour envoyer le formulaire de prise de rdv
function setupAppointmentForm() {
    const form = document.querySelector('.appointment-form');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const message = document.getElementById('message').value.trim();
        const prestationId = document.querySelector('input[name="prestation-type"]').value;

        if (!message || message.replace(/\s/g, '').length < 10) {
            showFeedbackMessage("Veuillez décrire vos disponibilités ou votre demande plus précisément");
            return;
        }

        if (!prestationId) {
            showFeedbackMessage("Veuillez sélectionner une prestation");
            return;
        }

        try {
            const response = await fetch(API_APPOINTMENTS_BASE_URL, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    prestation_id: prestationId
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Erreur lors de l'envoi de la demande de rendez-vous");
            }

            showFeedbackMessage("Votre demande a bien été envoyée. La praticienne va vous contacter.");
            form.reset();

            setTimeout(() => {
                window.location.href = '/base_files/templates/page_personnelle.html';
            }, 3500);

        } catch (error) {
            console.error("Erreur lors de l'envoi de la demande: ", error);
            showFeedbackMessage("Une erreur est survenue lors de l'envoi de votre demande. Veuillez réessayer");
        }
    });
}


document.addEventListener('DOMContentLoaded', function() {
    setupClearButton();
    setupCustomSelects();
    loadUserData();
    loadPrestationsForDropdown();
    setupAppointmentForm();
});
