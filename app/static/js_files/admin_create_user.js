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


// Fonction qui récupère les données du formulaire
function getCreateUserFormData() {
	const firstNameInput = document.getElementById('new-user-firstname');
	const lastNameInput = document.getElementById('new-user-lastname');
	const emailInput = document.getElementById('new-user-email');

	let first_name = '';
	let last_name = '';
	let email = '';

	if (firstNameInput && typeof firstNameInput.value === 'string') {
		first_name = firstNameInput.value.trim();
	}

	if (lastNameInput && typeof lastNameInput.value === 'string') {
		last_name = lastNameInput.value.trim();
	}

	if (emailInput && typeof emailInput.value === 'string') {
		email = emailInput.value.trim();
	}

	return { first_name, last_name, email };
}


// Fonction qui valide les données
async function validateCreateUserData(data) {
	// Vérifie que tous les champs sont remplis
	if (!data.first_name || !data.last_name || !data.email) {
		showFeedbackMessage('Tous les champs doivent être remplis', true);
		return false;
	}

	// Vérifie que les champs ne contiennent pas que des espaces
	if (data.first_name.length < 2 || data.last_name.length < 2) {
		showFeedbackMessage('Les champs doivent contenir au moins 2 caractères', true);
		return false;
	}

	// Vérifie que l'email est valide
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	if (!emailRegex.test(data.email)) {
		showFeedbackMessage("L'adresse email n'est pas valide", true);
		return false;
	}

	// Vérifie que l'email n'est pas trop long
	if (data.email.length > 150) {
		showFeedbackMessage("L'adresse email est trop longue", true);
		return false;
	}

	// Vérifie que les champs ne contiennent pas de caractères dangereux (pour éviter les injections HTML)
	const invalidChars = /[<>]/;
	if (invalidChars.test(data.first_name) || invalidChars.test(data.last_name) || invalidChars.test(data.email)) {
		showFeedbackMessage('Caractères invalides détectés', true);
		return false;
	}

	// Vérifie si l'email existe déjà
	try {
		const response = await fetch(`${API_USERS_URL}/search?email=${encodeURIComponent(data.email)}`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.ok) {
			const existingUser = await response.json();
			if (existingUser && existingUser.email) {
				showFeedbackMessage('Un utilisateur avec cet email existe déjà', true);
				return false;
			}
		}
	} catch (error) {
		console.error("Erreur lors de la vérification de l'email: ", error);
		showFeedbackMessage("Erreur lors de la vérification de l'email. Veuillez réessayer", true);
		return false;
	}

	return true;
}


// Fonction qui crée l'utilisateur
async function createUser(data) {
	try {
		const response = await fetch(`${API_USERS_URL}/admin-create`, {
			method: 'POST',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(data)
		});

		if (!response.ok) {
			if (response.status === 403 || response.status === 401) {
				showFeedbackMessage("Accès refusé, Vous devez être connecté en tant qu'administrateur", true);
				return;
			}
			
			let errorData = {};
			try {
				errorData = await response.json();
			} catch (e) {
				// Ignore JSON parsing errors
			}
			showFeedbackMessage(errorData.error || `Erreur HTTP: ${response.status}`, true);
			return;
		}

		showFeedbackMessage('Utilisateur créé avec succès !');
		document.getElementById('create-user-form').reset();

	} catch (error) {
		console.error("Erreur lors de la création de l'utilisateur: ", error);
		showFeedbackMessage("Erreur lors de la création de l'utilisateur. Veuillez réessayer", true);
	}
}


function init_create_user() {
	if (window.createUserInitialized) {
		return;
	}

	const form = document.getElementById('create-user-form');

	if (!form) return;

	// Soumission du formulaire
	form.addEventListener('submit', async (e) => {
		e.preventDefault();
		const data = getCreateUserFormData();

		const isValid = await validateCreateUserData(data);
		if (!isValid) return;

		await createUser(data);
	});

	window.createUserInitialized = true;
}

window.init_create_user = init_create_user;
