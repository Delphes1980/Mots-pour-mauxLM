const API_BASE_URL = 'http://localhost:5000/api/v1/authentication';
const API_LOGIN_URL = `${API_BASE_URL}/login`;
const API_LOGOUT_URL = `${API_BASE_URL}/logout`;

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
    return;
  }

  loginForm.addEventListener('submit', async (event) => {
    // Empêche le rechargement de la page par défaut
    event.preventDefault();

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
        window.location.href = '/base_files/templates/page_personnelle.html';

      } else {
        // Afficher le message d'erreur
        showFeedbackMessage("Email ou mot de passe invalide");

      }
    } catch (error) {
      console.error("Erreur lors de la connexion; ", error);
      showFeedbackMessage("Impossible de se connecter. Veuillez réessayer plus tard");
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
        window.location.href = '/base_files/templates/accueil.html';
      } else {
        const errorData = await response.json();
        showFeedbackMessage("Une erreur est survenue lors de la déconnexion: " + (errorData.error || 'Erreur inconnue'));
      }
    } catch (error) {
      console.error("Erreur de déconnexion: ", error);
      showFeedbackMessage("Une erreur est survenue lors de la déconnexion. Veuillez réessayer");
    } finally {
      logoutButton.disabled = false;
      logoutButton.textContent = 'Déconnexion';
    }
  });
}


// Fonction pour switcher entre le bouton Connexion et Déconnexion
async function checkLoginStatus() {
  const loginLink = document.getElementById('login_link');
  const logoutLink = document.getElementById('logout_link');
  const espaceLink = document.getElementById('espace_link');

  if (!loginLink && !logoutLink) {
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/status`, {
      method: 'GET',
      credentials: 'include'
    });

    if (response.ok) {
      // Utilisateur connecté
      if (loginLink) loginLink.style.display = 'none';
      if (logoutLink) logoutLink.style.display = 'inline-block';
      if (espaceLink) espaceLink.style.display = 'inline-block';
    } else {
      // Utilisateur déconnecté
      if (loginLink) loginLink.style.display = 'inline-block';
      if (logoutLink) logoutLink.style.display = 'none';
      if (espaceLink) espaceLink.style.display = 'none';
    }

  } catch (error) {
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
      window.location.href = '/base_files/templates/page_personnelle.html';
    } else {
      // Utilisateur déconnecté
      window.location.href = '/base_files/templates/accueil.html';
    }
  } catch (error) {
    window.location.href = '/base_files/templates/login.html';
  }
}


document.addEventListener('DOMContentLoaded', () => {
  const currentPage = window.location.pathname;

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
