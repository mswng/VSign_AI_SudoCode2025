from django.shortcuts import render


def login_view(request):
    return render(request, 'login.html', {'exception_notes': None})

from django.http import HttpResponse
def logout(request):
    return HttpResponse("Logout Page")
