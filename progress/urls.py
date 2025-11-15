from django.urls import path
from .views import *
urlpatterns = [
    path("summary/", get_progress),
    path("top-wrong/", get_top_wrong_questions),
    path("overview_progress", overview_progress),
]

