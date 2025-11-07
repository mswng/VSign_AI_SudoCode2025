from django.contrib import admin
from users.models import (
    Customer,
    Topic,
    Flashcard,
    UserFlashcard,
    TestQuestion,
    UserTest,
    AISession,
    AISessionLog,
    Reminder
)

# Đăng ký tất cả model
admin.site.register(Customer)
admin.site.register(Topic)
admin.site.register(Flashcard)
admin.site.register(UserFlashcard)
admin.site.register(TestQuestion)
admin.site.register(UserTest)
admin.site.register(AISession)
admin.site.register(AISessionLog)
admin.site.register(Reminder)



