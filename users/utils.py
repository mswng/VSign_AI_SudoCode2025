import random
from smtplib import SMTPException
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, get_connection
from asgiref.sync import sync_to_async
# Email
def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_email(email, otp=None):
    if otp is None:
        otp = generate_otp()
    context = {
        'otp': otp,
        'system_name': 'Silent Speak',
    }

    html_content = render_to_string('Email_Sign_up.html', context)

    email_message = EmailMessage(
        subject='Xác nhận đăng ký tài khoản',
        body=html_content,
        from_email=None,  # Django sẽ dùng DEFAULT_FROM_EMAIL
        to=[email],
    )
    email_message.content_subtype = 'html'

    try:
        email_message.send(fail_silently=False)
        print(f"OTP {otp} đã gửi tới {email}")
        return otp
    except SMTPException as e:
        print("Lỗi khi gửi email:", e)
        return None


def get_user_role(request):
    user = request.user
    if hasattr(user, 'customer'):
        return 'customer'
    elif user.is_superuser:
        return 'admin'
    return 'guest'


def get_menu_by_role(role):
    menu_dict = {
        'customer': [
            {'name': 'Trang chủ', 'url': '/'},
            {'name': 'Thông tin cá nhân', 'url': '/thong-tin/'},
        ],
        'guest': [
            {'name': 'Đăng nhập', 'url': '/login/'},
        ],
    }

    return menu_dict.get(role, [])
