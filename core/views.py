from django.shortcuts import render
from .models import Product, WishList
from django.http import JsonResponse
from django.shortcuts import get_object_or_404 
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q


def home(request):
    products = Product.objects.all()
    wishlist_ids = []
    if request.user.is_authenticated:
        # Lấy list các ID sản phẩm đã thích
        wishlist_ids = WishList.objects.filter(user=request.user).values_list('product_id', flat=True)
    components = Product.objects.filter(Q(is_vga=True) | Q(is_cpu=True) | Q(is_ram=True))[:5]
    return render(request, 'core/home.html', {'products': products, 'components': components, 'wishlist_ids': wishlist_ids})

@login_required # Đảm bảo chỉ user đã đăng nhập mới xem được
def wishlist_list(request):
    # Lấy tất cả các item trong wishlist của user hiện tại
    # Dùng select_related('product') để tối ưu query (lấy luôn thông tin sản phẩm)
    user_wishlist = WishList.objects.filter(user=request.user).select_related('product')
    
    return render(request, 'users/wishlist.html', {
        'wishlist': user_wishlist
    })
    
def toggle_wishlist(request):
    # Kiểm tra xem user đã đăng nhập chưa
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Bạn phải đăng nhập để thêm sản phẩm vào danh sách yêu thích!'
        }, status=200)

    if request.method == "POST":
        product_id = request.POST.get('id')
        product = get_object_or_404(Product, id=product_id)
        
        wishlist_item = WishList.objects.filter(user=request.user, product=product)

        if wishlist_item.exists():
            wishlist_item.delete()
            status = 'removed'
            message = 'Đã xóa khỏi danh sách yêu thích.'
        else:
            WishList.objects.create(user=request.user, product=product)
            status = 'added'
            message = 'Đã thêm vào danh sách yêu thích!'
            
        return JsonResponse({'status': status, 'message': message})