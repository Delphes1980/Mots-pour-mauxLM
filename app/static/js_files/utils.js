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
