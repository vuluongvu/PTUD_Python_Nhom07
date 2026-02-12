from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
try:
    from core.models import Address, Order, Profile
except Exception:
    Address = None
    Order = None
    Profile = None

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username') 
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            welcome_name = user.first_name or user.username
            messages.success(request, f"Đăng nhập thành công! \n Xin chào  {welcome_name}.")
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
        if not all([full_name, email, password, confirm_password]):
            messages.error(request, "Vui lòng điền đầy đủ tất cả các trường.")
            return redirect('users:register')
        if '@' not in email or '.' not in email:
            messages.error(request, "Định dạng email không hợp lệ.")
            return redirect('users:register')
            
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
        from core.models import Profile, Address
    except Exception:
        Profile = None
        Address = None

    profile = None
    if Profile is not None:
        profile, created = Profile.objects.get_or_create(user=request.user)

    default_address = None
    if Address is not None:
        default_address = Address.objects.filter(user=request.user, is_default=True).first()

    if request.method == 'POST':
        # Cập nhật thông tin User
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()

        # Cập nhật thông tin Profile
        if profile:
            profile.phone_number = request.POST.get('phone_number', '')
            profile.save()

        # Cập nhật hoặc tạo địa chỉ mặc định
        if Address:
            address_data = {
                'street_address': request.POST.get('street_address'),
                'province_code': request.POST.get('province'),
                'district_code': request.POST.get('district'),
                'ward_code': request.POST.get('ward'),
                'is_default': True,
            }
            Address.objects.update_or_create(user=request.user, is_default=True, defaults=address_data)
        
        messages.success(request, "Cập nhật hồ sơ thành công!")
        return redirect('users:profile')

    context = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'default_address': default_address,
        'avatar': profile.avatar if profile and getattr(profile, 'avatar', None) else None,
        'phone_number': profile.phone_number if profile else '',
    }
    return render(request, 'users/profile.html', context)

#logout view
def logout_view(request):
    logout(request)
    messages.success(request, "Đăng xuất thành công!")
    return redirect('core:home')
@login_required
def order_list_view(request):
    """
    Hiển thị danh sách các đơn hàng của người dùng.
    """
    # Lấy trạng thái lọc từ query params của URL
    current_status = request.GET.get('status')

    orders_query = Order.objects.filter(user=request.user)

    # Lọc theo trạng thái nếu có
    if current_status and current_status in Order.Status.values:
        orders_query = orders_query.filter(order_status=current_status)

    orders = orders_query.order_by('-created_at')
    
    profile = None
    if Profile is not None:
        profile, created = Profile.objects.get_or_create(user=request.user)

    context = {
        'username': request.user.username,
        'first_name': request.user.first_name,
        'avatar': profile.avatar if profile and getattr(profile, 'avatar', None) else None,
        'orders': orders,
        'order_statuses': Order.Status.choices, # Gửi các trạng thái để hiển thị nút lọc
        'current_status': current_status,       # Gửi trạng thái đang lọc để active nút
    }
    return render(request, 'users/order-detail.html', context)

@login_required
def get_default_address_api(request):
    try:
        address = Address.objects.get(user=request.user, is_default=True)
        data = {
            'fullname': request.user.first_name,
            'phone': request.user.profile.phone_number,
            'province_code': address.province_code,
            'district_code': address.district_code,
            'ward_code': address.ward_code,
            'street_address': address.street_address,
        }
        return JsonResponse({'status': 'success', 'address': data})
    except (Address.DoesNotExist, Profile.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy địa chỉ mặc định hoặc hồ sơ.'}, status=404)

@login_required
def order_detail_view(request, order_id):
    """
    Hiển thị chi tiết một đơn hàng cụ thể.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    profile = None
    if Profile is not None:
        profile, created = Profile.objects.get_or_create(user=request.user)

    context = {
        'username': request.user.username,
        'first_name': request.user.first_name,
        'avatar': profile.avatar if profile and getattr(profile, 'avatar', None) else None,
        'order': order, # Truyền đơn hàng cụ thể vào context
    }
    # Sử dụng lại template order-detail.html nhưng chỉ hiển thị 1 đơn hàng
    return render(request, 'users/order-detail.html', context)

@login_required
def cancel_order_view(request, order_id):
    """
    Xử lý yêu cầu hủy đơn hàng của người dùng.
    """
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Chỉ cho phép hủy khi đơn hàng đang ở trạng thái "Chờ xác nhận"
        if order.order_status == Order.Status.PENDING:
            order.order_status = Order.Status.CANCELLED
            order.save()
            messages.success(request, f"Đơn hàng #{order.id} đã được hủy thành công.")
        else:
            messages.error(request, "Bạn không thể hủy đơn hàng này vì nó đã được xử lý.")
            
        return redirect('users:order_detail', order_id=order.id)
    
    return redirect('users:order_list')