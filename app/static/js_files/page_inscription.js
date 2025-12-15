const API_USERS_BASE_URL = '/api/v1/users/'

// Fonctions utilitaires
// Valide le nom
function isValidName(name) {
	const regex = /^[A-Za-zÀ-ÿ' -]+$/;
	return regex.test(name);
}


// Valide l'email
function isValidEmail(email) {
	const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	return regex.test(email);
}


// Valide le mot de passe
function isPasswordSecure(password) {
	if (!password || password.length < 8) return false;
	if (!/[a-z]/.test(password)) return false;
	if (!/[A-Z]/.test(password)) return false;
	if (!/\d/.test(password)) return false;
	if (!/[!@#$%^&*()_+\-={}\[\]|\\:;"<,>.?/~`]/.test(password)) return false;

	return true;
}


// Soumission du formulaire d'inscription
async function setupRegistrationForm() {
	const form = document.querySelector('.registration-form');
	if (!form) return;

	form.addEventListener('submit', async (e) => {
		e.preventDefault();

		const lastName = document.getElementById('last-name').value.trim();
		const firstName = document.getElementById('first-name').value.trim();
		const email = document.getElementById('email').value.trim();
		const password = document.getElementById('password').value;

		if (!lastName || !firstName || !email || !password) {
			showFeedbackMessage("Tous les champs sont obligatoires", true);
			return;
		}

		if (!isValidName(lastName) || !isValidName(firstName)) {
			showFeedbackMessage("Le nom et le prénom doivent être valides", true);
			return;
		}

		if (!isValidEmail(email)) {
			showFeedbackMessage("Adresse email invalide", true);
			return;
		}

		if (!isPasswordSecure(password)) {
			showFeedbackMessage("Le mot de passe doit contenir au moins 8 caractères, 1 majuscule, 1 chiffre et 1 caractère spécial", true);
			return;
		}

		const csrfToken = getCookie('csrf_access_token');

		const headers = {
			'Content-Type': 'application/json'
		};

		if (csrfToken) {
			headers['X-CSRF-TOKEN'] = csrfToken;
		}

		try {
			const response = await fetch(API_USERS_BASE_URL, {
				method: 'POST',
				credentials: 'include',
				headers: headers,
				body: JSON.stringify({
					last_name: lastName,
					first_name: firstName,
					email: email,
					password: password
				})
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.error || "Erreur lors de l'inscription");
			}

			showFeedbackMessage("Inscription réussie !");
			form.reset();

			setTimeout(() => {
				window.location.href = '/login';
			}, 3500);

		} catch (error) {
			console.error("Erreur lors de l'inscription: ", error);
			showFeedbackMessage("Une erreur est survenue lors de l'inscription. Veuillez réessayer", true);
		}
	});
}


document.addEventListener('DOMContentLoaded', async () => {
	setupClearButton('.form-field input');
	await setupRegistrationForm();
});
