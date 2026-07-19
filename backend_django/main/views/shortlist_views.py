"""Shortlist endpoints."""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..models import ShortlistItem
from ..serializers import shortlist_to_list


@require_http_methods(["GET"])
def list_shortlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    return JsonResponse({"shortlist": shortlist_to_list(request.user)})


@csrf_exempt
@require_http_methods(["POST"])
def toggle_shortlist(request, university_id):
    """Add or remove a university from the user's shortlist (toggle)."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    item = ShortlistItem.objects.filter(user=request.user, university_id=university_id).first()
    if item:
        item.delete()
        action = "removed"
    else:
        ShortlistItem.objects.create(user=request.user, university_id=university_id)
        action = "added"

    return JsonResponse({
        "action": action,
        "university_id": university_id,
        "shortlist": shortlist_to_list(request.user),
    })
