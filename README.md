# Mots-pour-mauxLM
```
app/
|__README.md
|__base_files/					# Frontend folder
|	|__images/
|	|	|__favicon/
|	|	|	|__android-chrome-192x192.png
|	|	|	|__androif-chrome-512x512.png
|	|	|	|__apple-touch-icon.png
|	|	|	|__favicon-16x16.png
|	|	|	|__favion-32x32.png
|	|	|	|__favicon.ico
|	|	|	|__site.webmanifest
|	|	|__Logo Clair.png
|	|	|__Phot Profil.jpg
|	|__static/
|	|	|__css_files/
|	|	|	|__accueil.css
|	|	|	|__avis.css
|	|	|	|__coordonnees_horaires.css
|	|	|	|__en_savoir_plus.css
|	|	|	|__formulaire_commentaires.css
|	|	|	|__formulaire_rdv.css
|	|	|	|__login.css
|	|	|	|__page_inscription.css
|	|	|	|__page_personnelle.css
|	|	|	|__prestations_tarifs.css
|	|	|	|__styles.css
|	|	|	|__techniques_therapeutiques.css
|	|	|__js_files/
|	|		|__avis.js
|	|		|__formulaire_commentaires.js
|	|		|__formulaire_rdv.js
|	|		|__login.js
|	|		|__page_personnelle.js
|	|__templates/
|	|	|__accueil.html
|	|	|__avis.html
|	|	|__base.html
|	|	|__coordonnees_horaires.html
|	|	|__en_savoir_plus.html
|	|	|__formulaire_commentaires.html
|	|	|__formulaire_avis.html
|	|	|__login.html
|	|	|__page_inscription.html
|	|	|__page_personnelle.html
|	|	|__prestations_tarifs.html
|	|	|__techniques_therapeutiques.html
|	|
|___app/					# Backend folder
	├── __init__.py
	├── api/                                
	|    ├── __init__.py
	│    ├── users.py
	│    ├── appointments.py
	│    ├── reviews.py
	|    |__ auth.py                 
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
	|   |__ test_appointment.py
	|   |__ test_relationships.py
	|   |__ test_reviews.py
	|	|__test_user_appointment_relationship.py
	|	|__test_user_review_relationship.py
	|   |__ test_user.py
	|__ __init__.py
	|── run.py                             
	├── config.py
	├── requirements.txt
	|__ create_tables.sql   
	|__utils.py               
```