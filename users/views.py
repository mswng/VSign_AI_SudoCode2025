from datetime import datetime, timedelta, date 
from django.utils import timezone 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
import json, os, requests as py_requests
from .utils import send_otp_email, generate_otp



# ===================== 🔑 JWT Helper =====================
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def jwt_required(view_func):
    def wrapper(request, *args, **kwargs):
        auth = JWTAuthentication()
        try:
            user, token = auth.authenticate(request)
            request.user = user
        except Exception:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


# ===================== 🧩 LOGIN =====================
@csrf_exempt
def login_api(request):
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Username và password bắt buộc'}, status=400)

        user = authenticate(request, username=username, password=password)
        if user:
            tokens = get_tokens_for_user(user)
            return JsonResponse({
                'message': 'Đăng nhập thành công!',
                'user': {'username': user.username, 'email': user.email},
                'tokens': tokens
            })
        return JsonResponse({'error': 'Sai tên đăng nhập hoặc mật khẩu'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ===================== 🆕 REGISTER =====================
@csrf_exempt
def register_api(request):
    """Đăng ký user, yêu cầu OTP đã xác thực"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return JsonResponse({'error': 'Thiếu thông tin bắt buộc'}, status=400)

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email hoặc tên đăng nhập đã tồn tại'}, status=400)


        user = User.objects.create_user(username=username, email=email, password=password)
        tokens = get_tokens_for_user(user)

        return JsonResponse({
            'message': 'Đăng ký thành công!',
            'user': {'username': user.username, 'email': user.email,},
            'tokens': tokens
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ===================== 🌐 GOOGLE LOGIN =====================
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

@csrf_exempt
def google_login(request):
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=400)
    
    data = json.loads(request.body)
    token = data.get('token')
    if not token:
        return JsonResponse({'error': 'Token is required'}, status=400)

    verify_url = f'https://oauth2.googleapis.com/tokeninfo?id_token={token}'
    resp = py_requests.get(verify_url)
    if resp.status_code != 200:
        return JsonResponse({'error': 'Invalid Google token'}, status=400)

    info = resp.json()
    email = info.get('email')
    name = info.get('name')

    if not email:
        return JsonResponse({'error': 'Google không trả về email'}, status=400)

    user, created = User.objects.get_or_create(
        email=email,
        defaults={'username': email.split('@')[0], 'first_name': name}
    )

    tokens = get_tokens_for_user(user)

    return JsonResponse({
        'message': 'Google login successful',
        'user': {'email': user.email, 'name': user.first_name},
        'tokens': tokens,
        'created': created,
    })


# ===================== 🔒 LOGOUT =====================
@csrf_exempt
def logout_api(request):
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()  # invalidate token
        return JsonResponse({'success': True, 'message': 'Logout thành công'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

# ===================== OTP =====================
@csrf_exempt
def send_otp_api(request):
    """
    Gửi OTP cho register hoặc reset_password
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        purpose = data.get('purpose')  # 'register' hoặc 'reset_password'

        if not email or purpose not in ['register', 'reset_password']:
            return JsonResponse({'error': 'Thiếu email hoặc purpose'}, status=400)

        # Kiểm tra email theo mục đích
        if purpose == 'register' and User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email đã tồn tại'}, status=400)
        if purpose == 'reset_password' and not User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Không tìm thấy người dùng với email này'}, status=400)

        # Tạo OTP
        otp_code = generate_otp()
        now = timezone.now()

        # Lưu OTP vào session (1 phút)
        request.session['otp_code'] = otp_code
        request.session['otp_email'] = email
        request.session['otp_purpose'] = purpose
        request.session['otp_created_at'] = now.isoformat()
        request.session.set_expiry(60)

        # Gửi email
        send_otp_email(email, otp_code)

        return JsonResponse({
            'success': True,
            'message': f'OTP đã gửi tới {email}',
            'otp_code': otp_code  # để debug, production có thể bỏ
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def verify_otp_api(request):
    """
    Xác thực OTP cho register hoặc reset_password
    """
    try:
        data = json.loads(request.body)
        otp_input = data.get('otp')
        email_input = data.get('email')

        otp_code = request.session.get('otp_code')
        otp_email = request.session.get('otp_email')
        otp_purpose = request.session.get('otp_purpose')
        otp_created_at = request.session.get('otp_created_at')

        if not otp_code or not otp_email or not otp_created_at:
            return JsonResponse({'success': False, 'message': 'Không có OTP trong session'})

        # Kiểm tra OTP hết hạn
        otp_created_at = timezone.make_aware(timezone.datetime.fromisoformat(otp_created_at))
        if timezone.now() > otp_created_at + timedelta(minutes=5):
            # Xóa session khi hết hạn
            for key in ['otp_code', 'otp_email', 'otp_purpose', 'otp_created_at']:
                request.session.pop(key, None)
            return JsonResponse({'success': False, 'message': 'OTP đã hết hạn'})

        # Kiểm tra OTP và email
        if otp_input != otp_code or email_input != otp_email:
            return JsonResponse({'success': False, 'message': 'OTP không đúng'})

        # OTP hợp lệ → xóa session
        for key in ['otp_code', 'otp_email', 'otp_purpose', 'otp_created_at']:
            request.session.pop(key, None)

        return JsonResponse({'success': True, 'message': 'OTP hợp lệ', 'purpose': otp_purpose})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# ===================== RESET PASSWORD =====================
@csrf_exempt
def change_password_api(request):
    """Đổi mật khẩu, yêu cầu OTP đã xác thực"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        new_password = data.get('new_password')
        otp_verified = data.get('otp_verified', False)

        if not email or not new_password:
            return JsonResponse({'error': 'Thiếu thông tin'}, status=400)
        if not otp_verified:
            return JsonResponse({'error': 'Bạn phải xác thực OTP trước khi đổi mật khẩu'}, status=400)

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        return JsonResponse({'message': 'Đổi mật khẩu thành công'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'Người dùng không tồn tại'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ===================== 👤 PROFILE =====================
@csrf_exempt
@jwt_required
def profile_api(request):
    """Trả thông tin hồ sơ người dùng hiện tại"""
    user = request.user

    # Lấy thông tin từ bảng customer (nếu có)
    customer = getattr(user, "customer", None)

    data = {
        "username": user.username,
        "email": user.email,
        "sex": getattr(customer, "sex", None),
        "date_of_birth": (
            customer.date_of_birth.strftime("%d/%m/%Y")
            if getattr(customer, "date_of_birth", None)
            else None
        ),

    }

    return JsonResponse({"user": data}, status=200)


@csrf_exempt
@jwt_required
def update_profile_api(request):
    """Cập nhật thông tin hồ sơ người dùng"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    user = request.user

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("username")
    email = data.get("email")
    sex = data.get("sex")  # male/female/other
    dob = data.get("date_of_birth")  # yyyy-MM-dd

    # ✅ Cập nhật User
    if username:
        user.username = username
    if email:
        user.email = email
    user.save()

    # ✅ Cập nhật Customer (nếu có)
    customer = getattr(user, "customer", None)
    if customer:
        if sex in ["male", "female", "other"]:
            customer.sex = sex

        if dob:
            try:
                dob = dob.strip()  # loại bỏ khoảng trắng đầu/cuối
                customer.date_of_birth = datetime.strptime(dob, "%d/%m/%Y").date()
            except ValueError:
                return JsonResponse({"error": "Ngày sinh không hợp lệ"}, status=400)

        customer.save()

    return JsonResponse({
        "success": True,
        "message": "Cập nhật profile thành công!",
        "user": {
            "username": user.username,
            "email": user.email,
            "sex": getattr(customer, "sex", None),
            "date_of_birth": getattr(customer, "date_of_birth", None).strftime("%Y-%m-%d") if getattr(customer, "date_of_birth", None) else None,
        },
    }, status=200)