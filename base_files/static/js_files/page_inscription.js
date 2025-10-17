const API_USERS_BASE_URL = 'http://localhost:5000/api/v1/users/'

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


// Fonction pour afficher dynamiquement les symboles de validation ou non des champs
// function setupValidationIcons() {
// 	const fields = [
// 		{ id: 'last-name', validator: isValidName },
// 		{ id: 'first-name', validator: isValidName },
// 		{ id: 'email', validator: isValidEmail },
// 		{ id: 'password', validator: isPasswordSecure }
// 	];

// 	fields.forEach(({ id, validator }) => {
// 		const input = document.getElementById(id);
// 		const icon = document.getElementById(`${id}-icon`);

// 		input.addEventListener('input', () => {
// 			const value = input.value.trim();

// 			if (value.length === 0) {
// 				icon.textContent = '';
// 				icon.classList.remove('visible');
// 				return;
// 			} else {
// 				if (validator(value)) {
// 					icon.textContent = '✅';
// 					icon.style.color = 'green';
// 				} else {
// 					icon.textContent = '❌';
// 					icon.style.color = 'red';
// 				}
// 				icon.classList.add('visible');
// 			}
// 		});
// 	});
// }


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
			alert("Tous les champs sont obligatoires");
			return;
		}

		if (!isValidName(lastName) || !isValidName(firstName)) {
			alert("Le nom et le prénom doivent être valides");
			return;
		}

		if (!isValidEmail(email)) {
			alert("Adresse email invalide");
			return;
		}

		if (!isPasswordSecure(password)) {
			alert("Le mot de passe doit contenir au moins 8 caractères, 1 majuscule, 1 chiffre et 1 caractère spécial");
			return;
		}

		try {
			const response = await fetch(API_USERS_BASE_URL, {
				method: 'POST',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				},
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

			alert("Inscription réussie !");
			window.location.href = '../templates/login.html';
		} catch (error) {
			console.error("Erreur lors de l'inscription: ", error);
			alert(error.message);
		}
	});
}


document.addEventListener('DOMContentLoaded', async () => {
	setupClearButton();
	// setupValidationIcons();
	await setupRegistrationForm();
});
