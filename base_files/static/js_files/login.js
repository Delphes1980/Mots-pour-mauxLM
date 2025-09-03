document.addEventListener('DOMContentLoaded', function() {
  const inputFields = document.querySelectorAll('.form-field input');

  inputFields.forEach(input => {
    const clearButton = input.nextElementSibling;

    input.addEventListener('input', () => {
      if (input.value.length > 0) {
        clearButton.style.display = 'block';
      } else {
        clearButton.style.display = 'none';
        }
    });
    clearButton.addEventListener('click', () => {
      input.value = '';
      clearButton.style.display = 'none';
      input.focus();
    });
  });
});
