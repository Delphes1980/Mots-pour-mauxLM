const API_PUBLIC_REVIEWS_URL = 'http://localhost:5000/api/v1/reviews';

// Fonction qui génère les étoiles dans un avis déjà laissé
function generateStarsInReviews(rating) {
  let stars = '';
  const maxStars = 5;
  for (let i = 1; i <= maxStars; i++) {
  if (i <= rating) {
    stars += '<i class="bx bxs-star star"></i>';
    } else {
    stars += '<i class="bx bx-star star"></i>';
    }
  }
  return `<div class="rating-stars">${stars}</div>`;
}


// Fonction qui formate le nom de l'auteur du commentaire
function formatAuthor(user) {
  if (!user || !user.first_name) {
    return 'Utilisateur Anonyme';
  }
  return `${user.first_name} ${user.last_name || ''}`.trim();
}


// Fonction qui crée un bloc HTML pour un avis
function createReviewBlock(review) {
  const author = formatAuthor(review.user);
  const stars = generateStarsInReviews(review.rating);
  const text = review.text;

  return `
    <div class="review-box" role="listitem">
      <div class="review-name-box">
        <h3>${author}</h3>
        ${stars}
      </div>
      <div class="review-text-box">
        <p>${text}</p>
      </div>
    </div>
    `;
}


// Fonction pour charger les avis
async function loadPublicReviews() {
  try {
    const response = await fetch(`${API_PUBLIC_REVIEWS_URL}/public-reviews`);
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des commentaires');
    }

    const data = await response.json();
    const container = document.querySelector('.review-container');
    // On vide les commentaires statiques
    container.innerHTML = '';

    data.forEach(review => {
      const reviewHTML = createReviewBlock(review);
      container.insertAdjacentHTML('beforeend', reviewHTML);
    });
  } catch (error) {
    console.error('Erreur lors de la récupération des commentaires: ', error);
  }
}


// Fonction qui intercepte la soumission du formulaire d'avis
async function handleReviewFormSubmission(event) {
  event.preventDefault();

  const text = document.querySelector('#review-text')?.value.trim();
  const rating = parseInt(document.querySelector('#review-rating')?.value, 10);

  if (!text || isNaN(rating)) {
    alert('Veuillez remplir tous les champs');
    return;
  }

  const data = { text, rating };

  try {
    const response = await fetch(API_PUBLIC_REVIEWS_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error("Erreur lors de l'envoi du commentaire");
    }

    document.querySelector('#review-form').reset();
    loadPublicReviews();  // Recharge les avis après ajout
  } catch (error) {
    conseole.error("Erreur lors de l'ajout du commentaire: ", error);
    alert("Une erreur est survenue. Veuillez réessayer plus tard");
  }
}


document.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.review-container');
  if (container && container.children.length === 0) {
    loadPublicReviews();
  }
});