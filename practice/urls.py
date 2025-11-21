from django.urls import path
from .views import *

urlpatterns = [
    path("topics/", get_all_topics, name="get_all_topics"),
    path('vocab_topics/', vocab_topics_api, name='vocab_topics_api'),
    path('chatbot/', chatbot_api, name="chatbot_api"),
    path('curriculum_profile/', curriculum_profile_api, name="curriculum_profile_api"),
    path('test_session/', test_session_api, name="test_session_api"),

]
