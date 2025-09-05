![](https://res.cloudinary.com/dqeyi8yx1/image/upload/v1753661484/DentiaPro_Thumbnail_duokt6.jpg)
A robust, secure, and high-performance REST API for the **Dentia Pro** web application, a multi-tenant SaaS platform for dental practice management.

## Project Objective

The back-end for Dentia Pro is engineered to manage core business logic, data persistence, user authentication & authorization, multi-tenancy, and integrations, ensuring a seamless and reliable experience for dental practitioners, assistants, and patients.

## Core Features

### 🔑 Authentication & Authorization
*   **Multi-Tenant Registration:** New clinic administrators can sign up, creating an account and a dedicated clinic subdomain.
*   **JWT-Based Authentication:** Secure user login with JWT access and refresh tokens.
*   **Session Management:** User logout, access token refresh, and efficient delivery of user details upon login to minimize API calls.
*   **Secure Workflows:** OTP-based email verification and a two-step password reset process.
*   **Role-Based Access Control (RBAC):** Fundamentally built on roles (Admin, Dentist, Secretary, Receptionist) to ensure users only access permitted data and functionality.

### 🏥 Clinic & Patient Management
*   **Patient Records:** Full CRUD operations for patient records, including demographic data, profile picture uploads, and primary dentist assignment.
*   **Appointment Scheduling:** Full CRUD for appointments, including linking patients to dentists, defining time slots, and adding notes.
*   **Advanced Filtering & Search:** Retrieve paginated lists of patients and appointments with powerful filtering (by date, dentist, etc.) and search capabilities.
*   **Calendar Availability:** An endpoint to determine available time slots for a dentist within a given date range for efficient booking.

### 🦷 Procedures & Dental Records
*   **Procedure Management:** Full CRUD for defining and managing procedure categories ("Diagnostic", "Restorative") and specific procedure types ("Composite Filling").
*   **Clinical Logging:** Record procedure instances for patients, linking them to appointments, teeth, surfaces, and the performing dentist.
*   **Intelligent Status Management:** Automatically handles procedure statuses (Planned, Completed, Cancelled, etc.) and associated pricing and completion dates.
*   **Universal Tooth Reference:** A comprehensive API for all 52 teeth (Permanent and Primary) with multiple numbering systems (Universal, FDI, Palmer) and localized names.

### 📦 Inventory & Staff Management
*   **Inventory Control:** Full CRUD for inventory categories and individual items, including quantity tracking, stock levels, and cost price.
*   **Staff Management:** Allows tenant administrators to create and manage accounts for clinic staff.

### 🤖 AI Integration
*   **AI Chat Foundation:** An initial endpoint to explore AI-powered chat functionalities, with plans to evolve into a comprehensive AI Agent for tasks like clinical decision support and patient communication.

## 🛠️ Tech Stack & Architecture

*   **Framework:** Django Rest Framework (DRF)
*   **Database:** PostgreSQL
*   **Multi-Tenancy:** `django-tenants` for fully segregated clinic data and subdomains.
*   **Authentication:** `djangorestframework-simplejwt` for JWT-based auth.
*   **Image Storage & Manipulation:** Cloudinary, Pillow
*   **Web Server:** Nginx
*   **WSGI HTTP Server:** Gunicorn
*   **Deployment & DevOps:** Configuration management, SSL/TLS with Certbot, logging, and process management with Systemd.

## 🚀 Getting Started (Local Development)

This project is fully containerized using Docker 🐳. All you need to get started is Docker and Docker Compose installed on your system.

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/AbdeljalilOuafi/DentiaPro.git
cd DentiaPro/
```

### 2️⃣ Set Up Your Environment Variables

The application uses an `.env` file to manage secrets and environment-specific configuration. I have provided a template to make this easy. 📝

First, copy the example file to create your own local configuration:

```bash
cp .env.example .env
```

Next, open the newly created `.env` file and fill in the required values, especially `POSTGRES_PASSWORD` and `DJANGO_SECRET_KEY`. 🔑

### 3️⃣ Build and Run the Application

With your `.env` file configured, you can build the images and launch all the services with a single command:

```bash
docker compose up --build
```

- **`--build`**: This flag tells Docker Compose to build the backend image based on the Dockerfile. You only need to use this the first time or when you change the Dockerfile or requirements.txt. 🔨
- **Detached mode**: To run the containers in the background (detached mode), add the `-d` flag: `docker compose up --build -d`. 🌙

### 4️⃣ You're All Set! ✅

Docker Compose will now start the PostgreSQL database and the Django backend server with Gunicorn.

**🌐 The API will be running and available at http://localhost:8000/**

You can view the logs in real-time in your terminal. To stop the application, press `Ctrl + C` or run `docker compose down` from another terminal. 🛑