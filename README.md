<<<<<<< HEAD
# QR Code Attendance System

A lightweight attendance tracking system using QR codes. This application allows users to generate and scan QR codes for attendance tracking, suitable for schools, workplaces, and events.

## Features

- User registration and authentication
- QR code generation for events/sessions
- QR code scanning for attendance marking
- Offline functionality with sync capability
- Lightweight SQLite database
- Responsive web interface

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

4. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Project Structure

- `app/` - Main application package
  - `models/` - Database models
  - `routes/` - Application routes
  - `static/` - Static files (CSS, JS, images)
  - `templates/` - HTML templates
- `instance/` - Instance-specific files (database)
- `migrations/` - Database migrations
- `config.py` - Configuration settings
=======
# QR Code Attendance System

A lightweight attendance tracking system using QR codes. This application allows users to generate and scan QR codes for attendance tracking, suitable for schools, workplaces, and events.

## Features

- User registration and authentication
- QR code generation for events/sessions
- QR code scanning for attendance marking
- Offline functionality with sync capability
- Lightweight SQLite database
- Responsive web interface

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

4. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Project Structure

- `app/` - Main application package
  - `models/` - Database models
  - `routes/` - Application routes
  - `static/` - Static files (CSS, JS, images)
  - `templates/` - HTML templates
- `instance/` - Instance-specific files (database)
- `migrations/` - Database migrations
- `config.py` - Configuration settings
>>>>>>> 5ce8070 (Update app initialization for Gunicorn deployment)
- `run.py` - Application entry point 