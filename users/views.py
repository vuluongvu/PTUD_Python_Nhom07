from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
try:
    from core.models import Address
except Exception:
    Address = None


# Create your views here.


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username') 
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            welcome_name = user.first_name or user.username
            messages.success(request, f"Đăng nhập thành công! Chào mừng {welcome_name}.")
            return redirect('core:home')
        else:
            messages.error(request, "Email hoặc mật khẩu không đúng.")
            return redirect('users:login')
    return render(request, 'users/login.html')

def register_view(request):
    if request.method == 'POST':
        # lấy form data name
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Server-side validation
        if password != confirm_password:
            messages.error(request, "Mật khẩu và xác nhận mật khẩu không khớp.")
            return redirect('users:register')
        if not password or len(password) < 8:
            messages.error(request, "Mật khẩu cần ít nhất 8 ký tự.")
            return redirect('users:register')

        # Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email này đã được đăng ký!")
            return redirect('users:register')

        try:
            # Tạo user (dùng email làm username)
            user = User.objects.create_user(username=email, email=email, password=password)
            
            user.first_name = full_name
            user.save()

            messages.success(request, "Tạo tài khoản thành công! Vui lòng đăng nhập.")
            return redirect('users:login')
            
        except Exception as e:
            messages.error(request, "Có lỗi xảy ra trong quá trình đăng ký.")
            return redirect('users:register')
        
    return render(request, 'users/register.html')

# profile view
@login_required
def profile_view(request):
    try:
        from core.models import Profile
    except Exception:
        Profile = None

    profile = None
    if Profile is not None:
        profile, created = Profile.objects.get_or_create(user=request.user)

    context = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'address': Address.objects.filter(user=request.user) if Address else [],
        'avatar': profile.avatar if profile and getattr(profile, 'avatar', None) else None,
        'phone_number': profile.phone_number if profile and getattr(profile, 'phone_number', None) else '',
    }
    return render(request, 'users/profile.html', context)

#logout view
def logout_view(request):
    logout(request)
    messages.success(request, "Đăng xuất thành công!")
    return redirect('core:home')