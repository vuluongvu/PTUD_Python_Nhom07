from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages


# Create your views here.
def login_view(request):
    if request.method == 'POST':
        # The form uses 'username' for the email field
        username = request.POST.get('username') 
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Use first_name which is set during registration
            welcome_name = user.first_name or user.username
            messages.success(request, f"Chào mừng {welcome_name} quay trở lại!")
            return redirect('core:home')
        else:
            messages.error(request, "Email hoặc mật khẩu không đúng.")
            return redirect('users:login')
    return render(request, 'users/login.html')

def register_view(request):
    if request.method == 'POST':
        # 1. Lấy dữ liệu từ HTML dựa vào name="..."
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 2. Kiểm tra dữ liệu (Validation)
        
        # Kiểm tra mật khẩu nhập lại có khớp không
        if password != confirm_password:
            messages.error(request, "Mật khẩu nhập lại không khớp!")
            return redirect('users:register') # Load lại trang đăng ký
        
        # Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email này đã được đăng ký!")
            return redirect('users:register')

        # 3. Tạo User mới
        try:
            # Tạo user (dùng email làm username)
            user = User.objects.create_user(username=email, email=email, password=password)
            
            # Lưu họ tên (Django mặc định chia first_name/last_name, mình gộp tạm vào first_name)
            user.first_name = full_name
            user.save()

            # 4. Thành công -> Chuyển hướng sang trang đăng nhập
            messages.success(request, "Tạo tài khoản thành công! Vui lòng đăng nhập.")
            return redirect('users:login')
            
        except Exception as e:
            messages.error(request, "Có lỗi xảy ra trong quá trình đăng ký.")
            return redirect('users:register')

    # Nếu là GET (người dùng mới vào trang) thì hiện file HTML
    return render(request, 'users/register.html')