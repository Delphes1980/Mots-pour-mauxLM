from flask_restx import Namespace, Resource, fields, _http
from app.services import facade
from app.utils import (compare_data_and_model, CustomError, generate_temp_password, validate_entity_id)
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask import request
from app.services.mail_service import send_password_reset_notification


# Créer une instance de façade
facade = facade.Facade()

api = Namespace('users', description='User operations')

# Définir les modèles de données pour l'utilisateur
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='Le prénom de l\'utilisateur'),
    'last_name': fields.String(required=True, description='Le nom de l\'utilisateur'),
    'email': fields.String(required=True, description='Email de l\'utilisateur'),
    'password': fields.String(required=True, description='Mot de passe de l\'utilisateur'),
    'address': fields.String(required=False, description='Adresse de l\'utilisateur'),
    'phone_number': fields.String(required=False, description='Numéro de téléphone de l\'utilisateur')
})

# Définir le modèle de données pour la réponse
user_response_model = api.model('UserResponse', {
    'id': fields.String(required=True, description='ID de l\'utilisateur'),
    'first_name': fields.String(required=True, description='Prénom de l\'utilisateur'),
    'last_name': fields.String(required=True, description='Nom de l\'utilisateur'),
    'email': fields.String(required=True, description='Email de l\'utilisateur'),
    'address': fields.String(required=False, description='Adresse de l\'utilisateur'),
    'phone_number': fields.String(required=False, description='Numéro de téléphone de l\'utilisateur')
})

# Définir le modèle de données pour la mise à jour de l'utilisateur
user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(required=False, description='Prénom de l\'utilisateur'),
    'last_name': fields.String(required=False, description='Nom de l\'utilisateur'),
    'email': fields.String(required=False, description='Email de l\'utilisateur'),
    'old_password': fields.String(required=False, description='Ancien mot de passe de l\'utilisateur'),
    'new_password': fields.String(required=False, description='Nouveau mot de passe de l\'utilisateur'),
    'address': fields.String(required=False, description='Adresse de l\'utilisateur'),
    'phone_number': fields.String(required=False, description='Numéro de téléphone de l\'utilisateur')
})

# Définir le modèle de données pour l'erreur
error_model = api.model('Error', {
    'error': fields.String(description='Message d\'erreur')
})

# Définir le modèle de données pour la réponse de succès
msg_model = api.model('Message', {
    'message': fields.String(description='Message de succès')
})

@api.route('/')
class UserList(Resource):
    @api.doc('Create a user')
    @api.marshal_with(user_response_model, code=_http.HTTPStatus.CREATED, description='Utilisateur créé avec succès')
    @api.expect(user_model)
    @api.response(201, 'Utilisateur créé avec succès', user_response_model)
    @api.response(400, 'Données invalides', error_model)
    @api.response(409, 'L\'utilisateur existe déjà', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    
    def post(self):
        """Créer un nouvel utilisateur"""
        user_data = api.payload

        try:
            compare_data_and_model(user_data, user_model)
            new_user = facade.create_user(**user_data)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))

        if not new_user:
            api.abort(500, error='Erreur interne du serveur')

        return new_user, 201


    @api.doc('Get all users')
    @api.marshal_list_with(user_response_model, code=_http.HTTPStatus.OK, description='List of users retrieved successfully')
    @jwt_required()
    @api.response(200, 'Liste des utilisateurs récupérée avec succès', user_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self):
        """Récupérer tous les utilisateurs"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            users = facade.get_all_users()
            return users, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/search')
class UserSearch(Resource):
    @api.doc('Get a user by mail')
    @api.marshal_with(user_response_model, code=_http.HTTPStatus.OK, description='User retrieved successfully')
    @jwt_required()
    @api.response(200, 'Utilisateur récupéré avec succès', user_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(404, 'Utilisateur non trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self):
        """Récupérer un utilisateur par mail"""
        email = request.args.get('email')
        if not email:
            api.abort(400, error='L\'email de l\'utilisateur est requis')

        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            user = facade.get_user_by_email(email)
            return user, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))


@api.route('/<user_id>')
class User(Resource):
    @api.doc('Get user by ID')
    @api.marshal_with(user_response_model, code=_http.HTTPStatus.OK, description='User retrieved successfully')
    @jwt_required()
    @api.response(200, 'Utilisateur récupéré avec succès', user_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(404, 'Utilisateur non trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self, user_id):
        """Récupérer un utilisateur par son ID"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(user_id, 'user_id')
            user = facade.get_user_by_id(user_id)
            return user, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except ValueError as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))


    @api.doc('Update a user')
    @api.marshal_with(user_response_model, code=_http.HTTPStatus.OK, description='User updated successfully')
    @api.expect(user_update_model)
    @jwt_required()
    @api.response(200, 'Utilisateur mis à jour avec succès', user_response_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(400, 'Données invalides', error_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(404, 'Utilisateur non trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def patch(self, user_id):
        """Mettre à jour un utilisateur"""
        user_data = api.payload

        try:
            compare_data_and_model(user_data, user_update_model)
            validate_entity_id(user_id, 'user_id')

            current_user = get_jwt_identity()
            is_admin = get_jwt().get('is_admin', False)

            if not is_admin and current_user != user_id:
                raise CustomError('Vous ne pouvez pas modifier le compte de quelqu\'un d\'autre', 403)

            # Si l'utilisateur veut changer son mot de passe
            if 'old_password' in user_data and 'new_password' in user_data:
                if not user_data['old_password'] or not user_data['new_password']:
                    raise CustomError('L\'ancien et le nouveau mot de passe sont requis', 400)
                if is_admin:
                    raise CustomError('Vous ne pouvez pas changer directement le mot de passe de l\'utilisateur', 403)
                if current_user != user_id:
                    raise CustomError('Vous ne pouvez pas modifier le mot de passe de quelqu\'un d\'autre', 403)

                updated_user = facade.change_password(user_id, user_data['old_password'], user_data['new_password'])
                return updated_user, 200

            updated_user = facade.update_user(user_id, **user_data)
            return updated_user, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except ValueError as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))


    @api.doc('Delete a user')
    @api.marshal_with(msg_model, code=_http.HTTPStatus.OK, description='User deleted successfully')
    @jwt_required()
    @api.response(200, 'Utilisateur supprimé avec succès', msg_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(404, 'Utilisateur non trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def delete(self, user_id):
        """Supprimer un utilisateur"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(user_id, 'user_id')
            facade.delete_user(user_id)
            return {'message': 'Utilisateur supprimé avec succès'}, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except ValueError as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))


@api.route('/<user_id>/reset-password')
class AdminResetPassword(Resource):
    @api.doc('Admin reset user password')
    @api.marshal_with(msg_model, code=_http.HTTPStatus.OK, description='Password reset successfully')
    @jwt_required()
    @api.response(200, 'Mot de passe réinitialisé avec succès', msg_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(404, 'Utilisateur non trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def post(self, user_id):
        """Réinitialiser le mot de passe d'un utilisateur par l'admin"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        # Générer un mot de passe temporaire
        temp_password = generate_temp_password()

        try:
            updated_user = facade.admin_reset_password(user_id, temp_password)

            # Envoi du mail de notification à l'utilisateur
            try:
                send_password_reset_notification(updated_user.email, temp_password)
            except Exception as e:
                print(f"Echec de l'envoi du mail de notification à {updated_user.email}: {str(e)}")
            return {'message': 'Mot de passe réinitialisé avec succès'}, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))
