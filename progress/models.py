from django.db import models
from django.contrib.auth.models import User
from learning.models import Topic, Question
import nanoid

def generate_short_id():
    return nanoid.generate(size=5)

class ReviewReminder(models.Model):
    reviewReminder_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, blank=True)
    wrong_count = models.PositiveIntegerField(default=0)
    next_review_date = models.DateField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Review reminder for {self.user.username} - {self.topic.name}"


class ProgressStatistic(models.Model):
    progressStatistic_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    topics_learned = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    tests_completed = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

