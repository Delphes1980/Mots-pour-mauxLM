from flask import Blueprint

test_bp = Blueprint('test_page', __name__)

@test_bp.route('/')
def home():
    return "<h1>Accueil minimal</h1>"
