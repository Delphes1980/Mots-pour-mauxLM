from flask_restx import Namespace, Resource, fields, _http
from flask_jwt_extended import (jwt_required, get_jwt, get_jwt_identity)
from flask import request
from app.services import facade
from app.utils import (compare_data_and_model, CustomError, name_validation, validate_entity_id)


# Créer une instance de façade
facade = facade.Facade()

api = Namespace('prestations', description='Prestation operations')

# Définir le modèle de données pour la prestation
prestation_model = api.model('Prestation', {
    'name': fields.String(required=True, description='Le nom de la prestation')
})

# Définir le modèle de données pour la réponse
prestation_response_model = api.model('PrestationResponse', {
    'id': fields.String(required=True, description='ID de la prestation'),
    'name': fields.String(required=True, description='Le nom de la prestation', attribute='name')
})

# Définir le modèle de données pour la mise à jour d'une prestation
prestation_update_model = api.model('PrestationUpdate', {
    'name': fields.String(required=False, description='Le nom de la prestation', attribute='name')
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
class PrestationList(Resource):
    @api.doc('Create a prestation')
    @api.marshal_with(prestation_response_model, code=_http.HTTPStatus.CREATED, description='Prestation créée avec succès')
    @api.expect(prestation_model)
    @jwt_required()
    @api.response(201, 'Prestation créée avec succès', prestation_response_model)
    @api.response(400, 'Données invalides', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(409, 'La prestation existe déjà', error_model)

    def post(self):
        """Créer une nouvelle prestation"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        prestation_data = api.payload
        try:
            compare_data_and_model(prestation_data, prestation_model)
            new_prestation = facade.create_prestation(**prestation_data)

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))

        if not new_prestation:
            api.abort(500, error='Erreur interne du serveur')

        return new_prestation, 201


    @api.doc('Get all prestations (for admin or user)')
    @api.marshal_list_with(prestation_response_model, code=_http.HTTPStatus.OK, description='List of prestations retrieved successfully')
    @jwt_required()
    @api.response(200, 'Liste des prestations récupérée avec succès', prestation_response_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(404, 'Prestation non trouvée', error_model)
    def get(self):
        """Récupérer toutes les prestations selon le rôle"""
        is_admin = get_jwt()
        current_user = get_jwt_identity()

        if not current_user:
            api.abort(401, error='Vous devez vous connecter')

        print("→ Accès utilisateur standard à /prestations/")

        try:
            if is_admin.get('is_admin'):
                prestations = facade.get_all_prestations()
            else:
                prestations = facade.get_all_prestations_for_user()

            return prestations, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/search')
class PrestationSearch(Resource):
    @api.doc('Get prestation by name', params={'name': 'Le nom de la prestation à rechercher'})
    @api.marshal_with(prestation_response_model, code=_http.HTTPStatus.OK, description='Prestation retrieved successfully')
    @jwt_required()
    @api.response(200, 'Prestation récupérée avec succès', prestation_response_model)
    @api.response(404, 'Prestation non trouvée', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    def get(self):
        """Récupérer une prestation par son nom"""
        name = request.args.get('name')
        if not name:
            api.abort(400, error='Le nom de la prestation est requis')

        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            prestation = facade.get_prestation_by_name(name)
            return prestation, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))


@api.route('/<prestation_id>')
class Prestation(Resource):
    @api.doc('Get prestation by ID')
    @api.marshal_with(prestation_response_model, code=_http.HTTPStatus.OK, description='Prestation retrieved successfully')
    @jwt_required()
    @api.response(200, 'Prestation récupérée avec succès', prestation_response_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(404, 'Prestation non trouvée', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    def get(self, prestation_id):
        """Récupérer une prestation par son ID"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(prestation_id, 'prestation_id')
            prestation = facade.get_prestation_by_id(prestation_id)
            if not prestation:
                raise CustomError('La prestation n\'existe pas', 404)

            return prestation, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))


    @api.doc('Update a prestation')
    @api.marshal_with(prestation_response_model, code=_http.HTTPStatus.OK, description='Prestation updated successfully')
    @api.expect(prestation_update_model)
    @jwt_required()
    @api.response(200, 'Prestation mise à jour avec succès', prestation_response_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(400, 'Données invalides', error_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(404, 'Prestation non trouvée', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def put(self, prestation_id):
        """Mettre à jour une prestation"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        prestation_data = api.payload

        try:
            compare_data_and_model(prestation_data, prestation_update_model)
            validate_entity_id(prestation_id, 'prestation_id')

            if 'name' in prestation_data:
                name = prestation_data.get('name')
            try:
                name_validation(name, 'name')
            except ValueError as e:
                raise CustomError(str(e), 400) from e

            updated_prestation = facade.update_prestation(prestation_id, **prestation_data)
            return updated_prestation, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))


    @api.doc('Delete a prestation')
    @api.marshal_with(msg_model, code=_http.HTTPStatus.OK, description='Prestation deleted successfully')
    @jwt_required()
    @api.response(200, 'Prestation supprimée avec succès', msg_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(404, 'La prestation n\'a pas été trouvée', error_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def delete(self, prestation_id):
        """Supprimer une prestation"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(prestation_id, 'prestation_id')

            prestation = facade.get_prestation_by_id(prestation_id)
            if not prestation:
                api.abort(404, error='Prestation non trouvée')

            if prestation.name == 'Ghost prestation':
                api.abort(403, error='Vous ne pouvez pas supprimer la prestation fantôme')

            ghost_prestation = facade.get_prestation_by_name('Ghost prestation')
            if not ghost_prestation:
                api.abort(404, error='Prestation fantôme non trouvée')

            reviews = facade.get_review_by_prestation(prestation_id)
            if reviews:
                facade.reassign_reviews_from_prestation(prestation_id, ghost_prestation.id)

            facade.delete_prestation(prestation_id)
            return {'message': 'Prestation supprimée avec succès'}, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except ValueError as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))
