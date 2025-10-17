import unittest
import uuid
from app.tests.base_test import BaseTest
# Assurez-vous que ces imports correspondent à votre structure de projet
from app.models.user import User
from app.models.review import Review
from app.models.prestation import Prestation
# Importez votre classe de Repository pour les avis
from app.persistence.ReviewRepository import ReviewRepository 


class TestReviewRepository(BaseTest):
    """Tests d'intégration spécifiques aux fonctionnalités du ReviewRepository."""

    def setUp(self):
        super().setUp()
        # Initialisation du Repository
        self.repository = ReviewRepository() 
        
        # --- Données de test spécifiques à la réassignation ---
        # Utilisateur à SUPPRIMER (l'ancien propriétaire des avis)
        self.old_user_id = str(uuid.uuid4())
        self.old_user = User(
            first_name="UserOld",
            last_name="ToDelete",
            email=f"old_{self.old_user_id[:8]}@test.com",
            password="Password123!",
            is_admin=False
        )
        
        # Utilisateur DESTINATAIRE (le nouveau propriétaire des avis)
        self.new_user_id = str(uuid.uuid4())
        self.new_user = User(
            first_name="UserNew",
            last_name="ToKeep",
            email=f"new_{self.new_user_id[:8]}@test.com",
            password="Password123!",
            is_admin=False
        )

        # Création de deux prestations distinctes
        self.prestation1 = Prestation(name="Massage relaxant")
        self.prestation2 = Prestation(name="Massage tonique")

        self.save_to_db(self.old_user, self.new_user, self.prestation1, self.prestation2)

        # Création d'avis pour l'utilisateur à supprimer
        self.review1 = Review(
            rating=5,
            text='Avis 1',
            user=self.old_user,
            prestation=self.prestation1

        )
        self.review2 = Review(
            rating=4,
            text='Avis 2',
            user=self.old_user,
            prestation=self.prestation2
        )

        self.save_to_db(self.review1, self.review2)

        # Vérification initiale de l'état
        self.assertEqual(len(self.repository.get_by_user_id(self.old_user.id)), 2, "Pré-condition: L'ancien utilisateur doit avoir 2 avis.")
        self.assertEqual(len(self.repository.get_by_user_id(self.new_user.id)), 0, "Pré-condition: Le nouvel utilisateur doit avoir 0 avis.")


    def test_reassign_reviews_from_user_success(self):
        """
        [TEST CRITIQUE] Teste la réassignation d'avis d'un utilisateur à un autre.
        Ceci vérifie que l'écriture sur l'attribut ORM fonctionne et que le commit est effectif.
        """
        count = self.repository.reassign_reviews_from_user(
            self.old_user.id,
            self.new_user.id
        )

        self.assertEqual(count, 2)

        # Vérifie que l'ancien utilisateur n'a plus d'avis
        reviews_old = self.repository.get_by_user_id(self.old_user.id)
        self.assertEqual(len(reviews_old), 0)

        # Vérifie que le nouvel utilisateur a bien récupéré les avis
        reviews_new = self.repository.get_by_user_id(self.new_user.id)
        self.assertEqual(len(reviews_new), 2)

        # Vérifie que les objets en mémoire ont été mis à jour
        self.assertEqual(self.review1.user_id, self.new_user.id)
        self.assertEqual(self.review2.user_id, self.new_user.id)

    def test_reassign_reviews_no_reviews(self):
        """Teste quand l'utilisateur à supprimer n'a pas d'avis."""
        
        # Créer un troisième utilisateur sans avis
        empty_user_id = str(uuid.uuid4())
        empty_user = User(
            first_name="Empty",
            last_name="User",
            email=f"empty_{empty_user_id[:8]}@test.com",
            password="Password123!"
        )
        self.save_to_db(empty_user)
        
        # Exécution de la méthode
        count = self.repository.reassign_reviews_from_user(
            empty_user.id, 
            self.new_user.id
        )
        
        # Assertion: Doit retourner 0 et ne pas impacter les autres données.
        self.assertEqual(count, 0, "Doit retourner 0 car aucun avis n'a été trouvé.")
        
        # S'assurer que les autres avis n'ont pas bougé (vérification de non-régression)
        self.assertEqual(len(self.repository.get_by_user_id(self.old_user.id)), 2)
        self.assertEqual(len(self.repository.get_by_user_id(self.new_user.id)), 0)

if __name__ == '__main__':
    unittest.main()
