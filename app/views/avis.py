from flask import Blueprint, render_template
import requests

avis_bp = Blueprint('avis', __name__)

@avis_bp.route('/avis')
def avis():
	try:
		response = requests.get('http://localhost:5000/api/v1/reviews/public-reviews')
		response.raise_for_status()
		reviews = response.json()
	except Exception:
		reviews = []

	return render_template('avis.html', reviews=reviews)