from sqlalchemy.exc import SQLAlchemyError

class BaseRepository:
    def __init__(self, model_class):
        self.model_class = model_class
        from app import db
        self.db = db

    def create(self, **kwargs):
        """Créer une nouvelle entité"""
        try:
            entity = self.model_class(**kwargs)
            self.db.session.add(entity)
            self.db.session.commit()
            return entity
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e

    def get_by_id(self, entity_id):
        """Récupérer une entité par ID"""
        return self.db.session.query(self.model_class).get(entity_id)

    def get_by_attribute(self, attr_name, attr_value):
        """Récupérer une entité par attribut spécifique"""
        return self.db.session.query(self.model_class).filter_by(**{attr_name: attr_value}).first()

    def get_all(self):
        """Récupérer toutes les entités"""
        return self.db.session.query(self.model_class).all()

    def update(self, entity_id, **kwargs):
        """Mettre à jour une entité"""
        try:
            entity = self.get_by_id(entity_id)
            if entity:
                for key, value in kwargs.items():
                    setattr(entity, key, value)
                self.db.session.commit()
                return entity
            return None
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e

    def delete(self, entity_id):
        """Supprimer une entité"""
        try:
            entity = self.get_by_id(entity_id)
            if entity:
                self.db.session.delete(entity)
                self.db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e

