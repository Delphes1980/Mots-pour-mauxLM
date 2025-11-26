document.addEventListener('DOMContentLoaded', () => {
	const sideBarButtons = document.querySelectorAll('.admin-sidebar button');
	const sections = document.querySelectorAll('.admin-section');

	sideBarButtons.forEach(button => {
		button.addEventListener('click', () => {
			const target = button.getAttribute('data-section');

			// Masquer toutes les sections
			sections.forEach(section => {
				section.style.display = 'none';
			});

			// Afficher la section demandée
			const activeSection = document.getElementById(`section-${target}`);
			if (activeSection) {
				activeSection.style.display = 'block';
			}

			// Appelle la fonction init correspondante
			const initFunctionName = `init_${target}`;
			if (typeof window[initFunctionName] === 'function') {
				window[initFunctionName]();
			}
		});
	});

	// Charge par défaut la section prestations
	const defaultSection = document.getElementById('section-prestations');
	if (defaultSection) {
		defaultSection.style.display = 'block';
		if (typeof window.init_prestations === 'function') {
			window.init_prestations();
		}
	}
});
