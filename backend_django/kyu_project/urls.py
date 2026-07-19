"""URL configuration for kyu_project."""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from main.views.admin_dashboard import admin_dashboard

urlpatterns = [
    # Custom staff-only admin dashboard
    path("dashboard/", admin_dashboard, name="admin_dashboard"),

    # Django built-in admin (CRUD)
    path("admin/", admin.site.urls),

    # Public JSON API for the frontend
    path("api/", include("main.urls")),

    # ---- Frontend (served from the same origin so session cookies just work) ----
    # Root → home.html
    path("", lambda r: redirect("/home.html")),
    # Serve any .html file from ../frontend/
    re_path(r"^(?P<path>[^/]+\.html)$", serve, {"document_root": settings.FRONTEND_DIR}),
    # Serve /assets/... (css, js, images) from ../frontend/assets/
    re_path(r"^assets/(?P<path>.*)$", serve, {"document_root": settings.FRONTEND_DIR / "assets"}),
]

# Serve media files during local dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
