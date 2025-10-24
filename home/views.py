from django.shortcuts import render
from django.http import HttpResponse

from users.utils import get_user_role
from users.views import get_menu_by_role


def home(request):
     
    # Lấy thông tin user_role từ session
    user_role = get_user_role(request)
    menu = get_menu_by_role(user_role)
    
    context = {
        'menu': menu
    }  
    return render(request, 'index.html', context)