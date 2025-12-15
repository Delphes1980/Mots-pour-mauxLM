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


// Bouton pour supprimer les champs
function setupClearButton() {
	const inputFields = document.querySelectorAll('.form-field input');

	inputFields.forEach(input => {
		const clearButton = input.nextElementSibling;
		if (!clearButton || !clearButton.classList.contains('clear-input-button')) return;

		clearButton.style.display = 'none';

		input.addEventListener('input', () => {
			if (input.value.length > 0) {
				clearButton.style.display = 'block';
			} else {
				clearButton.style.display = 'none';
			}
		});

		clearButton.addEventListener('click', () => {
			input.value = '';
			clearButton.style.display = 'none';
			input.focus();

			input.dispatchEvent(new Event('input'));
		});
	});
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
	setupClearButton();
	await setupRegistrationForm();
});
