from datetime import timedelta
from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render,redirect
from django.views import View
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from requests import request
from .forms import *
from django.db.models import Q
from .utils import send_otp_email, generate_otp
from django.utils import timezone
from django.http import JsonResponse
from datetime import date
from .models import *
from django.contrib.auth.decorators import login_required
import json
import threading
from .models import Customer
from .utils import get_user_role, get_menu_by_role 
from django.contrib.auth import get_user_model
User = get_user_model()

# HÀM KIỂM TRA MÃ OTP ĐỂ TÁI SỬ DỤNG:
# GỬI OTP KHI NGƯỜI DÙNG YÊU CẦU
def handle_send_otp(request, form_input):
    if not form_input.is_valid():
        return

    username = form_input.cleaned_data['username']
    email = request.session.get('email')  # ✅ lấy từ session thay vì form
    if not email:
        raise ValueError("Không tìm thấy email để gửi OTP.")

    # 🔢 Tạo OTP
    otp = generate_otp()

    # 💾 Lưu OTP + thông tin tạm thời vào session
    request.session['otp'] = otp
    request.session['username'] = username
    request.session['email'] = email
    request.session['otp_created_at'] = timezone.now().isoformat()

    # 📩 Gửi OTP qua email
    send_otp_email(email, otp)

class Sign_Up(View):
    def get(self, request):
        sign_up = SignUpForm()
        context = {'SignUp': sign_up}
        return render(request, 'register.html', context)

    def post(self, request):
       
        sign_up = SignUpForm(request.POST)
        context = {'SignUp': sign_up}

        if not sign_up.is_valid():
            # Trả lỗi để JS hiển thị
            return render(request, 'register.html', context)

        # Lấy dữ liệu hợp lệ
        username = sign_up.cleaned_data['username']
        email = sign_up.cleaned_data['email']
        password = sign_up.cleaned_data['password']
        sex = sign_up.cleaned_data.get('sex')
        date_of_birth = sign_up.cleaned_data.get('date_of_birth')

        # Lưu tạm vào session
        request.session['username'] = username
        request.session['email'] = email
        request.session['password'] = password
        request.session['sex'] = sex
        request.session['date_of_birth'] = str(date_of_birth)

        # Gửi OTP trong luồng riêng (background thread)
        threading.Thread(target=handle_send_otp, args=(request, sign_up)).start()

        return redirect('trangOTP') 


# Trang nhập mã OTP   
def trangOTP(request):  
    return render(request, 'verify_OTP.html')      

# file get_user_role đã chuyển qua processor
def get_menu_by_role(user_role):
    if user_role == 'manage' or user_role == 'admin'or user_role == 'staff':
        return 'app1/Menu-manager.html'
    elif user_role == 'customer' or user_role == None:
        return 'app1/Menu.html'
    
#  hàm tạo User

def create_user_account(username,email, password, date_of_birth=None):
    try:
        if User.objects.filter(username=username).exists():
            return None
        if User.objects.filter(email=email).exists():
            return None

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            
        )
        user.save()
        return user

    except Exception as e:
        print("Error creating user:", e)
        return None


def validate_otp(request):
   
    otp_session = request.session.get("otp")
    otp_created_at = request.session.get("otp_created_at")

    if not otp_session or not otp_created_at:
        return {"valid": False, "message": "Mã OTP không tồn tại hoặc đã hết hạn."}

    # Kiểm tra thời gian hết hạn của OTP
    otp_created_at = timezone.datetime.fromisoformat(otp_created_at)
    if timezone.now() > otp_created_at + timedelta(minutes=1):
        return {"valid": False, "message": "Mã OTP đã hết hiệu lực. Vui lòng thử lại."}

    return {"valid": True, "otp_session": otp_session}


