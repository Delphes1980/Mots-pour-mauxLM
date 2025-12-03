const API_BASE_URL = '/api/v1/authentication';
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
        if (result.user && result.user.is_admin === true) {
          window.location.href = '/admin';
        } else {
          window.location.href = '/mon-espace';
        }

      } else {
        // Afficher le message d'erreur
        showFeedbackMessage("Email ou mot de passe invalide", true);

      }
    } catch (error) {
      console.error("Erreur lors de la connexion; ", error);
      showFeedbackMessage("Impossible de se connecter. Veuillez réessayer plus tard", true);
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
        window.location.href = '/';
      } else {
        const errorData = await response.json();
        showFeedbackMessage("Une erreur est survenue lors de la déconnexion: " + (errorData.error || 'Erreur inconnue'), true);
      }
    } catch (error) {
      console.error("Erreur de déconnexion: ", error);
      showFeedbackMessage("Une erreur est survenue lors de la déconnexion. Veuillez réessayer", true);
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
      const data = await response.json();
      // Utilisateur connecté
      if (loginLink) loginLink.style.display = 'none';
      if (logoutLink) logoutLink.style.display = 'inline-block';

      // Admin connecté
      if (espaceLink) {
        espaceLink.style.display = 'inline-block';
        if (data.is_admin === true) {
          espaceLink.href = '/admin';
        } else {
          espaceLink.href = '/mon-espace';
        }
      }
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
      const data = await response.json();
      // Admin connecté
      if (data.is_admin === true) {
        window.location.href = '/admin';
      } else {
        // Utilisateur connecté
        window.location.href = '/mon-espace';
      }
    } else if (response.status === 401) {
      // Utilisateur déconnecté (retour à l'accueil)
      window.location.href = '/login';
    } else {
      window.location.href = '/';
    }
  } catch (error) {
    window.location.href = '/login';
  }
}


// Fonction qui gère la demande de réinitialisation du mot de passe
async function sendForgotPasswordRequest() {
  const API_USERS_URL = '/api/v1/users';
  // Récupération de l'input
  const emailInput = document.getElementById('reset-email');
  const email = emailInput ? emailInput.value : '';

  if (!email) {
    showFeedbackMessage('Veuillez entrer une adresse email', true);
    return;
  }

  // Gestion du bouton 'Envoyer'
  const modal = document.getElementById('forgot-password-modal');
  const submitButton = modal.querySelector('.save-edit-button');

  if (submitButton) {
    submitButton.textContent = 'Envoi...';
    submitButton.disabled = true;
  }

  try {
    const response = await fetch(`${API_USERS_URL}/forgot-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ email: email })
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Erreur lors de la demande");
    }

    showFeedbackMessage('Un nouveau mot de passe a été envoyé');
    closeForgotPasswordModal();

  } catch (error) {
    console.error('Erreur lors de la demande de mot de passe: ', error);
    showFeedbackMessage(error.message || "Erreur technique, veuillez réessayer", true);

    if (submitButton) {
      submitButton.textContent = 'Envoyer';
      submitButton.disabled = false;
    }
  }
}


// Fonction qui gère l'ouverture de la modale
function openForgotPasswordModal() {
  const modal = document.getElementById('forgot-password-modal');
  if (!modal) return;

  // Réinitialisation du champ 'Email'
  const emailInput = document.getElementById('reset-email');
  if (emailInput) {
    emailInput.value = '';

    const clearButton = emailInput.nextElementSibling;
    if (clearButton && clearButton.classList.contains('clear-input-button')) {
      clearButton.style.display = 'none';
    }
  }

  // Gestion du bouton 'Envoyer'
  const submitButton = modal.querySelector('.save-edit-button');
  if (submitButton) {
    const newSubmitButton = submitButton.cloneNode(true);
    submitButton.parentNode.replaceChild(newSubmitButton, submitButton);

    newSubmitButton.textContent = 'Envoyer';
    newSubmitButton.disabled = false;

    newSubmitButton.addEventListener('click', (e) => {
      e.preventDefault();
      sendForgotPasswordRequest();
    });
  }

  // Gestion du bouton 'Annuler'
  const cancelButton = document.getElementById('closeModal');
  if (cancelButton) {
    const newCancelButton = cancelButton.cloneNode(true);
    cancelButton.parentNode.replaceChild(newCancelButton, cancelButton);

    newCancelButton.addEventListener('click', (e) => {
      e.preventDefault();
      closeForgotPasswordModal();
    });
  }

  // Affichage de la modale
  modal.style.display = 'flex';
}


// Fonction pour fermer la modale
function closeForgotPasswordModal() {
  const modal = document.getElementById('forgot-password-modal');
  if (modal) {
    modal.style.display = 'none';
  }
}


document.addEventListener('DOMContentLoaded', () => {
  const currentPage = window.location.pathname;

  if (currentPage.includes('/login')) {
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

  const forgotLink = document.getElementById('forgotPasswordLink');
  if (forgotLink) {
    forgotLink.addEventListener('click', (e) => {
      e.preventDefault();
      openForgotPasswordModal();
    });
  }
});
