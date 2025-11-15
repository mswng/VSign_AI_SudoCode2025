from django.utils import timezone
from django.contrib.auth.models import User
from apscheduler.schedulers.background import BackgroundScheduler
import atexit


def delete_expired_users():
    now = timezone.now()
    expired_users = User.objects.filter(
        is_active=False,
        customer__is_activated=False,
        customer__activation_expiry__lt=now
    )
    count = expired_users.count()
    expired_users.delete()
    print(f"Đã xóa {count} user không kích hoạt đúng hạn.")

scheduler = BackgroundScheduler()
# Chạy mỗi 2 phút
scheduler.add_job(delete_expired_users, 'interval', minutes=2)
scheduler.start()

# Đảm bảo scheduler dừng khi Django tắt
atexit.register(lambda: scheduler.shutdown())