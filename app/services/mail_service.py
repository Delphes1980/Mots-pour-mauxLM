from flask_mail import Message
from flask import current_app
from app import mail
import os


def send_mail_async(message):
    """Envoie un objet Message dans le contexte de l'application actuelle """
    try:
        mail.send(message)
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de l'e-mail : {e}")
        raise

def send_appointment_notifications(user_email, practitioner_email, **context):
    """Envoie un email de notification au practicien et un email de confirmation à l'utilisateur"""
    sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')

    # Vérification des clés attendues
    required_keys = ["user_full_name", "prestation_name", "message"]
    missing_keys = [key for key in required_keys if key not in context]

    if missing_keys:
        raise ValueError(f"Les clés suivantes sont manquantes dans le contexte: {', '.join(missing_keys)}")

    user_full_name = context['user_full_name']
    prestation_name = context['prestation_name']
    message = context['message']

    # Mail de notification pour le praticien
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
    user_notification = f"Accusé de réception de votre demande de rendez-vous"

    user_body = f"""
    Bonjour {user_full_name},

    Votre demande de rendez-vous pour {prestation_name} a bien été reçue.
    Je vous contacterai prochainement pour confirmer la date et l'heure.

    Rappel de votre message:
    {message}.

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

def send_password_reset_notification(user_email, temp_password):
    """Envoie un email à l'utilisateur après réinitialisation de son mot de passe par l'admin"""
    
    sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')

    subject = 'Votre mot de passe a été réinitialisé'
    body = f"""
    Bonjour,

    Votre mot de passe a été réinitialisé par l'administrateur.
    Vous pouvez vous connecter avec votre nouveau mot de passe temporaire: {temp_password}.

    N'oubliez pas de changer votre mot de passe lors de votre prochaine connexion dans votre espace personnel.

    Mélanie Laborda
    """

    message = Message(
        subject=subject,
        body=body,
        sender=sender_email,
        recipients=[user_email]
    )

    send_mail_async(message)

def send_user_created_by_admin_password(user_email, temp_password):
    """Envoie un email avec un mot de passe temporaire à l'utilisateur après création par l'admin"""

    sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')

    subject = "Votre compte a été créé par l'administrateur"
    body = f"""
    Bonjour,

    Un compte a été créé pour vous par l'administrateur du site Mots pour Maux LM.

    Voici votre mot de passe temporaire: {temp_password}.

    Vous pouvez vous connecter dès maintenant et modifier votre mot de passe dans votre espace personnel.

    Bien à vous,
    Mélanie Laborda
    """

    message = Message(
        subject=subject,
        body=body,
        sender=sender_email,
        recipients=[user_email]
    )

    send_mail_async(message)

def send_appointment_status_notification(user_email, **context):
    """Envoi un email à l'utilisateur lorsque le statut de son RDV change (Confirmé ou Annulé)"""
    sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')

    # Vérification des clés attendues
    required_keys = ["user_full_name", "prestation_name", "message", "status"]
    missing_keys = [key for key in required_keys if key not in context]

    if missing_keys:
        raise ValueError(f"Les clés suivantes sont manquantes dans le contexte: {', '.join(missing_keys)}")
    
    user_full_name = context['user_full_name']
    prestation_name = context['prestation_name']
    message = context['message']
    status = context['status']

    subject = ""
    body = ""

    if status == "CONFIRMED":
        subject = f"Confirmation de votre rendez-vous pour {prestation_name}"
        body = f"""
        Bonjour {user_full_name},

        J'ai le plaisir de vous confirmer votre rendez-vous pour la prestation: {prestation_name}.

        Rappel de votre message:
        {message}.

        Si nous avons convenu d'une date et d'une heure par téléphone ou par message, celles-ci sont désormais validées.

        En cas d'empêchement, merci de me prévenir au plus tôt.

        A bientôt, 
        Mélanie Laborda
        """
        
    elif status == "CANCELLED":
        subject = f"Votre rendez-vous pour {prestation_name} a été annulé"
        body = f"""
        Bonjour {user_full_name},

        Je vous informe que le rendez-vous pour la prestation: {prestation_name} a été annulé.

        Si vous n'êtes pas à l'origine de cette annulation, n'hésitez pas à me contacter pour en discuter ou pour replanifier une séance.

        Si vous avez des questions ou des préoccupations, n'hésitez pas à me contacter.

        Cordialement,
        Mélanie Laborda
        """

    else:
        # Si le statut est COMPLETED, on envoie rien
        return
    
    message = Message(
        subject=subject,
        body=body,
        sender=sender_email,
        recipients=[user_email]
    )

    send_mail_async(message)

def send_forgot_password_notification(user_email, temp_password):
    """Envoie un email à l'utilisateur avec un mot de passe temporaire suite à un oubli"""
    sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')
    subject = 'Réinitialisation de votre mot de passe'

    body = f"""
    Bonjour,

    Une demande de réinitialisation de mot de passe a été effectuée pour votre compte.

    Votre nouveau mot de passe temporaire est : {temp_password}

    Connectez vous dès que possible et modifiez ce mot de passe dans votre espace personnel.

    Si vous n'êtes pas à l'origine de cette demande, veuillez nous contacter immédiatement.

    Cordialement,
    Mélanie Laborda
    """

    message = Message(
        subject=subject,
        body=body,
        sender=sender_email,
        recipients=[user_email]
    )

    send_mail_async(message)
