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


// Bouton pour effacer le champ
function setupClearButton(selector) {
    const inputFields = document.querySelectorAll(selector);

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


// Fonction qui gère le spinner
function toggleLoadingSpinner(spinnerId, show) {
	const loadingSpinner = document.getElementById(spinnerId);
	if (loadingSpinner) {
		loadingSpinner.style.display = show ? 'block' : 'none';
	}
}


// Fonction qui gère le format date de la colonne 'Date de création'
function formatDate(dateString) {
	if (!dateString) {
		return 'N/A';
	}

	const date = new Date(dateString);
	return date.toLocaleDateString('fr-FR', {
		day: '2-digit',
		month: '2-digit',
		year: 'numeric'
	});
}


// Fonction qui valide les entrées
function isValidInput(input) {
	if (!input) {
		return false;
	}
	if (typeof input !== 'string') {
		return false;
	}
	if (input.trim().length === 0) {
		return false;
	}
	const dangerousChar = /[<>{}]/;
	if (dangerousChar.test(input.trim())) {
		return false;
	}
	return true;
}

// Fonction qui récupère la valeur du cookie CSRF
function getCookie(name) {
	// Validation de l'entrée
	if (!name || typeof name !== 'string') {
		return null;
	}

	// On échappe les éventuel caractères spéciaux
	const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

	// On construit une Regex précise
	const regex = new RegExp('(^|;\\s*)' + escapedName + '=([^;]*)');

	// On vérifie
	const match = document.cookie.match(regex);

	// On décode la valeur
	if (match) {
		return decodeURIComponent(match[2]);
	} else {
		return null;
	}
}


// Fonction qui trie les données par date
/**
 * @param {Array} data - Le tableau à trier
 * @param {string} dateKey - Le nom de la clé contenant la date (created_at)
 * @param {boolean} isAscending - true pour croissant, false pour décroissant
 */
function sortDataByDate(data, dateKey, isAscending) {
	if (!data || data.length === 0) {
		return;
	}

	data.sort((a, b) => {
		const dateA = new Date(a[dateKey]);
		const dateB = new Date(b[dateKey]);

		if (isAscending) {
			return dateA - dateB;
		} else {
			return dateB - dateA;
		}
	});
}


// Fonction qui met à jour l'icône de tri
/**
 * @param {string} iconId - l'ID de l'élément <i> à modifier
 * @param {boolean} isAscending - true si croissant, false si décroissant
 */
function updateSortIcon(iconId, isAscending) {
	const icon = document.getElementById(iconId);
	if (icon) {
		icon.className = isAscending ? 'bx bx-up-arrow-alt' : 'bx bx-down-arrow-alt';
		icon.style.verticalAlign = 'middle';
		icon.style.marginLeft = '5px';
	}
}
