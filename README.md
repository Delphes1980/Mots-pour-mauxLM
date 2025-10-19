# Mots-pour-mauxLM
```
app/
|__README.md
|__base_files/					# Frontend folder
|	|__images/
|	|	|__favicon/
|	|	|	|__ android-chrome-192x192.png
|	|	|	|__ androif-chrome-512x512.png
|	|	|	|__ apple-touch-icon.png
|	|	|	|__ favicon-16x16.png
|	|	|	|__ favion-32x32.png
|	|	|	|__ favicon.ico
|	|	|	|__ site.webmanifest
|	|	|__ Logo Clair.png
|	|	|__ Phot Profil.jpg
|	|__static/
|	|	|__css_files/
|	|	|	|__ accueil.css
|	|	|	|__ avis.css
|	|	|	|__ coordonnees_horaires.css
|	|	|	|__ en_savoir_plus.css
|	|	|	|__ formulaire_commentaires.css
|	|	|	|__ formulaire_rdv.css
|	|	|	|__ login.css
|	|	|	|__ page_inscription.css
|	|	|	|__ page_personnelle.css
|	|	|	|__ prestations_tarifs.css
|	|	|	|__ styles.css
|	|	|	|__ techniques_therapeutiques.css
|	|	|__js_files/
|	|		|__ avis.js
|	|		|__ formulaire_commentaires.js
|	|		|__ formulaire_rdv.js
|	|		|__ login.js
|	|		|__ page_inscription.js
|	|		|__ page_personnelle.js
|	|__templates/
|	|	|__ accueil.html
|	|	|__ avis.html
|	|	|__ base.html
|	|	|__ coordonnees_horaires.html
|	|	|__ en_savoir_plus.html
|	|	|__ formulaire_commentaires.html
|	|	|__ formulaire_rdv.html
|	|	|__ login.html
|	|	|__ page_inscription.html
|	|	|__ page_personnelle.html
|	|	|__ prestations_tarifs.html
|	|	|__ techniques_therapeutiques.html
|	|
|___app/					# Backend folder
	├── __init__.py
	├── api/
	|	 |__v1/                                
	|	      ├── __init__.py
	|	      ├── appointments.py
	|	  	  |__ authentication.py
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
	|	|__ api/
	|	|	|__ __init__.py
	|	|	|__ test_appointments_api.py
	|	|	|__ test_appointments_integration.py
	|	|	|__ test_appointments_security.py
	|	|	|__ test_appointments_unit.py
	|	|	|__ test_authentication_api.py
	|	|	|__ test_prestations_api.py
	|	|	|__ test_prestations_integration.py
	|	|	|__ test_prestations_security.py
	|	|	|__ test_prestations_unit.py
	|	|	|__ test_reviews_api.py
	|	|	|__ test_reviews_integration.py
	|	|	|__ test_reviews_security.py
	|	|	|__ test_reviews_unit.py
	|	|	|__ test_user_api_deletion.py
	|	|	|__ test_users_api.py
	|	|	|__ test_users_integration.py
	|	|	|__ test_users_security.py
	|	|	|__ test_users_unit.py
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
	|		|__ test_AuthenticationService_admin_reset.py
	|		|__ test_AuthenticationService_integration.py
	|		|__ test_AuthenticationService_jwt.py
	|		|__ test_AuthenticationService.py
	|		|__ test_facade.py
	|		|__ test_mail_service.py
	|		|__ test_PrestationService_integration.py
	|		|__ test_PrestationService.py
	|		|__ test_reassignation_integration.py
	|		|__ test_ReviewService_integration.py
	|		|__ test_ReviewService.py
	|		|__ test_UserService_admin_validation.py
	|		|__ test_UserService_integration.py
	|		|__ test_UserService.py
	|		|__ test_utils_password_validation.py
	|__ __init__.py                            
	├── config.py
	├── requirements.txt
	|__ run.py
	|__utils.py               
```

Lancer l'appli:
PYTHONPATH=. python app/run.py