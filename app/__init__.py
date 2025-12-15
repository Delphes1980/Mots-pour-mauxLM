import smtplib
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_jwt_extended import JWTManager


class PatchedSMTP(smtplib.SMTP):
    def __init__(self, *args, **kwargs):
        # Force le nom d'hôte utilisé dans le EHLO
        kwargs['local_hostname'] = "localhost.localdomain"
        super().__init__(*args, **kwargs)


db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
mail.smtp_cls = PatchedSMTP
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config.from_object('app.config.DevelopmentConfig')
    frontend_url = app.config['FRONTEND_URL']

    # Initialization of extensions
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)

    CORS(
        app,
        origins=[frontend_url],
        supports_credentials=True,  # Autorise l'envoi/réception de cookies
        allow_headers=['Content-Type'],  # Headers que le front est autorisé à envoyer
        methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
        )

    # Initialize API
    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': (
                'JWT Authorization header using the Bearer scheme.\n'
                'Enter your JWT token as: Bearer <your_token>\n\n'
                'Example: Bearer eyJhbGciOiJIUzI1NiIsInR5...'
            )
        }
    }

    api = Api(
        app,
        version='1.0',
        title='MotsPourMaux API',
        description='MotsPourMaux Application API',
        doc='/api/v1/',
        authorizations=authorizations,
        security='Bearer',
        prefix='/api'
        )

    # Import API namespaces
    from app.api.v1.users import api as users_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.appointments import api as appointments_ns
    from app.api.v1.prestations import api as prestations_ns
    from app.api.v1.authentication import api as authentication_ns

    # Register API namespaces
    api.add_namespace(users_ns, path='/v1/users')
    api.add_namespace(reviews_ns, path='/v1/reviews')
    api.add_namespace(appointments_ns, path='/v1/appointments')
    api.add_namespace(prestations_ns, path='/v1/prestations')
    api.add_namespace(authentication_ns, path='/v1/authentication')

    # Import of HTML routes
    from app.views.static_pages import static_bp

    app.register_blueprint(static_bp)


    return app
