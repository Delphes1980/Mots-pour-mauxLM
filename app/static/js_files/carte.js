// Fonction pour unitialiser la carte Leaflet (OpenStreetMap)
function initMap() {
	const mapContainer = document.getElementById('leaflet-map');
	if (!mapContainer) {
		console.error("Le conteneur de carte n'a pas été trouvé");
		return;
	}

	// Coordonnées du cabinet
	const cabinetLat = 43.3504;
	const cabinetLon = 1.9199;
	const zoomLevel = 15;

	// Initialisation de la carte
	const map = L.map('leaflet-map').setView([cabinetLat, cabinetLon], zoomLevel);

	// Ajout des tuiles (images) OpenStreetMap
	L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
		maxZoom: 19
	}).addTo(map);

	// Ajout d'un marqueur pour l'emplacement
	L.marker([cabinetLat, cabinetLon]).addTo(map)
		.bindPopup("<b>Mots pour Maux LM</b><br>7 rue de Bombée, 11400 Saint Papoul")
		.openPopup();
}

document.addEventListener('DOMContentLoaded', initMap);
