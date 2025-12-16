from flask_restx import Namespace, Resource, fields, _http
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask import request
from werkzeug.exceptions import HTTPException
from app.services import facade
from app.utils import (compare_data_and_model, CustomError, generate_temp_password, validate_entity_id, name_validation, sanitize_input, email_validation, validate_phone_number, validate_password)
from app.services.mail_service import (send_password_reset_notification, send_user_created_by_admin_password, send_forgot_password_notification)


# Créer une instance de façade
facade = facade.Facade()

api = Namespace('users', description='User operations')

# Définir le modèle de données pour l'utilisateur
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='Le prénom de l\'utilisateur'),
    'last_name': fields.String(required=True, description='Le nom de l\'utilisateur'),
    'email': fields.String(required=True, description='Email de l\'utilisateur'),
    'password': fields.String(required=True, description='Mot de passe de l\'utilisateur'),
    'address': fields.String(required=False, description='Adresse de l\'utilisateur'),
    'phone_number': fields.String(required=False, description='Numéro de téléphone de l\'utilisateur')
})


# Définir le modèle de données pour l'utilisateur créé par l'admin
admin_user_model = api.model('AdminUserModel', {
	'first_name': fields.String(required=True, description='Prénom de l\'utilisateur'),
	'last_name': fields.String(required=True, descriptioin='Nom de l\'utilisateur'),
	'email': fields.String(required=True, description='Email de l\'utilisateur'),
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

# Définir le modèle de données pour la réponse de user/me
user_me_response_model = api.model('UserMeResponse', {
	'id': fields.String(required=True, description='ID de l\'utilisateur'),
	'first_name': fields.String(required=True, description='Prénom de l\'utilisateur'),
	'last_name': fields.String(required=True, description='Nom de l\'utilisateur'),
	'email': fields.String(required=True, description='Email de l\'utilisateur'),
	'address': fields.String(required=False, description='Adresse de l\'utilisateur'),
	'phone_number': fields.String(required=False, description='Numéro de téléphone de l\'utilisateur'),
	'is_admin': fields.Boolean(required=True, description='Si l\'utilisateur est admin'),
    'created_at': fields.DateTime(required=True, description='Date de création de l\'utilisateur')
})

# Définir le modèle de données pour la réponse de user/me/review
user_me_reviews_response_model = api.model ('UserMeReviewsResponse', {
	'id': fields.String(required=True, description='ID de l\'utilisateur'),
	'rating': fields.Integer(required=True, description='La note du commentaire'),
	'text': fields.String(required=True, description='Le texte du commentaire'),
})

# Définir le modèle de données pour la demande de reset du mot de passe
forgot_password_model = api.model('ForgotPassword', {
	'email': fields.String(required=True, description='Email de l\'utilisateur')
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

            if 'first_name' in user_data:
                user_data['first_name'] = name_validation(user_data['first_name'], 'first_name')
            if 'last_name' in user_data:
                user_data['last_name'] = name_validation(user_data['last_name'], 'last_name')
            if 'email' in user_data:
                user_data['email'] = email_validation(user_data['email'])
            if 'password' in user_data:
                user_data['password'] = validate_password(user_data['password'])
            if 'address' in user_data and user_data['address']:
                user_data['address'] = sanitize_input(user_data['address'], 'address')
            if 'phone_number' in user_data and user_data['phone_number']:
                user_data['phone_number'] = validate_phone_number(user_data['phone_number'])

            new_user = facade.create_user(**user_data)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))

        if not new_user:
            api.abort(500, error='Erreur interne du serveur')

        return new_user, 201


    @api.doc('Get all users')
    @api.marshal_list_with(user_me_response_model, code=_http.HTTPStatus.OK, description='List of users retrieved successfully')
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


@api.route('/admin-create')
class AdminUserCreate(Resource):
    @api.doc('Admin creates a user')
    @api.marshal_with(user_response_model, code=_http.HTTPStatus.CREATED, description='Utilisateur créé par l\'administrateur')
    @api.expect(admin_user_model)
    @jwt_required()
    @api.response(201, 'Utilisateur créé avec succès', user_response_model)
    @api.response(400, 'Données invalides', error_model)
    @api.response(401, 'Vous devez être connecté', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(409, 'L\'utilisateur existe déjà', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def post(self):
        """Créer un nouvel utilisateur par l'admin"""
        current_user = get_jwt()
        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        user_data = api.payload

        # Générer un mot de passe temporaire
        temp_password = generate_temp_password()

        try:
            compare_data_and_model(user_data, admin_user_model)

            if 'first_name' in user_data:
                user_data['first_name'] = name_validation(user_data['first_name'], 'first_name')
            if 'last_name' in user_data:
                user_data['last_name'] = name_validation(user_data['last_name'], 'last_name')
            if 'email' in user_data:
                user_data['email'] = email_validation(user_data['email'])
            if 'address' in user_data and user_data['address']:
                user_data['address'] = sanitize_input(user_data['address'], 'address')
            if 'phone_number' in user_data and user_data['phone_number']:
                user_data['phone_number'] = validate_phone_number(user_data['phone_number'])

            created_user = facade.admin_create_user(temp_password, **user_data)

            if not created_user:
                api.abort(500, error='Erreur interne du serveur')

            # Envoi du mail de notification à l'utilisateur
            try:
                send_user_created_by_admin_password(created_user.email, temp_password)
            except Exception as e:
                print(f"Echec de l'envoi du mail de notification à {created_user.email}: {str(e)}")
            return created_user, 201

        except ValueError as e:
            api.abort(400, error=str(e))
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/search')
class UserSearch(Resource):
    @api.doc('Get a user by mail', params={'email': 'Email de l\'utilisateur'})
    @api.marshal_with(user_me_response_model, code=_http.HTTPStatus.OK, description='User retrieved successfully')
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


@api.route('/search-partial')
class UserSearchPartial(Resource):
    @api.doc('Search users by partial email', params={'email': 'Fragment de l\'email'})
    @api.marshal_list_with(user_me_response_model, code=_http.HTTPStatus.OK, description='Users retrieved successfully')
    @jwt_required()
    @api.response(200, 'Utilisateurs récupérés avec succès', user_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(404, 'Aucun utilisateur trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self):
        """Rechercher des utilisateurs par fragment d'email"""
        fragment = request.args.get('email')
        if not fragment:
            api.abort(400, error='Le fragment d\'email est requis')

        current_user = get_jwt()
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            users = facade.search_users_by_email_fragment(fragment)
            return users, 200
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/me')
class CurrentUser(Resource):
    @api.doc('Get current user informations')
    @api.marshal_with(user_me_response_model, code=_http.HTTPStatus.OK, description='User informations retrieved successfully')
    @jwt_required()
    @api.response(200, 'Informations de l\'utilisateur récupérées avec succès', user_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(404, 'Utilisateur non trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self):
        """Récupérer les informations de l'utilisateur actuel"""
        try:
            current_user = get_jwt_identity()

            try:
                validate_entity_id(current_user, 'user_id')
            except ValueError as e:
                api.abort(400, error=str(e))

            user = facade.get_user_by_id(current_user)

            if not user:
                api.abort(404, error='Utilisateur non trouvé')

            return user, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/me/reviews')
class CurrentUserReviews(Resource):
    @api.doc('Get all the reviews left by the current user')
    @api.marshal_list_with(user_me_reviews_response_model, code=_http.HTTPStatus.OK, description='User reviews retrieved successfully')
    @jwt_required()
    @api.response(200, 'Commentaires récupérés avec succès', user_me_reviews_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(404, 'Aucun commentaire trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self):
        """Récupérer tous les commentaires de l'utilisateur actuel"""
        try:
            current_user = get_jwt_identity()

            try:
                validate_entity_id(current_user, 'user_id')
            except ValueError as e:
                api.abort(400, error=str(e))

            reviews = facade.get_review_by_user(current_user)

            if not reviews:
                return [], 200

            return reviews, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/forgot-password')
class ForgotPassword(Resource):
    @api.doc('Forgot password')
    @api.expect(forgot_password_model)
    @api.response(200, 'Email de réinitialisation envoyé avec succès', msg_model)
    @api.response(400, 'Données invalides', error_model)
    @api.response(404, 'Utilisateur non trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def post(self):
        """Demande de réinitialisation pour mot de passe oublié"""
        data = api.payload
        email = data.get('email')

        if not email:
            api.abort(400, error='L\'email est requis')

        try:
            clean_email = sanitize_input(email, 'email')
            email_validation(clean_email)

            temp_password = generate_temp_password()

            updated_user = facade.reset_password_by_email(clean_email, temp_password)

            try:
                send_forgot_password_notification(updated_user.email, temp_password)
            except Exception as e:
                print(f"Echec de l'envoi du mail de notification à {updated_user.email}: {str(e)}")

            return {'message': 'Email de réinitialisation envoyé avec succès'}, 200

        except ValueError as e:
            api.abort(400, error=str(e))
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


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

            if 'first_name' in user_data:
                user_data['first_name'] = name_validation(user_data['first_name'], 'first_name')
            if 'last_name' in user_data:
                user_data['last_name'] = name_validation(user_data['last_name'], 'last_name')
            if 'email' in user_data:
                user_data['email'] = email_validation(user_data['email'])
            if 'password' in user_data:
                user_data['password'] = validate_password(user_data['password'])
            if 'address' in user_data and user_data['address']:
                user_data['address'] = sanitize_input(user_data['address'], 'address')
            if 'phone_number' in user_data and user_data['phone_number']:
                user_data['phone_number'] = validate_phone_number(user_data['phone_number'])

            # Si l'utilisateur veut changer son mot de passe
            if 'old_password' in user_data and 'new_password' in user_data:
                if not user_data['old_password'] or not user_data['new_password']:
                    raise CustomError('L\'ancien et le nouveau mot de passe sont requis', 400)
                validate_password(user_data['new_password'])
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

            user = facade.get_user_by_id(user_id)
            if not user:
                api.abort(404, error='Utilisateur non trouvé')

            if user.email == 'deleted@system.local':
                api.abort(403, error='Vous ne pouvez pas supprimer l\'utilisateur fantôme')

            ghost_user = facade.get_user_by_email('deleted@system.local')
            if not ghost_user:
                api.abort(404, error='Ghost user non trouvé')

            reviews = facade.get_review_by_user(user_id)
            if reviews:
                facade.reassign_reviews_from_user(user_id, ghost_user.id)

            appointments = facade.get_appointment_by_user(user_id)
            if appointments:
                facade.reassign_appointments_from_user(user_id, ghost_user.id)

            facade.delete_user(user_id)
            return {'message': 'Utilisateur supprimé avec succès'}, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except ValueError as e:
            api.abort(400, error=str(e))
        except HTTPException as e:
            raise e
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
            validate_entity_id(user_id, 'user_id')

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
