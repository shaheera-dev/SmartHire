# SmartHire – Job Application & Placement Management System

**A Python Full Stack Web Application**

🌐 **Live Website:** https://smarthire-afwx.onrender.com/

💻 **GitHub Repository:** https://github.com/shaheera-dev/SmartHire

## Project Overview

SmartHire is a web-based Job Application and Placement Management System developed using Python Flask. It helps users organize their job applications, track interview schedules, manage profiles, and monitor application progress through a centralized dashboard.

## Features

- **User Authentication:** User registration, login and logout with secure password hashing.
- **Dashboard:** View application statistics and recent job applications.
- **Application Management:** Add, view, edit and delete job applications.
- **Interview Tracker:** Schedule, update and manage interview details.
- **Profile Management:** Update username, email and password.
- **Settings:** Manage application preferences.
- **Notifications:** View notifications, mark them as read and delete them.
- **Search and Filter:** Find applications easily.
- **Multi-user Support:** Keep each user's application data separate.
- **Responsive Interface:** User-friendly layout for different screen sizes.

## Technologies Used

| Category | Technologies |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| Local Database | SQLite |
| Cloud Database | Neon PostgreSQL |
| Database Connector | Psycopg |
| Deployment | Render |
| Version Control | GitHub |

## Application Screens

- Login and Registration
- Dashboard
- Job Applications
- Interview Tracker
- Profile Management
- Settings
- Notifications

## Database Architecture

SmartHire supports two database environments:

- SQLite for local development.
- Neon PostgreSQL for the deployed application.

This allows local development and online deployment to use separate databases.

## Run Locally

1. Clone the repository:

   `git clone https://github.com/shaheera-dev/SmartHire.git`

2. Open the project folder:

   `cd SmartHire`

3. Install dependencies:

   `pip install -r requirements.txt`

4. Configure your local environment variables in `.env`:

   `USE_SQLITE=1`

5. Start the application:

   `python app.py`

6. Open your browser:

   `http://127.0.0.1:5000/`

## Live Deployment

SmartHire is deployed using Render, with Neon PostgreSQL as its cloud database.

**Live Website:** https://smarthire-afwx.onrender.com/

## Developer

**GitHub:** https://github.com/shaheera-dev

---

*Developed as a Python Full Stack Development project.*
