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
