# knowYourUniversity — Django Backend + Frontend

A **Django 5 + SQLite** monolithic college project that serves both the static
frontend AND the JSON API from a single server. Just start Django on port 8000
and you're done.

## Features

- **Auth**: Login, Signup, Logout — all wired to real Django sessions
- **Profile**: Edit name, phone, target country + upload profile picture
- **Change Password**: right on the dashboard, current-password verified
- **Shortlist & Compare** university lists (per user, saved in DB)
- **Consultant bookings** — create, list, cancel with server IDs
- **Custom staff Admin Dashboard** at `/dashboard/` — live stats, KPI cards, recent activity
- Standard Django admin at `/admin/` for CRUD

## Tech Stack
- Python 3.10+
- Django 5 · SQLite · Pillow · django-cors-headers

## Project Structure
```
backend_django/
├── manage.py
├── requirements.txt
├── kyu_project/                    # Django project (settings, urls)
└── main/                           # Django app
    ├── models.py                   # UserProfile · Shortlist · Compare · Booking
    ├── admin.py                    # Django admin config (filters, search)
    ├── forms.py · serializers.py · urls.py
    ├── templates/main/dashboard.html   # Custom staff dashboard
    ├── management/commands/seed_admin.py
    └── views/
        ├── admin_dashboard.py      # /dashboard/ landing page
        ├── auth_views.py           # signup/login/logout/me/change-password
        ├── profile_views.py        # /api/profile + avatar upload
        ├── shortlist_views.py · compare_views.py · booking_views.py
```

## Quick Start

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate            # macOS / Linux
# venv\Scripts\activate             # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the SQLite DB
python manage.py migrate

# 4. Seed the default admin user (admin / admin123)
python manage.py seed_admin

# 5. Start the backend (serves BOTH the frontend AND API on port 8000)
python manage.py runserver 0.0.0.0:8000
```

Now open **http://localhost:8000/** — Django will redirect to the home page.

### Key URLs
| URL | What it is |
|-----|-----------|
| http://localhost:8000/home.html      | Student-facing homepage |
| http://localhost:8000/login.html     | Login / Signup           |
| http://localhost:8000/dashboard.html | Student dashboard (edit profile, upload avatar, change password, cancel bookings) |
| http://localhost:8000/dashboard/     | **Staff admin dashboard** (`admin` / `admin123`) |
| http://localhost:8000/admin/         | Django admin CRUD |

## API Endpoints
Base URL: `http://localhost:8000/api`

| Method | Endpoint                | Description                          |
|--------|-------------------------|--------------------------------------|
| POST   | /auth/signup            | Register a new user                  |
| POST   | /auth/login             | Log in (session cookie)              |
| POST   | /auth/logout            | Log out                              |
| GET    | /auth/me                | Current logged-in user (or 401)      |
| POST   | /auth/change-password   | Change password (needs current + new)|
| GET    | /profile                | Get user profile                     |
| PATCH  | /profile                | Update name / phone / country        |
| POST   | /profile/avatar         | Upload profile picture (multipart)   |
| GET    | /shortlist              | List shortlisted university ids      |
| POST   | /shortlist/<uni_id>     | Toggle shortlist                     |
| GET    | /compare                | List compared university ids         |
| POST   | /compare/<uni_id>       | Toggle compare                       |
| GET    | /bookings               | List user's bookings                 |
| POST   | /bookings               | Create booking                       |
| DELETE | /bookings/<id>          | Cancel booking                       |

All endpoints return JSON. Authentication uses Django's session cookies.

## Custom Admin Dashboard (`/dashboard/`)

Shown only to staff. Includes:
- KPI cards: Total Users, Bookings, Shortlist, Compare, Profiles
- Weekly deltas (new users / new bookings this week)
- Booking status breakdown: Confirmed / Completed / Cancelled
- Recent Users & Recent Bookings tables
- Most Shortlisted Universities & Most Booked Consultants rankings
- Styled to match the dark + yellow frontend theme
- "View all" links jump to the Django admin for full CRUD

## Notes
- SQLite DB file `db.sqlite3` is created on `migrate`.
- Avatars land in `media/avatars/`.
- Change the default admin password in production:
  `python manage.py changepassword admin`
- Debug is on for dev — turn `DEBUG = False` and set `ALLOWED_HOSTS` for prod.
