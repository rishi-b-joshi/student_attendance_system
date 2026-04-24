# QR Code Generation & Student Attendance System

A comprehensive system for generating QR codes and managing student attendance records using Django.

## 📋 Project Overview

This project consists of two main components:
1. **QR Code Generator** - A utility to generate QR codes for student identification
2. **Student Attendance System** - A Django web application for tracking and managing student attendance

## 🏗️ Project Structure

```
QR_generation/
├── UI                               # UI
   ├── UI.py                         # UI (Streamlite)
├── requirement.txt                  # Project dependencies
└── student_attendance/              # Django project
    ├── manage.py                    # Django management script
    ├── db.sqlite3                   # SQLite database
    └── student_attendance/          # Main Django app configuration
        ├── settings.py              # Django settings
        ├── urls.py                  # URL routing
        ├── asgi.py                  # ASGI configuration
        ├── wsgi.py                  # WSGI configuration
        └── __init__.py
    └── attendance/                  # Attendance app
        ├── models.py                # Database models
        ├── views.py                 # View functions
        ├── urls.py                  # App URLs
        ├── admin.py                 # Django admin configuration
        ├── apps.py                  # App configuration
        └── migrations/              # Database migrations
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd QR_generation
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirement.txt
   ```

## 📦 Dependencies

- **qrcode[pil]** - QR code generation library with PIL support
- **django** - Web framework for the attendance system
- **djangorestframework** - REST API framework for Django

## 🔧 Features

### QR Code Generation
- Generate QR codes from student information (ID, Name)
- Encode student details into QR format
- Save QR codes as PNG images
- Support for batch generation of multiple student QR codes

### Student Attendance System
- Django-based web application for attendance management
- Student data models and management
- Admin panel for easy data administration
- RESTful API endpoints (via djangorestframework)

### Run Django Development Server
```bash
cd student_attendance
python manage.py runserver
```

The server will be available at `http://127.0.0.1:8000/`

### Perform Database Migrations

```bash
cd student_attendance
python manage.py migrate
```

## 📂 Database
The project uses SQLite (`db.sqlite3`) for data storage. All student attendance records and related data are stored here.

## 🛠️ Development

### Apply Changes to Models
After modifying models in `attendance/models.py`:

```bash
cd student_attendance
python manage.py makemigrations
python manage.py migrate
```

### Create Django Admin User

```bash
cd student_attendance
python manage.py createsuperuser
```

Then access the admin panel at `http://127.0.0.1:8000/admin/`


### RUN UI Server
```bash
cd UI
streamlit run .\UI.py
```
Then access the localhost of UI at `http://localhost:8501/`