from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt


static_bp = Blueprint('static_pages', __name__)

@static_bp.route('/')
def accueil():
    return render_template('accueil.html')

@static_bp.route('/en-savoir-plus')
def en_savoir_plus():
    return render_template('en_savoir_plus.html')

@static_bp.route('/techniques')
def techniques():
    return render_template('techniques_therapeutiques.html')

@static_bp.route('/prestations')
def prestations():
    return render_template('prestations_tarifs.html')

@static_bp.route('/coordonnees')
def coordonnees():
    return render_template('coordonnees_horaires.html')

@static_bp.route('/avis')
def avis():
    return render_template('avis.html')

@static_bp.route('/login')
def login():
    return render_template('login.html')

@static_bp.route('/mon-espace')
def espace():
    return render_template('page_personnelle.html')

@static_bp.route('/inscription')
def inscription():
    return render_template('page_inscription.html')

@static_bp.route('/formulaire-rdv')
def formulaire_rdv():
    return render_template('formulaire_rdv.html')

@static_bp.route('/formulaire-commentaires')
def formulaire_commentaires():
    return render_template('formulaire_commentaires.html')

@static_bp.route('/politique')
def politique_confidentialite():
    return render_template('politique_confidentialite.html')

@static_bp.route('/admin', methods=['GET'])
@jwt_required()
def admin_dashboard():
    try:
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        if not is_admin:
            return redirect(url_for('static_pages.accueil'))
        return render_template('admin_page.html')
    
    except Exception as e:
        return redirect(url_for('static_pages.login'))
