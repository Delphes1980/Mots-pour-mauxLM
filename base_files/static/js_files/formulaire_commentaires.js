// Fonction pour soumettre la notation par étoiles
function ratingSubmit() {
    const allStar = document.querySelectorAll('.rating .star');
    const ratingInput = document.getElementById('rating-input');

    if (!allStar.length || !ratingInput) {
      console.warn('Rating stars or input not found');
      return;
    }

    allStar.forEach((item, idx) => {
        item.addEventListener('click', () => {
          let click = 0;

        ratingInput.value = item.dataset.value;
        console.log('Selected rating value: ', ratingInput.value)

        // Réinitialisation de toutes les étoiles
        allStar.forEach(star => {
            star.classList.replace('bxs-star', 'bx-star');
            star.classList.remove('active');
        });

        // Pour les effets visuels
        for(let i = 0; i < allStar.length; i++) {
          const starCurrentValue = parseInt(allStar[i].dataset.value);
          const selectedRating = parseInt(ratingInput.value);

            if (starCurrentValue <= selectedRating) {
                allStar[i].classList.replace('bx-star', 'bxs-star');
                allStar[i].classList.add('active');
                allStar[i].style.setProperty('--i', i);

            } else {
                allStar[i].classList.replace('bxs-star', 'bx-star');
                allStar[i].classList.remove('active');
                allStar[i].style.setProperty('--i', click);
                click++;
            }
        }
    });
});
}

document.addEventListener('DOMContentLoaded', function() {
	// Pour faire apparaitre / disparaître la croix pour effacer le contenu
	const inputFields = document.querySelectorAll('.form-field input, .form-field textarea');

	inputFields.forEach(input => {
		// Ignore l'input de notation caché pour éviter de masquer la première étoile
		if (input.id === 'rating-input') return;

		const clearButton = input.nextElementSibling;

		if (clearButton) {
			clearButton.style.display = 'none';
		}

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
	});

	ratingSubmit();
});