# knowYourUniversity — College Project Bundle

Full-stack student-college-project:
- Static frontend (HTML / CSS / Vanilla JS / Bootstrap 5) in `frontend/`
- Python **Django + SQLite** backend in `backend_django/` that ALSO serves the frontend

Because Django serves both the frontend and the API on the same origin (port 8000),
you only need ONE terminal to run the whole app — no CORS, no session-cookie headaches.

## Quick Start (Just Django — recommended)

```bash
cd backend_django
python -m venv venv && source venv/bin/activate   # (or venv\Scripts\activate on Windows)
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_admin                       # creates admin / admin123
python manage.py runserver 0.0.0.0:8000
```

Then open:
- **http://localhost:8000/**              — student home
- **http://localhost:8000/login.html**    — Signup / Login
- **http://localhost:8000/dashboard.html**— Student dashboard (edit profile, avatar, change password)
- **http://localhost:8000/dashboard/**    — Staff admin dashboard (`admin` / `admin123`)
- **http://localhost:8000/admin/**        — Django admin (CRUD)

Read `backend_django/README.md` for the full API reference.
