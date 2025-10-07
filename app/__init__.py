from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail


db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config.from_object('app.config.DevelopmentConfig')

    # Initialization of extensions
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)


    # Initialize API
    api = Api(app, version='1.0', title='MotsPourMaux API', description='MotsPourMaux Application API', doc='/api/v1/')

    # Import models (to create the tables)
    from app.models import user, review, appointment, prestation

    # Import API namespaces
    from app.api.v1.users import api as users_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.appointments import api as appointments_ns
    from app.api.v1.prestations import api as prestations_ns
    from app.api.v1.authentication import api as authentication_ns

    # Register API namespaces
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(appointments_ns, path='/api/v1/appointments')
    api.add_namespace(prestations_ns, path='/api/v1/prestations')
    api.add_namespace(authentication_ns, path='/api/v1/auth')

    return app
