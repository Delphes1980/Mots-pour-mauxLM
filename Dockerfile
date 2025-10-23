FROM python:3.12-slim
# Définie le répertoire de travail dans le conteneur
WORKDIR /app

# Pour les dépendances PostgreSQL
RUN apt-get update && apt-get install -y gcc libpq-dev postgresql-client\
	&& rm -rf /var/lib/apt/lists/*

# Copie le fichier des dépendances Python
COPY app/requirements.txt .

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie le script d'entrée (entrypoint.sh)
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Rend le script exécutable
RUN chmod +x /usr/local/bin/entrypoint.sh

# Copie le reste du code source
COPY . .

# Définition de l'environnement Flask
ENV FLASK_APP=app.run
ENV FLASK_ENV=development
EXPOSE 5000

# Création des tables et lancement du serveur Gunicorn
CMD ["/usr/local/bin/entrypoint.sh"]