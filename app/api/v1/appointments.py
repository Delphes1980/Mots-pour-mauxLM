from flask_restx import Namespace, Resource, fields, _http
from app.services import facade
from app.utils import (compare_data_and_model, CustomError, text_field_validation, validate_entity_id)
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.mail_service import send_appointment_notifications
from app.models.appointment import AppointmentStatus
from flask import request


# Créer une instance de façade
facade = facade.Facade()

api = Namespace('appointments', description='Appointment operations')

# Définir le modèle de données pour le rendez-vous
appointment_model = api.model('Appointment', {
'message': fields.String(required=True, description='Le message du rendez-vous'),
'prestation_id': fields.String(required=True, description='L\'ID de la prestation associée au rendez-vous')
})

# Définir le modèle pour la mise à jour du statut
allowed_statuses = [
	AppointmentStatus.PENDING,
	AppointmentStatus.CONFIRMED,
	AppointmentStatus.CANCELLED,
	AppointmentStatus.COMPLETED
]

# Définir le modèle de données pour la mise à jour du statut
appointment_status_model = api.model('AppointmentStatusModel', {
	'status': fields.String(required=True, description='Le nouveau statut', enum=allowed_statuses, example=AppointmentStatus.CONFIRMED)
})

# Définir le modèle de données pour la réponse
appointment_response_model = api.model('AppointmentReponse', {
    'id': fields.String(required=True, description='L\'ID du rendez-vous'),
    'message': fields.String(required=True, description='Le message du rendez-vous'),
    'status': fields.String(required=True, description='Le statut du rendez-vous'),
    'prestation_id': fields.String(attribute=lambda appointment: f"{appointment.prestation_id}", required=True, description='L\'ID de la prestation associée au rendez-vous')
})

