from flask_restx import Namespace, Resource, fields, _http
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade
from app.utils import (compare_data_and_model, CustomError, validate_entity_id, rating_validation, text_field_validation)


# Créer une instance de façade
facade = facade.Facade()

api = Namespace('reviews', description='Review operations')

# Définir le modèle de données pour le commentaire
review_model = api.model('Review', {
    'rating': fields.Integer(required=True, description='La note du commentaire'),
    'text': fields.String(required=True, description='Le texte du commentaire'),
    'prestation_id': fields.String(required=True, description='L\'ID de la prestation associée au commentaire'),
})

# Définir le modèle de données pour la réponse
review_response_model = api.model('ReviewResponse', {
    'id': fields.String(required=True, description='ID du commentaire'),
    'rating': fields.Integer(required=True, description='La note du commentaire'),
    'text': fields.String(required=True, description='Le texte du commentaire'),
    'prestation_id': fields.String(attribute=lambda review: f"{review.prestation_id}", required=True, description='L\'ID de la prestation associé au commentaire'),
})

# Définir le modèle de données pour le nom de la prestation liée à l'avis
prestation_details_model = api.model('PrestationDetails', {
	'id': fields.String(required=True, description='ID de la prestation'),
	'name': fields.String(required=True, description='Le nom de la prestation')
})

# Définir le modèle de données pour l'utilisateur pour l'admin
user_admin_details_model = api.model('UserAdminDetails', {
	'id': fields.String(required=True, description='ID de l\'utilisateur'),
	'first_name': fields.String(required=True, description='Le prénom de l\'utilisateur'),
	'last_name': fields.String(required=True, description='Le nom de l\'utilisateur'),
	'email': fields.String(required=True, description='L\'email de l\'utilisateur')
})

# Définir le modèle de données pour la réponse pour l'admin
admin_review_response_model = api.model('AdminReviewResponse', {
    'id': fields.String(required=True, description='ID du commentaire'),
    'rating': fields.Integer(required=True, description='La note du commentaire'),
    'text': fields.String(required=True, description='Le texte du commentaire'),
    'created_at': fields.DateTime(description='Date de création'),
    'prestation': fields.Nested(prestation_details_model, description='Les détails de la prestation associée au commentaire'),
    'user': fields.Nested(user_admin_details_model, description='Les détails de l\'utilisateur associé au commentaire')
})

# Définir le modèle de données pour la mise à jour du commentaire
review_update_model = api.model('ReviewUpdate', {
    'rating': fields.Integer(required=False, description='La note du commentaire'),
    'text': fields.String(required=False, description='Le texte du commentaire')
})

# Définir le modèle de données pour l'utilisateur
user_details_model = api.model('UserDetails', {
	'id': fields.String(required=True, description='ID de l\'utilisateur'),
	'first_name': fields.String(required=True, description='Le prénom de l\'utilisateur'),
    'last_name': fields.String(required=True, description='Le nom de l\'utilisateur')
})

