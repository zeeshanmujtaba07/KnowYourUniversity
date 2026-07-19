"""Profile endpoints: get, update, upload avatar."""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..forms import ProfileUpdateForm
from ..models import UserProfile
from ..serializers import user_to_dict


@csrf_exempt
@require_http_methods(["GET", "PATCH"])
def profile_detail(request):
    """GET current profile or PATCH name/phone/country."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "GET":
        return JsonResponse({"user": user_to_dict(request.user, request)})

    # PATCH
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    form = ProfileUpdateForm(data)
    if not form.is_valid():
        return JsonResponse({"error": "Validation failed", "details": form.errors}, status=400)

    name = form.cleaned_data.get("name") or ""
    if name:
        parts = name.strip().split(" ", 1)
        request.user.first_name = parts[0]
        request.user.last_name = parts[1] if len(parts) > 1 else ""
        request.user.save()

    profile.phone = form.cleaned_data.get("phone") or profile.phone
    profile.country = form.cleaned_data.get("country") or profile.country
    profile.save()

    return JsonResponse({"user": user_to_dict(request.user, request)})


@csrf_exempt
@require_http_methods(["POST"])
def upload_avatar(request):
    """Upload / replace the profile picture. Expects multipart with an 'avatar' file."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    file = request.FILES.get("avatar")
    if not file:
        return JsonResponse({"error": "No avatar file provided"}, status=400)

    if file.size > 5 * 1024 * 1024:  # 5MB limit
        return JsonResponse({"error": "Image too large (max 5MB)"}, status=400)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.avatar = file
    profile.save()

    return JsonResponse({"user": user_to_dict(request.user, request)})
