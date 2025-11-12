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
    path('', home_views.home, name='home'),

    path('register/', views.Sign_Up.as_view(), name='register'),
    path('trangOTP/', views.trangOTP, name= 'trangOTP'),
    path('login/', views.Sign_In.as_view(), name='login'), 
    path('logout/', views.Logout, name='logout'),
    path('forgot_password/', views.ForgotPassword.as_view(), name= 'Forgot_password'),
    # xác thực OTP và đăng ký trong đăng ký
    path('validate_otp_and_register/', views.validate_otp_and_register, name='validate_otp_and_register'),
    # gửi lại mật khẩu trong đăng ký và quên mật khẩu
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    # xác thực OTP quên mật khẩu
    path('validate_otp_fogotpassword/', views.validate_otp_of_ForgotPassword, name='validate_otp_of_ForgotPassword'),
    path('new_password/', views.New_password.as_view(), name= 'New_Password'),
    

    path('profile/', views.ThongTinCaNhan, name='profile'),
    path('profile_edit/', views.ChinhSuaThongTinCaNhan.as_view(), name='profile_edit'),


    path('chatbot/', practice_views.ask_ai_page, name="ask_ai_page"),


    path('api/vocab_topics/', practice_views.vocab_topics_api, name='vocab_topics_api'),
    path('api/chatbot/', practice_views.chatbot_api, name="chatbot_api"),
    path('api/curriculum_profile/', practice_views.curriculum_profile_api, name="curriculum_profile_api"),
    path('api/test_session/', practice_views.test_session_api, name="test_session_api"),
    path('api/google', views.google_login, name='google-login'),
]