# Définir le modèle de données pour la réponse pour l'admin
admin_appointment_response_model = api.model('AdminAppointmentResponse', {
    'id': fields.String(required=True, description='ID du rendez-vous'),
    'message': fields.String(required=True, description='Le message du rendez-vous'),
    'status': fields.String(required=True, description='Le statut du rendez-vous'),
    'prestation_id': fields.String(attribute=lambda appointment: f"{appointment.prestation_id}", required=True, description='L\'ID de la prestation associée au rendez-vous'),
    'user_id': fields.String(attribute=lambda appointment: f"{appointment.user_id}", required=True, description='L\'ID de l\'utilisateur associé au rendez-vous')
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
class AppointmentList(Resource):
    @api.doc('Create an appointment')
    @api.marshal_with(appointment_response_model, code=_http.HTTPStatus.CREATED, description='Appointment successfully created')
    @api.expect(appointment_model)
    @jwt_required()
    @api.response(201, 'Le rendez-vous a été créé avec succès', appointment_response_model)
    @api.response(400, 'Données invalides', error_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def post(self):
        """Créer un nouveau rendez-vous"""
        appointment_data = api.payload

        try:
            compare_data_and_model(appointment_data, appointment_model)

            current_user_id = get_jwt_identity()
            appointment_data['user_id'] = current_user_id

            # Récupération de l'utilisateur complet
            current_user = facade.get_user_by_id(current_user_id)

            # Vérification des champs
            text_field_validation(appointment_data['message'], 'message', 1, 500)

            prestation_id = appointment_data.get('prestation_id')
            if not prestation_id:
                raise CustomError('L\'ID de la prestation est requis', 400)

            existing_prestation = facade.get_prestation_by_id(prestation_id)
            if not existing_prestation:
                raise CustomError('La prestation n\'existe pas', 404)

            appointment_data['user_full_name'] = f"{current_user.first_name} {current_user.last_name}"
            appointment_data['prestation_name'] = existing_prestation.name

            # Créer le rendez-vous
            new_appointment = facade.create_appointment(**appointment_data)

            return new_appointment, 201

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except (ValueError, TypeError) as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


    @api.doc('Get all appointments')
    @api.marshal_list_with(admin_appointment_response_model, code=_http.HTTPStatus.OK, description='List of all appointments retrieved successfully')
    @jwt_required()
    @api.response(200, 'Liste des rendez-vous récupérée avec succès', admin_appointment_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(500, 'Erreur interne du serveur')
    def get(self):
        """Récupérer tous les rendez-vous"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            appointments = facade.get_all_appointments()
            return appointments, 200
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/search')
class AppointmentSearch(Resource):
    @api.doc('Get appointment by status', params={'status': 'Le statut du rendez-vous à rechercher'})
    @api.marshal_list_with(admin_appointment_response_model, code=_http.HTTPStatus.OK, description='Appointments retrieved successfully')
    @jwt_required()
    @api.response(200, 'Rendez-vous récupérés avec succès', admin_appointment_response_model)
    @api.response(404, 'Rendez-vous non trouvés', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self):
        """Récupérer des rendez-vous par statut"""
        status = request.args.get('status')
        if not status:
            api.abort(400, error='Le statut du rendez-vous est requis')

        if status not in allowed_statuses:
            api.abort(400, error="Le statut doit être l'un des suivants : " + ", ".join(allowed_statuses))

        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            appointments = facade.get_appointments_by_status(status)
            return appointments, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except Exception as e:
            api.abort(400, error=str(e))


@api.route('/prestation/<prestation_id>')
class PrestationAppointmentList(Resource):
    @api.doc('Get all the appointments for a prestation')
    @api.marshal_list_with(admin_appointment_response_model, code=_http.HTTPStatus.OK, description='List of all appointments retrieved successfully')
    @jwt_required()
    @api.response(200, 'Liste des rendez-vous récupérée avec succès', admin_appointment_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits utilisateur', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self, prestation_id):
        """Récupérer tous les rendez-vous pour une prestation"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(prestation_id, 'prestation_id')
            existing_prestation = facade.get_prestation_by_id(prestation_id)
            if not existing_prestation:
                raise CustomError('La prestation n\'existe pas', 404)

            appointments = facade.get_appointment_by_prestation(prestation_id)
            return appointments, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except (ValueError, TypeError) as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/user/<user_id>')
class UserAppointmentList(Resource):
    @api.doc('Get all the appointments for a user')
    @api.marshal_list_with(admin_appointment_response_model, code=_http.HTTPStatus.OK, description='List of all appointments retrieved successfully')
    @jwt_required()
    @api.response(200, 'Liste des rendez-vous récupérée avec succès', admin_appointment_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self, user_id):
        """Récupérer tous les rendez-vous pour un utilisateur"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(user_id, 'user_id')
            existing_user = facade.get_user_by_id(user_id)
            if not existing_user:
                raise CustomError('L\'utilisateur n\'existe pas', 404)

            appointments = facade.get_appointment_by_user(user_id)
            return appointments, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except (ValueError, TypeError) as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/user/<user_id>/prestation/<prestation_id>')
class UserPrestationAppointmentList(Resource):
    @api.doc('Get all the appointments for a prestation by user')
    @api.marshal_list_with(admin_appointment_response_model, code=_http.HTTPStatus.OK, description='List of all appointments retrieved successfully')
    @jwt_required()
    @api.response(200, 'Liste des rendez-vous récupérée avec succès', admin_appointment_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self, user_id, prestation_id):
        """Récupérer tous les rendez-vous pour une prestation par utilisateur"""
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

            # Vérifier que  la prestation existe
            existing_prestation = facade.get_prestation_by_id(prestation_id)
            if not existing_prestation:
                raise CustomError('La prestation n\'existe pas', 404)

            appointments = facade.get_appointment_by_user_and_prestation(user_id, prestation_id)
            return appointments, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except (ValueError, TypeError) as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


@api.route('/<appointment_id>')
class Appointment(Resource):
    @api.doc('Get an appointment by its ID')
    @api.marshal_with(admin_appointment_response_model, code=_http.HTTPStatus.OK, description='Appointment retrieved successfully')
    @jwt_required()
    @api.response(200, 'Rendez-vous récupéré avec succès', admin_appointment_response_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(404, 'Rendez-vous non trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def get(self, appointment_id):
        """Récupérer un rendez-vous par son ID"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(appointment_id, 'appointment_id')
            appointment = facade.get_appointment_by_id(appointment_id)
            if not appointment:
                raise CustomError('Le rendez-vous n\'existe pas', 404)
            return appointment, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except (ValueError, TypeError) as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))


    @api.doc('Update appointment status')
    @api.marshal_with(admin_appointment_response_model, code=_http.HTTPStatus.OK, description='Appointment status updated successfully')
    @api.expect(appointment_status_model, validate=True)
    @jwt_required()
    @api.response(200, 'Statut du rendez-vous mis à jour avec succès', admin_appointment_response_model)
    @api.response(400, 'Statut invalide', error_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(404, 'Rendez-vous non trouvé', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def put(self, appointment_id):
        """Mettre à jour le statut d'un rendez-vous (Admin seulement)"""
        current_user= get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        appointment_data = api.payload
        new_status = appointment_data.get('status')

        if not new_status:
            api.abort(400, error="Le champ 'status' est requis")

        if new_status not in allowed_statuses:
            api.abort(400, error="Le statut doit être l'un des suivants : " + ", ".join(allowed_statuses))

        try:
            validate_entity_id(appointment_id, 'appointment_id')

            existing_appointment = facade.get_appointment_by_id(appointment_id)
            if not existing_appointment:
                raise CustomError('Le rendez-vous n\'existe pas', 404)

            updated_appointment = facade.update_appointment_status(appointment_id, **appointment_data)
            return updated_appointment, 200
        
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except (ValueError, TypeError) as e:
            api.abort(400, str(e))
        except Exception as e:
            api.abort(500, error=str(e))


    @api.doc('Delete an appointment')
    @api.marshal_with(msg_model, code=_http.HTTPStatus.OK, description='Appointment deleted successfully')
    @jwt_required()
    @api.response(200, 'Rendez-vous supprimé avec succès', msg_model)
    @api.response(403, 'Vous n\'avez pas les droits administrateur', error_model)
    @api.response(404, 'Le rendez-vous n\'a pas été trouvé', error_model)
    @api.response(401, 'Vous devez vous connecter', error_model)
    @api.response(500, 'Erreur interne du serveur', error_model)
    def delete(self, appointment_id):
        """Supprimer un rendez-vous"""
        current_user = get_jwt()

        # Vérifier que l'utilisateur a les droits admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Vous n\'avez pas les droits administrateur')

        try:
            validate_entity_id(appointment_id, 'appointment_id')

            appointment = facade.get_appointment_by_id(appointment_id)
            if not appointment:
                api.abort(404, error='Le rendez-vous n\'a pas été trouvé')

            facade.delete_appointment(appointment_id)
            return {'message': 'Rendez-vous supprimé avec succès'}, 200

        except CustomError as e:
            api.abort(e.status_code, error=str(e))
        except ValueError as e:
            api.abort(400, error=str(e))
        except Exception as e:
            api.abort(500, error=str(e))
