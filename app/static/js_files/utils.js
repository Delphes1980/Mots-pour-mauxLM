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