# Définir le modèle de données pour les commentaires publics
public_review_response_model = api.model('PublicReviewResponse', {
	'id': fields.String(required=True, description='ID du commentaire'),
	'rating': fields.Integer(required=True, description='La note du commentaire'),
	'text': fields.String(required=True, description='Le texte du commentaire'),
    'user': fields.Nested(user_details_model, required=True, description='Détails de l\'utilisateur associé au commentaire')
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
class ReviewList(Resource):
    @api.doc('Create a review')
    @api.marshal_with(review_response_model, code=_http.HTTPStatus.CREATED, description='Review successfully created')
    @api.expect(review_model)
    @jwt_required()
    @api.response(201, 'Le commentaire a été créé avec succès', review_response_model)
    @api.response(400, 'Données invalides', error_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(409, 'Un commentaire existe déjà pour cette prestation', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def post(self):
        """Créer un nouveau commentaire pour une prestation"""
        review_data = api.payload

        try:
            compare_data_and_model(review_data, review_model)

            current_user_id = get_jwt_identity()
            given_user_id = review_data.get('user_id')

            if given_user_id and given_user_id != current_user_id:
                raise CustomError('Vous ne pouvez pas créer un commentaire pour un autre utilisateur', 403)

            review_data['user_id'] = current_user_id

            # Vérification des champs
            rating_validation(review_data['rating'])
            text_field_validation(review_data['text'], 'text', 2, 500)

            prestation_id = review_data.get('prestation_id')
            if not prestation_id:
                raise CustomError('L\'ID de la prestation est requis', 400)

            existing_prestation = facade.get_prestation_by_id(prestation_id)
            if not existing_prestation:
                raise CustomError('La prestation n\'existe pas', 404)

            # Vérifier si le commentaire existe déjà pour cette prestation
            try:
                existing_review = facade.get_review_by_user_and_prestation(review_data['user_id'], prestation_id)
                if existing_review:
                    raise CustomError('Un commentaire pour cette prestation existe déjà', 409)
            except CustomError as e:
                if e.status_code == 404:
                    pass
                else:
                    raise e

            # Créer le commentaire
            new_review = facade.create_review(**review_data)
            return new_review, 201

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))


    @api.doc('Get all the reviews')
    @api.marshal_list_with(admin_review_response_model, code=_http.HTTPStatus.OK, description='List of all reviews retrieved successfully')
    @jwt_required()
    @api.response(200, 'Liste des commentaires récupérée avec succès', admin_review_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self):
        """Récupérer tous les commentaires pour l'admin"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            reviews = facade.get_all_reviews()
            return reviews, 200
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/public-reviews')
class PublicReviews(Resource):
    @api.doc('Get all the public reviews')
    @api.marshal_list_with(public_review_response_model, code=_http.HTTPStatus.OK, description='List of all reviews retrieved successfully')
    @api.response(200, 'Liste des commentaires récupérée avec succès', public_review_response_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self):
        """Récupérer tous les commentaires publiques"""
        try:
            reviews = facade.get_all_public_reviews()
            return reviews, 200
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/me')
class UserReviewList(Resource):
    @api.doc('Get all the reviews for the current user')
    @api.marshal_list_with(review_response_model, code=_http.HTTPStatus.OK, description='List of all reviews retrieved successfully')
    @jwt_required()
    @api.response(200, 'Liste des commentaires récupérée avec succès', review_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self):
        """Récupérer tous les commentaires pour l'utilisateur"""
        user_id = get_jwt_identity()

        try:
            existing_user = facade.get_user_by_id(user_id)
            if not existing_user:
                raise CustomError('L\'utilisateur n\'existe pas', 404)

            reviews = facade.get_review_by_user(user_id)
            return reviews, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/by-user/<user_id>')
class ReviewsByUser(Resource):
    @api.doc('Get all reviews for a specific user')
    @api.marshal_list_with(admin_review_response_model, code=_http.HTTPStatus.OK, description='List of reviews retrieved successfully')
    @jwt_required()
    @api.response(200, 'Liste des commentaires récupérée avec succès', admin_review_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\avez pas les droits administrateur', error_model)
    @api.response(404, 'Utilisateur non trouvé', error_model)
    @api.response(500, 'Erreur intern du serveur', error_model)
    def get(self, user_id):
        """Récupérer tous les commentaires d'un utilisateur spécifique"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les drois admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(user_id, 'user_id')
            existing_user = facade.get_user_by_id(user_id)
            if not existing_user:
                raise CustomError('L\'utilisateur n\'existe pas', 404)

            reviews = facade.get_review_by_user(user_id)
            return reviews, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/prestation/<prestation_id>')
class PrestationReviewList(Resource):
    @api.doc('Get all the reviews for a prestation')
    @api.marshal_list_with(admin_review_response_model, code=_http.HTTPStatus.OK, description='List of all reviews retrieved successfully')
    @jwt_required()
    @api.response(200, 'Liste des commentaires récupérée avec succès', admin_review_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self, prestation_id):
        """Récupérer tous les commentaires pour une prestation"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(prestation_id, 'prestation_id')
            existing_prestation = facade.get_prestation_by_id(prestation_id)
            if not existing_prestation:
                raise CustomError('La prestation n\'existe pas', 404)

            reviews = facade.get_review_by_prestation(prestation_id)
            return reviews, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except ValueError as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/user/<user_id>/prestation/<prestation_id>')
class UserPrestationReviewList(Resource):
    @api.doc('Get all the reviews for a prestation by user')
    @api.marshal_list_with(admin_review_response_model, code=_http.HTTPStatus.OK, description='List of all reviews retrieved successfully')
    @jwt_required()
    @api.response(200, 'Liste des commentaires récupérée avec succès', admin_review_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self, user_id, prestation_id):
        """Récupérer tous les commentaires pour une prestation par utilisateur"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(user_id, 'user_id')
            validate_entity_id(prestation_id, 'prestation_id')
            # Vérifier que l'utilisateur existe
            existing_user = facade.get_user_by_id(user_id)
            if not existing_user:
                raise CustomError('L\'utilisateur n\'existe pas', 404)

            # Vérifier que la prestation existe
            existing_prestation = facade.get_prestation_by_id(prestation_id)
            if not existing_prestation:
                raise CustomError('La prestation n\'existe pas', 404)

            reviews = facade.get_review_by_user_and_prestation(user_id, prestation_id)
            return reviews, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except ValueError as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/<review_id>')
class Review(Resource):
    @api.doc('Get a review by its ID')
    @api.marshal_with(admin_review_response_model, code=_http.HTTPStatus.OK, description='Review retrieved successfully')
    @jwt_required()
    @api.response(200, 'Commentaire récupéré avec succès', admin_review_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(404, 'Commentaire non trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self, review_id):
        """Récupérer un commentaire par son ID"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(review_id, 'review_id')
            review = facade.get_review_by_id(review_id)
            if not review:
                raise CustomError('Le commentaire n\'existe pas', 404)
            return review, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except ValueError as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


    @api.doc('Update a review')
    @api.marshal_with(review_response_model, code=_http.HTTPStatus.OK, description='Review updated successfully')
    @api.expect(review_update_model)
    @jwt_required()
    @api.response(200, 'Commentaire mis à jour avec succès', review_response_model)
    @api.response(400, 'Données invalides', error_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Action non autorisée', error_model)
    @api.response(404, 'Commentaire non trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def patch(self, review_id):
        """Mettre à jour un commentaire"""
        try:
            validate_entity_id(review_id, 'review_id')
            review_data = api.payload
            compare_data_and_model(review_data, review_update_model)

            is_admin = get_jwt()

            # Vérifier que l'utilisateur a les droits admin
            if is_admin.get('is_admin'):
                api.abort(403, error='Action non autorisée: l\'administrateur ne peut pas modifier les commentaires')

            current_user_id = get_jwt_identity()
            validate_entity_id(current_user_id, 'current_user_id')

            # Récupérer le commentaire
            review = facade.get_review_by_id(review_id)
            if not review:
                raise CustomError('Le commentaire n\'existe pas', 404)

            # Vérifier que l'utilisateur est bien l'auteur
            if str(current_user_id) != str(review.user_id):
                raise CustomError('Action non autorisée: vous ne pouvez pas modifier le commentaire de quelqu\'un d\'autre', 403)

            # Vérifier que l'utilisateur et la prestation existent toujours
            existing_user = facade.get_user_by_id(current_user_id)
            if not existing_user:
                raise CustomError('L\'utilisateur n\'existe pas', 404)

            existing_prestation = facade.get_prestation_by_id(review.prestation_id)
            if not existing_prestation:
                raise CustomError('La prestation n\'existe pas', 404)

            # Validation des champs modifiés
            if 'rating' in review_data:
                rating = review_data.get('rating')
                try:
                    rating_validation(rating)
                except ValueError as e:
                    raise CustomError(str(e), 400) from e

            if 'text' in review_data:
                text = review_data.get('text')
                try:
                    text_field_validation(text, 'text', 2, 500)
                except ValueError as e:
                    raise CustomError(str(e), 400) from e

            updated_data = {}

            if 'rating' in review_data:
                updated_data['rating'] = review_data['rating']

            if 'text' in review_data:
                updated_data['text'] = review_data['text']

            if not updated_data:
                raise CustomError('Aucune donnée fournie pour la miseà jour', 400)

            updated_review = facade.update_review(review_id, current_user_id=current_user_id, **updated_data)

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except ValueError as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))

        return updated_review, 200


    @api.doc('Delete a review')
    @api.marshal_with(msg_model, code=_http.HTTPStatus.OK, description='Review deleted successfully')
    @jwt_required()
    @api.response(200, 'Commentaire supprimé avec succès', msg_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Action non autorisée', error_model)
    @api.response(404, 'Commentaire non trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def delete(self, review_id):
        """Supprimer un commentaire"""
        current_user = get_jwt()

        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(review_id, 'review_id')
            review = facade.get_review_by_id(review_id)
            if not review:
                api.abort(404, 'Commentaire non trouvé')

            facade.delete_review(review_id)
            return {'message': 'Commentaire supprimé avec succès'}, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except ValueError as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))
