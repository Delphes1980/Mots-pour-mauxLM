from flask_mail import Message
from flask import current_app
from app import mail


def send_mail_async(message):
    """Envoie un objet Message dans le contexte de l'application actuelle """
    try:
        mail.send(message)
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de l'e-mail : {e}")
        raise

def send_appointment_notifications(user_email, practitioner_email, **context):
    """Envoie un email de notification au practicien et un email de confirmation à l'utilisateur"""
    sender_email = current_app.config.get("MAIL_USERNAME")

    user_full_name = context['user_full_name']
    prestation_name = context['prestation_name']
    message = context['message']

    # Mail de notification pour le practicien
    practitioner_notification = f"Nouvelle demande de rendez-vous: {prestation_name} de {user_full_name}"

    practitioner_body = f"""
    Bonjour,

    Une nouvelle demande de prise de rendez-vous a été enregistrée:

    Client: {user_full_name}
    Email client: {user_email}
    Prestation demandée: {prestation_name}

    Message du client: {message}

    Merci de prendre contact pour confirmer la date et l'heure.
    """

    msg_practitioner = Message(
        subject=practitioner_notification,
        body=practitioner_body,
        sender=sender_email,
        recipients=[practitioner_email]
    )
    send_mail_async(msg_practitioner)

    # Mail de confirmation pour l'utilisateur
    user_notification = f"Confirmation de votre demande de rendez-vous"

    user_body = f"""
    Bonjour {user_full_name},

    Votre demande de rendez-vous pour {prestation_name} a été enregistrée avec succès.
    Je vous contacterai prochainement pour confirmer la date et l'heure.

    Merci de votre confiance.
    Mélanie Laborda
    """

    msg_user = Message(
        subject=user_notification,
        body=user_body,
        sender=sender_email,
        recipients=[user_email]
    )
    send_mail_async(msg_user)
