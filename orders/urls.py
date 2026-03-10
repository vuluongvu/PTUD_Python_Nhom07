from django.urls import path
from . import views
from core import views as core_views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.view_cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('wishlist/', views.wishlist_list, name='wishlist'), # Trang hiển thị danh sách
    path('toggle-wishlist/', core_views.toggle_wishlist, name='toggle_wishlist'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    
    # --- MoMo Payment Routes ---
    path('momo/return/', views.momo_return, name='momo_return'),   # MoMo redirect user về đây
    path('momo/ipn/', views.momo_ipn, name='momo_ipn'),            # MoMo gửi IPN callback
]
