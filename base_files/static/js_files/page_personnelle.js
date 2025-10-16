console.log("Script chargé");
const API_USERS_BASE_URL = 'http://localhost:5000/api/v1/users';


// Fonction utilitaire: fait correspondre les noms des inputs HTML aux clés API
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
		console.warn(`Champ inconnu ignoré: ${name}`);
		return null;
	}

	return mapping[name];
}


// Fonction pour charger les données de l'utilisateur
async function loadUserData() {
	console.log("Appel à loadUserData");

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
		console.log("Données reçues: ", data);

		const inputFields = document.querySelectorAll('.form-field input');

		if (data.id) {
			window.currentUserId = data.id;
			console.log("ID utilisateur: ", window.currentUserId);
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
		console.error("Impossible de charger vos informations. Redirection vers l'accueil");
	}
}

// Gère le clic sur le bouton Modifier
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


// Active ou désactive le champ du formulaire
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


// Envoie les données modifiées à l'API
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
		alert(error.message);
		return;
	}

	// Vérifie que l'ID est disponible
	if (!window.currentUserId) {
		alert("Impossible d'identifier l'utilisateur");
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
		console.log("Réponse PATCH :", response.status);
		if (!response.ok) {
			throw new Error('Erreur lors de la mise à jour des données');
		}
		return response.json();
	})
	.then(() => {
		alert('Mise à jour réussie !');
	})
	.catch(error => {
		console.error(error);
		alert('Echec lors de la mise à jour. Veuillez réessayer');
	});
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


document.addEventListener('DOMContentLoaded', () => {
	console.log("DOM entièrement chargé !");

	const modifierButton = document.getElementById('modifier-button');
	const infoForm = document.getElementById('personal-info-form');

	// Vérifie que les éléments existent
	if (!modifierButton || !infoForm) {
		console.error("Eléments du formulaire introuvables");
		return;
	}

	const inputFields = infoForm.querySelectorAll('input');
	if (!inputFields || inputFields.length === 0) {
		console.warn("Aucun champ de saisie trouvé dans le formulaire");
		return;
	}

	loadUserData(inputFields);
	setupModifierButton(modifierButton, inputFields);
});

window.addEventListener('error', function (e) {
    console.error("Erreur JS globale :", e.message);
});
