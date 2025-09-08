document.addEventListener('DOMContentLoaded', (event) => {
	const modifierButton = document.getElementById('modifier-button');
	const infoForm = document.getElementById('personal-info-form');
	const inputFields = infoForm.querySelectorAll('input');

	modifierButton.addEventListener('click', function(e) {
		e.preventDefault();

		if (modifierButton.textContent === 'Modifier') {
			inputFields.forEach(input => {
				input.removeAttribute('readonly');
			});
			modifierButton.textContent = 'Enregistrer';
			modifierButton.style.backgroundColor = 'var(--writing-light)';
			modifierButton.style.color = 'var(--writing-dark)';
		} else {
			inputFields.forEach(input => {
				input.setAttribute('readonly', 'readonly');
			});
			modifierButton.textContent = 'Modifier';
			modifierButton.style.backgroundColor = 'var(--background-button)';
			modifierButton.style.color = 'var(--background-card)';
		}
	});
});
