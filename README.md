# Mots-pour-mauxLM
```
app/
|__README.md
|__base_files/					# Frontend folder
|	|__images/
|	|__static/
|	|	|__css_files/
|	|	|	|__login.css
|	|	|	|__formulaire_rdv.css
|	|	|	|__formulaire_commentaire.css
|	|	|	|__page_personnelle.css
|	|	|	|__page_inscription.css
|	|	|	|__styles.css
|	|	|__js_files/
|	|		|__accueil.js
|	|		|__login.js
|	|		|__formulaire_rdv.js
|	|		|__formulaire_commentaire.js
|	|		|__page_inscription.js
|	|		|__page_personnelle.js
|	|__templates/
|	|	|__base.html
|	|	|__accueil.html
|	|	|__avis.html
|	|	|__coordonnees_horaires.html
|	|	|__formulaire_rdv.html
|	|	|__formulaire_commentaire.html
|	|	|__login.html
|	|	|__page_inscription.html
|	|	|__page_personnelle.html
|	|	|__prestations_tarifs.html
|	|	|__techniques_therapeutiques.html
|	|
|___app/					# Backend folder
	├── __init__.py
	├── api/           
	│   ├── __init__.py
	│   ├── v1/                         
	│       ├── __init__.py
	│       ├── users.py
	│       ├── appointments.py
	│       ├── reviews.py
	|       |__ auth.py                 
	|       |__ apiResources.py         
	├── models/                         
	│   ├── __init__.py
	│   ├── user.py
	│   ├── appointment.py
	│   ├── review.py
	|   |__ basemodel.py
	├── services/                       
	│   ├── __init__.py
	│   ├── facade.py
	|   |__ AppointmentService.py
	|   |__ ReviewService.py
	|   |__ UserService.py
	├── persistence/                    
	|   ├── __init__.py
	|   ├── repository.py               
	|__ images/
	|   |__ ER Diagram.png              
	|   |__ ER Diagram_extra.png       
	|__ tests/                          
	|   |__ scripts/
	|   |   |__ populate_data.sh
	|   |   |__ tests_api.sh
	|   |__testSQL/
	|   |   |__ test_sql_crud.sql       
	|   |__ test_appointment.py
	|   |__ test_relationships.py
	|   |__ test_reviews.py
	|   |__ test_user.py
	|── run.py                             
	├── config.py
	├── requirements.txt
	|__ create_tables.sql                   
	├── README.md
```