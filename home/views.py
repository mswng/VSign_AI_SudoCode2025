from django.http import JsonResponse
from users.utils import get_user_role

def home_api(request):
    """
    API trả về thông tin cơ bản cho React frontend
    """
    if request.user.is_authenticated:
        role = get_user_role(request)
        data = {
            "user": {
                "username": request.user.username,
                "name": request.user.first_name,
                "email": request.user.email,
                "role": role,
            }
        }
    else:
        data = {"user": None}

    return JsonResponse(data)
