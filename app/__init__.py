from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt



db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config.from_object('app.config.DevelopmentConfig')

    # Initialization of extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Initialize API
    api = Api(app, version='1.0', title='MotsPourMaux API', description='MotsPourMaux Application API', doc='/api/v1/')

    # Import models (to create the tables)
    from app.models import user, review, appointment

    # Register API namespaces
    api.add_namespace(users_ns, path='/api/users')
    api.add_namespace(reviews_ns, path='/api/reviews')
    api.add_namespace(appointments_ns, path='/api/appointments')
    api.add_namespace(auth_ns, path='/api/auth')

    return app
