# Attendance Management System

This is a Django-based attendance management system.

## Project Structure

```
/Users/yammu/Desktop/AMS/
├───.gitignore
├───gemini.md
├───manage.py
├───requirements.txt
├───.git/...
├───ams/
│   ├───__init__.py
│   ├───asgi.py
│   ├───settings.py
│   ├───urls.py
│   ├───wsgi.py
│   └───__pycache__/
├───static/
│   ├───css/
│   │   └───style.css
│   └───images/
│       ├───bg1.jpeg
│       └───bg5.jpeg
├───student/
│   ├───__init__.py
│   ├───admin.py
│   ├───apps.py
│   ├───models.py
│   ├───tests.py
│   ├───urls.py
│   ├───views.py
│   ├───__pycache__/
│   ├───management/
│   │   └───commands/
│   │       ├───send_attendance_notifications.py
│   │       └───__pycache__/
│   ├───migrations/
│   │   ├───__init__.py
│   │   ├───0001_initial.py
│   │   └───__pycache__/
│   └───templates/
│       ├───base_anonymous.html
│       ├───base.html
│       └───student/
│           ├───login.html
│           ├───mark_attendance.html
│           ├───profile.html
│           ├───register.html
│           ├───scan_qr.html
│           └───student_dashboard.html
├───teacher/
│   ├───__init__.py
│   ├───admin.py
│   ├───apps.py
│   ├───models.py
│   ├───tests.py
│   ├───urls.py
│   ├───views.py
│   ├───__pycache__/
│   ├───migrations/
│   │   ├───__init__.py
│   │   ├───0001_initial.py
│   │   ├───0002_class_subject.py
│   │   └───__pycache__/
│   └───templates/
│       └───teacher/
│           ├───create_class.html
│           ├───create_course.html
│           ├───generate_qr.html
│           ├───profile.html
│           ├───register.html
│           ├───teacher_dashboard.html
│           ├───update_class.html
│           ├───update_course.html
│           └───view_report.html
└───venv/
    ├───bin/...
    ├───include/...
    └───lib/...
```

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    ```

2.  **Create a virtual environment and activate it:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the migrations:**

    ```bash
    python manage.py migrate
    ```

5.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

## Usage

-   The application will be available at `http://127.0.0.1:8000/`.
-   There are three roles: Admin, Teacher, and Student.
-   The admin interface is available at `http://127.0.0.1:8000/admin/`.

