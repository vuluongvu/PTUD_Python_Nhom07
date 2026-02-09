from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from core.views import toggle_wishlist
from core.models import WishList
app_name = 'orders'

# Create your views here.

def view_cart(request):
    """View hiển thị giỏ hàng."""
    # This view will eventually need to fetch cart data
    # For now, we pass an empty context
    return render(request, 'orders/cart.html')

def checkout(request):
    """View for the checkout page."""
    return render(request, 'orders/checkout.html')

@login_required
def wishlist_list(request):
    # Lấy danh sách item, dùng select_related để load thông tin product nhanh hơn
    items = WishList.objects.filter(user=request.user).select_related('product')
    return render(request, 'orders/wishlist.html', {'wishlist': items})



    