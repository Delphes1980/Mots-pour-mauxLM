from flask import jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (create_access_token, jwt_required, set_access_cookies, unset_jwt_cookies)
from app.services import facade
from app.utils import (compare_data_and_model, CustomError)


# Créer une instance de façade
facade = facade.Facade()

api = Namespace('authentication', description='Authentication operations')

# Définir le modèle de données pour l'authentification
login_model = api.model('Login', {
    'email': fields.String(required=True, description='Email de l\'utilisateur'),
    'password': fields.String(required=True, description='Mot de passe de l\'utilisateur')
})

# Définir le modèle de données pour la réponse
login_response_model = api.model('LoginResponse', {
    'access_token': fields.String(required=True, description='Token d\'authentification')
})

# Définir le modèle de données pour l'erreur
error_model = api.model('Error', {
    'error': fields.String(description='Message d\'erreur')
})

# Définir le modèle de données pour la réponse de succès
msg_model = api.model('Message', {
    'message': fields.String(description='Message')
})


@api.route('/login')
class Login(Resource):
    @api.doc('Login')
    @api.expect(login_model, validate=False)
    @api.response(200, 'Authentification réussie', login_response_model)
    @api.response(401, 'Authentification échouée', error_model)
    @api.response(400, 'Données de requête invalides', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def post(self):
        """Authentifier un utilisateur et retourner un JWT token"""
        credentials = api.payload

        try:
            compare_data_and_model(credentials, login_model)
            user = facade.get_user_by_email(credentials['email'])

            if (not user or not user.verify_password(credentials['password'])):
                return {'error': 'Authentification échouée'}, 401

        except ValueError as e:
            api.abort(400, error=str(e))
        except CustomError as e:
            if e.status_code == 404:
                api.abort(401, error='Authentification échouée')
            api.abort(e.status_code, error=str(e))

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'id': str(user.id), 'is_admin': user.is_admin}
        )

        response = jsonify({
            'message': 'Authentification réussie',
            'access_token': access_token
            })
        set_access_cookies(response, access_token)
        return response


@api.route('/logout')
class Logout(Resource):
    @api.doc('Logout')
    @jwt_required()
    @api.response(200, 'Déconnexion réussie', msg_model)
    def post(self):
        """Déconnecter un utilisateur"""
        # current_user = get_jwt_identity()
        # return {'message': 'Utilisateur déconnecté avec succès'}, 200
        response = jsonify({'message': 'Déconnexion réussie'})
        unset_jwt_cookies(response)  # Retire les cookies JWT du navigateur
        return response
