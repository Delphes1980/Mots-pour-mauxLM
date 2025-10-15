const API_BASE_URL = 'http://localhost:5000/api/v1/authentication';
const API_LOGIN_URL = `${API_BASE_URL}/login`;
const API_LOGOUT_URL = `${API_BASE_URL}/logout`;


// Fonction qui permet d'effacer le contenu des champs
function setupClearButton() {
  const inputFields = document.querySelectorAll('.form-field input');

  inputFields.forEach(input => {
    const clearButton = input.nextElementSibling;

    clearButton.style.display = 'none';

    input.addEventListener('input', () => {
      if (input.value.length > 0) {
        clearButton.style.display = 'block';
      } else {
        clearButton.style.display = 'none';
        }
    });
    // Efface le champ quand on clique
    clearButton.addEventListener('click', () => {
      input.value = '';
      clearButton.style.display = 'none';
      input.focus();
    });
  });
}


// Fonction pour se connecter
function setupLogin() {
  const loginForm = document.getElementById('loginForm');
  const errorMessageElement = document.getElementById('errorMessage');

  if(!loginForm) {
    console.error("Erreur: L'ID 'loginForm' est introuvable");
    return;
  }

  loginForm.addEventListener('submit', async (event) => {
    // Empêche le rechargement de la page par défaut
    event.preventDefault();

    if (errorMessageElement) {
      errorMessageElement.textContent = '';
      errorMessageElement.style.display = 'none';
    }

    // Récupération des valeurs des champs
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const data = {
      email: email,
      password: password
    };

    // Désactiver le bouton de soumission pour éviter les clics multiples
    const submitButton = loginForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;

    try {
      // Appel à l'API
      const response = await fetch(API_LOGIN_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (response.ok) {
        console.log("Authentification réussie. Les cookies JWT sont définis.");
        window.location.href = '../templates/page_personnelle.html';

      } else {
        console.error("Echec de l'authentification: ", result);

        // Afficher le message d'erreur
        const errorMessage = result.error || "Email ou mot de passe invalide";

        if (errorMessageElement) {
          errorMessageElement.textContent = errorMessage;
          errorMessageElement.style.display = 'block';
        }
      }
    } catch (error) {
      console.error("Erreur lors de la requête: ", error);
      if (errorMessageElement) {
        errorMessageElement.textContent = "Erreur de connexion au serveur. Réessayez.";
        errorMessageElement.style.display = 'block';
      }
    } finally {
      // Réactiver le bouton de soumission
      submitButton.disabled = false;
    }
  });
}


// Fonction pour se déconnecter
function setupLogout() {
  const logoutButton = document.getElementById('logout_link');

  // Sort si le bouton de déconnexion n'existe pas
  if (!logoutButton) {
    return;
  }

  logoutButton.addEventListener('click', async (event) => {
    event.preventDefault();

    logoutButton.disabled = true;
    logoutButton.textContent = 'Déconnexion...';

    try {
      // Appel à l'API
      const response = await fetch(API_LOGOUT_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({})
      });

      if (response.ok || response.status === 401) {
        console.log("Déconnexion réussie. Redirection vers la page d'accueil");
        window.location.href = '../templates/accueil.html';
      } else {
        const errorData = await response.json();
        console.error("Erreur lors de la déconnexion: ", errorData.error);
        alert("Une erreur est survenue lors de la déconnexion: " + (errorData.error || 'Erreur inconnue'));
      }
    } catch (error) {
      console.error("Erreur lors de la requête: ", error);
      alert("Une erreur est survenue lors de la déconnexion.");
    } finally {
      logoutButton.disabled = false;
      logoutButton.textContent = 'Déconnexion';
    }
  });
}


// Fonction pour switcher entre le bouton Connexion et Déconnexion
async function checkLoginStatus() {
  console.log("checkLoginStatus() appelée");

  const loginLink = document.getElementById('login_link');
  const logoutLink = document.getElementById('logout_link');
  const espaceLink = document.getElementById('espace_link');

  if (!loginLink && !logoutLink) {
    console.warn("Aucun bouton de connexion/déconnexion trouvé dans le DOM.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/status`, {
      method: 'GET',
      credentials: 'include'
    });

    console.log("Réponse de vérification :", response.status);

    if (response.ok) {
      // Utilisateur connecté
      if (loginLink) loginLink.style.display = 'none';
      if (logoutLink) logoutLink.style.display = 'inline-block';
      if (espaceLink) espaceLink.style.display = 'inline-block';
      console.log("Utilisateur connecté → bouton déconnexion affiché");
    } else {
      // Utilisateur déconnecté
      if (loginLink) loginLink.style.display = 'inline-block';
      if (logoutLink) logoutLink.style.display = 'none';
      if (espaceLink) espaceLink.style.display = 'none';
      console.log("Utilisateur non connecté → bouton connexion affiché");
    }

  } catch (error) {
    console.error("Erreur lors de la vérification de l'état de connexion :", error);
    if (loginLink) loginLink.style.display = 'inline-block';
    if (logoutLink) logoutLink.style.display = 'none';
    if (espaceLink) espaceLink.style.display = 'none';
  }
}


// Fonction pour rediriger le bouton 'Me contacter'
async function redirectToContactPage() {
  try {
    const response = await fetch(`${API_BASE_URL}/status`, {
      method: 'GET',
      credentials: 'include'
    });

    if (response.ok) {
      // Utilisateur connecté
      window.location.href = '../templates/page_personnelle.html';
    } else {
      // Utilisateur déconnecté
      window.location.href = '../templates/login.html';
    }
  } catch (error) {
    console.error("Erreur de redirection: ", error);
    window.location.href = '../templates/login.html';
  }
}


document.addEventListener('DOMContentLoaded', () => {
  const currentPage = window.location.pathname;

  const logoutLink = document.getElementById('logout_link');
  console.log("logout_link trouvé :", logoutLink);

  if (!logoutLink) {
    alert("Le bouton #logout_link n'existe pas dans le DOM !");
  }

  if (currentPage.includes('login.html')) {
    setupClearButton();
    setupLogin();
  }

  setupLogout();
  checkLoginStatus();

  // Activation du bouton 'Me contacter'
  const contactButton = document.getElementById('contact_button');
  if (contactButton) {
    contactButton.addEventListener('click', (e) => {
      e.preventDefault();
      redirectToContactPage();
    });
  }
});
