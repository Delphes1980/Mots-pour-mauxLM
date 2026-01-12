# Mots-pour-mauxLM

## Table of Contents
- [Introduction](#introduction)
- [Objectives](#objectives)
- [Features](#features)
- [Structure](#structure)
- [Tests](#tests-coverage)
- [Installation](#installation)
- [Admin](#admin-setup)
- [Data Management](#server-and-data-management-docker)
- [Usage](#usage)
- [Technologies](#technologies-used)
- [Author](#author)

---

### Introduction
This project aims to address a simple issue: the client, a **psychopractitioner**, needs a comprehensive website to improve her online visibility. It will enable online appointment booking and build customer loyalty (both current and future) through the implementation of a customer review and rating system. This will help build trust and increase the practitioner’s reputation.

This project is the **Minimum Viable Product (MVP)**, and there is still improvements to do, but it works as it is now.

---

### Objectives
The main objectives of this MVP include:
 - Developing an easy-to-use interface with a warm color scheme that inspires confidence and serenity in the customer.
 - The implementation of the full authentication service (account creation and login/ logout).
 - The user data management through their personal page with the ability to modify them.
 - The logic for appointment requests by email and notification to the user and the practitioner by sending a message to their email address.
 - The logic for submitting review, only if the user has an account and logged in, to ensure that the user has already had an appointment with the practitioner.
 - Ensuring secure and efficient data handling.

---

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

---

 ### Structure
 The application is built on a layered architecture:
 - **`app/api/`:** API controllers (versioned as v1).
 - **`app/services/`:** Business Logic.
 - **`app/models/`and `app/persistence/`:** Data and database layers.
 - **`app/static/`and `app/templates/`:** Presentation layer (front-end).
 - **`tests/`:** Complete tests coverage.

```
app/
|
| ---------------------- Couche de logique métier (Back-end)---------------------
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── appointments.py
│       ├── authentication.py
│       ├── prestations.py
│       ├── reviews.py
│       └── users.py
├── models/
│   ├── __init__.py
│   ├── appointment.py
│   ├── baseEntity.py
│   ├── prestation.py
│   ├── review.py
│   └── user.py
├── persistence/
│   ├── __init__.py
│   ├── AppointmentRepository.py
│   ├── BaseRepository.py
│   ├── PrestationRepository.py
│   ├── ReviewRepository.py
│   └── UserRepository.py
├── services/
│   ├── __init__.py
│   ├── AppointmentService.py
│   ├── AuthenticationService.py
│   ├── facade.py
│   ├── mail_service.py
│   ├── PrestationService.py
│   ├── ReviewService.py
│   └── UserService.py
|
| ------------------- Couche de présentation (Front-end) -------------------
├── static/
│   ├── css_files/
│   │   ├── accueil.css
│   │   ├── avis.css
│   │   ├── coordonnees_horaires.css
│   │   ├── en_savoir_plus.css
│   │   ├── formulaire_commentaires.css
│   │   ├── formulaire_rdv.css
│   │   ├── login.css
│   │   ├── page_inscription.css
│   │   ├── page_personnelle.css
│   │   ├── politique_confidentialite.css
│   │   ├── prestations_tarifs.css
│   │   ├── styles.css
│   │   └── techniques_therapeutiques.css
│   ├── images/
│   │   ├── favicon/
│   │   │   ├── android-chrome-192x192.png
│   │   │   ├── androif-chrome-512x512.png
│   │   │   ├── apple-touch-icon.png
│   │   │   ├── favicon-16x16.png
│   │   │   ├── favion-32x32.png
│   │   │   ├── favicon.ico
│   │   │   └── site.webmanifest
│   │   ├── Logo Clair.png
│   │   └── Phot Profil.jpg
│   └── js_files/
│       ├── avis.js
│       ├── carte.js
│       ├── formulaire_commentaires.js
│       ├── formulaire_rdv.js
│       ├── login.js
│       ├── page_inscription.js
│       ├── page_personnelle.js
├── templates/
│   ├── accueil.html
│   ├── avis.html
│   ├── base.html
│   ├── coordonnees_horaires.html
│   ├── en_savoir_plus.html
│   ├── formulaire_commentaires.html
│   ├── formulaire_rdv.html
│   ├── login.html
│   ├── page_inscription.html
│   ├── page_personnelle.html
│   ├── politique_confidentialite.html
│   ├── prestations_tarifs.html
│   └── techniques_therapeutiques.html
├── views/
│   └── static_pages.py
├── tests/
│   ├── __init__.py
│   ├── base_test.py
│   ├── api/
│   ├── database/
│   ├── models/
│   ├── repositories/
│   └── services/
├── __init__.py
├── config.py
├── requirements.txt
├── run.py
└── utils.py
```

---

### Tests Coverage
Tests were made with Unittest and Swagger. The end-to-end tests were organized by role to ensure a clear separation of responsibilities:
-**`tests/api/`:** Integration and unit tests for API endpoints (e.g., `POST/users`, `PATCH/reviews/{id}`).
-**`tests/services/`:** Unit validation of business rules and logic (e.g., password validation, appointment scheduling logic).
-**`tests/persistence/`:** Unit validation of CRUD operations and database access (Repository).
-**`tests/models/`:** Validation of relationships between entities (ORM).
-**`tests/database`:** Migration tests and final tests of the PostgreSQL structure.

To run the test, on your terminal, run:
```bash
python -m unittest app.tests.[the folder you want to test(services, repositories..)].[name of the test file without extension] -v
```

---

### Installation
#### Prerequisites
You must have **Git**, **Docker Compose** and **Docker Buildx** installed on your system.
This application does work with the 3.12.3 version of Python, I don't know if it works with other ulterior or more recent versions.

#### 1. Clone the repository
```bash
git clone https://github.com/Delphes1980/Mots-pour-mauxLM
```
```bash
cd Mots-pour-mauxLM
```

#### 2. Create Configuration file
Create a `.env` file at the root of the project (using `.env.model` as a template). You must fill in the **DB_USER, DB_PASSWORD**, and **all Mailjet keys** (**MAIL_USERNAME** for the public key and **MAIL_PASSWORD** for the private key) if you want to test the email functionality.
For Mailjet, you just have to create a free account, they will give you a public and a private key (**save this one somewhere, you can only have it once!**) that you put on your `.env` file. **⚠** Don't forget to put you `.env` in your `.gitignore`.**⚠**

#### 3. Launch the application (Containerization)
This command builds the necessary image, sets up the PostgreSQL databases (therapie_dev, therapie_test), creates all the tables, inserts the initial data (Prestations, Ghost user and Ghost prestation), and starts the web server.
```bash
docker-compose up --build -d
```
(**Note:** Use `docker compose` instead of `docker-compose` if your system supports the new syntax).

---

### Admin Setup
To fully test all API endpoints (e.g., retrieving all users/ reviews) and simulate administration roles, you must create a dedicated administrator account after the database has been initialized.
**1 - Ensure containers are running:** Verify that your `web` and `db` containers are active (`docker compose ps` must show **Up**).
**2 - Access the web container shell:** Open a new terminal session and execute a command to enter the running web container:
```	
docker-compose exec web bash
```
**3 - Create the admin account:** Inside the container shell, launch the Python interpreter and execute the commands to create the admin user (replace the password placeholder):
```bash
python3
```
then type:
```python
# Inside the Python interpreter
from app import db, create_app, bcrypt
from app.models.user import User

app = create_app()
app.app_context().push()

# IMPORTANT: Use a secure password here (1 uppercase letter, 1 digit, 1 special caracter, 8 caracters at least)
admin_password = 'YourSecureAdminPassword123+'

admin = User(
	first_name='Admin',
	last_name='Test',
	email='admin@test.com',
	password=bcrypt.generate_password_hash(admin_password).decode('utf-8'),
	is_admin=True
)

db.session.add(admin)
db.session.commit()

print('Admin user created successfully')
exit()
```
(Type `exit` again to leave the container shell).

**4. Access Admin API endpoints (Swagger):** Since there is no dedicated admin interface on the website yet, all administrative actions (retrieving all users, deleting content, etc.) must be performed through the API documentation:
 - Navigate to: `http://localhost:5000/api/v1/` (or the URL of your Swagger documentation).
 - Authenticate: Use the **Admin email** (`admin@test.com`) and the password defined above to log in and retrieve a JWT token (via the login endpoint).
 - Authorize: Use the token obtained to authorize requests in the Swagger interface (using the Bearer scheme).

---

### Server and Data Management (Docker)
Once the application is running, here are the essential commands:

**1. Stop the Application (Preserving Data)**
To stop the web server and the database container without deleting any data you have created (users, appointments, reviews):
```bash
docker-compose stop
```
**(Your data persists on your host machine)**

**2. Restart the Application**
To resume work from where you left off:
```bash
docker-compose start
```

**3. Permanently Delete ALL Data (For a Clean Reset)**
**_⚠ WARNING:_** This action deletes the PostgreSQL data volume and **all data** (users, reviews, initial seed data) permanently.
Use this command if you need to perform a clean, fresh install:
```bash
docker-compose down -v
```
(The `-v` flag deletes the data volume).

---

### Usage
Follow the link that you terminal will open or go to:
```
http://localhost:5000
```
You can now enjoy the web site and visit the different pages as a user do.
**_⚠ WARNING:_** If you want to try the email sending, when register a user, enter a valid email address.

---

### Technologies used
- Frontend: HTML5, CSS3, JavaScript ES6
- Backend: Python, Flask, Flask-RestX, Flask-JWT-Extended, Flask-Mail
- Database: PostgreSQL

---

### Author
[Delphine Coutouly-Laborda](https://github.com/Delphes1980)
