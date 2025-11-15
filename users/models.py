from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import nanoid
from django.db.models.signals import post_save
from django.dispatch import receiver

def generate_short_id():
    return nanoid.generate(size=5)


# ==============================
# 1. CUSTOMER (MỞ RỘNG USER)
# ==============================
class Customer(models.Model):
    customer_id = models.CharField(
        primary_key=True, max_length=6, default=generate_short_id, editable=False
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    email = models.EmailField(max_length=255, blank=True, null=True)
    sex = models.CharField(
        max_length=10,
        choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')],
        default='Khác'
    )
    date_of_birth = models.DateField(blank=True, null=True)
    joined_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)
    else:
        if hasattr(instance, 'customer'):
            instance.customer.save()


# ==============================
# 2. TOPICS
# ==============================
class Topic(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ==============================
# 3. FLASHCARDS
# ==============================
class Flashcard(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='flashcards')
    front_text = models.TextField()
    back_text = models.TextField()
    media = models.FileField(upload_to='flashcards/')  
    def __str__(self):
        return f"{self.topic.title}: {self.front_text[:30]}"


# ==============================
# 4. USER_FLASHCARDS
# ==============================
class UserFlashcard(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    learned = models.BooleanField(default=False)
    last_reviewed = models.DateTimeField(blank=True, null=True)
    correct_count = models.IntegerField(default=0)
    wrong_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'flashcard')


# ==============================
# 5. TESTS
# ==============================
class TestQuestion(models.Model):
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name='test_questions')
    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1)  # A/B/C/D

    def __str__(self):
        return f"{self.topic.title}: {self.question[:30]}"


# ==============================
# 6. USER_TESTS
# ==============================
class UserTest(models.Model):
    id = models.AutoField(primary_key=True)  # đảm bảo mỗi lần làm là 1 record mới

    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    test = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)

    user_answer = models.CharField(max_length=1)
    is_correct = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attempted_at']

    def __str__(self):
        return f"Test result - {self.user.user.username} ({'Đúng' if self.is_correct else 'Sai'})"



# ==============================
# 7. AI_SESSIONS
# ==============================
class AISession(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='ai_sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    result_summary = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"AI Session {self.id} - {self.user.user.username}"


# ==============================
# 8. AI_SESSION_LOGS
# ==============================
class AISessionLog(models.Model):
    session = models.ForeignKey(AISession, on_delete=models.CASCADE, related_name='logs')
    frame_time = models.DateTimeField(auto_now_add=True)
    recognized_symbol = models.CharField(max_length=100)
    expected_symbol = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)
    ai_explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Session {self.session.id} - {self.recognized_symbol}"


# ==============================
# 9. REMINDERS
# ==============================
class Reminder(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reminders')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    message = models.TextField()
    scheduled_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.user.user.username} - {self.topic.title}"
