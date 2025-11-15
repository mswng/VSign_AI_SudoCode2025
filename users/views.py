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
from datetime import timedelta
import urllib.parse
import requests
from users.models import Customer




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
    """Đăng ký user"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
<<<<<<< HEAD
        first_name = data.get('name', username)
     
=======
>>>>>>> 8f6a82b72ac1ab780291e0244241b75086780777

        if not username or not email or not password:
            return JsonResponse({'error': 'Thiếu thông tin bắt buộc'}, status=400)

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email hoặc tên đăng nhập đã tồn tại'}, status=400)


<<<<<<< HEAD
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, is_active=False)
        
        otp_code, otp_expiry = create_and_send_otp(email)

        # Lưu OTP vào session
        request.session['otp_code'] = otp_code
        request.session['otp_email'] = email
        request.session['otp_purpose'] = "register"
        request.session['otp_expiry'] = otp_expiry.isoformat()
        request.session.set_expiry(60)

        return JsonResponse({
            'message': 'Đăng ký thành công! vui lòng kiểm tra email để kích hoạt tài khoản.',
=======
        user = User.objects.create_user(username=username, email=email, password=password)
        tokens = get_tokens_for_user(user)

        return JsonResponse({
            'message': 'Đăng ký thành công!',
            'user': {'username': user.username, 'email': user.email,},
            'tokens': tokens
>>>>>>> 8f6a82b72ac1ab780291e0244241b75086780777
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ===================== 🌐 GOOGLE LOGIN =====================
@csrf_exempt
def google_get_url(request):
    google_auth_base = "https://accounts.google.com/o/oauth2/v2/auth"

    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),   
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account"
    }

    url = f"{google_auth_base}?{urllib.parse.urlencode(params)}"

    return JsonResponse({"auth_url": url})

@csrf_exempt
def google_callback(request):
    try:
        code = request.GET.get('code')

        if not code:
            return JsonResponse({"error": "Missing code"}, status=400)

        #  Đổi code lấy token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),          
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),  
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),     
            "grant_type": "authorization_code",
        }

        token_res = requests.post(token_url, data=data)
        token_json = token_res.json()

        if "access_token" not in token_json:
            return JsonResponse({
                "error": "Failed to exchange token",
                "details": token_json
            }, status=400)

        access_token = token_json["access_token"]

        #  Lấy thông tin user
        user_info_res = requests.get(  
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_info_res.json()

        email = user_info.get("email")
        name = user_info.get("name") or ""

        if not email:
            return JsonResponse({"error": "Google did not return email"}, status=400)

        # Tạo hoặc lấy user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0],
                "first_name": name.split()[0] if name else "",
                "last_name": " ".join(name.split()[1:]) if name else ""
            }
        )

        # Đảm bảo Customer tồn tại và kích hoạt
        customer, c_created = Customer.objects.get_or_create(
            user=user,
            defaults={
                "email": email,
                "is_activated": True,
    
            }
        )

        if not c_created:   # Customer đã tồn tại
            customer.is_activated = True
    
            if not customer.email:
                customer.email = email
            customer.save()

        #  Tạo JWT
        refresh = RefreshToken.for_user(user)

        return JsonResponse({
            "success": True,
            "message": "Google login successful",
            "created": created,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.get_full_name() or user.username
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)}, status=500)

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
def create_and_send_otp(email):
   
    otp_code = generate_otp()
    otp_expiry = timezone.now() + timedelta(minutes=1)

    # Gửi email OTP
    send_otp_email(email, otp_code)

    return otp_code, otp_expiry


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

        # Gửi OTP
        otp_code, otp_expiry = create_and_send_otp(email)

        # Lưu OTP vào session (1 phút)
        request.session['otp_code'] = otp_code
        request.session['otp_email'] = email
        request.session['otp_purpose'] = purpose
        request.session['otp_expiry'] = otp_expiry.isoformat()
        request.session.set_expiry(60)


        return JsonResponse({
            'success': True,
            'message': f'OTP đã gửi tới {email}',
            'otp_code': otp_code  # để debug, production có thể bỏ
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def verify_otp_session(request, purpose: str):

     # Parse JSON body
    try:
        data = json.loads(request.body)
    except:
        data = {}
   
    otp_input = data.get('otp')
    email_input = data.get('email')

    otp_code = request.session.get('otp_code')
    otp_email = request.session.get('otp_email')
    otp_purpose = request.session.get('otp_purpose')
    otp_expiry = request.session.get('otp_expiry')

    print(f"[DEBUG] otp_purpose from session: '{otp_purpose}' (type: {type(otp_purpose)})")
    print(f"[DEBUG] purpose from function arg: '{purpose}' (type: {type(purpose)})")

    if otp_purpose != purpose:
        return False, 'OTP không dùng cho mục đích này'

    if not otp_code or not otp_email or not otp_expiry:
        return False, 'Không có OTP trong session'

    otp_expiry = timezone.datetime.fromisoformat(otp_expiry)
    if timezone.now() > otp_expiry + timedelta(minutes=5):
        # Xóa session khi hết hạn
        for key in ['otp_code', 'otp_email', 'otp_purpose', 'otp_expiry']:
            request.session.pop(key, None)
        return False, 'OTP đã hết hạn'

    if otp_input != otp_code or email_input != otp_email:
        return False, 'OTP không đúng'

    # OTP hợp lệ → xóa session
    for key in ['otp_code', 'otp_email', 'otp_purpose', 'otp_expiry']:
        request.session.pop(key, None)

    return True, email_input


@csrf_exempt
def verify_otp_register_api(request):
    success, result = verify_otp_session(request, purpose='register')
    if not success:
        return JsonResponse({'success': False, 'message': result})

    # OTP hợp lệ → kích hoạt user
    try:
        user = User.objects.get(email=result)
        user.is_active = True
        user.save()

       # Đồng thời cập nhật Customer
        if hasattr(user, 'customer'):
            customer = user.customer
            customer.is_activated = True
            customer.save()
        else:
          
            return JsonResponse({'success': False, 'message': 'Customer chưa tồn tại cho user này'})
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User không tồn tại'})

    return JsonResponse({'success': True, 'message': 'Kích hoạt tài khoản thành công'})


# ===================== RESET PASSWORD =====================
@csrf_exempt
def reset_pass_validateEmail_api(request):

    try:
        data = json.loads(request.body)
       
        email = data.get('email')
        

       
        if User.objects.filter(email=email).exists():
            otp_code, otp_expiry = create_and_send_otp(email)
            # Lưu OTP vào session
            request.session['otp_code'] = otp_code
            request.session['otp_email'] = email
            request.session['otp_purpose'] = "reset_pasword"
            request.session['otp_expiry'] = otp_expiry.isoformat()
            request.session.set_expiry(60)
            return JsonResponse({
                'send_opt': True,
                'message': 'validate email thành công',
            })
        else:
            return JsonResponse({
                'send_opt': False,
                'error': 'Không tìm thấy người dùng với email này'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def reset_pass_validateOtp_api(request):

    # Parse JSON body
    try:
        data = json.loads(request.body)
    except:
        data = {}

    email = (
        data.get('email') or 
        request.POST.get('email') or
        request.GET.get('email') or
        request.session.get('otp_email')
    )

    if( not email):
        print("[DEBUG] Email:", email)
        return JsonResponse({'success': False, 'message': 'Thiếu email'}, status=400)
    elif User.objects.filter(email=email).exists() == False:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy người dùng với email này'}, status=400)

    success, result = verify_otp_session(request, purpose='reset_pasword')

    if not success:
        return JsonResponse({'success': False, 'message': result})
    return JsonResponse({'success': True, 'message': 'OTP hợp lệ'})

@csrf_exempt
def change_password_api(request):
    """Thay đổi mật khẩu cho user đã xác thực"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = data.get("email")
    new_password = data.get("new_password")

    if not email or not new_password:
        return JsonResponse({"error": "Email và mật khẩu mới bắt buộc"}, status=400)

    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        return JsonResponse({
            "success": True,
            "message": "Đổi mật khẩu thành công!",
        }, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "Không tìm thấy người dùng với email này"}, status=400)

    

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