from django.db import models
from django.contrib.auth.models import User
import nanoid

def generate_short_id():
    return nanoid.generate(size=5)


class Topic(models.Model):
    topic_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Flashcard(models.Model):
    Flashcard_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    term = models.CharField(max_length=100)
    meaning = models.TextField()
    image = models.ImageField(upload_to="flashcards/", blank=True, null=True)
    video = models.FileField(upload_to="flashcard_videos/", blank=True, null=True)

    def __str__(self):
        return f"{self.term} ({self.topic.name})"


class Note(models.Model):
    Note_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note by {self.user.username} on {self.flashcard.term}"


class Question(models.Model):
    question_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Câu hỏi dựa trên flashcard này"
    )
    text = models.TextField(help_text="Nội dung câu hỏi (dạng text)")
    question_type = models.CharField(
        max_length=20,
        choices=[
            ("choice", "Trắc nghiệm"),
            ("text", "Nhập câu trả lời"),
        ],
        default="choice",
        help_text="Loại câu hỏi: chọn đáp án hoặc nhập tay"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.flashcard:
            return f"Câu hỏi: {self.text[:40]} (Flashcard: {self.flashcard.title})"
        return self.text[:60]



class Answer(models.Model):
    answer_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'✔' if self.is_correct else '✖'})"


class UserAnswer(models.Model):
    user_answer_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(
        "learning.Answer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Đáp án người học chọn (nếu là trắc nghiệm)"
    )
    text_answer = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Câu trả lời nhập tay (nếu là câu hỏi tự luận)"
    )
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.id}"

