from django.urls import path
from .views import get_progress, get_top_wrong_questions

urlpatterns = [
    path("summary/", get_progress),
    path("top-wrong/", get_top_wrong_questions),
]
