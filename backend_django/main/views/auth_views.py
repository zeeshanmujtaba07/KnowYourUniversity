"""Authentication endpoints: signup, login, logout, me, change password."""
import json
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..forms import SignupForm, LoginForm
from ..models import UserProfile
from ..serializers import user_to_dict


@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    """Create a new user + profile and log them in."""
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    form = SignupForm(data)
    if not form.is_valid():
        return JsonResponse({"error": "Validation failed", "details": form.errors}, status=400)

    email = form.cleaned_data["email"].lower()
    user = User.objects.create_user(
        username=email,
        email=email,
        password=form.cleaned_data["password"],
        first_name=form.cleaned_data["first_name"],
        last_name=form.cleaned_data.get("last_name") or "",
    )
    UserProfile.objects.create(user=user)
    login(request, user)
    return JsonResponse({"user": user_to_dict(user, request)}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """Log in with email + password."""
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    form = LoginForm(data)
    if not form.is_valid():
        return JsonResponse({"error": "Validation failed", "details": form.errors}, status=400)

    email = form.cleaned_data["email"].lower()
    user = authenticate(request, username=email, password=form.cleaned_data["password"])
    if user is None:
        return JsonResponse({"error": "Invalid email or password"}, status=401)

    login(request, user)
    UserProfile.objects.get_or_create(user=user)
    return JsonResponse({"user": user_to_dict(user, request)})


@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    """End the user's session."""
    logout(request)
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def me(request):
    """Return the currently logged-in user, or 401."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    return JsonResponse({"user": user_to_dict(request.user, request)})


@csrf_exempt
@require_http_methods(["POST"])
def change_password(request):
    """Change the current user's password. Requires current_password + new_password."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    current = data.get("current_password") or ""
    new = data.get("new_password") or ""

    if not request.user.check_password(current):
        return JsonResponse({"error": "Current password is incorrect"}, status=400)
    if len(new) < 6:
        return JsonResponse({"error": "New password must be at least 6 characters"}, status=400)
    if new == current:
        return JsonResponse({"error": "New password must be different from current password"}, status=400)

    request.user.set_password(new)
    request.user.save()
    # Keep the user logged in after password change
    update_session_auth_hash(request, request.user)
    return JsonResponse({"ok": True, "message": "Password changed successfully"})