# Hàm validate OTP và đăng ký user
def validate_otp_and_register(request):
    if request.method == "POST":
        data = json.loads(request.body)
        otp_input = data.get("otp")

        # Kiểm tra mã OTP bằng hàm validate_otp
        otp_validation = validate_otp(request)
        if not otp_validation["valid"]:
            return JsonResponse({"success": False, "message": otp_validation["message"]})

        # So sánh mã OTP người dùng nhập
        if otp_input == otp_validation["otp_session"]:
            username = request.session.get("username")
            email = request.session.get("email")
            password = request.session.get("password")
            sex = request.session.get("sex")
            date_of_birth_str = request.session.get("date_of_birth")

            # Chuyển chuỗi ngày sinh → kiểu date
            if date_of_birth_str:
                try:
                    date_of_birth = date.fromisoformat(date_of_birth_str)
                except ValueError:
                    date_of_birth = None
            else:
                date_of_birth = None

            # Gọi hàm tạo user
            if username and password and email:
                user = create_user_account(username, email, password, date_of_birth)

                if user:
                    # Tạo hoặc cập nhật đối tượng Customer
                    customer, created = Customer.objects.get_or_create(user=user)
                    customer.sex = sex or 'Khác'
                    customer.date_of_birth = date_of_birth
                    customer.save()

                    # Dọn session sau khi đăng ký xong
                    for key in ["otp", "otp_created_at", "username", "email", "password", "sex", "date_of_birth"]:
                        request.session.pop(key, None)

                    return JsonResponse({"success": True, "message": "Đăng ký thành công!"})

                else:
                    return JsonResponse({"success": False, "message": "Email hoặc tên người dùng đã tồn tại."})

            return JsonResponse({"success": False, "message": "Thiếu thông tin đăng ký."})

        else:
            return JsonResponse({"success": False, "message": "Mã OTP không chính xác."})

    return JsonResponse({"success": False, "message": "Yêu cầu không hợp lệ."})



#hàm gửi lại mã OTP
def resend_otp(request):
    if request.method == "POST":
        # Lấy thông tin từ session
        username = request.session.get('username')
        email = request.session.get('email')

        if not username or not email:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy thông tin người dùng. Vui lòng thử lại.'
            })

        # Tạo mã OTP mới
        otp = generate_otp()
        request.session['otp'] = otp  # Cập nhật OTP mới vào session
        request.session['otp_created_at'] = timezone.now().isoformat()  # Cập nhật thời gian tạo OTP

        # Gửi email đúng cách
        send_otp_email(email, otp)

        return JsonResponse({'success': True, 'message': f'Mã OTP đã được gửi lại đến {email}.'})

    return JsonResponse({'success': False, 'message': 'Yêu cầu không hợp lệ.'})




class Sign_In(View):
    def get(self, request):
        remembered_email = request.COOKIES.get('remembered_email', '')
        sign_in_form = SignInForm(initial={'username': remembered_email})
        context = {
            'SignIn': sign_in_form,
            'remember_me': bool(remembered_email),
        }
        return render(request, 'login.html', context)

    def post(self, request):
        
        if request.user.is_authenticated:
            logout(request)

        sign_in_form = SignInForm(request.POST)
        failed_attempts = request.session.get('failed_attempts', 0)

        if not sign_in_form.is_valid():
            messages.error(request, "Vui lòng nhập đầy đủ thông tin.", extra_tags='login')
            return redirect('login')

        username = sign_in_form.cleaned_data['username']
        password = sign_in_form.cleaned_data['password']
        remember_me = request.POST.get('remember_me') == 'on'

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session['failed_attempts'] = 0

            # Xác định loại tài khoản
            if hasattr(user, 'customer'):
                user_role = 'customer'
            else:
                user_role = 'admin'

            request.session['user_role'] = user_role
            response = redirect('home')

            if remember_me:
                response.set_cookie('remembered_email', username, max_age=7 * 24 * 60 * 60)
            else:
                response.delete_cookie('remembered_email')

            return response 

        else:
            request.session['failed_attempts'] = failed_attempts + 1
            if failed_attempts >= 4:
                messages.error(request, "Bạn đã nhập sai quá 5 lần. Vui lòng đặt lại mật khẩu.", extra_tags='login')
            else:
                messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.", extra_tags='login')
            return redirect('login')



# Quên mật khẩu
class ForgotPassword(View):
    def get(self, request):
        forgot_password = ForgotPasswordForm()
        context = {'Forgot_Password_Form': forgot_password}
        return render(request, 'forgot.html', context)

    def post(self, request):
        forgot_password = ForgotPasswordForm(request.POST)
        context = {'Forgot_Password_Form': forgot_password}

        if not forgot_password.is_valid():
            return render(request, 'forgot.html', context)

        username = forgot_password.cleaned_data['username']

        try:
            # 🔍 Tìm user theo username
            user = User.objects.get(username=username)
            email = user.email or getattr(user.customer, 'email', None)

            if not email:
                messages.error(request, "Tài khoản này chưa có email. Vui lòng liên hệ quản trị viên.")
                return render(request, 'forgot.html', context)

            # 💾 Lưu thông tin user vào session để bước sau xác thực OTP
            request.session['username'] = username
            request.session['email'] = email

            # 📩 Gọi hàm gửi OTP (hàm này bạn đã có sẵn)
            handle_send_otp(request, forgot_password)

            # 🧭 Chuyển tới trang nhập OTP
            context['action'] = 'FORGOT_PASSWORD'
            messages.success(request, f"Đã gửi mã xác nhận đến email {email}.")
            return render(request, 'verify_OTP.html', context)

        except User.DoesNotExist:
            messages.error(request, "Tên đăng nhập không tồn tại.")
            return render(request, 'forgot.html', context)

