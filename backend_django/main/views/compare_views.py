"""Compare endpoints — max 3 universities per user."""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..models import CompareItem
from ..serializers import compare_to_list

MAX_COMPARE = 3


@require_http_methods(["GET"])
def list_compare(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    return JsonResponse({"compare": compare_to_list(request.user)})


@csrf_exempt
@require_http_methods(["POST"])
def toggle_compare(request, university_id):
    """Add or remove a university from the compare list (max 3)."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    item = CompareItem.objects.filter(user=request.user, university_id=university_id).first()
    if item:
        item.delete()
        action = "removed"
    else:
        if request.user.compare.count() >= MAX_COMPARE:
            return JsonResponse({
                "error": f"Compare list is full (max {MAX_COMPARE}). Remove one first.",
                "compare": compare_to_list(request.user),
            }, status=400)
        CompareItem.objects.create(user=request.user, university_id=university_id)
        action = "added"

    return JsonResponse({
        "action": action,
        "university_id": university_id,
        "compare": compare_to_list(request.user),
    })
