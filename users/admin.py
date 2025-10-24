from django.contrib import admin
from users.models import Customer, Goal, Favorite, Streak, Notification



# USER
admin.site.register(Customer)
admin.site.register(Goal)
admin.site.register(Favorite)
admin.site.register(Streak)
admin.site.register(Notification)


