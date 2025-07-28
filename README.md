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

## 🚀 Getting Started

Follow these instructions to get a local development environment running.

### **Prerequisites**
*   Python >=3.10
*   PostgreSQL
*   Git

### **Installation**

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/AbdeljalilOuafi/DentiaPro.git
    cd DentiaPro
    ```

2.  **Set up the PostgreSQL Database:**
    *   Create a new database and a user with privileges for that database.

3.  **Create a virtual environment and install dependencies:**
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Create a `.env` file in the root directory.
    ```env
    SECRET_KEY='your-django-secret-key'
    DEBUG=True
    DATABASE_URL='postgres://USER:PASSWORD@HOST:PORT/DBNAME'
    CLOUDINARY_URL='cloudinary://API_KEY:API_SECRET@CLOUD_NAME'
    ```

5.  **Run database migrations:**
    ```sh
    python3 manage.py migrate_schemas --shared
    ```

6.  **Run the development server:**
    ```sh
    python3 manage.py runserver
    ```

The API should now be running at `http://127.0.0.1:8000`.