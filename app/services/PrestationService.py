from app.persistence.PrestationRepository import PrestationRepository
from app.persistence.ReviewRepository import ReviewRepository
from app.models.prestation import Prestation
from app.utils import (validate_init_args, name_validation, validate_entity_id, CustomError)


class PrestationService:
    def __init__(self):
        self.prestation_repository = PrestationRepository()
        self.review_repository = ReviewRepository()

    def create_prestation(self, **kwargs):
        """Create a new prestation with the provided data

        Args:
            **kwargs: Prestation data (name)

        Returns:
            Prestation: Created Prestation

        Raises:
            CustomError: if the data are invalids(400), prestation exists(409)
        """
        # Valider que tous les champs requis sont présents
        validate_init_args(Prestation, **kwargs)

        # Valider les données
        name = kwargs.get('name')
        try:
            name_validation(name, 'name')
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        existing_prestation = self.prestation_repository.get_by_attribute("name", name)
        if existing_prestation:
            raise CustomError("La prestation existe déjà", 409)

        return self.prestation_repository.create_prestation(**kwargs)

    def get_prestation_by_id(self, prestation_id):
        """Get a prestation by its ID

        Args:
            prestation_id (str): The ID of the prestation to retrieve

        Returns:
            Prestation: The retrieved Prestation

        Raises:
            CustomError: if the ID is invalid(400) or if the prestation is not found(404)
        """
        try:
            prestation_id = validate_entity_id(prestation_id, 'prestation_id')
        except (ValueError, TypeError) as e:
            raise CustomError(str(e), 400) from e

        prestation = self.prestation_repository.get_by_id(prestation_id)
        if not prestation:
            raise CustomError("Prestation non trouvée", 404)

        return prestation

    def get_all_prestations(self):
        """Get all prestations for admin

        Returns:
            list: List of all prestations
        """
        return self.prestation_repository.get_all()

    def get_all_prestations_for_user(self):
        """Get all prestations for user
        
        Returns:
            list: List of all prestations
        """
        try:
            prestations = self.prestation_repository.get_all_prestations_for_user()
            return prestations

        except Exception as e:
            raise CustomError(str(e), 500) from e

    def get_prestation_by_name(self, name):
        """Get a prestation by its name

        Args:
            name (str): The name of the prestation to retrive

        Returns:
            Prestation: The retrieved Prestation

        Raises:
            CustomError: if the name is invalid(400) or if the prestation is not found(404)
        """
        if not name:
            raise CustomError("Le nom de la prestation est requis", 400)

        try:
            name_validation(name, 'name')
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        prestation = self.prestation_repository.get_by_attribute("name", name)
        if not prestation:
            raise CustomError("Prestation non trouvée", 404)

        return prestation

    def update_prestation(self, prestation_id, **kwargs):
        """Update a prestation by its ID
        
        Args:
            name_id (str): The ID of the prestation to update
            **kwargs: Prestation data to update (name)

        Returns:
            Prestation: The updated Prestation

        Raises:
            CustomError: if the ID is invalid(400), if the prestation is not found(404), if the prestation already exists(409)
        """
        try:
            prestation_id = validate_entity_id(prestation_id, 'prestation_id')
        except (ValueError, TypeError) as e:
            raise CustomError(str(e), 400) from e

        prestation = self.prestation_repository.get_by_id(prestation_id)
        if not prestation:
            raise CustomError("Prestation non trouvée", 404)

        if not kwargs:
            raise CustomError("Aucune donnée à mettre à jour", 400)

        if 'name' in kwargs:
            name = kwargs.get('name')
            try:
                name_validation(name, 'name')
            except ValueError as e:
                raise CustomError(str(e), 400) from e

            existing_prestation = self.prestation_repository.get_by_attribute("name", name)
            if existing_prestation and existing_prestation.id != prestation_id:
                raise CustomError("Prestation déjà existante", 409)

        return self.prestation_repository.update(prestation_id, **kwargs)

    def delete_prestation(self, prestation_id):
        """Delete a prestation by its ID

        Args:
            prestation_id (str): The ID of the prestation to delete

        Returns:
            bool: True if the prestation was deleted, False otherwise

        Raises:
            CustomError: if the ID is invalid(400) or if the prestation is not found(404)
        """
        try:
            prestation_id = validate_entity_id(prestation_id, 'prestation_id')
        except (ValueError, TypeError) as e:
            raise CustomError(str(e), 400) from e

        prestation = self.prestation_repository.get_by_id(prestation_id)
        if not prestation:
            raise CustomError("Prestation non trouvée", 404)

        if prestation.name.strip().lower() == 'ghost prestation':
            raise CustomError('Vous ne pouvez pas supprimer la prestation fantôme', 403)

        ghost_prestation = self.prestation_repository.get_by_attribute('name', 'Ghost prestation')
        if not ghost_prestation:
            raise CustomError('Prestation fantôme non trouvée', 404)

        # Vérifier si des avis existent pour cette prestation
        reviews = self.review_repository.get_by_prestation_id(prestation_id)
        if reviews:
            self.review_repository.reassign_reviews_from_prestation(prestation.id, ghost_prestation.id)

        return self.prestation_repository.delete(prestation_id)
