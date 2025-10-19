from flask import Blueprint, render_template, request


static_bp = Blueprint('static_pages', __name__)

@static_bp.route('/accueil')
def accueil():
    print("✅ Route / appelée")
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

@static_bp.route('/login')
def login():
    if 'email' in request.args or 'password' in request.args:
        print(f"⚠️ Requête GET avec identifiants interceptée : {request.args}")
        return "Requête non autorisée", 403
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