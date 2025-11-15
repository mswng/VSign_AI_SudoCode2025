"""
URL configuration for VSign_AI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from users import views 
from home import views as home_views 
from practice import views as practice_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('', home_views.home_api, name='home_api'),

    path('api/auth/login/', views.login_api, name="login_api"),
    path('api/auth/logout/', views.logout_api, name="logout_api"),

    
    path('api/auth/register/', views.register_api, name="register_api"),

    path('api/auth/google/login/', views.google_get_url, name="google_get_url"),
    path('api/auth/google/callback/', views.google_callback, name="google_callback"),

    path('api/auth/send-otp/', views.send_otp_api, name="send_otp_api"),
    path('api/auth/verify-otp-register/', views.verify_otp_register_api, name="verify-otp-register"),

    # xác thực email để đặt lại mật khẩu
    path('api/auth/reset-pass-validateEmail-api/', views.reset_pass_validateEmail_api, name="reset_pass_validateEmail_api"),
    # xác thực OTP để đặt lại mật khẩu
    path('api/auth/reset-pass-validateOtp-api/', views.reset_pass_validateOtp_api, name="reset_pass_validateOtp_api"),
    # đặt lại mật khẩu
    path('api/auth/change-password/', views.change_password_api, name="change_password_api"),

    path('api/auth/profile/', views.profile_api, name='profile_api'),
    path('api/auth/profile/update/', views.update_profile_api, name='update_profile_api'),


    path('chatbot/', practice_views.ask_ai_page, name="ask_ai_page"),


    path('api/vocab_topics/', practice_views.vocab_topics_api, name='vocab_topics_api'),
    path('api/chatbot/', practice_views.chatbot_api, name="chatbot_api"),
    path('api/curriculum_profile/', practice_views.curriculum_profile_api, name="curriculum_profile_api"),
    path('api/test_session/', practice_views.test_session_api, name="test_session_api"),

]
