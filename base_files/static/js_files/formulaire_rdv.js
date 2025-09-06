document.addEventListener('DOMContentLoaded', function() {
	// Pour faire apparaitre / disparaître la croix pour effacer le contenu
	const inputFields = document.querySelectorAll('.form-field input, .form-field textarea');

	inputFields.forEach(input => {
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

	// Code pour le menu déroulant personnalisé
	const customSelects = document.querySelectorAll('.select-wrapper');

	customSelects.forEach(customSelect => {
	  const selectedItem = customSelect.querySelector('.select-selected');
	  const itemsList = customSelect.querySelector('.select-items');
	  const hiddenInput = customSelect.querySelector('input[type="hidden"]');

	  selectedItem.addEventListener('click', function(e) {
		  e.stopPropagation();
		  itemsList.classList.toggle('select-hide');
	  });

	  itemsList.querySelectorAll('div').forEach(item => {
		  item.addEventListener('click', function(e) {
			  selectedItem.innerHTML = this.innerHTML;
			  hiddenInput.value = this.innerHTML;
			  itemsList.classList.add('select-hide');
		  });
	  });

	  document.addEventListener('click', function(e) {
		  const isClickInside = customSelect.contains(e.target);
		  if (!isClickInside) {
			  itemsList.classList.add('select-hide');
		  }
	  });
	});
});
