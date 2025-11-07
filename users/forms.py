from pyexpat import errors
from django import forms

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from datetime import date

# Kiểm tra định dạng email
def is_valid_email(email):
    
    try:
        validate_email(email)
    except ValidationError:
        return  False
    else:
        return True

def validate_username_and_otp(cleaned_data, initial_data):
    username = cleaned_data.get('username')
    otp = cleaned_data.get('otp')
    
    errors = {}

    if not is_valid_email(username):
        errors['username'] = "Email không hợp lệ."

    # Kiểm tra mã OTP nếu đã gửi
    if 'otp_sent' in cleaned_data and not otp:
        errors['otp'] = "Vui lòng nhập mã OTP đã gửi."

    if otp and otp != initial_data.get('otp', ''):
        errors['otp'] = "Mã OTP không chính xác."
    
    return errors


class SignUpForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Tên đăng nhập',
            'id': 'username_SignUp'
        })
    )
    email = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nhập email',
            'id': 'email'
        })
    )
    
    sex = forms.ChoiceField(
        choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')],
        required=True,
        widget=forms.Select(attrs={
            'id': 'sex'  
        })
    )

    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'id': 'date_of_birth'
        })  
    )

    password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mật khẩu',
            'id': 'id_password'
        })
    )
    confirm_password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nhập lại mật khẩu',
            'id': 'id_confirm_password'
        })
    )
    


    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        

        #  Biến để lưu lỗi
        errors = {}

        if not is_valid_email(email):
            errors['email'] = "Email không hợp lệ."
        
        # Kiểm tra tên người dùng
        if  User.objects.filter(username=username).exists():
            errors['username'] = "Người dùng đã tồn tại."

        if User.objects.filter(email=email).exists():
            errors['email'] = "Email này đã được sử dụng."

        if password and confirm_password and password != confirm_password:
            errors['confirm_password'] = "Mật khẩu không khớp."

            
        # Nếu có lỗi, thêm vào biểu mẫu
        for field, error in errors.items():
            self.add_error(field, error)

        return cleaned_data  # Trả về dữ liệu đã làm sạch
    




class SignInForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Tên đăng nhập',
            'id': 'username'
        })
    )
    password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mật khẩu',
            'id': 'id_password'
        })
    )

    # Nếu bạn vẫn muốn kiểm tra group, thì chỉ check khi user đã xác thực
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("Tài khoản chưa đăng ký.")
        return username

    
    
class ForgotPasswordForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Tên đăng nhập',
            'id': 'id_username_ForgotPassword'

        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        errors = {}

        if not User.objects.filter(username = username).exists():
            errors['username'] = "Người dùng không tồn tại."

       
        user = User.objects.filter(username=username).first()
        if user and user.groups.filter(name='Customer').exists():
            if not is_valid_email(username):
                errors['username'] = "Email không hợp lệ."

        for field, error in errors.items():
            self.add_error(field, error)

        return cleaned_data
    
class NewPasswordForm(forms.Form):
    new_password = forms.CharField(
        max_length=128,
        required=True,   
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nhập mật khẩu mới',
            'id': 'id_new_password'
        })
    )
    confirm_new_password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nhập lại mật khẩu',
            'id': 'id_confirm_new_password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")

        errors = {}
        if  new_password != confirm_new_password:
            errors['confirm_new_password'] = "Mật khẩu không khớp."

        for field, error in errors.items():
            self.add_error(field, error)

        return cleaned_data  # Trả về dữ liệu đã làm sạch

class FormChinhSuaThongTinCaNhan(forms.Form):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'id': 'email_UpdateForm',
            'class': 'form-control'
        })
    )

    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'placeholder': 'Ngày sinh',
            'id': 'dob_UpdateForm',
            'class': 'form-control'
        })
    )

    sex = forms.ChoiceField(
        required=False,
        choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')],
        widget=forms.Select(attrs={
            'id': 'sex_UpdateForm',
            'class': 'form-select'
        })
    )

    def __init__(self, *args, **kwargs):
        """Nhận user đang đăng nhập để điền thông tin hiện tại vào form."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Nếu user có hồ sơ Customer thì hiển thị thông tin hiện tại
        if self.user and hasattr(self.user, 'customer'):
            customer = self.user.customer
            self.fields['email'].initial = customer.email
            self.fields['sex'].initial = customer.sex
            if customer.date_of_birth:
                self.fields['date_of_birth'].initial = customer.date_of_birth

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        date_of_birth = cleaned_data.get("date_of_birth")
        errors = {}

        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors["email"] = "Email không hợp lệ."

        if date_of_birth and date_of_birth > date.today():
            errors["date_of_birth"] = "Ngày sinh không được lớn hơn ngày hiện tại."

        for field, error in errors.items():
            self.add_error(field, error)

        return cleaned_data