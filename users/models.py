from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth.models import User
from learning.models import Flashcard
import nanoid
from django.db.models.signals import post_save
from django.dispatch import receiver


def generate_short_id():
    return nanoid.generate(size=5)


class Customer(models.Model):
    customer_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    sex = models.CharField(max_length=10, choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')], default='Khác')
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    joined_date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"Profile of {self.user.username}"

@receiver(post_save, sender=User)
def create_or_update_customer_profile(sender, instance, created, **kwargs):
    # Khi user mới được tạo
    if created:
        # Kiểm tra nếu user thuộc nhóm Customer (hoặc không thuộc nhóm nào)
        if not hasattr(instance, 'customer'):
            Customer.objects.create(user=instance, email=instance.email)
    else:
        # Khi user đã tồn tại => đồng bộ email
        if hasattr(instance, 'customer'):
            instance.customer.email = instance.email
            instance.customer.save()

class Goal(models.Model):
    goal_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    daily_flashcard_goal = models.PositiveIntegerField(default=20)
    daily_test_goal = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Goal of {self.user.username}"


class Favorite(models.Model):
    favourite_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(Flashcard, on_delete=models.CASCADE) 
    object_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "content_type", "object_id")

    def __str__(self):
        return f"{self.user.username} - {self.content_type} {self.object_id}"


class Streak(models.Model):
    streak_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_checkin = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.current_streak} streaks"


class Notification(models.Model):
    notification_id = models.CharField(primary_key=True, max_length=6, default=generate_short_id, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif for {self.user.username}: {self.title}"


