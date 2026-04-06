# QR Code Generation & Student Attendance System

A comprehensive system for generating QR codes and managing student attendance records using Django.

## 📋 Project Overview

This project consists of two main components:
1. **QR Code Generator** - A utility to generate QR codes for student identification
2. **Student Attendance System** - A Django web application for tracking and managing student attendance

## 🏗️ Project Structure

```
QR_generation/
├── qr_generation.py                 # QR code generation utility
├── scan_demo.html                   # Demo HTML for QR scanning
├── requirement.txt                  # Project dependencies
├── text.txt                         # Supporting text file
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

## 📝 Usage

### Generate QR Codes

Run the QR code generator:
```bash
python qr_generation.py
```

This will generate QR code images for sample students (S001, S002, S003).

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

### Create Django Admin User

```bash
cd student_attendance
python manage.py createsuperuser
```

Then access the admin panel at `http://127.0.0.1:8000/admin/`

## 🎯 QR Code Generation Example

The `qr_generation.py` script demonstrates how to generate QR codes:

```python
from qr_generation import generate_qr_code

# Generate a QR code
qr_text = "ID: S001, Name: Alice Johnson"
generate_qr_code(qr_text, "student_qr.png")
```

## 🌐 Testing QR Codes

Open `scan_demo.html` in a web browser to test QR code scanning functionality.

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

### Access Django Shell

```bash
cd student_attendance
python manage.py shell
```

## 📖 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [QRCode Library](https://github.com/lincolnloop/python-qrcode)
- [Django REST Framework](https://www.django-rest-framework.org/)

## 📄 License

This project is provided as-is for educational and attendance management purposes.

---

**Created:** April 2026  
**Purpose:** Student Attendance Management & QR Code Generation
