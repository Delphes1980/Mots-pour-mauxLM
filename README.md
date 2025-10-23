# Mots-pour-mauxLM

## Table of Contents
- [Introduction](#introduction)
- [Objectives](#objectives)
- [Features](#features)
- [Structure](#structure)
- [Tests](#tests-coverage)
- [Installation](#installation)
- [Technologies](#technologies-used)
- [Author](#author)


### Introduction
This project aims to address a simple issue: the client, a psychopratitioner, needs a comprehensive website to improve her online visibility. It will enable online appointment booking and build customer loyalty (both current and future) through the implementation of a customer review and rating system. This will help build trust and increase the practitioner’s reputation.

This project is the Minimum Viable Product (MVP), and there is still improvements to do, but it work as it is now.

### Objectives
The main objectives of this MVP include:
 - Developing an easy-to-use interface with a warm color scheme that inspires confidence and serenity in the customer.
 - The implementation of the full authentication service (account creation and login/ logout).
 - The user data management through their personal page with the ability to modify them.
 - The logic for appointment requests by email and notification to the user and the practitioner by sending a message to their email address.
 - The logic for submitting review, only if the user has an account and loged in, to ensure that the user has already had an appointment with the practitioner.
 - Ensuring secure and efficient data handling.

 ### Features
This MVP provides the folowing key functionalities to the user:
- **Authentication & User Management:**
	- Secure account creation and authentication using **JWT via HTTP-only Cookies**.
	- User access to a personal space (`/mon-espace`) to view and **edit personal information** (Name, Address, Phone).
	- Session management ensuring automatic redirection to the login page when authentication is lost.

- **Client Reviews & Ratings:**
	- **Public Display of Reviews:** View client feedback and star ratings on a dedicated page (`/avis`).
	- **Authenticated Submission:** Users must be logged in to submit a review for a type of prestation, ensuring comments are tied to an actual client account.
	- **Dynamic Editing:** Users can **modify their submitted review text and rating** directly from their personal space, with immediate update of the review list upon saving.

- **Appointment Scheduling & Communication:**
	- **Secure Request Form:** Submit a request for an appointment specifying the desired service and providing availabilities.
	- **Email Notification System:** Automated sending of an appointment request summary to the practitioner and a confirmation to the user's registered email address.

- **Website Content:**
	- Comprehensive sections detailing the practitioner's therapeutic techniques (TCC, PNL, DTMA, EFT), professional approach, and service fees/conditions.
	- **RGPD Compliance:** Integration of a full **Privacy Policy** and use of **Leaflet/OpenStreetMap** for location display to avoid third-party tracking cookies.

 ### Structure
 The application is built on a layered architecture:
 - **`app/api/`:** API controllers (versioned as v1).
 - **`app/services/`:** Business Logic.
 - **`app/models/`and `app/persistence/`:** Data and database layers.
 - **`app/static/`and `app/templates/`:** Presentation layer (front-end).
 - **`tests/`:** Complete tests coverage.

```
app/
| #---------------------- Couche de logique métier (Back-end)---------------------
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
| #------------------- Couche de présentation (Front-end) -------------------
|__ static/
|	|__ css_files/
|	|	|__ accueil.css
|	|	|__ avis.css
|	|	|__ coordonnees_horaires.css
|	|	|__ en_savoir_plus.css
|	|	|__ formulaire_commentaires.css
|	|	|__ formulaire_rdv.css
|	|	|__ login.css
|	|	|__ page_inscription.css
|	|	|__ page_personnelle.css
|	|	|__ politique_confidentialite.css
|	|	|__ prestations_tarifs.css
|	|	|__ styles.css
|	|	|__ techniques_therapeutiques.css
|	|__ images/
|	|	|__ favicon/
|	|	|	|__ android-chrome-192x192.png
|	|	|	|__ androif-chrome-512x512.png
|	|	|	|__ apple-touch-icon.png
|	|	|	|__ favicon-16x16.png
|	|	|	|__ favion-32x32.png
|	|	|	|__ favicon.ico
|	|	|	|__ site.webmanifest
|	|	|__ Logo Clair.png
|	|	|__ Phot Profil.jpg
|	|__ js_files/
|		|__ avis.js
|		|__ carte.js
|		|__ formulaire_commentaires.js
|		|__ formulaire_rdv.js
|		|__ login.js
|		|__ page_inscription.js
|		|__ page_personnelle.js
|__ templates/
|	|__ accueil.html
|	|__ avis.html
|	|__ base.html
|	|__ coordonnees_horaires.html
|	|__ en_savoir_plus.html
|	|__ formulaire_commentaires.html
|	|__ formulaire_rdv.html
|	|__ login.html
|	|__ page_inscription.html
|	|__ page_personnelle.html
|	|__ politique_confidentialite.html
|	|__ prestations_tarifs.html
|	|__ techniques_therapeutiques.html
|__ views
|	|__ static_pages.py    
|__ tests/  
|	|__ __init__.py
|	|__ base_test.py
|	|__ api/
|	|__ database/
|	|__ models/  
|	|__ repositories/
|	|__ services/ 
|__ __init__.py                            
├── config.py
├── requirements.txt
|__ run.py
|__ utils.py
|__ README.md               
```

### Tests Coverage
Tests were made with Unittest and Swagger. The end-to-end tests were organized by role to ensure a clear separation of responsibilities:
-**`tests/api/`:** Integration and unit tests for API endpoints (e.g., `POST/users`, `PATCH/reviews/{id}`).
-**`tests/services/`:** Unit validation of business rules and logic (e.g., password validation, appointment scheduling logic).
-**`tests/persistence/`:** Unit validation of CRUD operations and database access (Repository).
-**`tests/models/`:** Validation of relationships between entities (ORM).
-**`tests/database`:** Migration tests and final tests of the PostgreSQL structure.

### Installation
#### 0. Install Python 3.12.3
This application does work with this version of Python, I don't know if it works with other ulterior or more recent versions.

#### 1. Clone the repository
```
git clone https://github.com/Delphes1980/Mots-pour-mauxLM
```
```
cd Mots-pour-mauxLM
```

#### 2. Create and activate a virtual environment
From the Mots-pour-mauxLM root, tape this command:
```
python3 -m venv venv
```
then
```
source venv/bin/activate
```

#### 3. Install dependencies
```
pip install -r requirements.txt
```

#### 4. Application utilization
From the Mots-pour-mauxLM root, run:
```
PYTHONPATH=. python app/run.py
```

#### 5. Usage
Follow the link that you terminal will open or go to:
```
http://127.0.0.1:5000
```
You can now enjoy the web site and visit the different pages as a user do.

### Technologies used
- Frontend: HTML5, CSS3, JavaScript ES6
- Backend: Python, Flask, Flask-RestX, Flask-JWT-Extended, Flask-Mail
- Database: PostgreSQL

### Author
[Delphine Coutouly-Laborda](https://github.com/Delphes1980)