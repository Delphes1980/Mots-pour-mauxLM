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
|	|	|__formulaire_rdv.html
|	|	|__login.html
|	|	|__page_inscription.html
|	|	|__page_personnelle.html
|	|	|__prestations_tarifs.html
|	|	|__techniques_therapeutiques.html
|	|
|___app/					# Backend folder
	├── __init__.py
	├── api/
	|	 |__v1/                                
	|	      ├── __init__.py
	|	      ├── appointments.py
	|	  	  |__ auth.py
	|	  	  |__ prestations.py
	|	      ├── reviews.py
	|	      |__ users.py                 
	├── models/                         
	│   ├── __init__.py
	│   ├── appointment.py
	|	|__ baseEntity.py
	│   ├── prestation.py
	|   |__ review.py
	|	|__ user.py
	├── persistence/                    
	|   ├── __init__.py
	|	|__ AppointmentRepository.py
	|	|__ BaseRepository.py
	|	|__ PrestationRepository.py
	|   ├── ReviewRepository.py  
	|	|__ UserRepository.py
	├── services/                       
	│   ├── __init__.py
	|   |__ AppointmentService.py
	|	|__ AuthenticationService.py
	│   ├── facade.py
	|	|__ mail_service.py
	|	|__ PrestationService.py
	|   |__ ReviewService.py
	|   |__ UserService.py
	|__ images/
	|   |__ ER Diagram.png              
	|   |__ ER Diagram_extra.png       
	|__ tests/  
	|	|__ __init__.py
	|	|__ base_test.py
	|	|__ database/
	|	|	|__ __init__.py
	|	|	|__ test_all_entities_relationships.py
	|	|	|__ test_final_postgresql.py
	|	|__ models/  
	|	|	|__ __init__.py
	|	|	|__ test_all_relationships.py                             
	|	|   |__ test_appointment.py
	|	|	|__ test_prestation_appointment_relationship.py
	|	|	|__ test_prestation_review_relationship.py
	|	|	|__ test_prestation.py
	|	|   |__ test_relationships.py
	|	|   |__ test_review.py
	|	|	|__ test_user_appointment_relationship.py
	|	| 	|__ test_user_review_relationship.py
	|	|   |__ test_user.py
	|	|__ repositories/
	|	|	|__ __init__.py
	|	|	|__ test_AppointmentRepository.py
	|	|	|__ test_PrestationRepository.py
	|	|	|__ test_ReviewRepository.py
	|	|	|__ test_UserRepository.py
	|	|__ services/
	|		|__ __init__.py
	|		|__ test_AppointmentService_integration.py
	|		|__ test_AppointmentService.py
	|		|__ test_AuthenticationService_integration.py
	|		|__ test_AuthenticationService.py
	|		|__ test_facade.py
	|		|__ test_mail_service.py
	|		|__ test_PrestationService_integration.py
	|		|__ test_PrestationService.py
	|		|__ test_ReviewService_integration.py
	|		|__ test_ReviewService.py
	|		|__ test_UserService_integration.py
	|		|__ test_UserService.py
	|__ __init__.py                            
	├── config.py
	├── requirements.txt
	|__ run.py
	|__utils.py               
```