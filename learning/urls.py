from django.urls import path
from .views import *

urlpatterns = [
    path("topics/", get_all_topics, name="get_all_topics"),
    path("topics/<int:topic_id>/flashcards/", get_topic_flashcards, name="get_topic_flashcards"),
    path("topics/<int:topic_id>/test-questions/", get_topic_test_questions, name="get_topic_test_questions"),
    path("topics/submit_answer/", submit_answer, name="submit_answer"),    # POST
]
