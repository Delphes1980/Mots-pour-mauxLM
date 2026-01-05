from app import db, create_app
from app.models.prestation import Prestation
from app.models.user import User
from app import bcrypt


def seed_prestations_and_ghosts():
    """Insère les prestations si la table est vide"""
    app = create_app()
    with app.app_context():

        # Vérifie si le Ghost User existe déjà
        GHOST_EMAIL = 'deleted@system.local'
        if User.query.filter_by(email=GHOST_EMAIL).count() == 0:
            print('Création de Ghost user...')

            # Hashage du mot de passe
            ghost_hashed_password = bcrypt.generate_password_hash('ghost_password_123').decode('utf-8')

            ghost_user = User(
                first_name='Ghost',
                last_name='user',
                email=GHOST_EMAIL,
                password=ghost_hashed_password,
                is_admin=False,
            )

            db.session.add(ghost_user)
            db.session.commit()
            print('Ghost user créé')
        else:
            print('Ghost user existe déjà')

        # Vérifie si Ghost Prestation existe déjà
        GHOST_PRESTATION_NAME = 'Ghost prestation'
        if Prestation.query.filter_by(name=GHOST_PRESTATION_NAME).count() == 0:
            print('Création de Ghost prestation...')

            ghost_prestation = Prestation (
                name=GHOST_PRESTATION_NAME,
                )
            
            db.session.add(ghost_prestation)
            print('Ghost prestation créée')
        else:
            print('Ghost prestation existe déjà')

        # Vérifie si les prestations existent déjà
        if Prestation.query.filter(Prestation.name != GHOST_PRESTATION_NAME).count() <= 1:
            print("Insertion des prestations...")

            # Définition des prestations à insérer
            prestations_data = [
                {'name': 'Séance de psychothérapie'},
                {'name': 'Séance d\'hypnose classique'},
                {'name': 'Programme Anneau gastrique virtuel'},
                {'name': 'Séance d\'hypnose pour l\'arrêt du tabac'},
                {'name': 'Nettoyage et purification de lieux'},
                {'name': 'Séance pendule'},
                {'name': 'Guidance cartomancie'},
                {'name': 'Accès annales akashiques'},
                {'name': 'Séance acupressure'},
                {'name': 'Séance réflexologie palmaire/plantaire'},
                {'name': 'Séance massage ayurvédique'}
            ]

            for data in prestations_data:
                prestation = Prestation(**data)
                db.session.add(prestation)

            db.session.commit()
            print('Prestations insérées avec succès')
        else:
            print('Les prestations existent déjà dans la base de données')


if __name__ == '__main__':
    seed_prestations_and_ghosts()
