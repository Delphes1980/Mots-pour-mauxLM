import json
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.review import Review
from app.models.prestation import Prestation
from app import db
from app.tests.base_test import BaseTest
from app.services.facade import Facade
from app.api.v1.users import api as users_api
from app.api.v1.authentication import api as auth_api
from app.utils import CustomError

class TestUserApiDeletion(BaseTest):
    """Tests API suppression utilisateur avec réassignation des reviews"""

    def setUp(self):
        super().setUp()

        self.api = self.create_test_api('UserApiDeletion')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.client = self.app.test_client()
        self.facade = Facade()

        self.ghost_user = User(
            email='deleted@system.local',
            password='Ghost#2025!!',
            first_name='Ghost',
            last_name='User',
            is_admin=False
        )
        self.admin_user = User(
            email='admin@example.com',
            password='Admin1234567!',
            first_name='Admin',
            last_name='Root',
            is_admin=True
        )
        self.save_to_db(self.ghost_user, self.admin_user)

        self.prestation1 = Prestation(name='Massage relaxant')
        self.prestation2 = Prestation(name='Massage tonique')
        self.save_to_db(self.prestation1, self.prestation2)

    def login_as(self, email, password):
        credentials = {'email': email, 'password': password}
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_api_delete_user_with_reviews(self):
        user = User(email='jean.dupont@example.com', password='Password123!', first_name='Jean', last_name='Dupont')
        self.save_to_db(user)
        user_id = user.id

        user = self.facade.get_user_by_email('jean.dupont@example.com')
        prestation1 = self.facade.get_prestation_by_name('Massage relaxant')
        prestation2 = self.facade.get_prestation_by_name('Massage tonique')
        assert user and prestation1 and prestation2

        review1 = Review(text="Très bon service", rating=5, user=user, prestation=prestation1)
        review2 = Review(text="Accueil chaleureux", rating=4, user=user, prestation=prestation2)
        self.save_to_db(review1, review2)

        assert self.facade.get_user_by_email('deleted@system.local') is not None

        self.login_as('admin@example.com', 'Admin1234567!')
        response = self.client.delete(f"/users/{user_id}")
        print("DELETE with reviews:", response.status_code, response.json)

        assert response.status_code == 200
        assert response.json["message"] == "Utilisateur supprimé avec succès"

        self.db.session.expire_all()
        try:
            self.facade.get_user_by_id(user_id)
            assert False, "L'utilisateur devrait être supprimé"
        except CustomError as e:
            assert str(e) == "User not found"

        assert len(self.facade.get_review_by_user(self.ghost_user.id)) == 2

    def test_api_delete_user_without_reviews(self):
        user = User(email='claire.martin@example.com', password='Claire456789!', first_name='Claire', last_name='Martin')
        self.save_to_db(user)
        user_id = user.id

        user = self.facade.get_user_by_email('claire.martin@example.com')
        assert user is not None

        assert self.facade.get_user_by_email('deleted@system.local') is not None

        self.login_as('admin@example.com', 'Admin1234567!')
        response = self.client.delete(f"/users/{user_id}")
        print("DELETE without reviews:", response.status_code, response.json)

        assert response.status_code == 200
        assert response.json["message"] == "Utilisateur supprimé avec succès"

        self.db.session.expire_all()
        try:
            self.facade.get_user_by_id(user_id)
            assert False, "L'utilisateur devrait être supprimé"
        except CustomError as e:
            assert str(e) == "User not found"

        assert len(self.facade.get_review_by_user(self.ghost_user.id)) == 0

    def test_api_delete_user_as_non_admin_forbidden(self):
        regular_user = User(email='user@example.com', password='User12345678!', first_name='User', last_name='Test')
        target_user = User(email='target@example.com', password='Target123456!', first_name='Target', last_name='User')
        self.save_to_db(regular_user, target_user)
        target_user_id = target_user.id

        self.login_as('user@example.com', 'User12345678!')
        response = self.client.delete(f"/users/{target_user_id}")
        print("DELETE as non-admin:", response.status_code, response.json)

        assert response.status_code == 403
        assert response.json["error"] == "Vous n'avez pas les droits administrateur"

        self.db.session.expire_all()
        assert self.facade.get_user_by_id(target_user_id) is not None

    def test_api_delete_ghost_user_forbidden(self):
        ghost_user_id = self.ghost_user.id
        self.login_as('admin@example.com', 'Admin1234567!')
        response = self.client.delete(f"/users/{ghost_user_id}")
        print("DELETE ghost user:", response.status_code, response.json)

        assert response.status_code == 403
        assert response.json["error"] == "Vous ne pouvez pas supprimer l'utilisateur fantôme"

        self.db.session.expire_all()
        assert self.facade.get_user_by_id(ghost_user_id) is not None
