from django.urls import path
from . import views
from core import views as core_views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.view_cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('wishlist/', views.wishlist_list, name='wishlist'), # Trang hiển thị danh sách
    path('toggle-wishlist/', core_views.toggle_wishlist, name='toggle_wishlist'),
]