# Hàm validate OTP của quên mật khẩu
def validate_otp_of_ForgotPassword(request):
    if request.method == "POST":
        data = json.loads(request.body)
        otp_input = data.get("otp")

        # Kiểm tra mã OTP bằng hàm validate_otp
        otp_validation = validate_otp(request)
        if not otp_validation["valid"]:
            return JsonResponse({"success": False, "message": otp_validation["message"]})  

        # So sánh mã OTP người dùng nhập
        if otp_input == otp_validation["otp_session"]:
            return JsonResponse({"success": True, "message": "Mã OTP chính xác"})
        else:
            return JsonResponse({"success": False, "message": "Mã OTP không chính xác"})
    
    return JsonResponse({"success": False, "message": "Yêu cầu không hợp lệ."})

# Đổi mật khẩu mới:
class New_password(View):
    def get(self,request):
        New_password = NewPasswordForm() 
        context = {'New_Password_Form': New_password}  
        return render(request, 'newpass.html',context)
    
    def post(self, request):
        New_password = NewPasswordForm(request.POST) 
        context = {'New_Password_Form': New_password}  

        if not New_password.is_valid():
            return render(request, 'newpass.html', context)
        
        username = request.session.get('username')
        
        # lấy mật khẩu mới của người dùng
        new_password = New_password.cleaned_data['new_password']
        # cập nhật mật khẩu mới
        user = User.objects.get(username = username)
       
        user.password = make_password(new_password)
        
        user.save()
        messages.success(request, "Đổi mật khẩu thành công!")
        return redirect('login')
    
# Đăng xuất 
def Logout(request):
    logout(request)
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # Duyệt qua để xóa toàn bộ message
    return redirect('home')

# Thông tin cá nhân
def ThongTinCaNhan(request):
    user = request.user  # Lấy thông tin người dùng đã đăng nhập
    user_role = get_user_role(request)
    menu = get_menu_by_role(user_role)

    profile = None
    role = 'other'

    # Kiểm tra loại tài khoản và lấy thông tin từ Customer
    if hasattr(user, 'customer'):
        role = 'customer'
        profile = user.customer
    else:
        messages.warning(request, "Tài khoản này chưa có hồ sơ cá nhân.")
    
    # Truyền thông tin ra template
    context = {
        'user': user,
        'profile': profile,  # Truyền hẳn object Customer ra
        'email': getattr(profile, 'email', None),
        'sex': getattr(profile, 'sex', None),
        'date_of_birth': getattr(profile, 'date_of_birth', None),
        'menu': menu,
    }
    return render(request, 'Profile.html', context)

def get_role_and_profile(user):
    if hasattr(user, 'customer'):  # Nếu user là Customer
        return 'customer', user.customer
    return 'other', 'none'

# Chỉnh sửa thông tin cá nhân
class ChinhSuaThongTinCaNhan(View):
    
    def get(self, request):
        user = request.user  # Lấy thông tin người dùng đã đăng nhập
        role, profile = get_role_and_profile(user)
        ChinhSuaThongTin = FormChinhSuaThongTinCaNhan(user=user)
        user_role = get_user_role(request)
        menu = get_menu_by_role(user_role)
    
   
        context = {
            "ChinhSuaThongTin": ChinhSuaThongTin,
            'role': role,  # Truyền loại tài khoản vào template
            'profile': profile,
            'menu': menu
        } 
        return render(request, 'profile_edit.html', context)

    def post(self, request):
        user = request.user
        role, profile = get_role_and_profile(user)
        form = FormChinhSuaThongTinCaNhan(request.POST, user=user)

        if not form.is_valid():
            return render(request, 'profile_edit.html', {
                'ChinhSuaThongTin': form,
                'role': role,
                'profile': profile,
            })

        email = form.cleaned_data.get('email')
        date_of_birth = form.cleaned_data.get('date_of_birth')
        sex = form.cleaned_data.get('sex')

        try:
            customer = user.customer
            if email:
                customer.email = email
            if date_of_birth:
                customer.date_of_birth = date_of_birth
            if sex:
                customer.sex = sex
            customer.save()
            messages.success(request, "Cập nhật thông tin cá nhân thành công!")
        except Exception as e:
            messages.error(request, f"Lỗi khi cập nhật thông tin: {str(e)}")

        return redirect('profile')
