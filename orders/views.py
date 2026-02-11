from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from core.views import toggle_wishlist
from core.models import Product, WishList, Cart
from django.db.models import Q, Count
app_name = 'orders'

# Create your views here.

# -------------------view cart----------------------- 
def view_cart(request):
    # Nếu người dùng chưa đăng nhập, hiển thị trang giỏ hàng trống
    if not request.user.is_authenticated:
        return render(request, 'orders/cart.html', {
            'cart_items': [],
            'product_count': 0,
            'needs_login': True
        })

    # Lấy giỏ hàng của người dùng. Nếu không có, tạo một giỏ hàng trống.
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Lấy tất cả các sản phẩm (CartItem) trong giỏ hàng đó
    cart_items = user_cart.items.select_related('product').prefetch_related('product__images').all()
    
    # Tính tổng tiền
    total_amount = 0
    for item in cart_items:
        total_amount += item.product.final_price * item.quantity

    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'product_count': cart_items.count(),
        'total_amount': total_amount,
    })

# -------------------checkout--------------------------- 
@login_required
def checkout(request):
    """View for the checkout page."""
    try:
        user_cart = Cart.objects.get(user=request.user)
        cart_items = user_cart.items.select_related('product').prefetch_related('product__images').all()
        if not cart_items:
            # Nếu giỏ hàng trống, không cho vào checkout
            return redirect('orders:cart')
    except Cart.DoesNotExist:
        # Nếu không có giỏ hàng, cũng không cho vào
        return redirect('orders:cart')

    # Tính tổng tiền
    total_amount = sum(item.product.final_price * item.quantity for item in cart_items)

    context = {
        'cart_items': cart_items,
        'product_count': cart_items.count(),
        'total_amount': total_amount,
    }
    return render(request, 'orders/checkout.html', context)


# -------------------view wishlist----------------------- 
def wishlist_list(request):
    if not request.user.is_authenticated:
        # Nếu chưa login, vẫn cho vào trang nhưng wishlist sẽ trống
        return render(request, 'orders/wishlist.html', {
            'wishlist': [],
            'needs_login': True # Gửi thêm biến này để template xử lý
        })
    
    user_wishlist = WishList.objects.filter(user=request.user).select_related('product')
    product_count = user_wishlist.count()
    return render(request, 'orders/wishlist.html', {
        'wishlist': user_wishlist, 
        'product_count': product_count,
        })
