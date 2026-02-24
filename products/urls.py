from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('product-detail/<slug:slug>/', views.product_detail, name='product-detail'),
    path('view-all-products/', views.view_all_products, name='view-all-products'),
    path('search-results/', views.search_results, name='search-results'),
    path('toggle-cart/', views.toggle_cart, name='toggle_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
]